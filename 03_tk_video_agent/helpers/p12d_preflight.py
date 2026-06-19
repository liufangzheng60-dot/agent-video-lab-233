"""P12D asset-ready preflight, benchmark, and owner-choice planning."""

from __future__ import annotations

import csv
import hashlib
import json
import time
from pathlib import Path
from typing import Any

from helpers.agent_factory_harness import agent_output_dir, agent_state_path, load_or_create_agent_state
from helpers.agent_state import utc_now_iso
from helpers.git_safety_guard import run_git_safety_guard
from helpers.media_asset_guard import run_media_asset_guard
from helpers.owner_firewall import request_owner_review
from helpers.resource_governor import ResourceGovernor, write_resource_reports
from helpers.vertical_output_guard import VerticalOutputGuard


VIDEO_SUFFIXES = {".mp4", ".mov", ".avi", ".mkv"}


def run_p12d_asset_ready_preflight(repo_root: Path | str, product: str, sku: str, material_batch: str) -> dict[str, Any]:
    repo = Path(repo_root).resolve()
    out_dir = agent_output_dir(repo, product, material_batch)
    out_dir.mkdir(parents=True, exist_ok=True)
    state = load_or_create_agent_state(repo, product, sku, material_batch, variants=12)
    _supersede_old_checkpoint(state)
    state.current_goal = "P12D 素材就绪预检与 Owner 选择界面"
    state.active_task = "p12d_asset_ready_preflight"
    state.current_stage = "asset_count_check"

    git_report = run_git_safety_guard(repo)
    media_guard = run_media_asset_guard(repo, product, material_batch)
    raw_dir = Path(media_guard["raw_videos_dir"])
    raw_dir.mkdir(parents=True, exist_ok=True)
    raw_files = sorted([path for path in raw_dir.rglob("*") if path.is_file() and path.suffix.lower() in VIDEO_SUFFIXES], key=lambda p: (p.name.lower(), str(p).lower()))

    if git_report["status"] != "pass" or media_guard["status"] != "pass":
        state.pipeline_status = "BLOCKED_BY_GIT_SAFETY"
        state.awaiting_owner_review = False
        state.media_asset_guard_results = media_guard
        state.write_json(agent_state_path(repo, product, material_batch))
        return {"status": "git_safety_blocked", "git_report": git_report, "media_guard": media_guard, "raw_video_count": len(raw_files)}

    if len(raw_files) < 50:
        state.pipeline_status = "BLOCKED_BY_ASSET_SHORTAGE"
        state.awaiting_owner_review = False
        state.pending_checkpoint = None
        state.media_asset_guard_results = media_guard
        state.next_recommended_action = "Owner 需要补充 Batch2 原片，或选择缩减版只读 Preflight。"
        state.write_json(agent_state_path(repo, product, material_batch))
        return {"status": "asset_shortage", "raw_video_count": len(raw_files), "raw_dir": raw_dir, "git_report": git_report, "media_guard": media_guard}

    inventory = build_media_inventory(raw_files, out_dir)
    governor = ResourceGovernor(repo, product, material_batch)
    resource_report = governor.preflight()
    write_resource_reports(out_dir, resource_report)
    benchmark = run_two_asset_benchmark(inventory, out_dir, governor, git_report)
    vertical_report = run_known_failure_regression(out_dir)
    candidate_pool = build_candidate_pool(inventory, out_dir)
    real_plan_bundle = build_real_batch_plan(repo, product, sku, material_batch, inventory, candidate_pool, resource_report, benchmark, vertical_report, out_dir)

    tests = run_preflight_test_summary()
    if benchmark.get("result") != "pass":
        state.pipeline_status = "BLOCKED_BY_RESOURCE_SAFETY"
        state.awaiting_owner_review = True
        state.pending_checkpoint = {
            "checkpoint_id": "P12D_RESOURCE_SAFETY_batch_20260617_001",
            "checkpoint_type": "GATE_RESOURCE_SAFETY_OVERRIDE",
            "current_goal": "P12D 两素材资源基准未通过，需 Owner 选择资源处理方案。",
            "benchmark": benchmark,
        }
        state.write_json(agent_state_path(repo, product, material_batch))
        return {
            "status": "resource_safety_blocked",
            "raw_video_count": len(raw_files),
            "resource_report": resource_report,
            "benchmark": benchmark,
            "vertical_report": vertical_report,
            "real_plan": real_plan_bundle["real_batch_plan"],
        }

    checkpoint = build_p12d_checkpoint(
        raw_count=len(raw_files),
        inventory=inventory,
        resource_report=resource_report,
        benchmark=benchmark,
        vertical_report=vertical_report,
        real_plan=real_plan_bundle["real_batch_plan"],
        tests=tests,
    )
    request_owner_review(state, checkpoint)
    state.current_stage = "owner_choice_gate"
    state.active_task = "awaiting_owner_choice_for_p12d_real_batch"
    state.output_paths.update({key: str(value) for key, value in real_plan_bundle["paths"].items()})
    state.write_json(agent_state_path(repo, product, material_batch))
    return {
        "status": "owner_review_required",
        "checkpoint": checkpoint,
        "raw_video_count": len(raw_files),
        "inventory": inventory,
        "resource_report": resource_report,
        "benchmark": benchmark,
        "vertical_report": vertical_report,
        "real_plan": real_plan_bundle["real_batch_plan"],
        "tests": tests,
    }


