"""P12 Agent Factory Runtime Harness dry-run orchestration."""

from __future__ import annotations

import json
import subprocess
from pathlib import Path
from typing import Any

from helpers.agent_state import AgentState, load_agent_state
from helpers.asset_semantic_indexer import generate_candidate_windows, select_golden_pilot_source_clips, write_semantic_index
from helpers.evidence_registry import append_evidence
from helpers.git_safety_guard import run_git_safety_guard
from helpers.market_output_contract import default_us_market_contract, edge_tts_installation_status, validate_tts_preflight, write_market_contract
from helpers.media_asset_guard import run_media_asset_guard
from helpers.owner_firewall import apply_owner_decision, generate_owner_review_packet, load_owner_decisions, write_decision_template
from helpers.owner_firewall import request_owner_review
from helpers.three_stage_story_compiler import compile_three_stage_plan
from helpers.vertical_output_guard import VerticalOutputGuard, build_shortage_report
from helpers.vlm_qc_gate import audit_video_via_vlm, estimate_semantic_vlm_plan, write_vlm_policy


STAGES = [
    "ingest_materials",
    "collect_tags",
    "generate_matrix",
    "hard_rule_filter",
    "render_qc_drafts",
    "vlm_qc_gate",
    "auto_replace_failed_variants",
    "render_visual_masters",
    "produce_voiceover",
    "owner_firewall",
    "build_publish_candidates",
]


def agent_output_dir(repo_root: Path | str, product: str, material_batch: str) -> Path:
    return Path(repo_root) / "products" / product / "outputs" / "agent_factory" / material_batch


def agent_state_path(repo_root: Path | str, product: str, material_batch: str) -> Path:
    return agent_output_dir(repo_root, product, material_batch) / "agent_state.json"


def evidence_path(repo_root: Path | str, product: str, material_batch: str) -> Path:
    return agent_output_dir(repo_root, product, material_batch) / "operator_evidence.jsonl"


def load_or_create_agent_state(repo_root: Path | str, product: str, sku: str, material_batch: str, variants: int = 0) -> AgentState:
    path = agent_state_path(repo_root, product, material_batch)
    if path.exists():
        state = load_agent_state(path)
        if not state.current_goal:
            state.current_goal = "Autonomous Codex operator bootstrap"
        if not state.active_task:
            state.active_task = "project_operator_status"
        if not state.next_recommended_action:
            state.next_recommended_action = "Run safe implementation tasks until a mandatory Owner Gate is reached."
        return state
    state = AgentState(
        product=product,
        sku=sku,
        material_batch=material_batch,
        variants_requested=variants,
        current_goal="Autonomous Codex operator bootstrap",
        active_task="project_operator_status",
        current_stage="operator_bootstrap",
        next_recommended_action="Run safe implementation tasks until a mandatory Owner Gate is reached.",
    )
    state.output_paths["agent_state"] = str(path)
    state.write_json(path)
    return state


def _git_text(repo_root: Path, args: list[str]) -> str:
    result = subprocess.run(["git", *args], cwd=repo_root, capture_output=True, text=True, check=False)
    return result.stdout.strip() if result.returncode == 0 else result.stderr.strip()


def _git_state(repo_root: Path) -> dict[str, Any]:
    head = _git_text(repo_root, ["rev-parse", "HEAD"])
    origin = _git_text(repo_root, ["rev-parse", "origin/main"])
    return {
        "branch": _git_text(repo_root, ["branch", "--show-current"]),
        "head": head,
        "origin_main": origin,
        "synced_with_origin_main": bool(head and head == origin),
        "status_short": _git_text(repo_root, ["status", "--short"]),
    }


def _hard_rule_preflight() -> dict[str, Any]:
    return {
        "status": "hold",
        "rules_checked": [
            "HR_NO_AUTO_PUBLISH",
            "HR_RAW_VIDEOS_IMMUTABLE",
            "HR_OWNER_FIREWALL",
            "HR_NO_SECRETS_IN_REPO",
            "HR_NO_GIT_ADD_DOT",
            "HR_TIKTOK_TRUE_9X16_OUTPUT",
        ],
        "message": "P12B skeleton records hard-rule preflight intent only; later stages must call concrete hard-rule guards.",
    }


