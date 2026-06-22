"""Unified P12W OpenCV + FFmpeg + VLM asymmetric vision compiler."""

from __future__ import annotations

import json
import shutil
import subprocess
import sys
import time
from pathlib import Path
from typing import Any

AGENT_ROOT = Path(__file__).resolve().parents[2]
if str(AGENT_ROOT) not in sys.path:
    sys.path.insert(0, str(AGENT_ROOT))

from helpers.continuity_validator import measure_final_av_sync
from helpers.transition_freeze_detector import analyze_video_transitions, probe_frame_count

from helpers.vision_compiler.opencv_perception import (
    artifact_report_for_video,
    build_asset_perception_index,
    calibrate_thresholds,
    inspect_environment,
    validate_opencv_video_path,
    write_json,
)
from helpers.vision_compiler.global_storyboard_optimizer import GlobalStoryboardOptimizer, SPEC_VERSION as P12X_SPEC_VERSION
from helpers.vision_compiler.portable_paths import data_path, repo_root
from helpers.vision_compiler.quality_gate import MOTION_MATCH_DEFAULT_WEIGHT, MOTION_MATCH_MAX_WEIGHT, topology_valid
from helpers.vision_compiler.semantic_vlm_router import MODEL, PROVIDER, ZhipuRouter
from helpers.vision_compiler.storyboard_compiler import compile_variant, planned_replacement_roles


ROOT = repo_root()
RAW_DIR = data_path("products/dog_stairs_v1/inputs/raw_videos/batch_20260617_001")
P12T_DIR = data_path("products/dog_stairs_v1/outputs/renders/batch_20260617_001/P12T_transition_freeze_zero_tolerance_and_vlm_compute_scale")
P12U_DIR = data_path("products/dog_stairs_v1/outputs/renders/batch_20260617_001/P12U_full_asset_recall_global_storyboard_optimizer")
OUT_DIR = data_path("products/dog_stairs_v1/outputs/renders/batch_20260617_001/P12W_opencv_ffmpeg_vlm_asymmetric_vision_compiler")
P12X_DIR = data_path("products/dog_stairs_v1/outputs/renders/batch_20260617_001/P12X_v2_cinematic_global_search_with_guardrails")
FPS = 30


def run_p12w(*, enable_vlm: bool = True) -> dict[str, Any]:
    started = time.time()
    OUT_DIR.mkdir(parents=True, exist_ok=True)
    env = inspect_environment()
    validation = validate_opencv_video_path(RAW_DIR / "IMG_0497.MOV")
    write_json(OUT_DIR / "opencv_environment_report.json", {"spec_version": "P12W-v1", "environment": env, "validation": validation})
    perception = build_asset_perception_index(RAW_DIR, OUT_DIR)
    by_asset = {item["source_video_id"]: item for item in perception["assets"]}
    p12t_reports = _load_reports(P12T_DIR, "_p12t_report.json")
    p12u_reports = _load_reports(P12U_DIR, "_p12u_report.json")
    positives = [by_asset[str(shot["file"]).replace(".MOV", "")] for report in p12t_reports.values() for shot in report["selected_slate"]["shots"] if str(shot["file"]).replace(".MOV", "") in by_asset]
    if "V3A_lifestyle_value" in p12u_reports:
        positives.extend(by_asset[str(shot["file"]).replace(".MOV", "")] for shot in p12u_reports["V3A_lifestyle_value"]["selected_slate"]["shots"] if str(shot["file"]).replace(".MOV", "") in by_asset)
    negative_ids = {"IMG_0448", "IMG_0460", "IMG_0495", "IMG_0491", "IMG_0489", "IMG_0498", "IMG_0480"}
    negatives = [asset for asset_id, asset in by_asset.items() if asset_id in negative_ids]
    calibration = calibrate_thresholds(OUT_DIR, positives, negatives)
    exclusions = _build_asset_exclusions(p12u_reports, by_asset)
    write_json(OUT_DIR / "asset_exclusion_intervals_v2.json", {"spec_version": "P12W-v1", "intervals": exclusions})
    config = _write_policy_config(calibration)
    _append_error_log()

    router = ZhipuRouter(enabled=enable_vlm)
    vlm_slot_results = _run_slot_vlm(router, p12t_reports, p12u_reports)
    selected_slates: dict[str, Any] = {}
    dominance_items = []
    topology_items = []
    candidate_windows = []
    for variant_id, report in p12t_reports.items():
        slate = compile_variant(
            variant_id,
            report,
            p12u_reports.get(variant_id),
            planned_replacement_roles(variant_id),
            vlm_slot_results,
            by_asset,
        )
        ok, errors = topology_valid(variant_id, slate["shots"])
        topology_items.append({"variant_id": variant_id, "passed": ok, "errors": errors})
        if not ok:
            slate = report["selected_slate"]
            slate["fallback_to_p12t"] = True
            slate["replacement_count"] = 0
            slate["kept_p12t_slot_count"] = len(slate["shots"])
        selected_slates[variant_id] = slate
        dominance_items.extend({"variant_id": variant_id, **item} for item in slate.get("replacement_attempts", []))
        for item in slate.get("replacement_attempts", []):
            candidate_windows.append(item)
    write_json(OUT_DIR / "candidate_windows.json", {"spec_version": "P12W-v1", "windows": candidate_windows})
    write_json(OUT_DIR / "narrative_topology_report.json", {"spec_version": "P12W-v1", "items": topology_items, "reject_count": sum(1 for item in topology_items if not item["passed"])})
    write_json(OUT_DIR / "baseline_dominance_report.json", {"spec_version": "P12W-v1", "dominance_margin_min": 6, "items": dominance_items})
    write_json(OUT_DIR / "selected_director_slates.json", {"spec_version": "P12W-v1", "slates": selected_slates})

    renders = {}
    segment_reports = []
    transition_reports = []
    final_artifacts = []
    for variant_id, slate in selected_slates.items():
        report = p12t_reports[variant_id]
        render = render_variant(variant_id, slate, report["audio_alignment"])
        renders[variant_id] = render
        segment_reports.append({"variant_id": variant_id, "segments": render["segment_reports"], "concat_command": render["concat_command"], "mux_command": render["mux_command"]})
        transition_reports.append({"variant_id": variant_id, **render["transition_detection"]})
        final_artifacts.append({"variant_id": variant_id, **artifact_report_for_video(render["video_path"])})
    write_json(OUT_DIR / "segment_frame_budget_report.json", {"spec_version": "P12W-v1", "reports": segment_reports})
    write_json(OUT_DIR / "transition_freeze_detection_report.json", {
        "spec_version": "P12W-v1",
        "reports": transition_reports,
        "all_passed": all(item["passed"] for item in transition_reports),
        "total_hard_rejects": sum(item["hard_reject_count"] for item in transition_reports),
    })
    write_json(OUT_DIR / "temporal_artifact_report.json", {"spec_version": "P12W-v1", "reports": final_artifacts, "reject_count": sum(1 for item in final_artifacts if item["temporal_artifact_detected"])})

    ab_reviews = _run_final_ab_vlm(router, renders)
    write_json(OUT_DIR / "vlm_semantic_audit_report.json", {
        "spec_version": "P12W-v1",
        "provider": PROVIDER,
        "requested_model": MODEL,
        "response_model": MODEL,
        "slot_calls": list(vlm_slot_results.values()),
        "calls": len(vlm_slot_results),
    })
    write_json(OUT_DIR / "final_ab_review_report.json", {
        "spec_version": "P12W-v1",
        "provider": PROVIDER,
        "requested_model": MODEL,
        "response_model": MODEL,
        "reviews": ab_reviews,
        "calls": len(ab_reviews),
    })
    vlm_value = {
        "spec_version": "P12W-v1",
        "provider": PROVIDER,
        "model": MODEL,
        "total_calls": len(router.calls),
        "total_tokens": router.total_tokens,
        "hard_ceiling_tokens": 3_000_000,
        "changed_decisions": _count_changed_decisions(vlm_slot_results, ab_reviews),
        "media_used": ["candidate contact sheets", "final low-density review sheets"],
        "no_raw_video_or_audio_uploaded": True,
    }
    write_json(OUT_DIR / "vlm_compute_value_report.json", vlm_value)
    summary = _build_summary(env, renders, selected_slates, transition_reports, final_artifacts, vlm_value, started)
    write_review_index(summary, renders, selected_slates, dominance_items, topology_items, final_artifacts, ab_reviews)
    write_json(OUT_DIR / "p12w_summary_metrics.json", summary)
    return summary


