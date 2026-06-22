from __future__ import annotations

from pathlib import Path
import sys
import unittest

ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(ROOT / "03_tk_video_agent"))

from helpers.vision_compiler.cinematic_feature_engine import (
    CinematicFeatureEngine,
    MOTION_CONTINUITY_MAX_WEIGHT,
)
from helpers.vision_compiler.global_storyboard_optimizer import (
    BEAM_WIDTH,
    PER_SLOT_TOP_K,
    GlobalStoryboardOptimizer,
)
from helpers.vision_compiler.portable_paths import data_path


P12W = data_path("products/dog_stairs_v1/outputs/renders/batch_20260617_001/P12W_opencv_ffmpeg_vlm_asymmetric_vision_compiler")
P12U = data_path("products/dog_stairs_v1/outputs/renders/batch_20260617_001/P12U_full_asset_recall_global_storyboard_optimizer")
P12X = data_path("products/dog_stairs_v1/outputs/renders/batch_20260617_001/P12X_v2_cinematic_global_search_with_guardrails")


class P12XCinematicGlobalSearchTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        if not (P12W / "selected_director_slates.json").exists():
            raise unittest.SkipTest("P12W/P12X business outputs are absent; desktop smoke test covers portable compiler dependencies.")
        cls.optimizer = GlobalStoryboardOptimizer(P12W, P12U, P12X)
        cls.engine: CinematicFeatureEngine = cls.optimizer.engine

    def test_p12w_candidate0_exists_and_search_limits(self):
        self.assertEqual(BEAM_WIDTH, 45)
        self.assertEqual(PER_SLOT_TOP_K, 8)
        for variant in self.optimizer.p12w_slates:
            self.assertTrue((P12W / f"{variant}_P12W.mp4").exists())

    def test_motion_weight_ceiling_and_low_confidence_zero(self):
        self.assertLessEqual(self.engine.motion_weight, MOTION_CONTINUITY_MAX_WEIGHT)
        result = self.engine.motion_continuity(
            {"tail_global_motion": {"confidence": 0.2}, "motion_source": "camera_motion"},
            {"head_global_motion": {"confidence": 0.9}, "motion_source": "camera_motion"},
        )
        self.assertTrue(result["low_confidence_zeroed"])
        self.assertEqual(result["score"], 0.0)

    def test_farneback_is_not_camera_motion_primary(self):
        shot = self.optimizer.p12w_slates["V2A_feature_proof"]["shots"][0]
        features = self.engine.candidate_features(shot)
        self.assertEqual(features["camera_motion_method"], "feature_points_sparse_lk_ransac_affine")
        self.assertTrue(features["farneback_used_for_residual_only"])

    def test_same_scale_is_not_auto_jump_cut(self):
        shots = self.optimizer.p12w_slates["V2A_feature_proof"]["shots"]
        risk = self.engine.jump_cut_risk(shots[0], shots[1])
        self.assertTrue(risk["same_shot_scale_is_not_auto_jump_cut"])
        self.assertFalse(risk["hard_reject"])

    def test_node_edge_sequence_scores_exist(self):
        result = self.optimizer.optimize_all()
        self.assertTrue(result["reports"]["node"])
        self.assertTrue(result["reports"]["edge"])
        self.assertTrue(result["reports"]["sequence"])

    def test_top3_candidate_families_are_distinct(self):
        result = self.optimizer.optimize_all()
        for item in result["reports"]["beam"]:
            self.assertGreaterEqual(len(set(item["top3_families"])), 3)

    def test_p12w_fallback_when_not_dominant(self):
        result = self.optimizer.optimize_all()
        self.assertTrue(result["selected_slates"]["V1A_pain_solution"]["fallback_to_p12w"])
        self.assertEqual(result["selected_slates"]["V1A_pain_solution"]["video_dominance_margin"], 0.0)

    def test_v2b_cutpoint_fix_candidate_survives(self):
        result = self.optimizer.optimize_all()
        selected = result["selected_slates"]["V2B_feature_proof"]
        self.assertFalse(selected["fallback_to_p12w"])
        self.assertGreaterEqual(selected["shots"][0]["duration_ms"], 1000)


if __name__ == "__main__":
    unittest.main()