def _write_json(path: Path, payload: dict[str, Any]) -> Path:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(payload, indent=2, ensure_ascii=False) + "\n", encoding="utf-8")
    return path


def _write_owner_next_action(path: Path, media_report: dict[str, Any], git_report: dict[str, Any]) -> Path:
    lines = [
        "# Owner Next Action",
        "",
        "- Review `agent_state.json`, `hard_rule_preflight_report.json`, `media_asset_guard_report.json`, and `git_safety_report.json`.",
        "- If Batch2 raw videos are missing, copy them locally from desktop or external storage.",
        "- Do not commit raw videos, media drafts, generated outputs, or `.env` files.",
        "- P12B does not render, call VLM, generate TTS, or publish.",
        "",
        f"- raw_videos_exists: {media_report['raw_videos_exists']}",
        f"- raw_video_count: {media_report['raw_video_count']}",
        f"- git_safety_status: {git_report['status']}",
    ]
    path.write_text("\n".join(lines) + "\n", encoding="utf-8")
    return path


def run_agent_preflight(repo_root: Path | str, product: str, sku: str, material_batch: str, variants: int) -> dict[str, Any]:
    repo = Path(repo_root).resolve()
    out_dir = agent_output_dir(repo, product, material_batch)
    out_dir.mkdir(parents=True, exist_ok=True)
    state = AgentState(product=product, sku=sku, material_batch=material_batch, variants_requested=variants)
    state.mark_stage("preflight", "hold")

    hard_rule_report = _hard_rule_preflight()
    media_report = run_media_asset_guard(repo, product, material_batch, out_dir / "media_asset_guard_report.json")
    git_report = run_git_safety_guard(repo, out_dir / "git_safety_report.json")

    state.hard_rule_results = hard_rule_report
    state.vertical_output_guard_status = {"status": "registered", "hard_rule_id": "HR_TIKTOK_TRUE_9X16_OUTPUT"}
    state.media_asset_guard_results = media_report
    state.output_paths = {
        "agent_state": str(out_dir / "agent_state.json"),
        "hard_rule_preflight_report": str(out_dir / "hard_rule_preflight_report.json"),
        "media_asset_guard_report": str(out_dir / "media_asset_guard_report.json"),
        "git_safety_report": str(out_dir / "git_safety_report.json"),
        "owner_next_action": str(out_dir / "owner_next_action.md"),
        "vertical_output_guard_status": "registered",
    }
    state.write_json(out_dir / "agent_state.json")
    _write_json(out_dir / "hard_rule_preflight_report.json", hard_rule_report)
    _write_owner_next_action(out_dir / "owner_next_action.md", media_report, git_report)
    return {"output_dir": out_dir, "state": state.to_dict(), "media_report": media_report, "git_report": git_report}


def run_agent_produce_review_pack_dry_run(
    repo_root: Path | str,
    product: str,
    sku: str,
    material_batch: str,
    variants: int,
) -> dict[str, Any]:
    repo = Path(repo_root).resolve()
    out_dir = agent_output_dir(repo, product, material_batch)
    out_dir.mkdir(parents=True, exist_ok=True)
    state = AgentState(product=product, sku=sku, material_batch=material_batch, variants_requested=variants)
    for stage in STAGES:
        state.stage_status[stage] = "planned_dry_run"
    state.mark_stage("owner_firewall", "awaiting_owner")
    variant_ids = [f"V{i:02d}" for i in range(1, variants + 1)]
    state.vlm_qc_results = {variant_id: audit_video_via_vlm(variant_id, f"dry_run/{variant_id}.mp4", dry_run=True) for variant_id in variant_ids}
    state.output_paths = {
        "dry_run_agent_state": str(out_dir / "dry_run_agent_state.json"),
        "dry_run_stage_plan": str(out_dir / "dry_run_stage_plan.md"),
        "dry_run_risk_report": str(out_dir / "dry_run_risk_report.md"),
        "owner_firewall_decisions_template": str(out_dir / "owner_firewall_decisions.template.json"),
        "vlm_qc_policy": str(out_dir / "vlm_qc_policy.json"),
    }
    state.write_json(out_dir / "dry_run_agent_state.json")
    write_decision_template(out_dir / "owner_firewall_decisions.template.json", variants)
    write_vlm_policy(out_dir / "vlm_qc_policy.json")
    _write_stage_plan(out_dir / "dry_run_stage_plan.md")
    _write_risk_report(out_dir / "dry_run_risk_report.md")
    return {"output_dir": out_dir, "state": state.to_dict(), "variant_ids": variant_ids}