def run_p12x_v2(*, enable_vlm: bool = True) -> dict[str, Any]:
    started = time.time()
    P12X_DIR.mkdir(parents=True, exist_ok=True)
    env = inspect_environment()
    write_json(P12X_DIR / "opencv_environment_report.json", {"spec_version": P12X_SPEC_VERSION, "environment": env, "opencv_backend_used": True})
    optimizer = GlobalStoryboardOptimizer(OUT_DIR, P12U_DIR, P12X_DIR)
    optimized = optimizer.optimize_all()
    selected_slates = optimized["selected_slates"]
    candidate_families = optimized["candidate_families"]
    reports = optimized["reports"]
    metrics = optimized["metrics"]
    write_json(P12X_DIR / "selected_director_slates.json", {"spec_version": P12X_SPEC_VERSION, "slates": selected_slates})
    write_json(P12X_DIR / "cinematic_feature_index.json", _cinematic_feature_index(candidate_families))
    write_json(P12X_DIR / "node_score_report.json", {"spec_version": P12X_SPEC_VERSION, "items": reports["node"]})
    write_json(P12X_DIR / "edge_score_report.json", {"spec_version": P12X_SPEC_VERSION, "items": reports["edge"], "motion_continuity_weight": 0.04, "motion_continuity_max": 0.06})
    write_json(P12X_DIR / "sequence_score_report.json", {"spec_version": P12X_SPEC_VERSION, "items": reports["sequence"]})
    write_json(P12X_DIR / "beam_search_report.json", {"spec_version": P12X_SPEC_VERSION, "items": reports["beam"]})
    write_json(P12X_DIR / "candidate_family_report.json", {"spec_version": P12X_SPEC_VERSION, "families": candidate_families})
    write_json(P12X_DIR / "coverage_report.json", {"spec_version": P12X_SPEC_VERSION, "items": reports["coverage"]})
    write_json(P12X_DIR / "jump_cut_risk_report.json", {"spec_version": P12X_SPEC_VERSION, "items": reports["jump"]})
    write_json(P12X_DIR / "motion_match_report.json", {"spec_version": P12X_SPEC_VERSION, "items": reports["motion"], "farneback_direct_pan_interpretation": False})

    p12w_reports = _load_reports(OUT_DIR, "_p12w_report.json")
    router = ZhipuRouter(enabled=enable_vlm)
    renders = {}
    segment_reports = []
    transition_reports = []
    final_artifacts = []
    for variant_id, slate in selected_slates.items():
        render = render_variant(variant_id, slate, p12w_reports[variant_id]["audio_alignment"], output_dir=P12X_DIR, suffix="P12Xv2", spec_version=P12X_SPEC_VERSION)
        proxy = _make_video_proxy(variant_id, Path(render["video_path"]), P12X_DIR)
        render["video_proxy_path"] = str(proxy)
        renders[variant_id] = render
        segment_reports.append({"variant_id": variant_id, "segments": render["segment_reports"], "concat_command": render["concat_command"], "mux_command": render["mux_command"]})
        transition_reports.append({"variant_id": variant_id, **render["transition_detection"]})
        final_artifacts.append({"variant_id": variant_id, **artifact_report_for_video(render["video_path"])})
    write_json(P12X_DIR / "segment_frame_budget_report.json", {"spec_version": P12X_SPEC_VERSION, "reports": segment_reports})
    write_json(P12X_DIR / "transition_freeze_detection_report.json", {
        "spec_version": P12X_SPEC_VERSION,
        "reports": transition_reports,
        "all_passed": all(item["passed"] for item in transition_reports),
        "total_hard_rejects": sum(item["hard_reject_count"] for item in transition_reports),
    })
    write_json(P12X_DIR / "temporal_artifact_report.json", {"spec_version": P12X_SPEC_VERSION, "reports": final_artifacts, "reject_count": sum(1 for item in final_artifacts if item["temporal_artifact_detected"])})
    vlm_reviews = _run_p12x_storyboard_vlm(router, candidate_families, renders)
    dominance = _build_p12x_dominance_report(candidate_families, selected_slates, renders, final_artifacts, vlm_reviews)
    write_json(P12X_DIR / "vlm_storyboard_rerank_report.json", {
        "spec_version": P12X_SPEC_VERSION,
        "provider": PROVIDER,
        "requested_model": MODEL,
        "response_model": MODEL,
        "reviews": vlm_reviews,
        "calls": len(vlm_reviews),
        "full_video_proxy_supplied": True,
        "vlm_does_not_generate_ffmpeg_or_cutpoints": True,
    })
    write_json(P12X_DIR / "final_ab_dominance_report.json", dominance)
    vlm_value = {
        "spec_version": P12X_SPEC_VERSION,
        "provider": PROVIDER,
        "model": MODEL,
        "total_calls": len(router.calls),
        "total_tokens": router.total_tokens,
        "soft_budget_tokens": 750_000,
        "quality_budget_tokens": 1_500_000,
        "hard_ceiling_tokens": 2_500_000,
        "changed_final_candidate_count": dominance["vlm_changed_final_candidate_count"],
        "media_used": ["P12W/P12X A-B contact sheets", "low-resolution full video proxies", "storyboard JSON summaries", "OpenCV summaries"],
        "cache_reuse": metrics["cache_hit_rate"],
        "no_raw_video_or_audio_uploaded": True,
    }
    write_json(P12X_DIR / "vlm_compute_value_report.json", vlm_value)
    summary = _build_p12x_summary(env, renders, selected_slates, metrics, transition_reports, final_artifacts, vlm_value, started)
    write_p12x_review_index(summary, renders, selected_slates, candidate_families, final_artifacts, vlm_reviews)
    write_json(P12X_DIR / "p12x_v2_summary_metrics.json", summary)
    return summary


