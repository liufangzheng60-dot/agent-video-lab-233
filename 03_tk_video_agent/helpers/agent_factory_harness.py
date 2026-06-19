"""P12 Agent Factory Runtime Harness dry-run orchestration."""

from __future__ import annotations

import json
import subprocess
from pathlib import Path
from typing import Any

from helpers.agent_state import AgentState, load_agent_state
from helpers.evidence_registry import append_evidence
from helpers.git_safety_guard import run_git_safety_guard
from helpers.media_asset_guard import run_media_asset_guard
from helpers.owner_firewall import apply_owner_decision, generate_owner_review_packet, load_owner_decisions, write_decision_template
from helpers.vlm_qc_gate import audit_video_via_vlm, write_vlm_policy


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
    state.media_asset_guard_results = media_report
    state.output_paths = {
        "agent_state": str(out_dir / "agent_state.json"),
        "hard_rule_preflight_report": str(out_dir / "hard_rule_preflight_report.json"),
        "media_asset_guard_report": str(out_dir / "media_asset_guard_report.json"),
        "git_safety_report": str(out_dir / "git_safety_report.json"),
        "owner_next_action": str(out_dir / "owner_next_action.md"),
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
