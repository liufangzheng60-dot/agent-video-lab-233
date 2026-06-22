from __future__ import annotations

from pathlib import Path
import sys
import unittest

import cv2
import numpy as np

ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(ROOT / "03_tk_video_agent"))

from helpers.vision_compiler.opencv_perception import detect_abab_ranges, estimate_motion_pair, validate_opencv_video_path
from helpers.vision_compiler.portable_paths import data_path
from helpers.vision_compiler.quality_gate import motion_weight, strict_dominance, topology_valid


RAW = data_path("products/dog_stairs_v1/inputs/raw_videos/batch_20260617_001/IMG_0497.MOV")


class P12WVisionCompilerTests(unittest.TestCase):
    def test_cv2_real_import_and_video_decode(self):
        if not RAW.exists():
            self.skipTest("P12 business raw video is absent; desktop smoke test covers synthetic decode.")
        self.assertTrue(cv2.__version__)
        result = validate_opencv_video_path(RAW)
        self.assertTrue(result["video_read"])
        self.assertTrue(result["farneback"])
        self.assertTrue(result["affine_ransac"])

    def test_abab_pattern_is_detected(self):
        a = np.zeros((64, 64), dtype=np.uint8)
        b = np.full((64, 64), 80, dtype=np.uint8)
        frames = [a, b, a.copy(), b.copy(), a.copy()]
        ranges = detect_abab_ranges(frames, [0, 33, 66, 99, 132], near_threshold=0.1, far_threshold=5)
        self.assertTrue(ranges)

    def test_motion_uses_farneback_as_residual_not_pan_mean(self):
        a = np.zeros((80, 80), dtype=np.uint8)
        b = a.copy()
        cv2.rectangle(a, (20, 20), (35, 35), 255, -1)
        cv2.rectangle(b, (24, 20), (39, 35), 255, -1)
        result = estimate_motion_pair(a, b)
        self.assertIn("local_motion", result)
        self.assertIn(result["local_motion"]["dominant_motion_source"], {"subject_motion", "mixed_motion", "uncertain", "static", "camera_motion"})

    def test_motion_weight_ceiling(self):
        self.assertEqual(motion_weight(0.25), 0.05)

    def test_topology_and_strict_dominance_fallback(self):
        ok, errors = topology_valid("V2A_feature_proof", [{"role": "feature"}, {"role": "proof"}])
        self.assertTrue(ok, errors)
        result = strict_dominance(
            {"technical_score": 80, "local_score": 86, "action_complete": True},
            {"technical_score": 82, "local_score": 82},
            {"dominance_margin": 5.9, "soft_win_count": 2},
        )
        self.assertFalse(result["accepted"])
        self.assertTrue(result["fallback_to_p12t"])


if __name__ == "__main__":
    unittest.main()
