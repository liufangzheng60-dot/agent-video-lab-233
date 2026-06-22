"""Deterministic physical and topology gates for P12W."""

from __future__ import annotations

from typing import Any


MOTION_MATCH_DEFAULT_WEIGHT = 0.03
MOTION_MATCH_MAX_WEIGHT = 0.05
DOMINANCE_MARGIN_MIN = 6.0


def motion_weight(weight: float = MOTION_MATCH_DEFAULT_WEIGHT) -> float:
    return min(float(weight), MOTION_MATCH_MAX_WEIGHT)


def reject_by_exclusion(candidate: dict[str, Any], exclusions: list[dict[str, Any]]) -> tuple[bool, str]:
    source = str(candidate.get("file", "")).replace(".MOV", "")
    start = int(candidate.get("source_start_ms", 0))
    end = start + int(candidate.get("source_duration_ms", candidate.get("duration_ms", 0)))
    for item in exclusions:
        if str(item.get("source_video_id")) != source:
            continue
        if str(item.get("severity")) != "fatal":
            continue
        overlap = min(end, int(item["end_ms"])) - max(start, int(item["start_ms"]))
        if overlap > 50:
            return True, f"fatal exclusion overlap: {item.get('violation_type')}"
    return False, ""


def temporal_hard_gate(report: dict[str, Any]) -> tuple[bool, list[str]]:
    reasons: list[str] = []
    if report.get("temporal_artifact_detected"):
        reasons.append("temporal_artifact_detected")
    if report.get("abab_frame_ranges"):
        reasons.append("ABAB_frame_pattern")
    if len(report.get("glitch_risk_ranges", [])) > 0:
        reasons.append("glitch_risk_ranges")
    return not reasons, reasons


def topology_valid(variant_id: str, shots: list[dict[str, Any]]) -> tuple[bool, list[str]]:
    roles = [str(shot.get("role", "")).lower() for shot in shots]
    errors: list[str] = []
    if variant_id.startswith("V1"):
        if not any("pain" in role for role in roles):
            errors.append("missing_problem_state")
        if not any(role in {"outcome", "product_use"} or "outcome" in role for role in roles):
            errors.append("missing_success_result")
    if variant_id.startswith("V2"):
        if not any("feature" in role for role in roles):
            errors.append("missing_feature")
        if not any("proof" in role for role in roles):
            errors.append("missing_proof")
    if variant_id.startswith("V3"):
        if not any("usage" in role or "transformation" in role for role in roles):
            errors.append("missing_usage_or_transformation")
        if not any("payoff" in role or "closure" in role for role in roles):
            errors.append("missing_payoff_or_closure")
    return not errors, errors


def strict_dominance(candidate: dict[str, Any], baseline: dict[str, Any], vlm: dict[str, Any], *, margin_min: float = DOMINANCE_MARGIN_MIN) -> dict[str, Any]:
    hard_reasons: list[str] = []
    if candidate.get("hand_present") or candidate.get("human_face_present") or candidate.get("human_body_present"):
        hard_reasons.append("semantic_hygiene_fail")
    if candidate.get("temporal_artifact_detected"):
        hard_reasons.append("temporal_artifact_fail")
    if not candidate.get("action_complete", True):
        hard_reasons.append("action_incomplete")
    if candidate.get("technical_score", 0) < baseline.get("technical_score", 0) - 3:
        hard_reasons.append("technical_quality_below_baseline")
    vlm_margin = float(vlm.get("dominance_margin", 0.0) or 0.0)
    local_margin = float(candidate.get("local_score", 0.0)) - float(baseline.get("local_score", 0.0))
    margin = round(max(vlm_margin, local_margin), 2)
    soft_wins = int(vlm.get("soft_win_count", 0) or 0)
    accepted = not hard_reasons and margin >= margin_min and soft_wins >= 2
    return {
        "accepted": accepted,
        "dominance_margin": margin,
        "dominance_margin_min": margin_min,
        "soft_win_count": soft_wins,
        "hard_reasons": hard_reasons,
        "fallback_to_p12t": not accepted,
    }