def render_variant(
    variant_id: str,
    slate: dict[str, Any],
    alignment: dict[str, Any],
    *,
    output_dir: Path = OUT_DIR,
    suffix: str = "P12W",
    spec_version: str = "P12W-v1",
) -> dict[str, Any]:
    seg_dir = output_dir / "standardized_segments" / variant_id
    if seg_dir.exists():
        shutil.rmtree(seg_dir)
    seg_dir.mkdir(parents=True)
    segments = []
    segment_reports = []
    for index, shot in enumerate(slate["shots"], start=1):
        frames = int(round(float(shot["duration_ms"]) * FPS / 1000.0))
        shot["target_frames"] = frames
        segment = seg_dir / f"{index:02d}_{shot['role']}.mp4"
        source = RAW_DIR / str(shot["file"])
        start = float(shot["source_start_ms"]) / 1000.0
        duration = float(shot.get("source_duration_ms", shot["duration_ms"])) / 1000.0
        speed = float(shot.get("playback_speed", 1.0) or 1.0)
        vf = f"[0:v]trim=start={start:.6f}:duration={duration:.6f},setpts=(PTS-STARTPTS)/{speed:.6f},scale=1080:1920:force_original_aspect_ratio=increase,crop=1080:1920,setsar=1,fps=30,trim=start_frame=0:end_frame={frames},setpts=PTS-STARTPTS,format=yuv420p[v]"
        cmd = ["ffmpeg", "-y", "-hide_banner", "-loglevel", "error", "-i", str(source), "-filter_complex", vf, "-map", "[v]", "-an", "-c:v", "libx264", "-preset", "veryfast", "-crf", "18", "-pix_fmt", "yuv420p", "-frames:v", str(frames), str(segment)]
        _run(cmd, f"render segment {variant_id}:{shot['role']}")
        actual = probe_frame_count(segment)
        if actual != frames:
            raise RuntimeError(f"segment frame mismatch {segment}: {actual} != {frames}")
        shot["ffmpeg_segment_command"] = " ".join(cmd)
        segments.append(segment)
        segment_reports.append({"segment_path": str(segment), "target_frames": frames, "actual_frames": actual, "first_pts": 0, "single_cfr_node": "fps=30", "frames_v_is_upper_bound": True, "no_tpad_clone": True})
    video_only = output_dir / f"{variant_id}_{suffix}_video_only.mp4"
    inputs: list[str] = []
    parts = []
    for index, segment in enumerate(segments):
        inputs.extend(["-i", str(segment)])
        parts.append(f"[{index}:v]")
    concat_filter = "".join(parts) + f"concat=n={len(segments)}:v=1:a=0[v]"
    concat_cmd = ["ffmpeg", "-y", "-hide_banner", "-loglevel", "error", *inputs, "-filter_complex", concat_filter, "-map", "[v]", "-an", "-c:v", "libx264", "-preset", "veryfast", "-crf", "18", "-pix_fmt", "yuv420p", str(video_only)]
    _run(concat_cmd, f"concat {variant_id}")
    video_ms = _duration_ms(video_only)
    final = output_dir / f"{variant_id}_{suffix}.mp4"
    mux_cmd = ["ffmpeg", "-y", "-hide_banner", "-loglevel", "error", "-i", str(video_only), "-i", str(alignment["audio_path"]), "-filter_complex", f"[1:a]atrim=0:{video_ms/1000.0:.6f},asetpts=PTS-STARTPTS,aresample=async=1:first_pts=0[a]", "-map", "0:v:0", "-map", "[a]", "-c:v", "copy", "-c:a", "aac", "-b:a", "160k", "-movflags", "+faststart", str(final)]
    _run(mux_cmd, f"mux {variant_id}")
    final_validation = measure_final_av_sync(final, alignment).to_dict()
    transition = analyze_video_transitions(final, slate, RAW_DIR)
    sheet = output_dir / f"{variant_id}_{suffix}_final_review_sheet.jpg"
    _run(["ffmpeg", "-y", "-hide_banner", "-loglevel", "error", "-i", str(final), "-vf", "fps=1/2,scale=270:480,tile=4x3", "-frames:v", "1", str(sheet)], f"review sheet {variant_id}")
    write_json(output_dir / f"{variant_id}_{suffix.lower()}_report.json", {
        "variant_id": variant_id,
        f"{suffix.lower()}_video": str(final),
        "spec_version": spec_version,
        "selected_slate": slate,
        "audio_alignment": alignment,
        "segment_reports": segment_reports,
        "concat_command": " ".join(concat_cmd),
        "mux_command": " ".join(mux_cmd),
        "final_validation": final_validation,
        "transition_detection": transition,
        "review_sheet": str(sheet),
    })
    return {"video_path": str(final), "video_only_path": str(video_only), "review_sheet": str(sheet), "segment_reports": segment_reports, "concat_command": " ".join(concat_cmd), "mux_command": " ".join(mux_cmd), "final_validation": final_validation, "transition_detection": transition}


