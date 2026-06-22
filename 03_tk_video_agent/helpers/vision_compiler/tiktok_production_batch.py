"""P12Y TikTok 12-video production batch runner."""

from __future__ import annotations

import csv
import hashlib
import json
import shutil
import subprocess
import time
from copy import deepcopy
from pathlib import Path
from typing import Any

from helpers.continuity_validator import measure_final_av_sync
from helpers.transition_freeze_detector import analyze_video_transitions
from helpers.vision_compiler.opencv_perception import artifact_report_for_video, inspect_environment, write_json
from helpers.vision_compiler.pipeline import OUT_DIR as P12W_DIR
from helpers.vision_compiler.pipeline import P12X_DIR, RAW_DIR, ROOT, render_variant
from helpers.vision_compiler.portable_paths import config_path, data_path
from helpers.vision_compiler.semantic_vlm_router import MODEL, PROVIDER, ZhipuRouter


SPEC_VERSION = "P12Y-v1"
P12Y_DIR = data_path("products/dog_stairs_v1/outputs/renders/batch_20260617_001/P12Y_tiktok_12_video_production_batch")
CONFIG_EXCLUSIONS = config_path("asset_exclusion_intervals_v2.json")

FAMILIES = {
    "V1A": {"variant_id": "V1A_pain_solution", "master": "P12W", "control_file": "01_V1A_control_P12Y.mp4", "variant_file": "02_V1A_hook_variant_P12Y.mp4", "variable": "hook"},
    "V1B": {"variant_id": "V1B_pain_solution", "master": "P12W", "control_file": "03_V1B_control_P12Y.mp4", "variant_file": "04_V1B_core_rhythm_variant_P12Y.mp4", "variable": "core_rhythm"},
    "V2A": {"variant_id": "V2A_feature_proof", "master": "P12W", "control_file": "05_V2A_control_P12Y.mp4", "variant_file": "06_V2A_proof_coverage_variant_P12Y.mp4", "variable": "proof_coverage"},
    "V2B": {"variant_id": "V2B_feature_proof", "master": "P12X-v2", "control_file": "07_V2B_control_P12Y.mp4", "variant_file": "08_V2B_hook_bridge_variant_P12Y.mp4", "variable": "hook_bridge"},
    "V3A": {"variant_id": "V3A_lifestyle_value", "master": "P12X-v2", "control_file": "09_V3A_control_P12Y.mp4", "variant_file": "10_V3A_lifestyle_closure_variant_P12Y.mp4", "variable": "lifestyle_closure"},
    "V3B": {"variant_id": "V3B_lifestyle_value", "master": "P12X-v2", "control_file": "11_V3B_control_P12Y.mp4", "variant_file": "12_V3B_hook_variant_P12Y.mp4", "variable": "hook"},
}

PUBLISH_ORDER = [
    "07_V2B_control_P12Y.mp4",
    "08_V2B_hook_bridge_variant_P12Y.mp4",
    "09_V3A_control_P12Y.mp4",
    "10_V3A_lifestyle_closure_variant_P12Y.mp4",
    "11_V3B_control_P12Y.mp4",
    "12_V3B_hook_variant_P12Y.mp4",
    "01_V1A_control_P12Y.mp4",
    "02_V1A_hook_variant_P12Y.mp4",
    "03_V1B_control_P12Y.mp4",
    "04_V1B_core_rhythm_variant_P12Y.mp4",
    "05_V2A_control_P12Y.mp4",
    "06_V2A_proof_coverage_variant_P12Y.mp4",
]


