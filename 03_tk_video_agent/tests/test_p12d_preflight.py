import tempfile
import unittest
from pathlib import Path

from helpers.p12d_preflight import _diversity_report, _supersede_old_checkpoint
from helpers.agent_state import AgentState
from helpers.resource_governor import ResourceGovernor


class P12DPreflightTests(unittest.TestCase):
    def test_supersedes_old_p12c_checkpoint(self):
        state = AgentState(product="dog_stairs_v1", sku="khaki", material_batch="batch_20260617_001", variants_requested=12)
        state.awaiting_owner_review = True
        state.pending_checkpoint = {"checkpoint_id": "P12C_REAL_BATCH_LAUNCH_batch_20260617_001"}
        _supersede_old_checkpoint(state)
        self.assertFalse(state.awaiting_owner_review)
        self.assertIsNone(state.pending_checkpoint)
        self.assertEqual(state.pipeline_status, "P12C_CHECKPOINT_SUPERSEDED")

    def test_diversity_requires_three_body_structures_and_unique_timeline(self):
        plans = [
            {"timeline_sequence_hash": "a", "body_structure_id": "one"},
            {"timeline_sequence_hash": "b", "body_structure_id": "two"},
            {"timeline_sequence_hash": "c", "body_structure_id": "three"},
        ]
        self.assertEqual(_diversity_report(plans)["result"], "pass")
        plans[2]["timeline_sequence_hash"] = "a"
        self.assertEqual(_diversity_report(plans)["result"], "fail")

    def test_resource_governor_profile_limits(self):
        with tempfile.TemporaryDirectory() as tmp:
            governor = ResourceGovernor(Path(tmp), "dog_stairs_v1", "batch_20260617_001")
            profile = governor.profile
            self.assertEqual(profile["max_concurrent_ffmpeg"], 1)
            self.assertEqual(profile["ffmpeg_threads_default"], 2)
            self.assertEqual(profile["max_python_workers"], 2)


if __name__ == "__main__":
    unittest.main()