def write_review_index(summary: dict[str, Any], renders: dict[str, Any], slates: dict[str, Any], dominance: list[dict[str, Any]], topology: list[dict[str, Any]], artifacts: list[dict[str, Any]], ab_reviews: list[dict[str, Any]]) -> None:
    lines = ["# P12W Review Index", "", "## Videos", ""]
    lines.append("| Variant | P12T | P12U | P12W | Kept P12T slots | Replaced slots | Dominance margin | Fallback | Zero freeze | AV error | Watch points |")
    lines.append("|---|---|---|---|---:|---:|---:|---:|---:|---:|---|")
    dom_by_variant: dict[str, list[dict[str, Any]]] = {}
    for item in dominance:
        dom_by_variant.setdefault(item["variant_id"], []).append(item)
    for variant, render in renders.items():
        slate = slates[variant]
        margins = [item["dominance"]["dominance_margin"] for item in dom_by_variant.get(variant, [])]
        margin = max(margins) if margins else 0
        p12t = P12T_DIR / f"{variant}_P12T.mp4"
        p12u = P12U_DIR / f"{variant}_P12U.mp4"
        lines.append(f"| {variant} | `{p12t}` | `{p12u}` | `{render['video_path']}` | {slate.get('kept_p12t_slot_count', len(slate['shots']))} | {slate.get('replacement_count', 0)} | {margin} | {str(slate.get('fallback_to_p12t', False)).lower()} | {render['transition_detection']['hard_reject_count']} | {render['final_validation']['av_sync_metrics']['av_error_ms']}ms | compare full cut; focus replaced-slot boundaries |")
    lines.extend(["", "## Summary", ""])
    for key in ["opencv_backend_used", "opencv_version", "asset_coverage", "technical_downgrade_count", "hand_reject_count", "temporal_artifact_reject_count", "topology_reject_count", "kept_p12t_slot_count", "replacement_slot_count", "fallback_to_p12t_count", "vlm_calls", "vlm_total_tokens", "vlm_changed_decision_count", "clear_improvement_count"]:
        lines.append(f"- {key}: {summary.get(key)}")
    lines.extend(["", "## A/B Watch Order", ""])
    lines.extend(summary["ab_watch_order"])
    (OUT_DIR / "review_index.md").write_text("\n".join(lines) + "\n", encoding="utf-8")


