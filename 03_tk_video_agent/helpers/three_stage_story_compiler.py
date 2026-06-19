"""Deterministic three-stage commercial story compiler for P12E."""

from __future__ import annotations

import hashlib
import json
from dataclasses import dataclass
from typing import Any


SKELETONS = {
    "pain_solution": ("pain", "intervention", "outcome"),
    "feature_proof": ("feature", "demonstration", "proof"),
    "lifestyle_value": ("situation", "usage", "lifestyle_payoff"),
}

HOOK_ROLES = {"hook_problem", "hook_result", "hook_contrast", "hook_transformation"}
CLOSURE_ROLES = {"closure_result", "closure_hero", "closure_cta"}
ALL_ALLOWED_ROLES = HOOK_ROLES | CLOSURE_ROLES | {role for roles in SKELETONS.values() for role in roles}


@dataclass(frozen=True)
class CompilerConfig:
    version: str = "p12e_three_stage_compiler_v1"
    target_duration_ms: int = 15000


def compile_three_stage_plan(
    *,
    automated_asset_ledger: list[dict[str, Any]],
    skeleton_id: str,
    business_intent: str,
    market_output_contract: dict[str, Any],
    variant_id: str = "P12E_V01",
    target_duration_range: tuple[int, int] = (12000, 15000),
    compiler_config: CompilerConfig | None = None,
) -> dict[str, Any]:
    config = compiler_config or CompilerConfig()
    failures: list[str] = []
    warnings: list[str] = []
    if skeleton_id not in SKELETONS:
        failures.append("unsupported_skeleton")
    invalid_roles = sorted({role for asset in automated_asset_ledger for role in asset.get("segment_role_candidates", []) if role not in ALL_ALLOWED_ROLES})
    if invalid_roles:
        failures.append("invalid_segment_roles:" + ",".join(invalid_roles))

    hook = _pick_asset(automated_asset_ledger, HOOK_ROLES)
    core_assets = [_pick_asset(automated_asset_ledger, {role}) for role in SKELETONS.get(skeleton_id, ())]
    closure = _pick_asset(automated_asset_ledger, CLOSURE_ROLES)
    selected = [item for item in [hook, *core_assets, closure] if item]

    if not hook:
        failures.append("missing_hook")
    if len(core_assets) != 3 or any(asset is None for asset in core_assets):
        failures.append("missing_core_role")
    if not closure:
        failures.append("missing_closure")
    if len({asset["window_id"] for asset in selected}) != len(selected):
        failures.append("duplicate_source_window")
    failures.extend(_continuity_failures(core_assets))
    failures.extend(_claim_evidence_failures(core_assets))

    timeline_segments = _timeline_segments(hook, core_assets, closure)
    voiceover_plan = _voiceover_plan(timeline_segments, market_output_contract)
    explanation = _build_explanation(skeleton_id, business_intent, hook, core_assets, closure)
    if not explanation["why_skeleton"] or any(not value for value in explanation["slot_reasons"].values()):
        failures.append("missing_explanation")

    plan = {
        "plan_id": _plan_id(variant_id, skeleton_id, selected, config.version),
        "variant_id": variant_id,
        "business_intent": business_intent,
        "skeleton_id": skeleton_id,
        "target_duration_ms": min(max(target_duration_range[0], config.target_duration_ms), target_duration_range[1]),
        "hook_plan": _slot_plan("hook", hook),
        "core_plan": [_slot_plan(role, asset) for role, asset in zip(SKELETONS.get(skeleton_id, ()), core_assets)],
        "closure_plan": _slot_plan("closure", closure),
        "voiceover_plan": voiceover_plan,
        "timeline_segments": timeline_segments,
        "continuity_report": {"hard_failures": failures, "soft_warnings": warnings},
        "claim_evidence_map": _claim_evidence_map(core_assets),
        "rule_evaluation": {"hard_pass": not failures, "failures": failures, "soft_warnings": warnings},
        "explanation": explanation,
        "uses_legacy_free_planner": False,
        "compiler_config_version": config.version,
        "deterministic_signature": "",
        "plan_status": "pass" if not failures else "fail",
    }
    plan["deterministic_signature"] = deterministic_signature(plan)
    return plan


def deterministic_signature(plan: dict[str, Any]) -> str:
    clone = dict(plan)
    clone["deterministic_signature"] = ""
    return hashlib.sha256(json.dumps(clone, sort_keys=True, ensure_ascii=False).encode("utf-8")).hexdigest()[:20]


def _pick_asset(ledger: list[dict[str, Any]], roles: set[str]) -> dict[str, Any] | None:
    candidates = [asset for asset in ledger if roles.intersection(set(asset.get("segment_role_candidates", [])))]
    if not candidates:
        return None
    return sorted(
        candidates,
        key=lambda asset: (
            -float(asset.get("confidence", 0)),
            -float(asset.get("hook_strength", 0)),
            str(asset.get("clip_id", "")),
            int(asset.get("start_ms", 0)),
            str(asset.get("window_id", "")),
        ),
    )[0]