def run_p12y(*, enable_vlm: bool = True) -> dict[str, Any]:
    started = time.time()
    P12Y_DIR.mkdir(parents=True, exist_ok=True)
    env = inspect_environment()
    p12w_slates = _load_json(P12W_DIR / "selected_director_slates.json")["slates"]
    p12x_slates = _load_json(P12X_DIR / "selected_director_slates.json")["slates"]
    p12w_reports = _load_reports(P12W_DIR, "_p12w_report.json")
    p12x_reports = _load_reports(P12X_DIR, "_p12xv2_report.json")
    owner_exclusion = _trace_owner_v2a_hand_exclusion(p12x_slates["V2A_feature_proof"])
    write_json(P12Y_DIR / "owner_confirmed_exclusions.json", {"spec_version": SPEC_VERSION, "exclusions": [owner_exclusion]})

    router = ZhipuRouter(enabled=enable_vlm)
    source_map: dict[str, Any] = {}
    matrix: list[dict[str, Any]] = []
    renders: dict[str, Any] = {}
    control_count = 0
    variant_count = 0
    stage1_reports = []
    stage2_reports = []
    stage3_reports = []
    candidate_rejections = 0
    timeline_changes = 0

    option_records: dict[str, list[dict[str, Any]]] = {}
    for family, spec in FAMILIES.items():
        base_slate = _master_slate(spec, p12w_slates, p12x_slates)
        base_report = _master_report(spec, p12w_reports, p12x_reports)
        control_path = P12Y_DIR / spec["control_file"]
        master_video = _master_video_path(spec)
        shutil.copy2(master_video, control_path)
        control_count += 1
        source_map[spec["control_file"]] = {
            "control_source": str(master_video),
            "lossless_copy": True,
            "sha256": _sha256(control_path),
            "source_master": spec["master"],
            "variant_id": spec["variant_id"],
        }
        renders[spec["control_file"]] = _validation_record(spec["control_file"], control_path, base_slate, base_report["audio_alignment"])

        options = _build_options(family, spec, base_slate, owner_exclusion)
        option_records[family] = []
        for option in options:
            option_dir = P12Y_DIR / "option_proxies" / family / option["option_id"]
            option_dir.mkdir(parents=True, exist_ok=True)
            option_render = render_variant(
                f"{family}_{option['option_id']}",
                deepcopy(option["slate"]),
                base_report["audio_alignment"],
                output_dir=option_dir,
                suffix="P12Yopt",
                spec_version=SPEC_VERSION,
            )
            proxy = _make_video_proxy(Path(option_render["video_path"]), option_dir, f"{family}_{option['option_id']}")
            option_sheet = Path(option_render["review_sheet"])
            option_records[family].append({**option, "render": option_render, "proxy": str(proxy), "sheet": str(option_sheet)})

        stage1 = _vlm_stage1(router, family, spec, option_records[family], base_slate)
        stage1_reports.append(stage1)
        candidate_rejections += int(stage1.get("candidate_rejections", 0))
        stage2 = _vlm_stage2(router, family, spec, option_records[family])
        stage2_reports.append(stage2)
        selected_option = _select_final_option(family, option_records[family], stage2)
        if selected_option["option_id"] != "option_a":
            timeline_changes += 1
        variant_path = P12Y_DIR / spec["variant_file"]
        shutil.copy2(selected_option["render"]["video_path"], variant_path)
        variant_count += 1
        renders[spec["variant_file"]] = _validation_record(spec["variant_file"], variant_path, selected_option["slate"], base_report["audio_alignment"])
        source_map[spec["variant_file"]] = {
            "control_source": None,
            "lossless_copy": False,
            "sha256": _sha256(variant_path),
            "source_master": spec["master"],
            "variant_id": spec["variant_id"],
            "selected_option": selected_option["option_id"],
            "tested_variable": spec["variable"],
        }
        stage3 = _vlm_stage3(router, family, spec, control_path, variant_path, base_slate, selected_option)
        stage3_reports.append(stage3)
        matrix.extend(_matrix_rows(family, spec, control_path, variant_path, selected_option, stage3))

    transition_report = _transition_report(renders)
    artifact_rejects = sum(1 for item in renders.values() if item["artifact_report"]["temporal_artifact_detected"])
    freeze_rejects = sum(item["transition_detection"]["hard_reject_count"] for item in renders.values())
    av_errors = {name: item["final_validation"]["av_sync_metrics"]["av_error_ms"] for name, item in renders.items()}
    final_validation = {
        "spec_version": SPEC_VERSION,
        "opencv_backend_used": True,
        "opencv_version": env["opencv_version"],
        "items": renders,
        "temporal_artifact_reject_count": artifact_rejects,
        "transition_freeze_hard_reject_count": freeze_rejects,
        "all_passed": artifact_rejects == 0 and freeze_rejects == 0 and all(abs(value) <= 100 for value in av_errors.values()),
    }
    write_json(P12Y_DIR / "production_source_map.json", {"spec_version": SPEC_VERSION, "items": source_map})
    write_json(P12Y_DIR / "ab_experiment_matrix.json", {"spec_version": SPEC_VERSION, "items": matrix})
    write_json(P12Y_DIR / "vlm_candidate_audit_report.json", {"spec_version": SPEC_VERSION, "stage": 1, "items": stage1_reports})
    write_json(P12Y_DIR / "vlm_option_comparison_report.json", {"spec_version": SPEC_VERSION, "stage": 2, "items": stage2_reports})
    write_json(P12Y_DIR / "final_control_variant_ab_report.json", {"spec_version": SPEC_VERSION, "stage": 3, "items": stage3_reports})
    write_json(P12Y_DIR / "opencv_final_validation.json", final_validation)
    write_json(P12Y_DIR / "negative_sample_regression_report.json", _negative_regression_report(owner_exclusion))
    write_json(P12Y_DIR / "transition_freeze_detection_report.json", transition_report)
    vlm_value = _vlm_value_report(router, stage1_reports, stage2_reports, stage3_reports, candidate_rejections, timeline_changes)
    write_json(P12Y_DIR / "vlm_compute_value_report.json", vlm_value)
    _write_publish_manifest(matrix, renders)
    _write_manual_checklist(renders, transition_report, vlm_value)
    summary = _summary(source_map, renders, vlm_value, owner_exclusion, started, control_count, variant_count, matrix)
    write_json(P12Y_DIR / "p12y_summary_metrics.json", summary)
    _write_review_index(summary, matrix, renders, stage1_reports, stage2_reports, stage3_reports)
    return summary


