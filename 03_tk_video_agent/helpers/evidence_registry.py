"""Append-only JSONL evidence registry for P12C operator events."""

from __future__ import annotations

import json
from pathlib import Path
from typing import Any

from helpers.agent_state import utc_now_iso


ALLOWED_EVENT_TYPES = {
    "code_change",
    "test_result",
    "git_safety_result",
    "checkpoint_created",
    "owner_decision",
    "resume",
    "vlm_result",
    "batch_launch",
}


def append_evidence(path: Path | str, event_type: str, payload: dict[str, Any]) -> Path:
    if event_type not in ALLOWED_EVENT_TYPES:
        raise ValueError(f"Unsupported evidence event type: {event_type}")
    output = Path(path)
    output.parent.mkdir(parents=True, exist_ok=True)
    record = {"event_type": event_type, "created_at": utc_now_iso(), "payload": payload}
    with output.open("a", encoding="utf-8") as handle:
        handle.write(json.dumps(record, ensure_ascii=False) + "\n")
    return output