def _continuity_failures(core_assets: list[dict[str, Any] | None]) -> list[str]:
    failures: list[str] = []
    usable = [asset for asset in core_assets if asset]
    if len(usable) < 3:
        return failures
    product_states = [asset.get("product_state") for asset in usable if asset.get("product_state")]
    if len(product_states) >= 2 and product_states[0] != product_states[-1] and not any(asset.get("product_state_change_explained") for asset in usable):
        failures.append("product_state_jump_without_explanation")
    for asset in usable:
        roles = set(asset.get("segment_role_candidates", []))
        if roles.intersection({"outcome", "proof"}) and asset.get("action_completeness") != "complete":
            failures.append("incomplete_action_used_as_outcome_or_proof")
    return failures


def _claim_evidence_failures(core_assets: list[dict[str, Any] | None]) -> list[str]:
    failures: list[str] = []
    for asset in [item for item in core_assets if item]:
        roles = set(asset.get("segment_role_candidates", []))
        if "proof" in roles and not asset.get("claim_evidence_candidates"):
            failures.append("proof_missing_claim_evidence")
    return failures


def _timeline_segments(hook: dict[str, Any] | None, core_assets: list[dict[str, Any] | None], closure: dict[str, Any] | None) -> list[dict[str, Any]]:
    result = []
    cursor = 0
    for zone, asset in [("hook", hook), *[(f"core_{index + 1}", asset) for index, asset in enumerate(core_assets)], ("closure", closure)]:
        if not asset:
            continue
        duration = min(3000, max(1000, int(asset.get("duration_ms") or 2000)))
        result.append({
            "visual_segment_id": asset["window_id"],
            "zone": zone,
            "clip_id": asset.get("clip_id"),
            "source_path": asset.get("source_path"),
            "source_start_ms": asset.get("start_ms"),
            "source_end_ms": asset.get("end_ms"),
            "timeline_start_ms": cursor,
            "timeline_end_ms": cursor + duration,
            "selected_role": _first_role(asset),
        })
        cursor += duration
    return result


def _voiceover_plan(timeline_segments: list[dict[str, Any]], contract: dict[str, Any]) -> list[dict[str, Any]]:
    result = []
    for index, segment in enumerate(timeline_segments, start=1):
        claim_type = "non_factual" if segment["zone"] in {"hook", "closure"} else "factual"
        evidence = [segment["visual_segment_id"]] if claim_type == "factual" else []
        result.append({
            "voiceover_segment_id": f"vo_{index:02d}",
            "zone": segment["zone"],
            "visual_segment_ids": [segment["visual_segment_id"]],
            "claim_id": f"claim_{index:02d}" if claim_type == "factual" else None,
            "claim_type": claim_type,
            "claim_evidence_ids": evidence,
            "target_duration_ms": segment["timeline_end_ms"] - segment["timeline_start_ms"],
            "actual_audio_duration_ms": None,
            "allowed_adjustment_ms": 350,
            "semantic_alignment_result": "pass" if claim_type == "non_factual" or evidence else "fail",
            "script_locale": contract.get("script_language", "en-US"),
        })
    return result


def _claim_evidence_map(core_assets: list[dict[str, Any] | None]) -> dict[str, list[str]]:
    mapping = {}
    for asset in [item for item in core_assets if item]:
        for claim in asset.get("claim_evidence_candidates", []):
            mapping.setdefault(str(claim), []).append(asset["window_id"])
    return mapping


def _slot_plan(slot: str, asset: dict[str, Any] | None) -> dict[str, Any]:
    if not asset:
        return {"slot": slot, "status": "missing"}
    return {
        "slot": slot,
        "status": "selected",
        "window_id": asset["window_id"],
        "clip_id": asset.get("clip_id"),
        "role_candidates": asset.get("segment_role_candidates", []),
        "selection_reason": f"匹配 {slot} 槽位，置信度 {asset.get('confidence')}",
    }


def _build_explanation(skeleton_id: str, business_intent: str, hook: dict[str, Any] | None, core_assets: list[dict[str, Any] | None], closure: dict[str, Any] | None) -> dict[str, Any]:
    slots = {"hook": hook, "closure": closure}
    for role, asset in zip(SKELETONS.get(skeleton_id, ()), core_assets):
        slots[role] = asset
    return {
        "why_skeleton": f"{skeleton_id} 支持当前商业目标：{business_intent}" if skeleton_id in SKELETONS else "",
        "slot_reasons": {slot: (f"{asset.get('window_id')} 承担 {slot}，角色标签与槽位匹配。" if asset else "") for slot, asset in slots.items()},
        "rejected_candidates_policy": "候选按置信度、hook_strength、clip_id、start_ms 确定性排序；未胜出的候选保留在资产字典中。",
        "hard_rules": ["三段式顺序", "Core Skeleton 顺序", "Proof 绑定 Claim", "9:16 后续硬审计"],
        "soft_rules": ["景别变化", "光线和空间方向自然"],
    }


def _plan_id(variant_id: str, skeleton_id: str, selected: list[dict[str, Any]], version: str) -> str:
    basis = "|".join([variant_id, skeleton_id, version, *[asset.get("window_id", "") for asset in selected]])
    return "plan_" + hashlib.sha1(basis.encode("utf-8")).hexdigest()[:12]


def _first_role(asset: dict[str, Any]) -> str | None:
    roles = asset.get("segment_role_candidates", [])
    return roles[0] if roles else None