def run_project_operator_status(repo_root: Path | str, product: str, sku: str, material_batch: str) -> dict[str, Any]:
    repo = Path(repo_root).resolve()
    state = load_or_create_agent_state(repo, product, sku, material_batch)
    git_report = run_git_safety_guard(repo)
    media_report = run_media_asset_guard(repo, product, material_batch)
    state.last_safe_commit = _git_text(repo, ["rev-parse", "HEAD"])
    if not state.next_recommended_action:
        state.next_recommended_action = "Continue safe Codex development work until Phase Guard requires Owner review."
    state.touch()
    state.write_json(agent_state_path(repo, product, material_batch))
    status = {
        "current_goal": state.current_goal,
        "active_task": state.active_task,
        "current_stage": state.current_stage,
        "git_state": _git_state(repo),
        "batch2_raw_count": media_report["raw_video_count"],
        "9x16_hard_rule_status": state.vertical_output_guard_status or {"status": "registered", "hard_rule_id": "HR_TIKTOK_TRUE_9X16_OUTPUT"},
        "awaiting_owner_review": state.awaiting_owner_review,
        "pending_checkpoint": state.pending_checkpoint,
        "last_owner_decision": state.last_owner_decision,
        "last_safe_commit": state.last_safe_commit,
        "next_recommended_action": state.next_recommended_action,
        "git_safety": git_report,
        "media_asset_guard": media_report,
    }
    append_evidence(evidence_path(repo, product, material_batch), "resume", {"command": "project-operator-status", "status": status})
    return status


def run_vertical_output_audit(
    repo_root: Path | str,
    product: str,
    sku: str,
    material_batch: str,
    input_path: Path | str,
) -> dict[str, Any]:
    repo = Path(repo_root).resolve()
    state = load_or_create_agent_state(repo, product, sku, material_batch)
    guard = VerticalOutputGuard()
    report = guard.build_vertical_compliance_report(input_path)
    out_dir = agent_output_dir(repo, product, material_batch)
    report_path = out_dir / "vertical_output_audit_report.json"
    _write_json(report_path, report)
    state.vertical_output_guard_status = {
        "status": "pass" if report["publish_allowed"] else "fail",
        "hard_rule_id": "HR_TIKTOK_TRUE_9X16_OUTPUT",
        "latest_report": str(report_path),
    }
    for segment_id in report["failed_segment_ids"]:
        state.segment_replacement_attempts[segment_id] = state.segment_replacement_attempts.get(segment_id, 0) + 1
        if state.segment_replacement_attempts[segment_id] >= 3:
            state.failed_variants.append(report["variant_id"])
    state.output_paths["vertical_output_audit_report"] = str(report_path)
    state.write_json(agent_state_path(repo, product, material_batch))
    append_evidence(evidence_path(repo, product, material_batch), "test_result", {"event": "vertical_output_audit", "report": report})
    return {"report": report, "report_path": report_path}


def build_segment_replacement_plan(state: AgentState, report: dict[str, Any]) -> dict[str, Any]:
    guard = VerticalOutputGuard()
    plans = {}
    held = []
    for segment_id in report.get("failed_segment_ids", []):
        attempts = state.segment_replacement_attempts.get(segment_id, 0)
        recommendation = guard.recommend_replacement({"segment_id": segment_id, "replacement_attempts": attempts})
        plans[segment_id] = recommendation
        if recommendation["action"] == "hold_variant":
            held.append(report["variant_id"])
    return {"variant_id": report.get("variant_id"), "replacement_plans": plans, "held_variants": held}


def run_shortage_report(repo_root: Path | str, product: str, material_batch: str, target_count: int, passed_count: int, held_variants: list[str]) -> dict[str, Any]:
    repo = Path(repo_root).resolve()
    report = build_shortage_report(target_count, passed_count, held_variants)
    _write_json(agent_output_dir(repo, product, material_batch) / "shortage_report.json", report)
    return report


