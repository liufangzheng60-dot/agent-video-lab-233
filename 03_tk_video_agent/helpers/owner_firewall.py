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