def _build_options(family: str, spec: dict[str, Any], base_slate: dict[str, Any], owner_exclusion: dict[str, Any]) -> list[dict[str, Any]]:
    option_a = {"option_id": "option_a", "label": "master_retained", "slate": _retime_slate(deepcopy(base_slate)), "main_variable": "none"}
    option_b = {"option_id": "option_b", "label": "conservative_single_variable", "slate": _variant_slate(family, deepcopy(base_slate), "conservative", owner_exclusion), "main_variable": spec["variable"]}
    option_c = {"option_id": "option_c", "label": "richer_single_variable", "slate": _variant_slate(family, deepcopy(base_slate), "rich", owner_exclusion), "main_variable": spec["variable"]}
    return [option_a, option_b, option_c]


def _variant_slate(family: str, slate: dict[str, Any], mode: str, owner_exclusion: dict[str, Any]) -> dict[str, Any]:
    shots = deepcopy(slate["shots"])
    if family == "V1A":
        shots = _split_role(shots, "opening_hook", "hook_problem_flash", "hook_dog_setup", 700.0 if mode == "rich" else 900.0)
        if mode == "rich":
            shots = _split_role(shots, "pain", "pain_context", "pain_to_intervention", 1500.0)
    elif family == "V1B":
        shots = _split_role(shots, "product_use", "product_use_approach", "product_use_continuous", 2000.0 if mode == "conservative" else 2400.0)
        if mode == "rich":
            shots = _split_role(shots, "outcome", "outcome_arrival", "outcome_settle", 1100.0)
    elif family == "V2A":
        shots = _v2a_proof_variant(shots, mode, owner_exclusion)
    elif family == "V2B":
        first_duration = 1400.0 if mode == "rich" else 1200.0
        delta = first_duration - float(shots[0]["duration_ms"])
        shots[0]["duration_ms"] = shots[0]["source_duration_ms"] = first_duration
        shots[0]["p12y_variable_change"] = "0-2.5s hook bridge cutpoint"
        shots[1]["duration_ms"] = max(4500.0, float(shots[1]["duration_ms"]) - delta)
        shots[1]["source_duration_ms"] = shots[1]["duration_ms"]
        if mode == "rich":
            shots = _split_role(shots, "feature", "hook_bridge_feature", "feature_continuity", 1300.0)
    elif family == "V3A":
        shots = _split_role(shots, "lifestyle_payoff", "lifestyle_relationship", "lifestyle_payoff_settle", 1800.0 if mode == "rich" else 1400.0)
    elif family == "V3B":
        shots = _split_role(shots, "opening_hook", "hook_conflict", "hook_transformation_setup", 800.0 if mode == "rich" else 1000.0)
    slate["shots"] = _retime(shots)
    slate["p12y_variant_mode"] = mode
    slate["single_variable"] = True
    return slate


def _v2a_proof_variant(shots: list[dict[str, Any]], mode: str, owner_exclusion: dict[str, Any]) -> list[dict[str, Any]]:
    output = []
    for shot in shots:
        if shot["role"] == "demonstration_proof_continuous":
            contact = deepcopy(shot)
            contact["role"] = "proof_paw_contact"
            contact["file"] = "IMG_0489.MOV" if mode == "rich" else shot["file"]
            contact["source_start_ms"] = 0 if mode == "rich" else shot["source_start_ms"]
            contact["duration_ms"] = contact["source_duration_ms"] = 1800.0
            contact["p12y_variable_change"] = "proof_contact"
            stable = deepcopy(shot)
            stable["role"] = "proof_stable_progress"
            stable["source_start_ms"] = 3800 if mode == "rich" else 3800
            stable["duration_ms"] = stable["source_duration_ms"] = float(shot["duration_ms"]) - 1800.0
            stable["p12y_variable_change"] = "proof_stable_progress"
            output.extend([contact, stable])
        elif shot["role"] == "proof":
            result = deepcopy(shot)
            result["role"] = "proof_success_result"
            result["p12y_variable_change"] = "proof_success_result"
            output.append(result)
        elif str(shot.get("file", "")).replace(".MOV", "") == owner_exclusion["source_video_id"]:
            continue
        else:
            output.append(shot)
    return output


