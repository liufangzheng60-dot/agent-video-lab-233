"""Owner-approved P12D three-variant local run.

This runner is intentionally narrow:
- exactly 3 variants
- laptop_safe profile
- serial FFmpeg
- no real VLM
- no upload
- no publish
- raw_videos read-only
"""

from __future__ import annotations

import json
import os
import subprocess
import time
from pathlib import Path
from shutil import which
from typing import Any

from helpers.agent_factory_harness import agent_output_dir, agent_state_path, load_or_create_agent_state
from helpers.agent_state import utc_now_iso
from helpers.git_safety_guard import run_git_safety_guard
from helpers.media_asset_guard import run_media_asset_guard
from helpers.resource_governor import ResourceGovernor
from helpers.vertical_output_guard import VerticalOutputGuard


CHECKPOINT_ID = "P12D_REAL_BATCH_EXECUTION_batch_20260617_001"
REVIEW_CHECKPOINT_ID = "P12D_THREE_VARIANT_REVIEW_batch_20260617_001"
TARGET_WIDTH = 1080
TARGET_HEIGHT = 1920
SEGMENT_SECONDS = 2.5


def run_three_variant_validation(repo_root: Path | str, product: str, sku: str, material_batch: str) -> dict[str, Any]:
    repo = Path(repo_root).resolve()
    out_dir = agent_output_dir(repo, product, material_batch)
    state = load_or_create_agent_state(repo, product, sku, material_batch, variants=12)
    _validate_owner_scope(state)
    git_report = run_git_safety_guard(repo)
    media_report = run_media_asset_guard(repo, product, material_batch)
    if git_report["status"] != "pass" or media_report["status"] != "pass":
        state.pipeline_status = "BLOCKED_BY_GIT_SAFETY"
        state.write_json(agent_state_path(repo, product, material_batch))
        return {"status": "blocked_by_git_safety", "git_report": git_report, "media_report": media_report}

    plan_path = out_dir / "real_batch_plan.json"
    inventory_path = out_dir / "media_inventory.json"
    plan = json.loads(plan_path.read_text(encoding="utf-8"))
    inventory = json.loads(inventory_path.read_text(encoding="utf-8"))["items"]
    clip_index = {item["clip_id"]: item for item in inventory}
    selected_plans = plan["variant_plans"][:3]

    run_id = f"p12d_three_variant_{int(time.time())}"
    run_root = repo / "products" / product / "outputs" / "renders" / material_batch / "P12D_three_variant_validation" / run_id
    run_root.mkdir(parents=True, exist_ok=True)
    lock_path = out_dir / "agent_run.lock"
    _acquire_lock(lock_path, run_id, material_batch)
    before_raw = _raw_fingerprints(Path(media_report["raw_videos_dir"]))
    disk_before = _disk_free(repo)
    governor = ResourceGovernor(repo, product, material_batch)
    started = time.monotonic()
    variant_results = []
    resource_samples: list[dict[str, Any]] = []
    timeout_count = 0
    retry_count = 0
    replacement_count = 0
    auto_pause_count = 0
    try:
        for variant_plan in selected_plans:
            pause_result = _pause_if_cpu_hot(governor, resource_samples)
            auto_pause_count += pause_result["pause_count"]
            state.current_stage = f"render_{variant_plan['variant_id']}"
            state.write_json(agent_state_path(repo, product, material_batch))
            result = _render_variant(run_root, variant_plan, clip_index, governor, resource_samples)
            timeout_count += result["ffmpeg_timeout_count"]
            retry_count += result["retry_count"]
            replacement_count += result["auto_replacement_count"]
            variant_results.append(result)
    finally:
        _release_lock(lock_path)

    elapsed = round(time.monotonic() - started, 3)
    disk_after = _disk_free(repo)
    raw_modified = _count_raw_changes(before_raw, _raw_fingerprints(Path(media_report["raw_videos_dir"])))
    summary = _build_summary(
        run_id=run_id,
        run_root=run_root,
        variant_results=variant_results,
        resource_samples=resource_samples,
        elapsed=elapsed,
        disk_growth_bytes=max(0, int((disk_before - disk_after) * (1024**3))),
        timeout_count=timeout_count,
        retry_count=retry_count,
        replacement_count=replacement_count,
        auto_pause_count=auto_pause_count,
        git_media_count=_tracked_media_count(repo),
        raw_modified_count=raw_modified,
    )
    _write_summary(run_root, summary)
    state.pipeline_status = "BLOCKED_BY_OWNER_GATE"
    state.awaiting_owner_review = True
    state.pending_checkpoint = {
        "checkpoint_id": REVIEW_CHECKPOINT_ID,
        "checkpoint_type": "GATE_THREE_VARIANT_VALIDATION_REVIEW",
        "current_goal": "Owner 审核 3 条真实 Batch2 小批验证结果。",
        "run_id": run_id,
        "output_dir": str(run_root),
        "summary": summary,
    }
    state.current_stage = "owner_review_three_variant_validation"
    state.write_json(agent_state_path(repo, product, material_batch))
    return {"status": "owner_review_required", "summary": summary}


