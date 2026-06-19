import unittest

from helpers.market_output_contract import default_us_market_contract
from helpers.three_stage_story_compiler import compile_three_stage_plan


def asset(window_id, role, **extra):
    payload = {
        "window_id": window_id,
        "clip_id": window_id.split(":")[0],
        "source_path": f"C:/raw/{window_id}.mp4",
        "start_ms": 0,
        "end_ms": 2000,
        "duration_ms": 2000,
        "segment_role_candidates": [role],
        "confidence": 0.9,
        "hook_strength": 0.8,
        "action_completeness": "complete",
        "product_state": "open",
        "product_state_change_explained": True,
        "claim_evidence_candidates": ["stable_steps_claim"] if role == "proof" else [],
    }
    payload.update(extra)
    return payload


class ThreeStageStoryCompilerTests(unittest.TestCase):
    def contract(self):
        return default_us_market_contract().to_dict()

    def test_pain_solution_order_and_single_skeleton(self):
        ledger = [
            asset("h:0-1000", "hook_problem"),
            asset("p:0-1000", "pain"),
            asset("i:0-1000", "intervention"),
            asset("o:0-1000", "outcome"),
            asset("c:0-1000", "closure_hero"),
        ]
        plan = compile_three_stage_plan(
            automated_asset_ledger=ledger,
            skeleton_id="pain_solution",
            business_intent="solve sofa climb pain",
            market_output_contract=self.contract(),
        )
        self.assertEqual(plan["plan_status"], "pass")
        self.assertEqual([slot["slot"] for slot in plan["core_plan"]], ["pain", "intervention", "outcome"])
        self.assertFalse(plan["uses_legacy_free_planner"])

    def test_feature_proof_requires_claim_evidence(self):
        ledger = [
            asset("h:0-1000", "hook_result"),
            asset("f:0-1000", "feature"),
            asset("d:0-1000", "demonstration"),
            asset("p:0-1000", "proof", claim_evidence_candidates=[]),
            asset("c:0-1000", "closure_cta"),
        ]
        plan = compile_three_stage_plan(
            automated_asset_ledger=ledger,
            skeleton_id="feature_proof",
            business_intent="prove stability",
            market_output_contract=self.contract(),
        )
        self.assertEqual(plan["plan_status"], "fail")
        self.assertIn("proof_missing_claim_evidence", plan["rule_evaluation"]["failures"])

    def test_incomplete_outcome_fails(self):
        ledger = [
            asset("h:0-1000", "hook_problem"),
            asset("p:0-1000", "pain"),
            asset("i:0-1000", "intervention"),
            asset("o:0-1000", "outcome", action_completeness="partial"),
            asset("c:0-1000", "closure_result"),
        ]
        plan = compile_three_stage_plan(
            automated_asset_ledger=ledger,
            skeleton_id="pain_solution",
            business_intent="solve sofa climb pain",
            market_output_contract=self.contract(),
        )
        self.assertIn("incomplete_action_used_as_outcome_or_proof", plan["rule_evaluation"]["failures"])

    def test_product_state_jump_fails_without_explanation(self):
        ledger = [
            asset("h:0-1000", "hook_result"),
            asset("s:0-1000", "situation", product_state="folded", product_state_change_explained=False),
            asset("u:0-1000", "usage", product_state="open", product_state_change_explained=False),
            asset("l:0-1000", "lifestyle_payoff", product_state="open", product_state_change_explained=False),
            asset("c:0-1000", "closure_hero"),
        ]
        plan = compile_three_stage_plan(
            automated_asset_ledger=ledger,
            skeleton_id="lifestyle_value",
            business_intent="show home value",
            market_output_contract=self.contract(),
        )
        self.assertIn("product_state_jump_without_explanation", plan["rule_evaluation"]["failures"])

    def test_same_input_produces_same_signature(self):
        ledger = [
            asset("h:0-1000", "hook_problem"),
            asset("p:0-1000", "pain"),
            asset("i:0-1000", "intervention"),
            asset("o:0-1000", "outcome"),
            asset("c:0-1000", "closure_hero"),
        ]
        first = compile_three_stage_plan(
            automated_asset_ledger=ledger,
            skeleton_id="pain_solution",
            business_intent="solve sofa climb pain",
            market_output_contract=self.contract(),
        )
        second = compile_three_stage_plan(
            automated_asset_ledger=ledger,
            skeleton_id="pain_solution",
            business_intent="solve sofa climb pain",
            market_output_contract=self.contract(),
        )
        self.assertEqual(first["deterministic_signature"], second["deterministic_signature"])


if __name__ == "__main__":
    unittest.main()