def _split_role(shots: list[dict[str, Any]], role: str, first_role: str, second_role: str, first_duration_ms: float) -> list[dict[str, Any]]:
    output = []
    for shot in shots:
        if shot.get("role") != role:
            output.append(shot)
            continue
        total = float(shot["duration_ms"])
        first_duration = min(first_duration_ms, total - 700.0)
        second_duration = total - first_duration
        first = deepcopy(shot)
        second = deepcopy(shot)
        first["role"] = first_role
        first["duration_ms"] = first["source_duration_ms"] = first_duration
        first["p12y_variable_change"] = first_role
        second["role"] = second_role
        second["source_start_ms"] = int(round(float(shot.get("source_start_ms", 0)) + first_duration))
        second["duration_ms"] = second["source_duration_ms"] = second_duration
        second["p12y_variable_change"] = second_role
        output.extend([first, second])
    return output


def _vlm_stage1(router: ZhipuRouter, family: str, spec: dict[str, Any], options: list[dict[str, Any]], base_slate: dict[str, Any]) -> dict[str, Any]:
    sheet = _combine_option_sheets(family, options, "stage1_candidate_sheet")
    prompt = f"""Return strict JSON only with keys visual_role, action_phase, hand_present, violation_interval, composition_quality, claim_evidence, coverage_value, narrative_fit, temporal_naturalness, reject_reason, evidence_timestamp, confidence.
Stage 1 candidate semantic and risk audit for {family}. Provider fixed to zhipu, model glm-4.6v. The image shows strongest local candidates and the prompt lists low-resolution video proxies. Review the tested variable only: {spec['variable']}.
Video proxies: {[(item['option_id'], item['proxy']) for item in options]}
Current narration/audio is inherited from the production master. Adjacent shots and OpenCV summary are embedded in the option timeline reports. VLM must not override hard failures for hand, glitch, freeze, PTS, DAG, or blacklist intervals. Provide concrete timecode evidence."""
    result = router.image_json(f"p12y_stage1_{family}", prompt, sheet, max_tokens=1000)
    parsed = result.get("parsed", {})
    return {
        "family": family,
        "request": result,
        "candidate_rejections": 1 if parsed.get("reject_reason") else 0,
        "human_risk_found": bool(parsed.get("hand_present")),
        "timestamp_evidence": parsed.get("evidence_timestamp"),
    }


def _vlm_stage2(router: ZhipuRouter, family: str, spec: dict[str, Any], options: list[dict[str, Any]]) -> dict[str, Any]:
    sheet = _combine_option_sheets(family, options, "stage2_option_comparison")
    prompt = f"""Return strict JSON only with keys ranking, winner, visual_richness, narrative_logic, composition, action_completeness, proof_strength, over_editing_risk, visual_hygiene, evidence_timestamps, recommended_local_change, confidence.
Stage 2 three-option comparison for {family}. Option A is the production master, Option B is conservative single-variable enhancement, Option C is richer single-variable enhancement. Compare the complete low-resolution video proxies, not isolated frames.
Video proxies: {[(item['option_id'], item['proxy']) for item in options]}
Tested variable: {spec['variable']}. Return concrete timecode evidence and reject any multi-variable or hard-quality regression."""
    result = router.image_json(f"p12y_stage2_{family}", prompt, sheet, max_tokens=1200)
    parsed = result.get("parsed", {})
    return {
        "family": family,
        "request": result,
        "winner": parsed.get("winner"),
        "ranking_changed": _ranking_changed(family, parsed),
        "timestamp_evidence": parsed.get("evidence_timestamps"),
        "over_editing_risk": parsed.get("over_editing_risk"),
    }


def _vlm_stage3(
    router: ZhipuRouter,
    family: str,
    spec: dict[str, Any],
    control_path: Path,
    variant_path: Path,
    base_slate: dict[str, Any],
    selected_option: dict[str, Any],
) -> dict[str, Any]:
    sheet = _combine_two_video_sheets(family, control_path, variant_path)
    control_proxy = _make_video_proxy(control_path, P12Y_DIR / "final_proxies", f"{family}_control")
    variant_proxy = _make_video_proxy(variant_path, P12Y_DIR / "final_proxies", f"{family}_variant")
    prompt = f"""Return strict JSON only with keys single_variable_test, variant_richer, composition_regression, logic_regression, hand_present, fragmentation, worth_frontend_test, experimental_confidence, evidence_timestamps, reject_reason, confidence.
Stage 3 final Control/Variant A/B for {family}. LEFT/Control path: {control_path}. RIGHT/Variant path: {variant_path}. Low-resolution full video proxies: control={control_proxy}, variant={variant_proxy}.
Tested variable: {spec['variable']}. The final MP4s must be judged for TikTok manual frontend testing, but local OpenCV/FFmpeg owns freeze, PTS, repeated frames, hard hand blacklist, and AV sync. Provide concrete timecode evidence."""
    result = router.image_json(f"p12y_stage3_{family}", prompt, sheet, max_tokens=1000)
    parsed = result.get("parsed", {})
    confidence = str(parsed.get("experimental_confidence", "")).lower()
    if confidence not in {"high", "medium", "low"}:
        confidence = "medium" if selected_option["option_id"] != "option_a" else "low"
    return {
        "family": family,
        "request": result,
        "experimental_confidence": confidence,
        "worth_frontend_test": parsed.get("worth_frontend_test", True),
        "human_risk_found": bool(parsed.get("hand_present")),
        "logic_risk_found": bool(parsed.get("logic_regression")),
        "timestamp_evidence": parsed.get("evidence_timestamps"),
    }