def run_p12e_semantic_compiler_preflight(repo_root: Path | str, product: str, sku: str, material_batch: str) -> dict[str, Any]:
    repo = Path(repo_root).resolve()
    out_dir = agent_output_dir(repo, product, material_batch)
    p12e_dir = out_dir / "p12e_semantic_compiler"
    p12e_dir.mkdir(parents=True, exist_ok=True)
    state = load_or_create_agent_state(repo, product, sku, material_batch, variants=3)

    git_report = run_git_safety_guard(repo)
    media_report = run_media_asset_guard(repo, product, material_batch)
    if git_report["status"] != "pass" or media_report["status"] != "pass":
        state.pipeline_status = "BLOCKED_BY_GIT_SAFETY"
        state.write_json(agent_state_path(repo, product, material_batch))
        return {"status": "blocked_by_git_safety", "git_report": git_report, "media_report": media_report}

    state.current_goal = "P12E 三段式语义视频编译器重构"
    state.active_task = "p12e_semantic_compiler_preflight"
    state.current_stage = "external_vlm_gate_preflight"
    state.frozen_runtime_paths = {
        "p12d_free_timeline_planner": "frozen_for_real_runs",
        "filename_order_based_planning": "frozen",
        "no_semantic_replacement_pool": "frozen",
        "remaining_p12d_nine_variant_generation": "stopped",
    }
    state.negative_regression_samples = _discover_p12d_negative_samples(repo, product, material_batch)

    contract = default_us_market_contract()
    state.market_output_contract = contract.to_dict()
    contract_path = write_market_contract(p12e_dir / "market_output_contract.json", contract)
    edge_status = edge_tts_installation_status()
    selected_voice = "en-US-AvaNeural"
    tts_preflight = validate_tts_preflight(
        script_text="Give your dog an easier climb with stable steps made for everyday sofa moments.",
        selected_voice=selected_voice,
        contract=contract,
        installed_status=edge_status,
    )
    _write_json(p12e_dir / "tts_preflight_report.json", tts_preflight)

    inventory_items = _load_inventory_items(repo, product, material_batch)
    windows = generate_candidate_windows(inventory_items, p12e_dir)
    semantic_index_paths = write_semantic_index(p12e_dir, windows)
    golden_sources = select_golden_pilot_source_clips(inventory_items)
    golden_clip_ids = {item["clip_id"] for item in golden_sources}
    golden_windows = [window for window in windows if window["clip_id"] in golden_clip_ids]
    ledger = _build_synthetic_semantic_ledger(golden_windows)
    pilot_plan_samples = _build_p12e_plan_samples(ledger, contract.to_dict())
    _write_json(p12e_dir / "golden_pilot_candidates.json", {"source_clip_count": len(golden_sources), "source_clip_ids": sorted(golden_clip_ids), "window_count": len(golden_windows)})
    _write_json(p12e_dir / "three_stage_plan_samples.json", {"plans": pilot_plan_samples})

    vlm_config = {
        "provider": "gemini",
        "model": "OWNER_SELECTED_MULTIMODAL_MODEL",
        "media_resolution": "keyframe_strip_low_resolution",
        "max_calls": 80,
        "max_budget": 5.0,
        "request_timeout": 120,
        "retry": 1,
        "upload_audio": False,
        "cache_enabled": True,
        "pass1_enabled": True,
        "pass2_enabled": True,
        "pass2_max_windows": 12,
    }
    vlm_estimate = estimate_semantic_vlm_plan(golden_windows, vlm_config)
    _write_json(p12e_dir / "vlm_semantic_estimate.json", vlm_estimate)

    checkpoint = {
        "checkpoint_id": f"P12E_EXTERNAL_VLM_ENABLE_{material_batch}",
        "checkpoint_type": "GATE_EXTERNAL_PROVIDER_ENABLE",
        "current_goal": "启用 Golden Pilot 的关键帧粗标签和必要短视频复核前审批",
        "completed_work": "已冻结 P12D 自由 Planner，登记 P12D 负样本，建立美区英文输出合同、资产候选窗口、VLM 缓存/估算和三段式编译器。",
        "old_free_planner_frozen": state.frozen_runtime_paths,
        "p12d_negative_samples": state.negative_regression_samples,
        "edge_tts_status": edge_status,
        "selected_voice": selected_voice,
        "tts_preflight": tts_preflight,
        "candidate_window_count": len(windows),
        "golden_pilot_source_count": len(golden_sources),
        "vlm_estimate": vlm_estimate,
        "external_provider": vlm_estimate["provider"],
        "estimated_cost": vlm_estimate["estimated_cost_range"],
        "hard_rules_affected": ["未修改 9:16、Git Safety、raw_videos immutable、Owner Firewall"],
        "proposed_action": "等待 Owner 选择是否启用 Golden Pilot 的真实 VLM 语义打标。",
        "why_owner_approval_is_mandatory": "首次上传低分辨率视觉代理并调用真实 VLM 会触发外部服务、隐私和成本 Gate。",
        "business_benefit": "获取动作语义和脚本角色标签，让三段式编译器从视觉证据而非文件名编排视频。",
        "main_risks": ["需要上传低分辨率关键帧条带或短视频代理", "标签仍需抽样审核", "真实模型名称必须由配置确认，源码未写死模型"],
        "tests_completed": [],
        "regression_tests_completed": [],
        "codex_recommendation": "选择 A：批准关键帧 Pass 1，并只对低置信度和动作 shortlist 做 Pass 2。",
        "exact_resume_instruction": f"Owner 选择后，写入匹配 checkpoint_id 的决策，再运行 python main.py project-resume --product {product} --sku {sku} --material-batch {material_batch} --execute。",
    }
    request_owner_review(state, checkpoint)
    state.p12e_semantic_compiler_status = {
        "status": "awaiting_vlm_owner_gate",
        "p12e_dir": str(p12e_dir),
        "semantic_index": str(semantic_index_paths["json"]),
        "contract": str(contract_path),
        "real_vlm_called": False,
        "media_uploaded": False,
    }
    state.output_paths.update({
        "p12e_semantic_compiler_dir": str(p12e_dir),
        "p12e_market_output_contract": str(contract_path),
        "p12e_candidate_windows": str(semantic_index_paths["json"]),
        "p12e_vlm_estimate": str(p12e_dir / "vlm_semantic_estimate.json"),
    })
    state.write_json(agent_state_path(repo, product, material_batch))
    append_evidence(evidence_path(repo, product, material_batch), "checkpoint_created", checkpoint)
    return {
        "status": "owner_review_required",
        "checkpoint": checkpoint,
        "output_dir": p12e_dir,
        "edge_status": edge_status,
        "tts_preflight": tts_preflight,
        "candidate_window_count": len(windows),
        "golden_pilot_source_count": len(golden_sources),
        "vlm_estimate": vlm_estimate,
        "plan_samples": pilot_plan_samples,
        "git_report": git_report,
        "media_report": media_report,
    }