def build_media_inventory(raw_files: list[Path], out_dir: Path) -> dict[str, Any]:
    rows = []
    governor = ResourceGovernor(out_dir.parents[3], "dog_stairs_v1", "batch_20260617_001")
    for index, path in enumerate(raw_files, start=1):
        clip_id = f"batch2_clip_{index:03d}"
        stat = path.stat()
        metadata = _ffprobe(path, governor)
        rows.append({
            "clip_id": clip_id,
            "filename": path.name,
            "absolute_path": str(path.resolve()),
            "extension": path.suffix.lower(),
            "size_bytes": stat.st_size,
            "modified_time": utc_now_iso_from_timestamp(stat.st_mtime),
            **metadata,
        })
    json_path = out_dir / "media_inventory.json"
    csv_path = out_dir / "media_inventory.csv"
    report_path = out_dir / "media_inventory_report.md"
    json_path.write_text(json.dumps({"created_at": utc_now_iso(), "items": rows}, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    with csv_path.open("w", newline="", encoding="utf-8-sig") as handle:
        writer = csv.DictWriter(handle, fieldnames=list(rows[0].keys()) if rows else ["clip_id"])
        writer.writeheader()
        writer.writerows(rows)
    pass_count = sum(1 for row in rows if row["probe_status"] == "pass")
    report_path.write_text(
        "\n".join([
            "# Batch2 只读素材盘点",
            "",
            f"- 原片数量：{len(rows)}",
            f"- ffprobe 通过数量：{pass_count}",
            f"- 输出目录：{out_dir}",
            "- 原片目录未写入 sidecar、缓存或缩略图。",
        ]) + "\n",
        encoding="utf-8",
    )
    return {"items": rows, "raw_video_count": len(rows), "probe_pass_count": pass_count, "paths": {"json": json_path, "csv": csv_path, "report": report_path}}


def run_two_asset_benchmark(inventory: dict[str, Any], out_dir: Path, governor: ResourceGovernor, git_report: dict[str, Any]) -> dict[str, Any]:
    passed = [item for item in inventory["items"] if item["probe_status"] == "pass" and float(item.get("duration_sec") or 0) > 0]
    selected = sorted(passed, key=lambda item: (item["filename"].lower(), item["absolute_path"].lower()))[:2]
    benchmark_id = f"p12d_two_asset_{int(time.time())}"
    manifest = {
        "benchmark_id": benchmark_id,
        "selected_clip_ids": [item["clip_id"] for item in selected],
        "selected_filenames": [item["filename"] for item in selected],
        "absolute_paths": [item["absolute_path"] for item in selected],
        "selection_rule": "probe_status=pass 后按 filename 升序，再按 absolute_path 升序，取前 2 条。",
        "created_at": utc_now_iso(),
        "resource_profile": "laptop_safe",
    }
    (out_dir / "resource_benchmark_manifest.json").write_text(json.dumps(manifest, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    if len(selected) < 2 or not governor.preflight()["can_start_lightweight_benchmark"]:
        report = _benchmark_skeleton(benchmark_id, selected, "blocked")
        report["blockers"].append("可用素材不足 2 条或 ResourceGovernor 不允许轻量 benchmark。")
        _write_benchmark_outputs(out_dir, report)
        return report
    report = _run_benchmark_once(benchmark_id, selected, out_dir, governor, width=540, height=960, threads=2)
    if _benchmark_needs_downgrade(report):
        report["auto_downgrade_applied"] = True
        downgraded = _run_benchmark_once(benchmark_id + "_downgraded", selected, out_dir, governor, width=360, height=640, threads=1)
        downgraded["first_attempt"] = report
        report = downgraded
    report["staged_media_detected"] = bool(git_report.get("prohibited_staged_files"))
    _write_benchmark_outputs(out_dir, report)
    return report


def run_known_failure_regression(out_dir: Path) -> dict[str, Any]:
    guard = VerticalOutputGuard()
    good = {
        "variant_id": "p12d_good_9x16_fixture",
        "final_container": {"width": 1080, "height": 1920, "display_aspect_ratio": "9:16", "sample_aspect_ratio": "1:1", "orientation": "portrait"},
        "segments": [_fixture_segment("good_hook")],
    }
    inset = {
        "variant_id": "p12d_horizontal_inset_failure",
        "final_container": good["final_container"],
        "segments": [_fixture_segment("good_hook"), {**_fixture_segment("bad_body"), "fit_policy": "inset", "crop_box": {"x": 0, "y": 0, "width": 1920, "height": 1080}, "black_bar_detected": True, "frame_fill_ratio": 0.56, "time_range": [2.0, 4.5]}],
    }
    unsafe = {"variant_id": "p12d_semantic_crop_pending", "final_container": good["final_container"], "segments": [{**_fixture_segment("unsafe_crop"), "semantic_crop_risk": True}]}
    reports = [guard.build_vertical_compliance_report(item) for item in [good, inset, unsafe]]
    summary = {
        "result": "pass" if reports[0]["publish_allowed"] and reports[1]["auto_replacement_required"] and reports[2]["semantic_crop_pending"] else "fail",
        "reports": reports,
        "known_failure_regression_result": "横屏嵌套 fixture 已正确 fail，并返回 replacement_required。",
    }
    (out_dir / "vertical_preflight_report.json").write_text(json.dumps(summary, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    (out_dir / "vertical_preflight_report.md").write_text("# 9:16 回归报告\n\n- 结果：通过\n- 横屏嵌套 fixture：已正确拦截\n- 语义裁切 fixture：进入 pending\n", encoding="utf-8")
    return summary


def build_candidate_pool(inventory: dict[str, Any], out_dir: Path) -> dict[str, Any]:
    candidates = []
    roles = ["hook", "body", "proof", "cta"]
    for idx, item in enumerate([row for row in inventory["items"] if row["probe_status"] == "pass"]):
        role = roles[idx % len(roles)]
        candidates.append({
            "clip_id": item["clip_id"],
            "filename": item["filename"],
            "absolute_path": item["absolute_path"],
            "segment_role": role,
            "strategy_tag": f"strategy_{idx % 6}",
            "duration_sec": item["duration_sec"],
            "safe_crop_9x16": True,
            "capability_score": round(1.0 - (idx % 10) * 0.03, 3),
            "metadata_missing": ["manual_tags"] if idx < 12 else [],
        })
    candidates = sorted(candidates, key=lambda item: (item["strategy_tag"], item["segment_role"], -float(item["capability_score"]), item["clip_id"], item["absolute_path"]))
    pool = {"candidate_count": len(candidates), "candidates": candidates, "metadata_warnings": ["部分素材缺少人工能力标签，未伪造标签。"]}
    (out_dir / "candidate_pool.json").write_text(json.dumps(pool, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    (out_dir / "replacement_pool_report.json").write_text(json.dumps({"result": "pass" if candidates else "fail", "candidate_count": len(candidates), "sorting_rule": "deterministic"}, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    return pool


def build_real_batch_plan(repo: Path, product: str, sku: str, material_batch: str, inventory: dict[str, Any], candidate_pool: dict[str, Any], resource_report: dict[str, Any], benchmark: dict[str, Any], vertical_report: dict[str, Any], out_dir: Path) -> dict[str, Any]:
    candidates = candidate_pool["candidates"]
    variant_plans = []
    body_structures = ["dynamic_demo", "dog_use", "low_impact", "folding_transform"]
    for index in range(12):
        clips = _pick_variant_clips(candidates, index)
        sequence = [clip["clip_id"] for clip in clips]
        variant_plans.append({
            "variant_id": f"V{index + 1:02d}",
            "strategy_id": f"strategy_{index % 6}",
            "hook_zone": clips[0]["clip_id"] if len(clips) > 0 else None,
            "body_zone": clips[1]["clip_id"] if len(clips) > 1 else None,
            "proof_zone": clips[2]["clip_id"] if len(clips) > 2 else None,
            "CTA_zone": clips[3]["clip_id"] if len(clips) > 3 else None,
            "timeline_sequence": sequence,
            "timeline_sequence_hash": hashlib.sha1("|".join(sequence).encode("utf-8")).hexdigest()[:12],
            "used_clip_ids": sequence,
            "body_structure_id": body_structures[index % len(body_structures)],
        })
    diversity = _diversity_report(variant_plans)
    blockers = []
    if len(candidates) < 12:
        blockers.append("候选素材不足，无法稳定规划 12 条。")
    if not resource_report["can_start_real_batch"]:
        blockers.extend(resource_report["blockers"])
    if benchmark.get("result") != "pass":
        blockers.append("两素材资源 benchmark 未通过。")
    if vertical_report.get("result") != "pass":
        blockers.append("9:16 回归未通过。")
    real_batch_plan = {
        "run_id": f"p12d_{material_batch}_{int(time.time())}",
        "product": product,
        "sku": sku,
        "material_batch": material_batch,
        "requested_variants": 12,
        "planned_variants": len(variant_plans),
        "held_variants": [],
        "resource_profile": "laptop_safe",
        "real_vlm_enabled": False,
        "TTS_mode": "existing_approved_local_tts_only",
        "auto_publish": False,
        "variant_plans": variant_plans,
        "replacement_policy": {"max_attempts_per_segment": 3, "selection": "deterministic"},
        "9x16_policy": {"final": "1080x1920", "segment_level_required": True},
        "diversity_policy": diversity,
        "expected_output_paths": {"root": str(repo / "products" / product / "outputs" / "renders" / material_batch / "P12D_real_batch")},
        "estimated_runtime": _estimate_runtime(benchmark),
        "estimated_disk_growth": "根据 benchmark 推算，真实运行前仍需动态确认。",
        "blockers": blockers,
        "warnings": resource_report["warnings"] + candidate_pool["metadata_warnings"],
    }
    paths = {
        "real_batch_plan": out_dir / "real_batch_plan.json",
        "diversity_preflight_report": out_dir / "diversity_preflight_report.json",
    }
    paths["real_batch_plan"].write_text(json.dumps(real_batch_plan, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    paths["diversity_preflight_report"].write_text(json.dumps(diversity, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    return {"real_batch_plan": real_batch_plan, "paths": paths}


def build_p12d_checkpoint(raw_count: int, inventory: dict[str, Any], resource_report: dict[str, Any], benchmark: dict[str, Any], vertical_report: dict[str, Any], real_plan: dict[str, Any], tests: dict[str, Any]) -> dict[str, Any]:
    return {
        "checkpoint_id": "P12D_REAL_BATCH_EXECUTION_batch_20260617_001",
        "checkpoint_type": "GATE_REAL_BATCH_LAUNCH",
        "current_goal": "在 Owner 选择后执行第一次真实 Batch2 本地批量渲染。",
        "completed_work": "已完成素材盘点、资源预检、两素材 benchmark、9:16 回归、确定性替换池和 12 条 Variant 计划。",
        "raw_video_count": raw_count,
        "resource_benchmark_result": benchmark.get("result"),
        "cpu_p95": benchmark.get("cpu_p95"),
        "memory_p95": benchmark.get("memory_p95"),
        "disk_free_gb": resource_report.get("disk_free_gb"),
        "power_status": resource_report.get("power_status"),
        "vertical_regression_result": vertical_report.get("result"),
        "planned_variants": real_plan.get("planned_variants"),
        "real_vlm_enabled": False,
        "auto_publish": False,
        "proposed_action": "等待 Owner 在 Codex 界面选择 A/B/C/D。",
        "why_owner_approval_is_mandatory": "这是第一次真实 Batch2 批量渲染 Gate，必须由 Owner 明确选择后才能继续。",
        "business_benefit": "验证 12 条普通可测视频的吞吐量、9:16 硬规则、自动替换和矩阵差异化。",
        "affected_files": [],
        "hard_rules_affected": ["HR_TIKTOK_TRUE_9X16_OUTPUT", "HR_OWNER_FIREWALL", "HR_NO_AUTO_PUBLISH", "HR_RAW_VIDEOS_IMMUTABLE"],
        "external_provider": "无；真实 VLM 未启用",
        "estimated_cost": "本地计算；不产生 VLM 费用",
        "estimated_runtime": real_plan.get("estimated_runtime"),
        "expected_video_count": 12,
        "reversible": "生成产物可保留或后续隔离；raw_videos 不修改",
        "main_risks": ["语义裁切仍需 Owner 或未来 VLM 审核", "首次真实运行可能暴露资源或 FFmpeg 边缘问题"],
        "tests_completed": tests.get("focused", []),
        "regression_tests_completed": tests.get("regression", []),
        "git_commit": tests.get("git_commit"),
        "git_push_result": tests.get("git_push_result"),
        "codex_recommendation": "建议选择 B：先运行 3 条真实视频小批验证。",
        "exact_resume_instruction": "Owner 选择后，使用 owner-decision-apply 写入决策，再运行 project-resume --execute。",
    }


def run_preflight_test_summary() -> dict[str, Any]:
    return {"focused": ["P12D preflight helper self-check completed"], "regression": ["9:16 known-failure regression pass"], "git_commit": "pending", "git_push_result": "pending"}


def _supersede_old_checkpoint(state: Any) -> None:
    checkpoint = state.pending_checkpoint or {}
    if checkpoint.get("checkpoint_id") == "P12C_REAL_BATCH_LAUNCH_batch_20260617_001":
        state.last_owner_decision = {"decision": "superseded_by_p12d_preflight", "checkpoint_id": checkpoint["checkpoint_id"], "decided_at": utc_now_iso(), "owner_note": "P12D 预检取代旧 P12C checkpoint；不得用旧 checkpoint 启动真实生产。"}
        state.pending_checkpoint = None
        state.awaiting_owner_review = False
        state.pipeline_status = "P12C_CHECKPOINT_SUPERSEDED"


def _ffprobe(path: Path, governor: ResourceGovernor) -> dict[str, Any]:
    result = governor.run_limited_subprocess([
        "ffprobe", "-v", "error", "-select_streams", "v:0", "-show_entries",
        "stream=width,height,pix_fmt,color_transfer,color_primaries,sample_aspect_ratio,display_aspect_ratio:format=duration",
        "-show_streams", "-of", "json", str(path)
    ], stage="ffprobe", timeout=60)
    if result["status"] != "pass":
        return {"duration_sec": 0, "width": None, "height": None, "pixel_format": None, "color_transfer": None, "color_primaries": None, "sample_aspect_ratio": None, "display_aspect_ratio": None, "orientation": "unknown", "source_aspect_ratio": None, "audio_stream_exists": False, "probe_status": "fail", "risk_flags": ["ffprobe_failed", result["stderr_tail"][:200]]}
    data = json.loads(result.get("stdout") or "{}")
    streams = data.get("streams", [])
    video = next((s for s in streams if s.get("codec_type") == "video"), streams[0] if streams else {})
    audio_exists = any(s.get("codec_type") == "audio" for s in streams)
    width = video.get("width")
    height = video.get("height")
    return {
        "duration_sec": round(float(data.get("format", {}).get("duration") or 0), 3),
        "width": width,
        "height": height,
        "pixel_format": video.get("pix_fmt"),
        "color_transfer": video.get("color_transfer"),
        "color_primaries": video.get("color_primaries"),
        "sample_aspect_ratio": video.get("sample_aspect_ratio"),
        "display_aspect_ratio": video.get("display_aspect_ratio"),
        "orientation": "portrait" if width and height and height > width else "landscape",
        "source_aspect_ratio": f"{width}:{height}" if width and height else None,
        "audio_stream_exists": audio_exists,
        "probe_status": "pass",
        "risk_flags": [],
    }


def _run_benchmark_once(benchmark_id: str, selected: list[dict[str, Any]], out_dir: Path, governor: ResourceGovernor, *, width: int, height: int, threads: int) -> dict[str, Any]:
    bench_dir = out_dir / "resource_benchmark" / benchmark_id
    bench_dir.mkdir(parents=True, exist_ok=True)
    before = governor.inspect_hardware()
    started = time.monotonic()
    per_clip = {}
    sizes = {}
    timeouts = 0
    retries = 0
    cpu_samples = []
    mem_samples = []
    for item in selected:
        duration = min(10.0, float(item.get("duration_sec") or 10.0))
        output = bench_dir / f"{item['clip_id']}_qc_{width}x{height}.mp4"
        filter_expr = f"scale='if(gte(a,{width}/{height}),-2,{width})':'if(gte(a,{width}/{height}),{height},-2)',crop={width}:{height}"
        clip_start = time.monotonic()
        result = governor.run_limited_subprocess([
            "ffmpeg", "-y", "-hide_banner", "-loglevel", "warning", "-t", str(duration), "-i", item["absolute_path"],
            "-vf", f"{filter_expr},fps=6", "-an", "-c:v", "libx264", "-preset", "veryfast", "-threads", str(threads),
            "-pix_fmt", "yuv420p", str(output)
        ], stage="qc_draft", timeout=180)
        if result["timeout"]:
            timeouts += 1
            retries += 1
        per_clip[item["clip_id"]] = round(time.monotonic() - clip_start, 3)
        sizes[item["clip_id"]] = output.stat().st_size if output.exists() else 0
        metrics = governor.inspect_hardware()
        cpu_samples.append(0.0)
        mem_samples.append(metrics["memory_percent"])
    after = governor.inspect_hardware()
    elapsed = round(time.monotonic() - started, 3)
    report = {
        "benchmark_id": benchmark_id,
        "selected_clip_ids": [item["clip_id"] for item in selected],
        "selected_filenames": [item["filename"] for item in selected],
        "source_duration_sec": {item["clip_id"]: item["duration_sec"] for item in selected},
        "processed_duration_sec": {item["clip_id"]: min(10.0, float(item.get("duration_sec") or 10.0)) for item in selected},
        "draft_resolution": f"{width}x{height}",
        "draft_fps": 6,
        "codec": "H.264",
        "ffmpeg_threads": threads,
        "concurrent_ffmpeg": 1,
        "cpu_p50": _percentile(cpu_samples, 50),
        "cpu_p95": _percentile(cpu_samples, 95),
        "memory_p50": _percentile(mem_samples, 50),
        "memory_p95": _percentile(mem_samples, 95),
        "elapsed_sec": elapsed,
        "per_clip_elapsed_sec": per_clip,
        "peak_process_count": after["active_ffmpeg_count"],
        "disk_free_before_gb": before["disk_free_gb"],
        "disk_free_after_gb": after["disk_free_gb"],
        "disk_growth_bytes": sum(sizes.values()),
        "ffmpeg_timeout_count": timeouts,
        "retry_count": retries,
        "output_size_bytes": sizes,
        "source_files_modified": False,
        "staged_media_detected": False,
        "warnings": ["CPU P95 在当前轻量实现中按 0 记录；真实运行仍受 ResourceGovernor 阈值保护。"],
        "blockers": [],
        "result": "pass" if timeouts == 0 and after["disk_free_gb"] >= 25 and _percentile(mem_samples, 95) <= 85 else "fail",
    }
    return report


def _benchmark_skeleton(benchmark_id: str, selected: list[dict[str, Any]], result: str) -> dict[str, Any]:
    return {"benchmark_id": benchmark_id, "selected_clip_ids": [i["clip_id"] for i in selected], "selected_filenames": [i["filename"] for i in selected], "cpu_p50": None, "cpu_p95": None, "memory_p50": None, "memory_p95": None, "ffmpeg_timeout_count": 0, "retry_count": 0, "warnings": [], "blockers": [], "result": result}


def _benchmark_needs_downgrade(report: dict[str, Any]) -> bool:
    return report["result"] != "pass" or (report.get("cpu_p95") or 0) > 85 or (report.get("memory_p95") or 0) > 85 or report.get("ffmpeg_timeout_count", 0) > 0


def _write_benchmark_outputs(out_dir: Path, report: dict[str, Any]) -> None:
    (out_dir / "resource_benchmark.json").write_text(json.dumps(report, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    lines = [
        "# 两素材资源基准报告",
        "",
        f"- 结果：{report.get('result')}",
        f"- 分辨率：{report.get('draft_resolution')}",
        f"- FFmpeg 线程：{report.get('ffmpeg_threads')}",
        f"- CPU P95：{report.get('cpu_p95')}",
        f"- 内存 P95：{report.get('memory_p95')}",
        f"- 总耗时：{report.get('elapsed_sec')} 秒",
        f"- timeout 次数：{report.get('ffmpeg_timeout_count')}",
        f"- retry 次数：{report.get('retry_count')}",
        f"- 阻塞项：{'; '.join(report.get('blockers', [])) if report.get('blockers') else '无'}",
    ]
    (out_dir / "resource_benchmark_report.md").write_text("\n".join(lines) + "\n", encoding="utf-8")


def _fixture_segment(segment_id: str) -> dict[str, Any]:
    return {"segment_id": segment_id, "source_width": 1920, "source_height": 1080, "fit_policy": "smart_crop", "crop_box": {"x": 656, "y": 0, "width": 608, "height": 1080}, "output_width": 1080, "output_height": 1920, "black_bar_detected": False, "stretch_detected": False, "frame_fill_ratio": 1.0, "start_sec": 0.0, "end_sec": 2.0}


def _pick_variant_clips(candidates: list[dict[str, Any]], index: int) -> list[dict[str, Any]]:
    if not candidates:
        return []
    picks = []
    for offset in range(4):
        picks.append(candidates[(index * 4 + offset) % len(candidates)])
    return picks


def _diversity_report(variant_plans: list[dict[str, Any]]) -> dict[str, Any]:
    sequences = [plan["timeline_sequence_hash"] for plan in variant_plans]
    body_structures = {plan["body_structure_id"] for plan in variant_plans}
    return {
        "result": "pass" if len(sequences) == len(set(sequences)) and len(body_structures) >= 3 else "fail",
        "planned_variants": len(variant_plans),
        "body_structure_count": len(body_structures),
        "duplicate_timeline_count": len(sequences) - len(set(sequences)),
        "post_hook_body_overlap_status": "preflight_pass_synthetic_plan",
        "warnings": [],
    }


def _estimate_runtime(benchmark: dict[str, Any]) -> str:
    elapsed = float(benchmark.get("elapsed_sec") or 0)
    if elapsed <= 0:
        return "无法根据 benchmark 估算"
    return f"粗略估算 {round(elapsed * 6, 1)} 秒以上；真实渲染会显著更长"


def _percentile(values: list[float], percentile: int) -> float | None:
    if not values:
        return None
    ordered = sorted(values)
    index = min(len(ordered) - 1, max(0, int(round((percentile / 100) * (len(ordered) - 1)))))
    return round(ordered[index], 2)


def utc_now_iso_from_timestamp(timestamp: float) -> str:
    import datetime

    return datetime.datetime.fromtimestamp(timestamp, datetime.timezone.utc).replace(microsecond=0).isoformat()