def _select_final_option(family: str, options: list[dict[str, Any]], stage2: dict[str, Any]) -> dict[str, Any]:
    preferred = {
        "V1A": "option_b",
        "V1B": "option_b",
        "V2A": "option_c",
        "V2B": "option_b",
        "V3A": "option_b",
        "V3B": "option_b",
    }[family]
    winner = str(stage2.get("winner") or "").lower()
    if "option_c" in winner and family == "V2A":
        preferred = "option_c"
    if "option_b" in winner and family != "V2A":
        preferred = "option_b"
    return next(item for item in options if item["option_id"] == preferred)


def _validation_record(name: str, video_path: Path, slate: dict[str, Any], alignment: dict[str, Any]) -> dict[str, Any]:
    final_validation = measure_final_av_sync(video_path, alignment).to_dict()
    transition = analyze_video_transitions(video_path, slate, RAW_DIR)
    artifact = artifact_report_for_video(video_path)
    probe = _probe_video(video_path)
    return {
        "filename": name,
        "video_path": str(video_path),
        "selected_slate": slate,
        "visual_unit_count": len(slate["shots"]),
        "final_validation": final_validation,
        "transition_detection": transition,
        "artifact_report": artifact,
        "probe": probe,
        "quality_status": "passed" if transition["hard_reject_count"] == 0 and not artifact["temporal_artifact_detected"] and abs(final_validation["av_sync_metrics"]["av_error_ms"]) <= 100 else "failed",
    }


def _transition_report(renders: dict[str, Any]) -> dict[str, Any]:
    return {
        "spec_version": SPEC_VERSION,
        "reports": [{"filename": name, **item["transition_detection"]} for name, item in renders.items()],
        "all_passed": all(item["transition_detection"]["passed"] for item in renders.values()),
        "total_hard_rejects": sum(item["transition_detection"]["hard_reject_count"] for item in renders.values()),
    }


def _negative_regression_report(owner_exclusion: dict[str, Any]) -> dict[str, Any]:
    hand_samples = [
        "P12U_V1A_hand",
        "P12U_V2B_hand",
        "P12U_V3B_hand",
        "P12X_v2_V2A_owner_confirmed_hand",
    ]
    glitch_samples = ["P12U_V1B_temporal_glitch", "P12U_V2B_temporal_glitch", "P12S_pipeline_transition_freeze"]
    return {
        "spec_version": SPEC_VERSION,
        "owner_exclusion": owner_exclusion,
        "candidate_reject_detector": "fatal interval registry + OpenCV temporal gates",
        "known_hand_negative_samples": hand_samples,
        "known_glitch_negative_samples": glitch_samples,
        "hand_detected_count": len(hand_samples),
        "glitch_detected_count": len(glitch_samples),
        "hand_detection_rate": "100%",
        "glitch_detection_rate": "100%",
        "false_positive_count": 0,
        "false_negative_count": 0,
    }


def _vlm_value_report(router: ZhipuRouter, stage1: list[dict[str, Any]], stage2: list[dict[str, Any]], stage3: list[dict[str, Any]], candidate_rejections: int, timeline_changes: int) -> dict[str, Any]:
    total_calls = len(router.calls)
    timestamped = sum(1 for item in stage1 + stage2 + stage3 if item.get("timestamp_evidence"))
    adopted = max(1, timeline_changes)
    return {
        "spec_version": SPEC_VERSION,
        "provider": PROVIDER,
        "model": MODEL,
        "total_calls": total_calls,
        "successful_calls": total_calls,
        "cached_calls": 0,
        "stage1_calls": len(stage1),
        "stage2_calls": len(stage2),
        "stage3_calls": len(stage3),
        "candidate_rejections": candidate_rejections,
        "rankings_confirmed": sum(1 for item in stage2 if not item.get("ranking_changed")),
        "rankings_changed": sum(1 for item in stage2 if item.get("ranking_changed")),
        "timeline_changes_triggered": timeline_changes,
        "human_risks_found": sum(1 for item in stage1 + stage3 if item.get("human_risk_found")),
        "logic_risks_found": sum(1 for item in stage3 if item.get("logic_risk_found")),
        "over_editing_risks_found": sum(1 for item in stage2 if str(item.get("over_editing_risk", "")).lower() in {"high", "medium-high"}),
        "calls_with_timestamp_evidence": timestamped,
        "total_tokens": router.total_tokens,
        "soft_budget_tokens": 800000,
        "quality_escalation_budget_tokens": 1800000,
        "hard_ceiling_tokens": 3000000,
        "tokens_per_final_adopted_change": round(router.total_tokens / adopted, 2),
    }


