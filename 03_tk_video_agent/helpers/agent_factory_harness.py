"""P12 Agent Factory Runtime Harness dry-run orchestration."""

from __future__ import annotations

import json
from pathlib import Path
from typing import Any

from helpers.agent_state import AgentState
from helpers.git_safety_guard import run_git_safety_guard
from helpers.media_asset_guard import run_media_asset_guard
from helpers.owner_firewall import write_decision_template
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