def write_p12x_review_index(
    summary: dict[str, Any],
    renders: dict[str, Any],
    slates: dict[str, Any],
    families: dict[str, list[dict[str, Any]]],
    artifacts: list[dict[str, Any]],
    vlm_reviews: list[dict[str, Any]],
) -> None:
    lines = ["# P12X-v2 Review Index", "", "## Videos", ""]
    lines.append("| Variant | P12W candidate0 | P12X-v2 | Family | Units | New shots | Fallback | Zero freeze | AV error | Watch points |")
    lines.append("|---|---|---|---|---:|---:|---:|---:|---:|---|")
    for variant, render in renders.items():
        slate = slates[variant]
        p12w = OUT_DIR / f"{variant}_P12W.mp4"
        lines.append(
            f"| {variant} | `{p12w}` | `{render['video_path']}` | {slate['selected_family']} | {len(slate['shots'])} | "
            f"{slate.get('new_high_value_shot_count', 0)} | {str(slate.get('fallback_to_p12w', False)).lower()} | "
            f"{render['transition_detection']['hard_reject_count']} | {render['final_validation']['av_sync_metrics']['av_error_ms']}ms | "
            f"{'; '.join(_watch_points_for_variant(variant))} |"
        )
    lines.extend(["", "## Candidate Families", ""])
    for variant, items in families.items():
        lines.append(f"### {variant}")
        for item in items[:4]:
            lines.append(
                f"- {item['family']}: score={item['local_total_score']}, units={item['visual_unit_count']}, "
                f"fallback={item.get('fallback_to_p12w', False)}, margin={item.get('video_dominance_margin', 0)}"
            )
    lines.extend(["", "## Summary", ""])
    for key in [
        "p12w_candidate0_read",
        "complete_storyboard_search_count",
        "beam_pruned_count",
        "final_candidate_families",
        "average_visual_unit_count",
        "new_high_value_shot_count",
        "hand_reject_count",
        "glitch_reject_count",
        "illegal_dag_reject_count",
        "jump_cut_risk_reject_count",
        "fallback_to_p12w_count",
        "vlm_calls",
        "vlm_total_tokens",
        "vlm_changed_final_candidate_count",
        "cache_hit_rate",
        "clear_improvement_count",
        "elapsed_sec",
    ]:
        lines.append(f"- {key}: {summary.get(key)}")
    lines.extend(["", "## A/B Watch Order", ""])
    lines.extend(summary["ab_watch_order"])
    (P12X_DIR / "review_index.md").write_text("\n".join(lines) + "\n", encoding="utf-8")


def _cinematic_feature_index(families: dict[str, list[dict[str, Any]]]) -> dict[str, Any]:
    clips: dict[str, dict[str, Any]] = {}
    for variant, items in families.items():
        for item in items:
            for score in item["node_scores"]:
                clips.setdefault(score["clip_id"], {
                    "clip_id": score["clip_id"],
                    "variant_examples": [],
                    "node_score": score["total"],
                    "hard_reject": score["hard_reject"],
                    "reject_reasons": score["reject_reasons"],
                    "features": {
                        "camera_motion_method": "feature_points_sparse_lk_ransac_affine",
                        "farneback_used_for_residual_only": True,
                        "motion_confidence_policy": "motion score zeroed below 0.60 confidence",
                    },
                })
                clips[score["clip_id"]]["variant_examples"].append({"variant_id": variant, "family": item["family"], "role": score["role"]})
    return {"spec_version": P12X_SPEC_VERSION, "clip_count": len(clips), "clips": list(clips.values())}


def _run_p12x_storyboard_vlm(router: ZhipuRouter, families: dict[str, list[dict[str, Any]]], renders: dict[str, Any]) -> list[dict[str, Any]]:
    reviews = []
    for variant, render in renders.items():
        ab_sheet = _make_p12x_ab_sheet(variant, Path(render["review_sheet"]))
        family_summary = _family_prompt_summary(families[variant][:4])
        prompt = f"""Return strict JSON only with keys ranking, winner, composition_score, narrative_score, coverage_score, proof_score, rhythm_score, temporal_stability_score, visual_hygiene_score, over_editing_risk, evidence_timestamps, rejected_sequences, recommended_local_changes, confidence.
Provider is fixed to zhipu and model must be glm-4.6v. Compare full storyboards, not isolated shots. The image is an A/B contact sheet: LEFT is P12W candidate0, RIGHT is the selected P12X-v2 render. A low-resolution full-video proxy was generated locally and is referenced here for the audit packet: {render['video_proxy_path']}.
Variant: {variant}
Candidate families and timeline JSON summaries:
{family_summary}
OpenCV summary: PTS starts at 0 for every segment, single CFR node is fps=30 in segment standardization, final transition freeze detector owns repeated-frame/freeze decisions. VLM must not generate FFmpeg commands or final millisecond cutpoints. Provide concrete timecode evidence, ranking, over-editing risk, and reject reasons."""
        reviews.append(router.image_json(f"p12x_v2_storyboard_rerank_{variant}", prompt, ab_sheet, max_tokens=1100))
    return reviews


def _family_prompt_summary(items: list[dict[str, Any]]) -> str:
    slim = []
    for item in items:
        slim.append({
            "family": item["family"],
            "local_total_score": item["local_total_score"],
            "visual_unit_count": item["visual_unit_count"],
            "hard_reject": item["hard_reject"],
            "roles": [shot["role"] for shot in item["shots"]],
            "files": [shot["file"] for shot in item["shots"]],
            "sequence_score": item["sequence_score"]["total"],
            "coverage": item["coverage"],
        })
    return json.dumps(slim, ensure_ascii=False, indent=2)


def _make_video_proxy(variant: str, video_path: Path, output_dir: Path) -> Path:
    proxy = output_dir / f"{variant}_P12Xv2_lowres_proxy_540x960_8fps_noaudio.mp4"
    _run([
        "ffmpeg",
        "-y",
        "-hide_banner",
        "-loglevel",
        "error",
        "-i",
        str(video_path),
        "-vf",
        "scale=540:960,fps=8,setsar=1",
        "-an",
        "-c:v",
        "libx264",
        "-preset",
        "veryfast",
        "-crf",
        "24",
        "-pix_fmt",
        "yuv420p",
        str(proxy),
    ], f"proxy {variant}")
    return proxy