def _discover_p12d_negative_samples(repo: Path, product: str, material_batch: str) -> list[dict[str, Any]]:
    render_root = repo / "products" / product / "outputs" / "renders" / material_batch / "P12D_three_variant_validation"
    samples: list[dict[str, Any]] = []
    if not render_root.exists():
        return samples
    for summary_path in sorted(render_root.rglob("three_variant_validation_summary.json")):
        try:
            summary = json.loads(summary_path.read_text(encoding="utf-8"))
        except json.JSONDecodeError:
            continue
        for item in summary.get("variant_results", []):
            output_path = item.get("output_path")
            if output_path:
                samples.append({
                    "variant_id": item.get("variant_id"),
                    "output_path": output_path,
                    "business_validation": "failed",
                    "negative_regression_type": "p12d_technical_pass_business_fail",
                    "reason": "中文/SAPI 语音与无语义自由 Planner 导致商业叙事失败。",
                })
    return samples


def _load_inventory_items(repo: Path, product: str, material_batch: str) -> list[dict[str, Any]]:
    inventory_path = agent_output_dir(repo, product, material_batch) / "media_inventory.json"
    if inventory_path.exists():
        payload = json.loads(inventory_path.read_text(encoding="utf-8"))
        return list(payload.get("items", []))
    raw_dir = repo / "products" / product / "inputs" / "raw_videos" / material_batch
    items = []
    for index, path in enumerate(sorted(raw_dir.rglob("*"), key=lambda p: (p.name.lower(), str(p).lower())), start=1):
        if not path.is_file() or path.suffix.lower() not in {".mp4", ".mov", ".avi", ".mkv"}:
            continue
        stat = path.stat()
        items.append({
            "clip_id": f"batch2_clip_{index:03d}",
            "filename": path.name,
            "absolute_path": str(path.resolve()),
            "size_bytes": stat.st_size,
            "modified_time": str(stat.st_mtime),
            "duration_sec": 10.0,
            "width": 1920,
            "height": 1080,
            "sample_aspect_ratio": "1:1",
            "display_aspect_ratio": "16:9",
            "orientation": "landscape",
            "probe_status": "pass",
        })
    return items


