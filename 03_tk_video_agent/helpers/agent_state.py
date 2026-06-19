"""P12 runtime agent state model and JSON helpers."""

from __future__ import annotations

import json
import os
from dataclasses import asdict, dataclass, field, fields
from datetime import datetime, timezone
from pathlib import Path
from typing import Any


def utc_now_iso() -> str:
    return datetime.now(timezone.utc).replace(microsecond=0).isoformat()


@dataclass
class AgentState:
    """Serializable state for the P12 Agent Factory runtime harness."""

    product: str
    sku: str
    material_batch: str
    variants_requested: int
    current_stage: str = "draft"
    stage_status: dict[str, str] = field(default_factory=dict)
    hard_rule_results: dict[str, Any] = field(default_factory=dict)
    media_asset_guard_results: dict[str, Any] = field(default_factory=dict)
    vlm_qc_results: dict[str, Any] = field(default_factory=dict)
    owner_firewall_status: dict[str, Any] = field(default_factory=lambda: {"status": "not_started"})
    pipeline_status: str = "draft"
    output_paths: dict[str, str] = field(default_factory=dict)
    failed_variants: list[str] = field(default_factory=list)
    rerun_history: list[dict[str, Any]] = field(default_factory=list)
    final_review_pack_path: str | None = None
    current_goal: str | None = None
    active_task: str | None = None
    awaiting_owner_review: bool = False
    pending_checkpoint: dict[str, Any] | None = None
    last_owner_decision: dict[str, Any] | None = None
    resume_instruction: str | None = None
    last_safe_commit: str | None = None
    next_recommended_action: str | None = None
    vertical_output_guard_status: dict[str, Any] = field(default_factory=dict)
    segment_replacement_attempts: dict[str, int] = field(default_factory=dict)
    created_at: str = field(default_factory=utc_now_iso)
    updated_at: str = field(default_factory=utc_now_iso)

    def mark_stage(self, stage: str, status: str) -> None:
        self.current_stage = stage
        self.stage_status[stage] = status
        self.touch()

    def touch(self) -> None:
        self.updated_at = utc_now_iso()

    def to_dict(self) -> dict[str, Any]:
        return asdict(self)

    @classmethod
    def from_dict(cls, payload: dict[str, Any]) -> "AgentState":
        allowed = {item.name for item in fields(cls)}
        compatible_payload = {key: value for key, value in payload.items() if key in allowed}
        return cls(**compatible_payload)

    def write_json(self, path: Path | str) -> Path:
        output_path = Path(path)
        output_path.parent.mkdir(parents=True, exist_ok=True)
        temp_path = output_path.with_name(output_path.name + ".tmp")
        with temp_path.open("w", encoding="utf-8") as handle:
            handle.write(json.dumps(self.to_dict(), indent=2, ensure_ascii=False) + "\n")
            handle.flush()
            os.fsync(handle.fileno())
        os.replace(temp_path, output_path)
        return output_path


def load_agent_state(path: Path | str) -> AgentState:
    payload = json.loads(Path(path).read_text(encoding="utf-8"))
    return AgentState.from_dict(payload)