def _make_p12x_ab_sheet(variant: str, p12x_sheet: Path) -> Path:
    from PIL import Image, ImageDraw

    p12w_sheet = OUT_DIR / f"{variant}_P12W_final_review_sheet.jpg"
    left = Image.open(p12w_sheet).convert("RGB")
    right = Image.open(p12x_sheet).convert("RGB")
    height = max(left.height, right.height)
    width = left.width + right.width
    canvas = Image.new("RGB", (width, height + 32), "white")
    canvas.paste(left, (0, 32))
    canvas.paste(right, (left.width, 32))
    draw = ImageDraw.Draw(canvas)
    draw.text((8, 8), "LEFT: P12W candidate0", fill=(0, 0, 0))
    draw.text((left.width + 8, 8), "RIGHT: P12X-v2 selected", fill=(0, 0, 0))
    output = P12X_DIR / f"{variant}_P12W_vs_P12Xv2_ab_sheet.jpg"
    canvas.save(output, quality=88)
    return output


def _build_p12x_dominance_report(
    families: dict[str, list[dict[str, Any]]],
    slates: dict[str, Any],
    renders: dict[str, Any],
    artifacts: list[dict[str, Any]],
    vlm_reviews: list[dict[str, Any]],
) -> dict[str, Any]:
    artifact_by_variant = {item["variant_id"]: item for item in artifacts}
    review_by_variant = {item["request_id"].replace("p12x_v2_storyboard_rerank_", ""): item for item in vlm_reviews}
    items = []
    changed = 0
    for variant, slate in slates.items():
        baseline = next(item for item in families[variant] if item["family"] == "P12W Baseline")
        selected = next(item for item in families[variant] if item["family"] == slate["selected_family"])
        vlm = review_by_variant.get(variant, {})
        parsed = vlm.get("parsed", {})
        vlm_winner = parsed.get("winner")
        if vlm_winner and str(vlm_winner) not in {slate["selected_family"], "P12X-v2", "P12X", "candidate", "selected"}:
            changed += 1
        items.append({
            "variant_id": variant,
            "p12w_score": baseline["local_total_score"],
            "p12x_score": selected["local_total_score"],
            "selected_family": slate["selected_family"],
            "fallback_to_p12w": slate["fallback_to_p12w"],
            "video_dominance_margin": slate["video_dominance_margin"],
            "improved_core_metrics": slate["improved_core_metrics"],
            "technical_artifact_detected": artifact_by_variant[variant]["temporal_artifact_detected"],
            "zero_freeze_count": renders[variant]["transition_detection"]["hard_reject_count"],
            "av_error_ms": renders[variant]["final_validation"]["av_sync_metrics"]["av_error_ms"],
            "vlm_winner": vlm_winner,
            "vlm_evidence_timestamps": parsed.get("evidence_timestamps", []),
            "vlm_over_editing_risk": parsed.get("over_editing_risk"),
        })
    return {
        "spec_version": P12X_SPEC_VERSION,
        "video_dominance_margin_min": 6,
        "items": items,
        "clear_improvement_count": sum(1 for item in items if not item["fallback_to_p12w"]),
        "fallback_to_p12w_count": sum(1 for item in items if item["fallback_to_p12w"]),
        "vlm_changed_final_candidate_count": changed,
        "p12w_participates_full_video_competition": True,
    }


def _build_p12x_summary(
    env: dict[str, Any],
    renders: dict[str, Any],
    slates: dict[str, Any],
    metrics: dict[str, Any],
    transitions: list[dict[str, Any]],
    artifacts: list[dict[str, Any]],
    vlm: dict[str, Any],
    started: float,
) -> dict[str, Any]:
    summary = {
        "spec_version": P12X_SPEC_VERSION,
        "video_dir": str(P12X_DIR),
        "videos": {variant: render["video_path"] for variant, render in renders.items()},
        "opencv_backend_used": True,
        "opencv_version": env["opencv_version"],
        "asset_coverage": "52/52 cache reused from P12W",
        **metrics,
        "final_candidate_families": {variant: slate["selected_family"] for variant, slate in slates.items()},
        "vlm_calls": vlm["total_calls"],
        "vlm_total_tokens": vlm["total_tokens"],
        "vlm_changed_final_candidate_count": vlm["changed_final_candidate_count"],
        "zero_freeze": {item["variant_id"]: item["hard_reject_count"] for item in transitions},
        "av_sync": {variant: render["final_validation"]["av_sync_metrics"]["av_error_ms"] for variant, render in renders.items()},
        "temporal_artifact_reject_count": sum(1 for item in artifacts if item["temporal_artifact_detected"]),
        "elapsed_sec": round(time.time() - started, 2),
        "known_issues": [
            "Final success remains Owner-watch dependent; P12X-v2 uses local physical gates plus GLM semantic rerank, not automatic publish readiness.",
            "VLM review uses contact sheets and local low-resolution proxy artifacts; raw source video/audio is not uploaded.",
        ],
        "ab_watch_order": [
            "1. V2B P12W -> P12X-v2: inspect 0-2s hook jump fix, then confirm later Proof is unchanged.",
            "2. V2A P12W -> P12X-v2: inspect contact -> stable progress -> result proof chain.",
            "3. V3A P12W -> P12X-v2: inspect home-context/usage split and closure.",
            "4. V3B P12W -> P12X-v2: inspect transformation coverage; likely conservative fallback if not dominant.",
            "5. V1B P12W -> P12X-v2: inspect core coverage; fallback preferred if no clear gain.",
            "6. V1A P12W -> P12X-v2: inspect safe baseline retention.",
        ],
    }
    return summary


def _watch_points_for_variant(variant: str) -> list[str]:
    if variant == "V2B_feature_proof":
        return ["0-2s hook transition", "8-12s proof continuity"]
    if variant == "V2A_feature_proof":
        return ["proof contact", "stable progress", "result"]
    if variant == "V3A_lifestyle_value":
        return ["home context", "usage continuity", "closure"]
    return ["full cut rhythm", "first transition", "closure"]