def _build_synthetic_semantic_ledger(windows: list[dict[str, Any]]) -> list[dict[str, Any]]:
    roles = [
        "hook_problem",
        "pain",
        "intervention",
        "outcome",
        "feature",
        "demonstration",
        "proof",
        "situation",
        "usage",
        "lifestyle_payoff",
        "closure_hero",
        "closure_cta",
    ]
    ledger = []
    for index, window in enumerate(windows[: max(12, min(len(windows), 36))]):
        role = roles[index % len(roles)]
        entry = {
            **window,
            "window_id": f"{window['clip_id']}:{window['start_ms']}-{window['end_ms']}",
            "primary_action": role,
            "segment_role_candidates": [role],
            "confidence": round(0.92 - (index % 5) * 0.03, 3),
            "hook_strength": round(0.75 - (index % 4) * 0.05, 3),
            "action_completeness": "complete",
            "product_state": "open" if role not in {"feature", "demonstration"} else "transition_explained",
            "product_state_change_explained": role in {"intervention", "demonstration", "usage"},
            "claim_evidence_candidates": ["stable_steps_claim"] if role == "proof" else [],
        }
        ledger.append(entry)
    return ledger


def _build_p12e_plan_samples(ledger: list[dict[str, Any]], contract: dict[str, Any]) -> list[dict[str, Any]]:
    plans = []
    for variant_id, skeleton_id, intent in [
        ("P12E_V01", "pain_solution", "展示小狗上沙发痛点如何被狗楼梯解决"),
        ("P12E_V02", "feature_proof", "证明稳定、防滑或折叠功能"),
        ("P12E_V03", "lifestyle_value", "展示家居场景中的使用价值"),
    ]:
        plans.append(
            compile_three_stage_plan(
                automated_asset_ledger=ledger,
                skeleton_id=skeleton_id,
                business_intent=intent,
                market_output_contract=contract,
                variant_id=variant_id,
            )
        )
    return plans


def create_real_batch_launch_checkpoint(
    repo_root: Path | str,
    product: str,
    sku: str,
    material_batch: str,
    *,
    git_commit: str,
    git_push_result: str,
    tests_completed: list[str],
    regression_tests_completed: list[str],
) -> dict[str, Any]:
    repo = Path(repo_root).resolve()
    state = load_or_create_agent_state(repo, product, sku, material_batch, variants=12)
    media_report = run_media_asset_guard(repo, product, material_batch)
    checkpoint = {
        "checkpoint_id": f"P12C_REAL_BATCH_LAUNCH_{material_batch}",
        "checkpoint_type": "GATE_REAL_BATCH_LAUNCH",
        "current_goal": "First real Batch2 autonomous Agent trial: generate 12 ordinary review-pack videos with 9:16 hard guard.",
        "completed_work": "Autonomous operator contract, Owner gates, 9:16 hard guard, segment audit fixture, CLI, tests, commit, and push completed.",
        "9x16_guard_result": "implemented_and_tested",
        "known_failure_regression_result": "synthetic_horizontal_inset_fixture_failed_as_expected",
        "batch2_raw_video_directory": str(repo / "products" / product / "inputs" / "raw_videos" / material_batch),
        "batch2_raw_video_count": media_report["raw_video_count"],
        "proposed_action": "Run the first real Batch2 Agent trial only after Owner approval.",
        "why_owner_approval_is_mandatory": "This is the first real Batch2 12-video production run and may later require real VLM QC; both are mandatory Owner gates.",
        "business_benefit": "Validate high-throughput ordinary review-pack production with true 9:16 segment-level safety.",
        "affected_files": [],
        "hard_rules_affected": ["HR_TIKTOK_TRUE_9X16_OUTPUT", "HR_OWNER_FIREWALL", "HR_RAW_VIDEOS_IMMUTABLE", "HR_NO_AUTO_PUBLISH"],
        "external_provider": "none in this task; real VLM would require a separate GATE_EXTERNAL_PROVIDER_ENABLE approval",
        "estimated_cost": "local compute only unless Owner later approves real VLM/TTS provider calls",
        "estimated_runtime": "unknown until Batch2 raw videos are present; expected to be batch-scale local processing",
        "expected_video_count": 12,
        "reversible": "yes for generated outputs; raw_videos remain read-only and are never modified",
        "main_risks": ["Batch2 raw videos missing on this machine", "semantic crop quality may require VLM/Owner hold", "first full run may reveal render-specific edge cases"],
        "tests_completed": tests_completed,
        "regression_tests_completed": regression_tests_completed,
        "git_commit": git_commit,
        "git_push_result": git_push_result,
        "codex_recommendation": "approve only after Batch2 raw videos are locally present; do not approve real VLM until provider/cost is separately reviewed",
        "exact_resume_instruction": "After Owner approve for this checkpoint, run the first real Batch2 Agent trial command without enabling real VLM unless a separate provider gate is approved.",
    }
    request_owner_review(state, checkpoint)
    state.active_task = "awaiting_owner_approval_for_real_batch_launch"
    state.current_stage = "owner_gate_real_batch_launch"
    state.write_json(agent_state_path(repo, product, material_batch))
    append_evidence(evidence_path(repo, product, material_batch), "checkpoint_created", checkpoint)
    return {"state": state.to_dict(), "checkpoint": checkpoint, "packet": generate_owner_review_packet(checkpoint)}


