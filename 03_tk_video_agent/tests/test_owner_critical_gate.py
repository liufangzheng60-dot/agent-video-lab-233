import json
import tempfile
import unittest
from pathlib import Path

from helpers.agent_state import AgentState, load_agent_state
from helpers.owner_firewall import apply_owner_decision, generate_owner_review_packet, request_owner_review, validate_owner_decision


def _checkpoint() -> dict:
    return {
        "checkpoint_id": "CP_TEST_001",
        "checkpoint_type": "GATE_REAL_BATCH_LAUNCH",
        "current_goal": "Generate 12 review pack videos",
        "completed_work": "Dry-run completed",
        "proposed_action": "Run real Batch2 production",
        "why_needed": "Validate throughput",
        "business_benefit": "More A/B test volume",
        "affected_files": [],
        "hard_rules_affected": [],
        "estimated_cost": "none",
        "estimated_runtime": "unknown",
        "reversible": "yes",
        "main_risks": ["media generation"],
        "tests_completed": ["focused"],
        "codex_recommendation": "approve only after raw material is present",
        "exact_resume_instruction": "Run the approved real batch command.",
    }


class OwnerCriticalGateTests(unittest.TestCase):
    def test_owner_review_packet_format(self):
        packet = generate_owner_review_packet(_checkpoint())
        self.assertIn("OWNER_REVIEW_REQUIRED", packet)
        self.assertIn("checkpoint_id: CP_TEST_001", packet)
        self.assertIn("- approve", packet)

    def test_checkpoint_mismatch_rejected(self):
        decision = {"decision": "approve", "checkpoint_id": "OTHER", "decided_at": "2026-06-19T00:00:00Z", "owner_note": "ok", "actor": "owner"}
        result = validate_owner_decision(decision, _checkpoint())
        self.assertEqual(result["status"], "fail")
        self.assertEqual(result["error"], "checkpoint_id_mismatch")

    def test_approve_generates_resume_instruction_and_clears_checkpoint(self):
        state = AgentState(product="dog_stairs_v1", sku="khaki", material_batch="batch_20260617_001", variants_requested=12)
        request_owner_review(state, _checkpoint())
        decision = {"decision": "approve", "checkpoint_id": "CP_TEST_001", "decided_at": "2026-06-19T00:00:00Z", "owner_note": "approved", "actor": "owner"}
        result = apply_owner_decision(state, decision)
        self.assertEqual(result["status"], "pass")
        self.assertFalse(state.awaiting_owner_review)
        self.assertIsNone(state.pending_checkpoint)
        self.assertIn("Resume", state.resume_instruction)

    def test_reject_keeps_task_stopped(self):
        state = AgentState(product="dog_stairs_v1", sku="khaki", material_batch="batch_20260617_001", variants_requested=12)
        request_owner_review(state, _checkpoint())
        decision = {"decision": "reject", "checkpoint_id": "CP_TEST_001", "decided_at": "2026-06-19T00:00:00Z", "owner_note": "no", "actor": "owner"}
        result = apply_owner_decision(state, decision)
        self.assertEqual(result["status"], "pass")
        self.assertIn("Stop gated work", state.resume_instruction)

    def test_gpt_suggestion_is_not_owner_authorization(self):
        state = AgentState(product="dog_stairs_v1", sku="khaki", material_batch="batch_20260617_001", variants_requested=12)
        request_owner_review(state, _checkpoint())
        decision = {"decision": "approve", "checkpoint_id": "CP_TEST_001", "decided_at": "2026-06-19T00:00:00Z", "owner_note": "GPT says yes", "actor": "gpt"}
        result = apply_owner_decision(state, decision)
        self.assertEqual(result["status"], "fail")
        self.assertEqual(result["validation"]["error"], "owner_actor_required")

    def test_old_agent_state_schema_loads_with_defaults(self):
        with tempfile.TemporaryDirectory() as tmp:
            path = Path(tmp) / "agent_state.json"
            old_payload = {
                "product": "dog_stairs_v1",
                "sku": "khaki",
                "material_batch": "batch_20260617_001",
                "variants_requested": 12,
                "current_stage": "preflight",
                "stage_status": {},
                "hard_rule_results": {},
                "media_asset_guard_results": {},
                "vlm_qc_results": {},
                "owner_firewall_status": {"status": "not_started"},
                "output_paths": {},
                "failed_variants": [],
                "rerun_history": [],
                "final_review_pack_path": None,
                "created_at": "2026-06-19T00:00:00+00:00",
                "updated_at": "2026-06-19T00:00:00+00:00",
                "future_unknown_field": "ignored",
            }
            path.write_text(json.dumps(old_payload), encoding="utf-8")
            state = load_agent_state(path)
            self.assertFalse(state.awaiting_owner_review)
            self.assertIsNone(state.pending_checkpoint)
            self.assertIsNone(state.last_owner_decision)


if __name__ == "__main__":
    unittest.main()
