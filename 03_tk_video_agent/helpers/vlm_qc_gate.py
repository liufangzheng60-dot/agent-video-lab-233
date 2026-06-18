"""P12 VLM QC sidecar skeleton.

This module intentionally does not call Gemini in P12B. VLM output can hold or
reject candidates, but it cannot bypass hard rules or Owner firewall decisions.
"""

from __future__ import annotations

import json
import os
from pathlib import Path
from typing import Any


VLM_QC_SCHEMA = {
    "type": "object",
    "required": [
        "variant_id",
        "hook_has_reason",
        "human_hand_problem",
        "clutter_problem",
        "product_visible",
        "feature_destroyed_by_crop",
        "body_too_repetitive",
        "audio_natural",
        "decision",
        "risk_flags",
        "notes",
    ],
    "properties": {
        "variant_id": {"type": "string"},
        "hook_has_reason": {"type": "boolean"},
        "human_hand_problem": {"type": "boolean"},
        "clutter_problem": {"type": "boolean"},
        "product_visible": {"type": "boolean"},
        "feature_destroyed_by_crop": {"type": "boolean"},
        "body_too_repetitive": {"type": "boolean"},
        "audio_natural": {"type": "boolean"},
        "decision": {"enum": ["approve", "hold", "reject"]},
        "risk_flags": {"type": "array", "items": {"type": "string"}},
        "notes": {"type": "string"},
    },
}


TIMEOUT_RETRY_HOLD_POLICY = {
    "timeout_seconds": 45,
    "max_retries": 1,
    "provider_failure_decision": "hold",
    "hard_rule_override_allowed": False,
    "owner_override_required_for_hold": True,
}


def compress_to_qc_draft(
    source_video: Path | str,
    output_path: Path | str,
    *,
    dry_run: bool = True,
) -> dict[str, Any]:
    """Plan a low-bitrate QC draft. P12B dry-run does not invoke ffmpeg."""
    source = Path(source_video)
    output = Path(output_path)
    plan = {
        "status": "planned" if dry_run else "not_implemented",
        "dry_run": dry_run,
        "source_video": str(source),
        "qc_draft_path": str(output),
        "target_resolution": "480p",
        "target_fps": "5-6",
        "target_size_mb": "1-3",
        "message": "P12B sidecar skeleton only; no draft media was generated.",
    }
    return plan


def audit_video_via_vlm(
    variant_id: str,
    video_path: Path | str,
    *,
    dry_run: bool = True,
    api_key_env: str = "GEMINI_API_KEY",
) -> dict[str, Any]:
    """Return a strict-schema hold result unless a future real provider is wired."""
    risk_flags = ["vlm_dry_run"] if dry_run else []
    if not os.environ.get(api_key_env):
        risk_flags.append("missing_gemini_api_key")
    return {
        "variant_id": variant_id,
        "hook_has_reason": False,
        "human_hand_problem": False,
        "clutter_problem": False,
        "product_visible": False,
        "feature_destroyed_by_crop": False,
        "body_too_repetitive": False,
        "audio_natural": False,
        "decision": "hold",
        "risk_flags": risk_flags,
        "notes": f"No real VLM call was made for {video_path}. Hard rules and Owner Firewall remain authoritative.",
    }


def write_vlm_policy(path: Path | str) -> Path:
    output = Path(path)
    output.parent.mkdir(parents=True, exist_ok=True)
    payload = {"schema": VLM_QC_SCHEMA, "timeout_retry_hold_policy": TIMEOUT_RETRY_HOLD_POLICY}
    output.write_text(json.dumps(payload, indent=2, ensure_ascii=False) + "\n", encoding="utf-8")
    return output