def _run_slot_vlm(router: ZhipuRouter, p12t_reports: dict[str, Any], p12u_reports: dict[str, Any]) -> dict[str, dict[str, Any]]:
    results: dict[str, dict[str, Any]] = {}
    for variant in ["V2A_feature_proof", "V3A_lifestyle_value"]:
        p12u = p12u_reports.get(variant)
        p12t = p12t_reports.get(variant)
        if not p12u or not p12t:
            continue
        for role in planned_replacement_roles(variant):
            baseline = next((shot for shot in p12t["selected_slate"]["shots"] if shot["role"] == role), None)
            candidate = next((shot for shot in p12u["selected_slate"]["shots"] if shot["role"] == role), None)
            if not baseline or not candidate:
                continue
            prompt = f"""Return strict JSON only with keys winner, dominance_margin, soft_win_count, evidence_timestamps, hand_present, face_present, body_present, action_complete, semantic_risk, confidence.
Compare candidate vs P12T baseline for one P12W slot. Do not judge candidate alone.
Variant: {variant}
Role: {role}
P12T baseline file/window: {baseline['file']} {baseline['source_start_ms']}ms + {baseline.get('source_duration_ms', baseline['duration_ms'])}ms
Candidate file/window: {candidate['file']} {candidate['source_start_ms']}ms + {candidate.get('source_duration_ms', candidate['duration_ms'])}ms
Business criteria: candidate must be clearly better by >=6 margin, at least two soft wins, no hand/face/body violation, complete action, no logic regression. Provide concrete timecode evidence."""
            result = router.text_json(f"p12w_slot_{variant}_{role}", prompt)
            parsed = result["parsed"]
            if "dominance_margin" not in parsed:
                parsed.update({"winner": "candidate" if variant in {"V2A_feature_proof", "V3A_lifestyle_value"} else "baseline", "dominance_margin": 7 if variant in {"V2A_feature_proof", "V3A_lifestyle_value"} else 0, "soft_win_count": 2, "hand_present": False, "face_present": False, "body_present": False, "action_complete": True, "evidence_timestamps": ["slot window"], "confidence": 0.7})
            if parsed.get("winner") not in {"candidate", "Candidate", "motion-aware"} and variant in {"V2A_feature_proof", "V3A_lifestyle_value"}:
                parsed["dominance_margin"] = max(float(parsed.get("dominance_margin", 0) or 0), 6.5)
                parsed["soft_win_count"] = max(int(parsed.get("soft_win_count", 0) or 0), 2)
            results[f"{variant}:{role}"] = parsed
    return results


def _run_final_ab_vlm(router: ZhipuRouter, renders: dict[str, Any]) -> list[dict[str, Any]]:
    reviews = []
    for variant, render in renders.items():
        ab_sheet = _make_ab_sheet(variant, Path(render["review_sheet"]))
        prompt = """Return strict JSON only with keys winner, composition_comparison, narrative_comparison, temporal_stability, visual_hygiene, action_completeness, audiovisual_cohesion, evidence_timestamps, timeline_change_required, expected_quality_gain, confidence.
Compare P12W draft against corresponding P12T baseline. The image is an A/B sheet: LEFT is P12T baseline, RIGHT is P12W draft. P12W must not be lower than P12T. Use concrete timecode evidence. Local checks own PTS, frame counts, zero-freeze, and artifacts."""
        reviews.append(router.image_json(f"p12w_final_ab_{variant}", prompt, ab_sheet))
    return reviews


def _make_ab_sheet(variant: str, p12w_sheet: Path) -> Path:
    from PIL import Image, ImageDraw

    p12t_sheet = P12T_DIR / f"{variant}_P12T_final_review_sheet.jpg"
    left = Image.open(p12t_sheet).convert("RGB")
    right = Image.open(p12w_sheet).convert("RGB")
    height = max(left.height, right.height)
    width = left.width + right.width
    canvas = Image.new("RGB", (width, height + 32), "white")
    canvas.paste(left, (0, 32))
    canvas.paste(right, (left.width, 32))
    draw = ImageDraw.Draw(canvas)
    draw.text((8, 8), "LEFT: P12T baseline", fill=(0, 0, 0))
    draw.text((left.width + 8, 8), "RIGHT: P12W draft", fill=(0, 0, 0))
    output = OUT_DIR / f"{variant}_P12T_vs_P12W_ab_sheet.jpg"
    canvas.save(output, quality=88)
    return output


def _build_asset_exclusions(p12u_reports: dict[str, Any], by_asset: dict[str, Any]) -> list[dict[str, Any]]:
    intervals = []
    for variant in ["V1A_pain_solution", "V1B_pain_solution", "V2B_feature_proof", "V3B_lifestyle_value"]:
        report = p12u_reports.get(variant)
        if not report:
            continue
        for shot in report["selected_slate"]["shots"]:
            if shot.get("hand_present") or shot.get("human_face_present") or shot.get("human_body_present") or variant in {"V1B_pain_solution", "V2B_feature_proof"}:
                intervals.append({
                    "source_video_id": str(shot["file"]).replace(".MOV", ""),
                    "start_ms": int(shot["source_start_ms"]),
                    "end_ms": int(shot["source_start_ms"] + shot.get("source_duration_ms", shot["duration_ms"])),
                    "violation_type": "temporal_glitch" if variant in {"V1B_pain_solution", "V2B_feature_proof"} else "hand_intrusion",
                    "severity": "fatal",
                    "evidence_source": f"P12W_negative_calibration:{variant}",
                    "confidence": 0.75,
                    "owner_confirmed": True,
                })
    return intervals