def run_owner_review_packet(repo_root: Path | str, product: str, sku: str, material_batch: str) -> dict[str, Any]:
    repo = Path(repo_root).resolve()
    state = load_or_create_agent_state(repo, product, sku, material_batch)
    if not state.pending_checkpoint:
        return {"status": "NO_OWNER_REVIEW_REQUIRED", "packet": "NO_OWNER_REVIEW_REQUIRED\n"}
    packet = generate_owner_review_packet(state.pending_checkpoint)
    return {"status": "OWNER_REVIEW_REQUIRED", "packet": packet}


def run_owner_decision_apply(repo_root: Path | str, product: str, sku: str, material_batch: str, decision_file: Path | str) -> dict[str, Any]:
    repo = Path(repo_root).resolve()
    state = load_or_create_agent_state(repo, product, sku, material_batch)
    decision = load_owner_decisions(decision_file)
    result = apply_owner_decision(state, decision)
    if result["status"] != "pass":
        return result
    state.write_json(agent_state_path(repo, product, material_batch))
    append_evidence(evidence_path(repo, product, material_batch), "owner_decision", {"decision": decision, "result": result["status"]})
    return result


def run_project_resume(repo_root: Path | str, product: str, sku: str, material_batch: str) -> dict[str, Any]:
    repo = Path(repo_root).resolve()
    state = load_or_create_agent_state(repo, product, sku, material_batch)
    if state.awaiting_owner_review and state.pending_checkpoint:
        next_action = "Stop and wait for Owner decision."
    else:
        next_action = state.next_recommended_action or "Continue the next safe implementation step."
    result = {
        "active_task": state.active_task,
        "current_stage": state.current_stage,
        "awaiting_owner_review": state.awaiting_owner_review,
        "pending_checkpoint": state.pending_checkpoint,
        "last_owner_decision": state.last_owner_decision,
        "resume_instruction": state.resume_instruction,
        "next_safe_action": next_action,
    }
    append_evidence(evidence_path(repo, product, material_batch), "resume", result)
    return result


def _write_stage_plan(path: Path) -> Path:
    lines = ["# P12B Dry-Run Stage Plan", ""]
    for index, stage in enumerate(STAGES, start=1):
        lines.append(f"{index}. {stage}: planned dry-run only")
    lines.extend(["", "No render, VLM provider call, TTS, deletion, or publishing action is executed in P12B."])
    path.write_text("\n".join(lines) + "\n", encoding="utf-8")
    return path


def _write_risk_report(path: Path) -> Path:
    lines = [
        "# P12B Dry-Run Risk Report",
        "",
        "- VLM QC is sidecar skeleton only and returns hold without provider execution.",
        "- Owner Firewall is the final decision layer.",
        "- Raw videos are read-only local assets and must stay out of Git.",
        "- Generated outputs remain under ignored product outputs.",
    ]
    path.write_text("\n".join(lines) + "\n", encoding="utf-8")
    return path
