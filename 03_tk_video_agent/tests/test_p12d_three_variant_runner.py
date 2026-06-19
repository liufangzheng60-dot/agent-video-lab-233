import tempfile
import unittest
from pathlib import Path

from helpers.p12d_three_variant_runner import _build_segment_plans, _repeat_rate


class P12DThreeVariantRunnerTests(unittest.TestCase):
    def test_repeat_rate(self):
        self.assertEqual(_repeat_rate(["a", "b", "c"]), 0.0)
        self.assertEqual(_repeat_rate(["a", "a", "b"]), 0.333)

    def test_segment_plan_is_true_9x16_crop(self):
        clip_index = {
            "c1": {"absolute_path": "a.mov", "width": 1920, "height": 1080},
            "c2": {"absolute_path": "b.mov", "width": 1920, "height": 1080},
            "c3": {"absolute_path": "c.mov", "width": 1920, "height": 1080},
            "c4": {"absolute_path": "d.mov", "width": 1920, "height": 1080},
        }
        plan = {"hook_zone": "c1", "body_zone": "c2", "proof_zone": "c3", "CTA_zone": "c4"}
        segments = _build_segment_plans(plan, clip_index)
        self.assertEqual(len(segments), 4)
        for segment in segments:
            self.assertEqual(segment["output_width"], 1080)
            self.assertEqual(segment["output_height"], 1920)
            self.assertEqual(segment["output_aspect_ratio"], "9:16")
            crop = segment["crop_box"]
            self.assertAlmostEqual(crop["width"] / crop["height"], 9 / 16, places=2)


if __name__ == "__main__":
    unittest.main()
