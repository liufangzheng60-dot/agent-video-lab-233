"""P12 VLM QC sidecar skeleton.

This module intentionally does not call Gemini in P12B. VLM output can hold or
reject candidates, but it cannot bypass hard rules or Owner firewall decisions.
"""

from __future__ import annotations

import json
import os
import hashlib
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


SEMANTIC_LABEL_SCHEMA_VERSION = "p12e_semantic_label_v1"

SEMANTIC_LABEL_SCHEMA = {
    "type": "object",
    "required": [
        "clip_id",
        "start_ms",
        "end_ms",
        "primary_action",
        "secondary_action",
        "dog_present",
        "dog_identity",
        "dog_motion_direction",
        "product_present",
        "product_state",
        "product_visibility",
        "shot_scale",
        "camera_motion",
        "room_or_scene",
        "action_completeness",
        "safe_vertical_crop",
        "hook_strength",
        "emotional_tone",
        "segment_role_candidates",
        "claim_evidence_candidates",
        "continuity_keys",
        "quality_risks",
        "requires_video_review",
        "confidence",
        "provider",
        "model",
        "schema_version",
    ],
    "properties": {
        "clip_id": {"type": "string"},
        "start_ms": {"type": "integer"},
        "end_ms": {"type": "integer"},
        "primary_action": {"type": "string"},
        "secondary_action": {"type": "string"},
        "dog_present": {"type": "boolean"},
        "dog_identity": {"type": "string"},
        "dog_motion_direction": {"type": "string"},
        "product_present": {"type": "boolean"},
        "product_state": {"type": "string"},
        "product_visibility": {"type": "string"},
        "shot_scale": {"type": "string"},
        "camera_motion": {"type": "string"},
        "room_or_scene": {"type": "string"},
        "action_completeness": {"type": "string"},
        "safe_vertical_crop": {"type": "boolean"},
        "hook_strength": {"type": "number"},
        "emotional_tone": {"type": "string"},
        "segment_role_candidates": {
            "type": "array",
            "items": {
                "enum": [
                    "hook_problem",
                    "hook_result",
                    "hook_contrast",
                    "hook_transformation",
                    "pain",
                    "intervention",
                    "outcome",
                    "feature",
                    "demonstration",
                    "proof",
                    "situation",
                    "usage",
                    "lifestyle_payoff",
                    "closure_result",
                    "closure_hero",
                    "closure_cta",
                ]
            },
        },
        "claim_evidence_candidates": {"type": "array", "items": {"type": "string"}},
        "continuity_keys": {"type": "array", "items": {"type": "string"}},
        "quality_risks": {"type": "array", "items": {"type": "string"}},
        "requires_video_review": {"type": "boolean"},
        "confidence": {"type": "number"},
        "provider": {"type": "string"},
        "model": {"type": "string"},
        "schema_version": {"type": "string"},
    },
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


def build_semantic_vlm_cache_key(
    *,
    asset_hash: str,
    window_start_ms: int,
    window_end_ms: int,
    prompt_schema_version: str,
    provider: str,
    model: str,
    media_resolution: str,
    proxy_version: str,
) -> str:
    basis = {
        "asset_hash": asset_hash,
        "window_start_ms": window_start_ms,
        "window_end_ms": window_end_ms,
        "prompt_schema_version": prompt_schema_version,
        "provider": provider,
        "model": model,
        "media_resolution": media_resolution,
        "proxy_version": proxy_version,
    }
    return hashlib.sha256(json.dumps(basis, sort_keys=True).encode("utf-8")).hexdigest()


def build_semantic_cache_record(
    *,
    cache_key: str,
    provider: str,
    model: str,
    input_type: str,
    parsed_result: dict[str, Any] | None = None,
    token_usage: dict[str, int] | None = None,
    estimated_cost: float = 0.0,
    retry_count: int = 0,
    schema_version: str = SEMANTIC_LABEL_SCHEMA_VERSION,
) -> dict[str, Any]:
    return {
        "cache_key": cache_key,
        "provider": provider,
        "model": model,
        "input_type": input_type,
        "result_status": "pass" if parsed_result else "pending",
        "parsed_result": parsed_result or {},
        "token_usage": token_usage or {"input_tokens": 0, "output_tokens": 0},
        "estimated_cost": estimated_cost,
        "retry_count": retry_count,
        "schema_version": schema_version,
    }


def estimate_semantic_vlm_plan(windows: list[dict[str, Any]], config: dict[str, Any]) -> dict[str, Any]:
    """Estimate Pass 1/Pass 2 request volume without uploading or calling VLM."""
    provider = str(config.get("provider") or "owner_selected_provider")
    model = str(config.get("model") or "owner_selected_model")
    pass1_enabled = bool(config.get("pass1_enabled", True))
    pass2_enabled = bool(config.get("pass2_enabled", True))
    pass2_max_windows = int(config.get("pass2_max_windows", 8))
    max_calls = int(config.get("max_calls", 0) or 0)
    pass1_requests = len(windows) if pass1_enabled else 0
    pass2_requests = min(pass2_max_windows, max(0, len(windows) // 3)) if pass2_enabled else 0
    total_requests = pass1_requests + pass2_requests
    if max_calls:
        total_requests = min(total_requests, max_calls)
    estimated_input_tokens = pass1_requests * int(config.get("pass1_input_tokens_per_call", 900)) + pass2_requests * int(config.get("pass2_input_tokens_per_call", 1800))
    estimated_output_tokens = total_requests * int(config.get("output_tokens_per_call", 450))
    max_budget = float(config.get("max_budget", 0.0) or 0.0)
    return {
        "provider": provider,
        "model": model,
        "media_resolution": config.get("media_resolution", "keyframe_strip_low_resolution"),
        "pass1_enabled": pass1_enabled,
        "pass2_enabled": pass2_enabled,
        "pass1_estimated_requests": pass1_requests,
        "pass2_max_requests": pass2_requests,
        "max_calls": max_calls or total_requests,
        "estimated_keyframe_uploads": pass1_requests,
        "estimated_video_proxy_uploads": pass2_requests,
        "upload_audio": bool(config.get("upload_audio", False)),
        "estimated_input_tokens": estimated_input_tokens,
        "estimated_output_tokens": estimated_output_tokens,
        "estimated_cost_range": {"low": 0.0, "high": max_budget},
        "max_budget": max_budget,
        "cache_enabled": bool(config.get("cache_enabled", True)),
        "schema_version": SEMANTIC_LABEL_SCHEMA_VERSION,
        "requires_owner_gate": True,
        "real_api_called": False,
        "media_uploaded": False,
    }
