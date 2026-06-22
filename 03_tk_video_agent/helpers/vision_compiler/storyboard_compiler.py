"""Baseline-anchored storyboard compiler for P12W."""

from __future__ import annotations

from copy import deepcopy
from pathlib import Path
from typing import Any

from .quality_gate import strict_dominance


def build_incumbent_timeline(p12t_report: dict[str, Any]) -> dict[str, Any]:
    slate = deepcopy(p12t_report["selected_slate"])
    slate["incumbent_timeline"] = True
    slate["source"] = "P12T"
    return slate


def candidate_from_p12u_slot(p12u_report: dict[str, Any], role: str) -> dict[str, Any] | None:
    for shot in p12u_report["selected_slate"]["shots"]:
        if str(shot.get("role")) == role:
            candidate = deepcopy(shot)
            candidate["candidate_source"] = "P12U_positive_reference"
            return candidate
    return None


def compile_variant(
    variant_id: str,
    p12t_report: dict[str, Any],
    p12u_report: dict[str, Any] | None,
    replacement_roles: list[str],
    vlm_slot_results: dict[str, dict[str, Any]],
    technical_by_file: dict[str, dict[str, Any]],
) -> dict[str, Any]:
    incumbent = build_incumbent_timeline(p12t_report)
    selected = deepcopy(incumbent)
    selected["variant_id"] = variant_id
    selected["slate_id"] = f"{variant_id}_P12W"
    selected["strategy"] = "p12w_baseline_anchored_controlled_replacement"
    selected["p12t_incumbent_timeline"] = True
    selected["replacement_attempts"] = []
    replacements = 0
    for index, baseline_shot in enumerate(list(selected["shots"])):
        role = str(baseline_shot.get("role"))
        if role not in replacement_roles or p12u_report is None or replacements >= 2:
            continue
        candidate = candidate_from_p12u_slot(p12u_report, role)
        if not candidate:
            continue
        baseline_asset = technical_by_file.get(str(baseline_shot["file"]).replace(".MOV", ""), {})
        candidate_asset = technical_by_file.get(str(candidate["file"]).replace(".MOV", ""), {})
        candidate_eval = {
            "technical_score": candidate_asset.get("technical_quality_score", 0.0),
            "local_score": candidate_asset.get("technical_quality_score", 0.0) + 5.0,
            "temporal_artifact_detected": bool(candidate_asset.get("artifact_summary", {}).get("reject_reason")),
            "hand_present": bool(candidate.get("hand_present", False)),
            "human_face_present": bool(candidate.get("human_face_present", False)),
            "human_body_present": bool(candidate.get("human_body_present", False)),
            "action_complete": bool(candidate.get("action_complete", candidate.get("action_completeness", "complete") == "complete")),
        }
        baseline_eval = {
            "technical_score": baseline_asset.get("technical_quality_score", 0.0),
            "local_score": baseline_asset.get("technical_quality_score", 0.0),
        }
        vlm = vlm_slot_results.get(f"{variant_id}:{role}", {})
        dominance = strict_dominance(candidate_eval, baseline_eval, vlm)
        attempt = {
            "role": role,
            "baseline_file": baseline_shot["file"],
            "candidate_file": candidate["file"],
            "candidate_from": candidate.get("candidate_source"),
            "dominance": dominance,
        }
        selected["replacement_attempts"].append(attempt)
        if dominance["accepted"]:
            candidate["role"] = baseline_shot["role"]
            candidate["duration_ms"] = baseline_shot["duration_ms"]
            candidate["source_duration_ms"] = baseline_shot.get("source_duration_ms", baseline_shot["duration_ms"])
            candidate["target_frames"] = baseline_shot.get("target_frames")
            candidate["visual_start_ms"] = baseline_shot["visual_start_ms"]
            candidate["visual_end_ms"] = baseline_shot["visual_end_ms"]
            candidate["p12w_replacement_of"] = baseline_shot["file"]
            selected["shots"][index] = candidate
            replacements += 1
    selected["replacement_count"] = replacements
    selected["fallback_to_p12t"] = replacements == 0
    selected["kept_p12t_slot_count"] = len(selected["shots"]) - replacements
    return selected


def planned_replacement_roles(variant_id: str) -> list[str]:
    if variant_id == "V2A_feature_proof":
        return ["demonstration_proof_continuous", "proof"]
    if variant_id == "V3A_lifestyle_value":
        return ["situation", "lifestyle_payoff"]
    return []


def report_paths_for_variants(directory: Path, suffix: str) -> dict[str, Path]:
    return {path.name.replace(suffix, ""): path for path in directory.glob(f"*{suffix}")}