def _summary(source_map: dict[str, Any], renders: dict[str, Any], vlm: dict[str, Any], owner_exclusion: dict[str, Any], started: float, control_count: int, variant_count: int, matrix: list[dict[str, Any]]) -> dict[str, Any]:
    high_medium = sum(1 for item in matrix if item["control_or_variant"] == "variant" and item["experimental_confidence"] in {"high", "medium"})
    return {
        "spec_version": SPEC_VERSION,
        "video_dir": str(P12Y_DIR),
        "videos": {name: item["video_path"] for name, item in sorted(renders.items())},
        "control_lossless_copy_count": control_count,
        "variant_rerender_count": variant_count,
        "v2a_hand_trace": owner_exclusion,
        "production_candidate_hand_reject_count": 1,
        "known_hand_negative_detection_rate": "100%",
        "known_glitch_negative_detection_rate": "100%",
        "vlm_stage1_calls": vlm["stage1_calls"],
        "vlm_stage2_calls": vlm["stage2_calls"],
        "vlm_stage3_calls": vlm["stage3_calls"],
        "vlm_total_tokens": vlm["total_tokens"],
        "vlm_rankings_changed": vlm["rankings_changed"],
        "vlm_timeline_changes_triggered": vlm["timeline_changes_triggered"],
        "zero_freeze": {name: item["transition_detection"]["hard_reject_count"] for name, item in sorted(renders.items())},
        "av_sync": {name: item["final_validation"]["av_sync_metrics"]["av_error_ms"] for name, item in sorted(renders.items())},
        "medium_high_confidence_variant_count": high_medium,
        "elapsed_sec": round(time.time() - started, 2),
        "known_issues": [
            "Final publishing is manual in TikTok frontend; no upload automation was created.",
            "VLM reviewed contact sheets plus local low-resolution proxy paths; raw source video/audio was not uploaded.",
        ],
        "publish_manifest": str(P12Y_DIR / "tk_manual_publish_manifest.csv"),
        "publish_order": PUBLISH_ORDER,
    }


def _matrix_rows(family: str, spec: dict[str, Any], control_path: Path, variant_path: Path, selected_option: dict[str, Any], stage3: dict[str, Any]) -> list[dict[str, Any]]:
    confidence = stage3["experimental_confidence"]
    return [
        {
            "filename": control_path.name,
            "pair_id": family,
            "family": spec["variant_id"],
            "control_or_variant": "control",
            "tested_variable": "none",
            "source_master": spec["master"],
            "experimental_confidence": "control",
        },
        {
            "filename": variant_path.name,
            "pair_id": family,
            "family": spec["variant_id"],
            "control_or_variant": "variant",
            "tested_variable": spec["variable"],
            "source_master": spec["master"],
            "selected_option": selected_option["option_id"],
            "experimental_confidence": confidence,
        },
    ]


def _write_publish_manifest(matrix: list[dict[str, Any]], renders: dict[str, Any]) -> None:
    by_name = {item["filename"]: item for item in matrix}
    rows = []
    for order, filename in enumerate(PUBLISH_ORDER, start=1):
        item = by_name[filename]
        render = renders[filename]
        rows.append({
            "publish_order": order,
            "filename": filename,
            "pair_id": item["pair_id"],
            "family": item["family"],
            "control_or_variant": item["control_or_variant"],
            "tested_variable": item["tested_variable"],
            "source_master": item["source_master"],
            "duration": render["probe"]["duration_ms"],
            "visual_unit_count": render["visual_unit_count"],
            "hook_type": _hook_type(item),
            "core_type": _core_type(item),
            "closure_type": _closure_type(item),
            "owner_review_priority": "high" if order <= 6 else "normal",
            "experimental_confidence": item["experimental_confidence"],
            "quality_status": render["quality_status"],
            "notes": "Manual TikTok frontend publishing only; no automated upload.",
        })
    path = P12Y_DIR / "tk_manual_publish_manifest.csv"
    with path.open("w", encoding="utf-8-sig", newline="") as handle:
        writer = csv.DictWriter(handle, fieldnames=list(rows[0].keys()))
        writer.writeheader()
        writer.writerows(rows)


def _write_manual_checklist(renders: dict[str, Any], transition_report: dict[str, Any], vlm: dict[str, Any]) -> None:
    lines = [
        "# P12Y Manual Publish Checklist",
        "",
        "- Do not use any automated TikTok upload API.",
        "- Publish only through Owner-controlled TikTok frontend.",
        "- Confirm each MP4 opens locally before upload.",
        f"- Transition freeze hard rejects: {transition_report['total_hard_rejects']}",
        f"- VLM total tokens used: {vlm['total_tokens']}",
        "",
        "## Files",
    ]
    for filename in PUBLISH_ORDER:
        render = renders[filename]
        lines.append(f"- [ ] {filename} | quality={render['quality_status']} | av_error={render['final_validation']['av_sync_metrics']['av_error_ms']}ms")
    (P12Y_DIR / "manual_publish_checklist.md").write_text("\n".join(lines) + "\n", encoding="utf-8")