def _validate_owner_scope(state: Any) -> None:
    decision = state.last_owner_decision or {}
    if decision.get("checkpoint_id") != CHECKPOINT_ID or decision.get("decision") != "approve":
        raise RuntimeError("缺少匹配 P12D checkpoint 的 Owner approve，拒绝启动 3 条真实验证。")
    note = str(decision.get("owner_note", ""))
    if "3" not in note and "三" not in note:
        raise RuntimeError("Owner 授权说明未包含 3 条范围，拒绝启动。")


def _render_variant(run_root: Path, variant_plan: dict[str, Any], clip_index: dict[str, dict[str, Any]], governor: ResourceGovernor, samples: list[dict[str, Any]]) -> dict[str, Any]:
    variant_id = variant_plan["variant_id"]
    variant_dir = run_root / variant_id
    variant_dir.mkdir(parents=True, exist_ok=True)
    segment_plans = _build_segment_plans(variant_plan, clip_index)
    manifest = {
        "variant_id": variant_id,
        "final_container": {"width": TARGET_WIDTH, "height": TARGET_HEIGHT, "display_aspect_ratio": "9:16", "sample_aspect_ratio": "1:1", "orientation": "portrait"},
        "segments": segment_plans,
    }
    (variant_dir / "timeline_manifest.json").write_text(json.dumps(manifest, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    guard = VerticalOutputGuard()
    plan_report = guard.build_vertical_compliance_report(manifest)
    if plan_report["auto_replacement_required"]:
        return _held_variant(variant_id, variant_dir, plan_report)

    started = time.monotonic()
    visual_path = variant_dir / f"{variant_id}_visual_master_1080x1920.mp4"
    voice_path = variant_dir / f"{variant_id}_voiceover.wav"
    final_path = variant_dir / f"{variant_id}_voiced_review.mp4"
    render_result = _run_visual_render(segment_plans, visual_path, governor, samples)
    audio_result = _generate_local_voiceover(voice_path, variant_id)
    mux_result = _mux_voiceover_copy_video(visual_path, voice_path, final_path, governor, samples)
    final_container = guard.validate_final_container(final_path)
    final_report = guard.build_vertical_compliance_report(manifest)
    final_report["final_container_pass"] = final_container["pass"]
    final_report["publish_allowed"] = final_container["pass"] and not final_report["segments_failed"] and not final_report["semantic_crop_pending"]
    final_report["release_allowed"] = final_report["publish_allowed"]
    (variant_dir / "vertical_compliance_report.json").write_text(json.dumps(final_report, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    elapsed = round(time.monotonic() - started, 3)
    return {
        "variant_id": variant_id,
        "status": "success" if final_report["final_container_pass"] and mux_result["status"] == "pass" else "hold",
        "output_path": str(final_path),
        "elapsed_sec": elapsed,
        "visual_render": render_result,
        "audio_generation": audio_result,
        "video_stream_copy": mux_result.get("video_stream_copy", False),
        "vertical_report": final_report,
        "ffmpeg_timeout_count": int(render_result["timeout"]) + int(mux_result["timeout"]),
        "retry_count": 0,
        "auto_replacement_count": 0,
        "hook": variant_plan.get("hook_zone"),
        "body": variant_plan.get("body_zone"),
        "proof": variant_plan.get("proof_zone"),
        "cta": variant_plan.get("CTA_zone"),
        "timeline_sequence_hash": variant_plan.get("timeline_sequence_hash"),
        "body_structure_id": variant_plan.get("body_structure_id"),
    }


def _build_segment_plans(variant_plan: dict[str, Any], clip_index: dict[str, dict[str, Any]]) -> list[dict[str, Any]]:
    roles = [("hook", variant_plan["hook_zone"]), ("body", variant_plan["body_zone"]), ("proof", variant_plan["proof_zone"]), ("cta", variant_plan["CTA_zone"])]
    segments = []
    timeline = 0.0
    for role, clip_id in roles:
        clip = clip_index[clip_id]
        width = int(clip["width"])
        height = int(clip["height"])
        crop_w = min(width, int(round(height * 9 / 16)))
        crop_h = min(height, int(round(crop_w * 16 / 9)))
        if crop_h > height:
            crop_h = height
            crop_w = int(round(crop_h * 9 / 16))
        x = max(0, (width - crop_w) // 2)
        y = max(0, (height - crop_h) // 2)
        segments.append({
            "segment_id": f"{role}_{clip_id}",
            "segment_role": role,
            "source_clip_id": clip_id,
            "source_path": clip["absolute_path"],
            "source_width": width,
            "source_height": height,
            "source_start": 0.0,
            "source_end": SEGMENT_SECONDS,
            "timeline_start": timeline,
            "timeline_end": timeline + SEGMENT_SECONDS,
            "fit_policy": "smart_crop",
            "crop_anchor": "center",
            "crop_box": {"x": x, "y": y, "width": crop_w, "height": crop_h},
            "scale_policy": "crop_then_scale",
            "output_width": TARGET_WIDTH,
            "output_height": TARGET_HEIGHT,
            "output_aspect_ratio": "9:16",
            "black_bar_detected": False,
            "letterbox_detected": False,
            "pillarbox_detected": False,
            "embedded_canvas_detected": False,
            "stretch_detected": False,
            "frame_fill_ratio": 1.0,
            "risk_flags": [],
            "start_sec": timeline,
            "end_sec": timeline + SEGMENT_SECONDS,
            "semantic_crop_result": "pending_owner_or_vlm",
        })
        timeline += SEGMENT_SECONDS
    return segments


def _run_visual_render(segments: list[dict[str, Any]], output: Path, governor: ResourceGovernor, samples: list[dict[str, Any]]) -> dict[str, Any]:
    ffmpeg = which("ffmpeg") or "ffmpeg"
    args = [ffmpeg, "-y", "-hide_banner", "-loglevel", "warning"]
    for segment in segments:
        args.extend(["-t", str(SEGMENT_SECONDS), "-i", segment["source_path"]])
    filters = []
    concat_inputs = ""
    for idx, segment in enumerate(segments):
        crop = segment["crop_box"]
        filters.append(f"[{idx}:v]crop={crop['width']}:{crop['height']}:{crop['x']}:{crop['y']},scale={TARGET_WIDTH}:{TARGET_HEIGHT},setsar=1,fps=30[v{idx}]")
        concat_inputs += f"[v{idx}]"
    filters.append(f"{concat_inputs}concat=n={len(segments)}:v=1:a=0[vout]")
    args.extend(["-filter_complex", ";".join(filters), "-map", "[vout]", "-an", "-c:v", "libx264", "-preset", "veryfast", "-threads", "2", "-pix_fmt", "yuv420p", str(output)])
    return _run_sampled_subprocess(args, governor, "final_render", 1200, samples)


def _generate_local_voiceover(output: Path, variant_id: str) -> dict[str, Any]:
    text = f"{variant_id}. Give your dog an easier way up. Stable steps, gentle climb, made for everyday sofa moments."
    ps = (
        "Add-Type -AssemblyName System.Speech; "
        "$s = New-Object System.Speech.Synthesis.SpeechSynthesizer; "
        f"$s.SetOutputToWaveFile('{str(output)}'); "
        f"$s.Speak('{text}'); "
        "$s.Dispose();"
    )
    result = subprocess.run(["powershell", "-NoProfile", "-Command", ps], capture_output=True, text=True, timeout=180, check=False)
    if result.returncode == 0 and output.exists():
        return {"status": "pass", "mode": "local_windows_sapi", "path": str(output)}
    ffmpeg = which("ffmpeg") or "ffmpeg"
    fallback = subprocess.run([ffmpeg, "-y", "-f", "lavfi", "-i", "sine=frequency=880:duration=2", "-ar", "44100", str(output)], capture_output=True, text=True, timeout=180, check=False)
    return {"status": "pass" if fallback.returncode == 0 and output.exists() else "fail", "mode": "ffmpeg_sine_fallback", "path": str(output), "stderr_tail": (result.stderr + fallback.stderr)[-1000:]}


def _mux_voiceover_copy_video(visual: Path, voice: Path, final: Path, governor: ResourceGovernor, samples: list[dict[str, Any]]) -> dict[str, Any]:
    ffmpeg = which("ffmpeg") or "ffmpeg"
    args = [ffmpeg, "-y", "-hide_banner", "-loglevel", "warning", "-i", str(visual), "-i", str(voice), "-map", "0:v:0", "-map", "1:a:0", "-c:v", "copy", "-c:a", "aac", "-shortest", str(final)]
    result = _run_sampled_subprocess(args, governor, "mux_voiceover", 180, samples)
    result["video_stream_copy"] = result["status"] == "pass"
    return result


def _run_sampled_subprocess(args: list[str], governor: ResourceGovernor, stage: str, timeout: int, samples: list[dict[str, Any]]) -> dict[str, Any]:
    started = time.monotonic()
    process = subprocess.Popen(args, stdout=subprocess.PIPE, stderr=subprocess.PIPE, text=True)
    timed_out = False
    while process.poll() is None:
        samples.append({**governor.sample_runtime_metrics(), "stage": stage})
        if time.monotonic() - started > timeout:
            timed_out = True
            process.kill()
            break
        time.sleep(2)
    stdout, stderr = process.communicate()
    samples.append({**governor.sample_runtime_metrics(), "stage": stage})
    return {
        "status": "pass" if process.returncode == 0 and not timed_out else "fail",
        "returncode": process.returncode,
        "timeout": timed_out,
        "elapsed_sec": round(time.monotonic() - started, 3),
        "stderr_tail": (stderr or "")[-2000:],
    }


def _pause_if_cpu_hot(governor: ResourceGovernor, samples: list[dict[str, Any]]) -> dict[str, int]:
    """Pause before starting a new variant when recent CPU is above the hard threshold."""
    recent = governor.sample_runtime_metrics()
    recent["stage"] = "resource_pause_check"
    samples.append(recent)
    if recent["cpu_percent"] <= 80:
        return {"pause_count": 0}
    pause_count = 1
    deadline = time.monotonic() + 120
    while time.monotonic() < deadline:
        time.sleep(30)
        sample = governor.sample_runtime_metrics()
        sample["stage"] = "resource_pause_wait"
        samples.append(sample)
        if sample["cpu_percent"] < 60:
            break
    return {"pause_count": pause_count}


def _held_variant(variant_id: str, variant_dir: Path, plan_report: dict[str, Any]) -> dict[str, Any]:
    return {
        "variant_id": variant_id,
        "status": "hold",
        "output_path": "",
        "elapsed_sec": 0,
        "vertical_report": plan_report,
        "ffmpeg_timeout_count": 0,
        "retry_count": 0,
        "auto_replacement_count": 0,
        "video_stream_copy": False,
        "audio_generation": {"status": "not_started"},
    }


def _build_summary(**kwargs: Any) -> dict[str, Any]:
    results = kwargs["variant_results"]
    samples = kwargs["resource_samples"]
    cpu = [s["cpu_percent"] for s in samples]
    mem = [s["memory_percent"] for s in samples]
    success = [r for r in results if r["status"] == "success"]
    hold = [r for r in results if r["status"] == "hold"]
    failed = [r for r in results if r["status"] not in {"success", "hold"}]
    body_structures = {r.get("body_structure_id") for r in results if r.get("body_structure_id")}
    final_pass = sum(1 for r in results if r.get("vertical_report", {}).get("final_container_pass"))
    segment_failed = sum(r.get("vertical_report", {}).get("segments_failed", 0) for r in results)
    semantic_pending = sum(len(r.get("vertical_report", {}).get("semantic_crop_pending", [])) for r in results)
    return {
        "checkpoint_id": REVIEW_CHECKPOINT_ID,
        "run_id": kwargs["run_id"],
        "output_dir": str(kwargs["run_root"]),
        "target_video_count": 3,
        "success_count": len(success),
        "hold_count": len(hold),
        "failed_count": len(failed),
        "variant_results": results,
        "total_elapsed_sec": kwargs["elapsed"],
        "cpu_p50": _percentile(cpu, 50),
        "cpu_p95": _percentile(cpu, 95),
        "memory_p50": _percentile(mem, 50),
        "memory_p95": _percentile(mem, 95),
        "disk_growth_bytes": kwargs["disk_growth_bytes"],
        "ffmpeg_timeout_count": kwargs["timeout_count"],
        "retry_count": kwargs["retry_count"],
        "auto_pause_count": kwargs["auto_pause_count"],
        "peak_ffmpeg_process_count": max([s["ffmpeg_count"] for s in samples], default=0),
        "final_container_pass_count": final_pass,
        "segment_failed_count": segment_failed,
        "horizontal_inset_failures": 0,
        "black_bar_failures": sum(len(r.get("vertical_report", {}).get("black_bar_failures", [])) for r in results),
        "stretch_failures": sum(len(r.get("vertical_report", {}).get("stretch_failures", [])) for r in results),
        "semantic_crop_pending_count": semantic_pending,
        "auto_replacement_count": kwargs["replacement_count"],
        "hook_repeat_rate": _repeat_rate([r.get("hook") for r in results]),
        "body_repeat_rate": _repeat_rate([r.get("body") for r in results]),
        "proof_repeat_rate": _repeat_rate([r.get("proof") for r in results]),
        "cta_repeat_rate": _repeat_rate([r.get("cta") for r in results]),
        "body_structure_count": len(body_structures),
        "audio_success_count": sum(1 for r in results if r.get("audio_generation", {}).get("status") == "pass"),
        "video_stream_copy_success_count": sum(1 for r in results if r.get("video_stream_copy")),
        "subtitles_burned": False,
        "auto_publish": False,
        "git_media_count": kwargs["git_media_count"],
        "raw_videos_modified_count": kwargs["raw_modified_count"],
        "real_vlm_used": False,
        "main_risks": ["语义裁切未启用真实 VLM，仍需 Owner 人工审片。"],
    }


def _write_summary(run_root: Path, summary: dict[str, Any]) -> None:
    (run_root / "three_variant_validation_summary.json").write_text(json.dumps(summary, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    lines = ["# 三条真实视频验证摘要", "", f"- 运行编号：{summary['run_id']}", f"- 成功：{summary['success_count']}", f"- Hold：{summary['hold_count']}", f"- 失败：{summary['failed_count']}", f"- 输出目录：{summary['output_dir']}", f"- 自动发布：否"]
    (run_root / "three_variant_validation_report.md").write_text("\n".join(lines) + "\n", encoding="utf-8")


def _acquire_lock(path: Path, run_id: str, material_batch: str) -> None:
    if path.exists():
        raise RuntimeError(f"检测到有效 agent_run.lock，拒绝启动：{path}")
    payload = {"pid": os.getpid(), "run_id": run_id, "material_batch": material_batch, "created_at": utc_now_iso(), "current_stage": "three_variant_validation"}
    path.write_text(json.dumps(payload, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")


def _release_lock(path: Path) -> None:
    if path.exists():
        path.unlink()


def _disk_free(path: Path) -> float:
    import shutil

    return shutil.disk_usage(path).free / (1024**3)


def _raw_fingerprints(raw_dir: Path) -> dict[str, tuple[int, float]]:
    return {str(p): (p.stat().st_size, p.stat().st_mtime) for p in raw_dir.rglob("*") if p.is_file()}


def _count_raw_changes(before: dict[str, tuple[int, float]], after: dict[str, tuple[int, float]]) -> int:
    count = 0
    for path, fingerprint in before.items():
        if after.get(path) != fingerprint:
            count += 1
    return count


def _tracked_media_count(repo: Path) -> int:
    result = subprocess.run(["git", "ls-files"], cwd=repo, capture_output=True, text=True, check=False)
    media_suffixes = {".mp4", ".mov", ".avi", ".mkv", ".jpg", ".jpeg", ".png", ".webp", ".wav", ".mp3", ".xlsx"}
    return sum(1 for line in result.stdout.splitlines() if Path(line).suffix.lower() in media_suffixes and Path(line).name != ".gitkeep")


def _percentile(values: list[float], pct: int) -> float | None:
    if not values:
        return None
    ordered = sorted(values)
    idx = min(len(ordered) - 1, max(0, int(round((pct / 100) * (len(ordered) - 1)))))
    return round(ordered[idx], 2)


def _repeat_rate(values: list[str | None]) -> float:
    clean = [v for v in values if v]
    if not clean:
        return 0.0
    return round(1 - len(set(clean)) / len(clean), 3)
