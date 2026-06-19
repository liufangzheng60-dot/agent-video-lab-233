"""Minimal P12C phase guard for autonomous Codex operation."""

from __future__ import annotations

from typing import Any


ALLOW = "allow"
OWNER_REVIEW_REQUIRED = "owner_review_required"
BLOCK = "block"


OWNER_GATE_TYPES = {
    "hard_rule_change": "GATE_HARD_RULE_CHANGE",
    "architecture_breaking_change": "GATE_ARCHITECTURE_BREAKING_CHANGE",
    "external_provider_enable": "GATE_EXTERNAL_PROVIDER_ENABLE",
    "real_batch_launch": "GATE_REAL_BATCH_LAUNCH",
    "release_or_publish": "GATE_RELEASE_OR_PUBLISH",
    "security_relaxation": "GATE_SECURITY_RELAXATION",
}

BLOCKED_TYPES = {
    "force_push",
    "history_rewrite",
    "raw_video_delete",
    "raw_video_move",
    "raw_video_overwrite",
    "auto_publish",
    "staged_media",
    "secret_staged",
}


def evaluate_phase_action(action: dict[str, Any]) -> dict[str, Any]:
    """Classify an intended action as allow, owner review, or block."""
    action_type = action.get("type", "ordinary_code_change")
    if action.get("prohibited_staged_files"):
        return _block("GATE_SECURITY_RELAXATION", "Prohibited files are staged.", action)
    if action_type in BLOCKED_TYPES:
        return _block(_gate_for_block(action_type), f"Blocked unsafe action: {action_type}", action)
    if action_type in OWNER_GATE_TYPES:
        return _owner_review(OWNER_GATE_TYPES[action_type], f"Mandatory Owner gate: {OWNER_GATE_TYPES[action_type]}", action)
    if action.get("enable_real_vlm"):
        return _owner_review("GATE_EXTERNAL_PROVIDER_ENABLE", "Real VLM enablement requires Owner approval.", action)
    if action.get("real_batch2") and int(action.get("variants", 0)) >= 12:
        return _owner_review("GATE_REAL_BATCH_LAUNCH", "First real Batch2 12+ video production requires Owner approval.", action)
    if action.get("auto_publish"):
        return _block("GATE_RELEASE_OR_PUBLISH", "Automatic publishing is blocked.", action)
    return {"result": ALLOW, "checkpoint_type": None, "reason": "Ordinary safe action.", "action": action}


def _owner_review(checkpoint_type: str, reason: str, action: dict[str, Any]) -> dict[str, Any]:
    return {"result": OWNER_REVIEW_REQUIRED, "checkpoint_type": checkpoint_type, "reason": reason, "action": action}


def _block(checkpoint_type: str, reason: str, action: dict[str, Any]) -> dict[str, Any]:
    return {"result": BLOCK, "checkpoint_type": checkpoint_type, "reason": reason, "action": action}


def _gate_for_block(action_type: str) -> str:
    if action_type in {"staged_media", "secret_staged"}:
        return "GATE_SECURITY_RELAXATION"
    if action_type == "auto_publish":
        return "GATE_RELEASE_OR_PUBLISH"
    return "GATE_DESTRUCTIVE_ACTION"