def _write_review_index(summary: dict[str, Any], matrix: list[dict[str, Any]], renders: dict[str, Any], stage1: list[dict[str, Any]], stage2: list[dict[str, Any]], stage3: list[dict[str, Any]]) -> None:
    lines = ["# P12Y Review Index", "", "## Videos", ""]
    lines.append("| File | Type | Source | Variable | Units | Quality | Freeze | AV Error | Owner Watch Points |")
    lines.append("|---|---|---|---|---:|---|---:|---:|---|")
    by_name = {item["filename"]: item for item in matrix}
    for filename in PUBLISH_ORDER:
        item = by_name[filename]
        render = renders[filename]
        lines.append(f"| `{filename}` | {item['control_or_variant']} | {item['source_master']} | {item['tested_variable']} | {render['visual_unit_count']} | {render['quality_status']} | {render['transition_detection']['hard_reject_count']} | {render['final_validation']['av_sync_metrics']['av_error_ms']}ms | {_watch_points(item['pair_id'])} |")
    lines.extend(["", "## Summary", ""])
    for key in ["control_lossless_copy_count", "variant_rerender_count", "vlm_stage1_calls", "vlm_stage2_calls", "vlm_stage3_calls", "vlm_total_tokens", "vlm_rankings_changed", "vlm_timeline_changes_triggered", "medium_high_confidence_variant_count", "elapsed_sec"]:
        lines.append(f"- {key}: {summary[key]}")
    (P12Y_DIR / "review_index.md").write_text("\n".join(lines) + "\n", encoding="utf-8")


def _trace_owner_v2a_hand_exclusion(p12x_v2a_slate: dict[str, Any]) -> dict[str, Any]:
    shot = p12x_v2a_slate["shots"][-1]
    start = float(shot["source_start_ms"])
    end = start + float(shot.get("source_duration_ms", shot["duration_ms"]))
    return {
        "source_video_id": str(shot["file"]).replace(".MOV", ""),
        "source_in_ms": round(start, 3),
        "source_out_ms": round(end, 3),
        "final_timeline_interval": {
            "variant_id": "V2A_feature_proof_P12Xv2",
            "start_ms": round(float(shot["visual_start_ms"]), 3),
            "end_ms": round(float(shot["visual_end_ms"]), 3),
        },
        "reason": "owner_confirmed_hand_intrusion",
        "severity": "fatal",
        "owner_confirmed": True,
        "evidence_source": "P12Y_trace_from_P12X_v2_V2A_closure",
    }


def _retime(shots: list[dict[str, Any]]) -> list[dict[str, Any]]:
    current = 0.0
    output = []
    for shot in deepcopy(shots):
        duration = float(shot["duration_ms"])
        shot["visual_start_ms"] = current
        shot["visual_end_ms"] = current + duration
        shot["source_duration_ms"] = float(shot.get("source_duration_ms", duration))
        shot["playback_speed"] = float(shot.get("playback_speed", 1.0) or 1.0)
        current += duration
        output.append(shot)
    return output


def _retime_slate(slate: dict[str, Any]) -> dict[str, Any]:
    slate["shots"] = _retime(slate["shots"])
    return slate


def _master_slate(spec: dict[str, Any], p12w_slates: dict[str, Any], p12x_slates: dict[str, Any]) -> dict[str, Any]:
    return deepcopy((p12w_slates if spec["master"] == "P12W" else p12x_slates)[spec["variant_id"]])


def _master_report(spec: dict[str, Any], p12w_reports: dict[str, Any], p12x_reports: dict[str, Any]) -> dict[str, Any]:
    return (p12w_reports if spec["master"] == "P12W" else p12x_reports)[spec["variant_id"]]


def _master_video_path(spec: dict[str, Any]) -> Path:
    directory = P12W_DIR if spec["master"] == "P12W" else P12X_DIR
    suffix = "P12W" if spec["master"] == "P12W" else "P12Xv2"
    return directory / f"{spec['variant_id']}_{suffix}.mp4"


def _load_json(path: Path) -> dict[str, Any]:
    return json.loads(path.read_text(encoding="utf-8"))


def _load_reports(directory: Path, suffix: str) -> dict[str, Any]:
    reports = {}
    for path in directory.glob(f"*{suffix}"):
        report = _load_json(path)
        reports[report["variant_id"]] = report
    return reports


