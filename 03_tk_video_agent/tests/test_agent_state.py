import json
import tempfile
import unittest
from pathlib import Path

from helpers.agent_state import AgentState, load_agent_state


class AgentStateTests(unittest.TestCase):
    def test_state_round_trip_includes_required_fields(self):
        with tempfile.TemporaryDirectory() as tmp:
            path = Path(tmp) / "agent_state.json"
            state = AgentState(product="dog_stairs_v1", sku="khaki", material_batch="batch_20260617_001", variants_requested=12)
            state.mark_stage("preflight", "hold")
            state.write_json(path)

            payload = json.loads(path.read_text(encoding="utf-8"))
            for key in [
                "product",
                "sku",
                "material_batch",
                "variants_requested",
                "current_stage",
                "stage_status",
                "hard_rule_results",
                "media_asset_guard_results",
                "vlm_qc_results",
                "owner_firewall_status",
                "output_paths",
                "failed_variants",
                "rerun_history",
                "final_review_pack_path",
                "created_at",
                "updated_at",
            ]:
                self.assertIn(key, payload)
            self.assertEqual(load_agent_state(path).current_stage, "preflight")


if __name__ == "__main__":
    unittest.main()
