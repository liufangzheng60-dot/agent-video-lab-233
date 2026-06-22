from pathlib import Path
import sys
import unittest

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))

from helpers.storyboard_search_optimizer import motion_transition_score
from helpers.owner_preference_ranker import score_owner_preference


class AssetRecallStoryboardOptimizerTests(unittest.TestCase):
    def test_low_confidence_motion_does_not_affect_ranking(self):
        prev = {"tail_motion_descriptor": {"confidence": 0.4, "vector": [10, 0], "magnitude": 10}}
        nxt = {"head_motion_descriptor": {"confidence": 0.9, "vector": [10, 0], "magnitude": 10}}
        result = motion_transition_score(prev, nxt)
        self.assertEqual(result["motion_match_score"], 0.0)
        self.assertEqual(result["ranking_effect"], "zero_low_confidence")

    def test_motion_weight_is_capped(self):
        prev = {"tail_motion_descriptor": {"confidence": 0.95, "vector": [10, 0], "magnitude": 10}}
        nxt = {"head_motion_descriptor": {"confidence": 0.95, "vector": [10, 0], "magnitude": 10}}
        result = motion_transition_score(prev, nxt, weight=0.99)
        self.assertLessEqual(result["weight"], 0.15)

    def test_owner_preference_score(self):
        score = score_owner_preference({"zero_transition_freeze": True, "no_hand_intrusion": True, "motion_continuity": 0.5})
        self.assertGreater(score, 80)


if __name__ == "__main__":
    unittest.main()
