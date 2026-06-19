"""Owner Firewall dry-run executor for P12 Agent Factory."""

from __future__ import annotations

import json
from datetime import datetime, timezone
from pathlib import Path
from typing import Any


SUPPORTED_ACTIONS = {
    "approve_all",
    "approve_selected",
    "force_reject",
    "force_delete_candidate",
    "force_rerun_variant",
    "force_stop_pipeline",
    "force_override_vlm",
    "force_write_negative_example",
}

OWNER_DECISIONS = {"approve", "reject", "revise", "stop"}


def default_decision_template(variants_requested: int) -> dict[str, Any]:
    variants = [f"V{i:02d}" for i in range(1, variants_requested + 1)]
    return {
        "mode": "dry_run",
        "actions": [
            {
                "action": "approve_selected",
                "variant_ids": variants,
                "reason": "Template only. Owner must edit before non-dry-run execution.",
            }
        ],
        "notes": "Supported actions: " + ", ".join(sorted(SUPPORTED_ACTIONS)),
    }


def write_decision_template(path: Path | str, variants_requested: int) -> Path:
    output = Path(path)
    output.parent.mkdir(parents=True, exist_ok=True)
    output.write_text(json.dumps(default_decision_template(variants_requested), indent=2, ensure_ascii=False) + "\n", encoding="utf-8")
    return output


def load_owner_decisions(path: Path | str) -> dict[str, Any]:
    return json.loads(Path(path).read_text(encoding="utf-8"))


def generate_owner_review_packet(checkpoint: dict[str, Any]) -> str:
    """Render the standard Owner Review Packet text."""
    fields = [
        "checkpoint_id",
        "checkpoint_type",
        "current_goal",
        "completed_work",
        "proposed_action",
        "why_needed",
        "business_benefit",
        "affected_files",
        "hard_rules_affected",
        "estimated_cost",
        "estimated_runtime",
        "reversible",
        "main_risks",
        "tests_completed",
        "codex_recommendation",
    ]
    lines = ["OWNER_REVIEW_REQUIRED", ""]
    for name in fields:
        value = checkpoint.get(name, "")
        if isinstance(value, list):
            value = ", ".join(str(item) for item in value)
        lines.append(f"{name}: {value}")
    lines.extend(["owner_options:", "- approve", "- reject", "- revise", "exact_resume_instruction: " + str(checkpoint.get("exact_resume_instruction", ""))])
    return "\n".join(lines) + "\n"


def request_owner_review(state: Any, checkpoint: dict[str, Any]) -> dict[str, Any]:
    """Mark an AgentState-like object as waiting for Owner review."""
    state.awaiting_owner_review = True
    state.pending_checkpoint = checkpoint
    state.owner_firewall_status = {"status": "owner_review_required", "checkpoint_id": checkpoint.get("checkpoint_id")}
    state.next_recommended_action = "Owner must approve, reject, revise, or stop the checkpoint."
    state.touch()
    return state.to_dict()


def validate_owner_decision(decision: dict[str, Any], pending_checkpoint: dict[str, Any] | None) -> dict[str, Any]:
    """Validate that a decision is an explicit Owner decision for the pending checkpoint."""
    required = ["decision", "checkpoint_id", "decided_at", "owner_note"]
    missing = [key for key in required if not decision.get(key)]
    if missing:
        return {"status": "fail", "error": "missing_required_fields", "missing": missing}
    if decision.get("decision") not in OWNER_DECISIONS:
        return {"status": "fail", "error": "unsupported_owner_decision", "allowed": sorted(OWNER_DECISIONS)}
    actor = str(decision.get("actor") or decision.get("decision_by") or decision.get("source") or "").lower()
    if actor != "owner":
        return {"status": "fail", "error": "owner_actor_required"}
    if not pending_checkpoint:
        return {"status": "fail", "error": "no_pending_checkpoint"}
    if decision["checkpoint_id"] != pending_checkpoint.get("checkpoint_id"):
        return {"status": "fail", "error": "checkpoint_id_mismatch"}
    return {"status": "pass"}


def apply_owner_decision(state: Any, decision: dict[str, Any]) -> dict[str, Any]:
    validation = validate_owner_decision(decision, state.pending_checkpoint)
    if validation["status"] != "pass":
        return {"status": "fail", "validation": validation}
    state.last_owner_decision = decision
    state.owner_firewall_status = {"status": "decision_applied", "decision": decision["decision"], "checkpoint_id": decision["checkpoint_id"]}
    if decision["decision"] == "approve":
        clear_checkpoint_after_approval(state)
        state.resume_instruction = "Resume the approved checkpoint with the next safe implementation step."
    elif decision["decision"] == "revise":
        state.awaiting_owner_review = False
        state.resume_instruction = "Revise the proposed action according to Owner note, then re-run Phase Guard."
        state.pending_checkpoint = None
    else:
        state.awaiting_owner_review = False
        state.resume_instruction = "Stop gated work. Do not continue this checkpoint without a new Owner instruction."
    state.touch()
    return {"status": "pass", "state": state.to_dict(), "resume_instruction": state.resume_instruction}


def clear_checkpoint_after_approval(state: Any) -> None:
    state.awaiting_owner_review = False
    state.pending_checkpoint = None
    state.next_recommended_action = "Continue approved work; rerun safety checks before commit."


def evaluate_owner_firewall(decisions: dict[str, Any], *, dry_run: bool = True) -> dict[str, Any]:
    actions = decisions.get("actions", [])
    violations = []
    normalized_actions = []
    for index, item in enumerate(actions):
        action = item.get("action")
        if action not in SUPPORTED_ACTIONS:
            violations.append({"index": index, "error": "unsupported_action", "action": action})
        if action == "force_delete_candidate" and not dry_run:
            violations.append({"index": index, "error": "delete_not_enabled_in_p12b", "action": action})
        normalized_actions.append({"index": index, "action": action, "dry_run_only": dry_run})

    return {
        "status": "pass" if not violations else "fail",
        "dry_run": dry_run,
        "actions_checked": normalized_actions,
        "violations": violations,
        "supported_actions": sorted(SUPPORTED_ACTIONS),
        "message": "P12B Owner Firewall validated decisions without deleting, rendering, publishing, or mutating candidates.",
    }


def run_owner_firewall(
    decision_file: Path | str,
    audit_log_path: Path | str,
    result_path: Path | str,
    *,
    product: str,
    sku: str,
    material_batch: str,
    dry_run: bool = True,
) -> dict[str, Any]:
    decisions = load_owner_decisions(decision_file)
    result = evaluate_owner_firewall(decisions, dry_run=dry_run)
    result.update({"product": product, "sku": sku, "material_batch": material_batch, "decision_file": str(decision_file)})

    result_output = Path(result_path)
    result_output.parent.mkdir(parents=True, exist_ok=True)
    result_output.write_text(json.dumps(result, indent=2, ensure_ascii=False) + "\n", encoding="utf-8")

    timestamp = datetime.now(timezone.utc).replace(microsecond=0).isoformat()
    lines = [
        "# Owner Firewall Audit Log",
        "",
        f"- timestamp: {timestamp}",
        f"- product: {product}",
        f"- sku: {sku}",
        f"- material_batch: {material_batch}",
        f"- dry_run: {dry_run}",
        f"- status: {result['status']}",
        f"- decision_file: {decision_file}",
        "",
        "No files were deleted, no videos were generated, and no publishing action was taken.",
    ]
    Path(audit_log_path).write_text("\n".join(lines) + "\n", encoding="utf-8")
    return result