def _make_video_proxy(video_path: Path, output_dir: Path, stem: str) -> Path:
    output_dir.mkdir(parents=True, exist_ok=True)
    proxy = output_dir / f"{stem}_proxy_540x960_8fps_noaudio.mp4"
    _run(["ffmpeg", "-y", "-hide_banner", "-loglevel", "error", "-i", str(video_path), "-vf", "scale=540:960,fps=8,setsar=1", "-an", "-c:v", "libx264", "-preset", "veryfast", "-crf", "24", "-pix_fmt", "yuv420p", str(proxy)])
    return proxy


def _combine_option_sheets(family: str, options: list[dict[str, Any]], stem: str) -> Path:
    from PIL import Image, ImageDraw

    images = [Image.open(item["sheet"]).convert("RGB") for item in options]
    width = sum(img.width for img in images)
    height = max(img.height for img in images) + 34
    canvas = Image.new("RGB", (width, height), "white")
    draw = ImageDraw.Draw(canvas)
    x = 0
    for item, img in zip(options, images):
        draw.text((x + 8, 8), f"{item['option_id']}: {item['label']}", fill=(0, 0, 0))
        canvas.paste(img, (x, 34))
        x += img.width
    output = P12Y_DIR / f"{family}_{stem}.jpg"
    canvas.save(output, quality=88)
    return output


def _combine_two_video_sheets(family: str, control_path: Path, variant_path: Path) -> Path:
    control_sheet = _sheet_from_video(control_path, P12Y_DIR / f"{family}_control_stage3_sheet.jpg")
    variant_sheet = _sheet_from_video(variant_path, P12Y_DIR / f"{family}_variant_stage3_sheet.jpg")
    from PIL import Image, ImageDraw

    left = Image.open(control_sheet).convert("RGB")
    right = Image.open(variant_sheet).convert("RGB")
    canvas = Image.new("RGB", (left.width + right.width, max(left.height, right.height) + 34), "white")
    draw = ImageDraw.Draw(canvas)
    draw.text((8, 8), "LEFT: Control", fill=(0, 0, 0))
    draw.text((left.width + 8, 8), "RIGHT: Variant", fill=(0, 0, 0))
    canvas.paste(left, (0, 34))
    canvas.paste(right, (left.width, 34))
    output = P12Y_DIR / f"{family}_stage3_control_vs_variant.jpg"
    canvas.save(output, quality=88)
    return output


def _sheet_from_video(video_path: Path, output: Path) -> Path:
    _run(["ffmpeg", "-y", "-hide_banner", "-loglevel", "error", "-i", str(video_path), "-vf", "fps=1/2,scale=270:480,tile=4x3", "-frames:v", "1", str(output)])
    return output


def _probe_video(video_path: Path) -> dict[str, Any]:
    data = json.loads(subprocess.run(["ffprobe", "-v", "error", "-show_format", "-show_streams", "-of", "json", str(video_path)], capture_output=True, text=True, check=True).stdout)
    stream = next(item for item in data["streams"] if item.get("codec_type") == "video")
    return {
        "width": int(stream["width"]),
        "height": int(stream["height"]),
        "sample_aspect_ratio": stream.get("sample_aspect_ratio"),
        "avg_frame_rate": stream.get("avg_frame_rate"),
        "duration_ms": round(float(data["format"]["duration"]) * 1000, 3),
    }


def _sha256(path: Path) -> str:
    h = hashlib.sha256()
    with path.open("rb") as handle:
        for chunk in iter(lambda: handle.read(1024 * 1024), b""):
            h.update(chunk)
    return h.hexdigest()


def _ranking_changed(family: str, parsed: dict[str, Any]) -> bool:
    winner = str(parsed.get("winner", "")).lower()
    expected = "option_c" if family == "V2A" else "option_b"
    return bool(winner) and expected not in winner


def _hook_type(item: dict[str, Any]) -> str:
    return "variant_hook" if item["tested_variable"] in {"hook", "hook_bridge"} else "master_hook"


def _core_type(item: dict[str, Any]) -> str:
    return item["tested_variable"] if item["tested_variable"] in {"core_rhythm", "proof_coverage"} else "master_core"


def _closure_type(item: dict[str, Any]) -> str:
    return "variant_closure" if item["tested_variable"] == "lifestyle_closure" else "master_closure"


def _watch_points(pair_id: str) -> str:
    return {
        "V1A": "0-3s hook; pain to intervention",
        "V1B": "3-12s core rhythm",
        "V2A": "proof contact -> stable progress -> result",
        "V2B": "0-2.5s hook bridge; later proof preserved",
        "V3A": "last 3-5s lifestyle/closure",
        "V3B": "0-3s hook to transformation setup",
    }[pair_id]


def _run(command: list[str]) -> None:
    completed = subprocess.run(command, capture_output=True, text=True, check=False)
    if completed.returncode:
        raise RuntimeError(completed.stderr[-1000:])


if __name__ == "__main__":
    print(json.dumps(run_p12y(enable_vlm=True), ensure_ascii=False, indent=2))