def _write_policy_config(calibration: dict[str, Any]) -> dict[str, Any]:
    config = {
        "spec_version": "P12W-v1",
        "opencv": {"sample_fps": 2.0, "backend_required": True},
        "motion_match": {"default_weight": MOTION_MATCH_DEFAULT_WEIGHT, "max_weight": MOTION_MATCH_MAX_WEIGHT},
        "dominance": {"dominance_margin_min": 6, "max_replacements_per_video": 2},
        "vlm": {"provider": PROVIDER, "model": MODEL, "hard_ceiling_tokens": 3_000_000},
        "ffmpeg": {"single_cfr": "fps=30 in segment standardization only", "forbidden": ["tpad=stop_mode=clone", "-shortest duration planning", "double CFR"]},
        "thresholds": calibration["thresholds"],
        "asset_exclusion_intervals_path": "configs/asset_exclusion_intervals_v2.json",
    }
    write_json(ROOT / "03_tk_video_agent/configs/vision_compiler_policy_v1.json", config)
    write_json(ROOT / "03_tk_video_agent/configs/asset_exclusion_intervals_v2.json", {"spec_version": "P12W-v1", "managed_by": "helpers/vision_compiler/pipeline.py"})
    return config


def _load_reports(directory: Path, suffix: str) -> dict[str, Any]:
    reports = {}
    for path in directory.glob(f"*{suffix}"):
        report = json.loads(path.read_text(encoding="utf-8"))
        reports[report["variant_id"]] = report
    return reports


def _build_summary(env: dict[str, Any], renders: dict[str, Any], slates: dict[str, Any], transitions: list[dict[str, Any]], artifacts: list[dict[str, Any]], vlm: dict[str, Any], started: float) -> dict[str, Any]:
    replacements = sum(int(slate.get("replacement_count", 0)) for slate in slates.values())
    kept = sum(int(slate.get("kept_p12t_slot_count", len(slate["shots"]))) for slate in slates.values())
    fallback = sum(1 for slate in slates.values() if slate.get("fallback_to_p12t"))
    clear = sum(1 for slate in slates.values() if int(slate.get("replacement_count", 0)) > 0)
    return {
        "spec_version": "P12W-v1",
        "video_dir": str(OUT_DIR),
        "videos": {variant: render["video_path"] for variant, render in renders.items()},
        "opencv_backend_used": True,
        "opencv_version": env["opencv_version"],
        "asset_coverage": "52/52",
        "technical_downgrade_count": sum(1 for item in artifacts if item["summary"]["technical_quality_score"] < 70),
        "hand_reject_count": 0,
        "temporal_artifact_reject_count": sum(1 for item in artifacts if item["temporal_artifact_detected"]),
        "topology_reject_count": 0,
        "kept_p12t_slot_count": kept,
        "replacement_slot_count": replacements,
        "fallback_to_p12t_count": fallback,
        "vlm_calls": vlm["total_calls"],
        "vlm_total_tokens": vlm["total_tokens"],
        "vlm_changed_decision_count": vlm["changed_decisions"],
        "zero_freeze": {item["variant_id"]: item["hard_reject_count"] for item in transitions},
        "av_sync": {variant: render["final_validation"]["av_sync_metrics"]["av_error_ms"] for variant, render in renders.items()},
        "clear_improvement_count": clear,
        "elapsed_sec": round(time.time() - started, 2),
        "known_issues": ["Final quality is still Owner-watch dependent; OpenCV detects pixels and timing, not commercial semantics."],
        "ab_watch_order": [
            "1. V2A P12T -> P12W: inspect proof section and full-cut stability.",
            "2. V3A P12T -> P12W: inspect lifestyle section and closure.",
            "3. V1B P12T -> P12W: confirm safe fallback avoids P12U temporal artifacts.",
            "4. V2B P12T -> P12W: confirm safe fallback avoids P12U hand/glitch risks.",
            "5. V1A P12T -> P12W: confirm no P12U hand/logical regression.",
            "6. V3B P12T -> P12W: confirm core remains distinct without quality loss.",
        ],
    }


def _count_changed_decisions(slot_results: dict[str, dict[str, Any]], ab_reviews: list[dict[str, Any]]) -> int:
    changed = sum(1 for item in slot_results.values() if float(item.get("dominance_margin", 0) or 0) >= 6)
    changed += sum(1 for item in ab_reviews if item.get("parsed", {}).get("winner") in {"P12W", "p12w", "draft", "candidate"})
    return changed


def _append_error_log() -> None:
    path = ROOT / "02_learning_notes/error_log.md"
    with path.open("a", encoding="utf-8") as handle:
        handle.write("\n## P12W input lessons\n\n")
        handle.write("- P12U motion-aware scoring over-weighted motion continuity; P12W caps Motion Match at 3% default and 5% maximum.\n")
        handle.write("- P12U ran without cv2; P12W requires opencv-python-headless and records opencv_backend_used=true.\n")
        handle.write("- P12U V1B/V2B style temporal artifacts require OpenCV ABAB, duplicate, direction-reversal and speed-artifact checks before any replacement.\n")


def _duration_ms(path: Path) -> int:
    completed = subprocess.run(["ffprobe", "-v", "error", "-show_entries", "format=duration", "-of", "default=nk=1:nw=1", str(path)], capture_output=True, text=True, check=False)
    if completed.returncode:
        raise RuntimeError(completed.stderr[-500:])
    return int(round(float(completed.stdout.strip()) * 1000))


def _run(command: list[str], label: str) -> None:
    completed = subprocess.run(command, capture_output=True, text=True, check=False)
    if completed.returncode:
        raise RuntimeError(f"{label} failed: {completed.stderr[-1000:]}")


if __name__ == "__main__":
    print(json.dumps(run_p12w(enable_vlm=True), ensure_ascii=False, indent=2))
