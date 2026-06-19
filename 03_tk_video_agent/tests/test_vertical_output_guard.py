import json
import tempfile
import unittest
from pathlib import Path

from helpers.vertical_output_guard import VerticalOutputGuard, build_shortage_report


def _good_segment(segment_id="s1"):
    return {
        "segment_id": segment_id,
        "source_width": 1920,
        "source_height": 1080,
        "source_aspect_ratio": "16:9",
        "source_orientation": "landscape",
        "fit_policy": "smart_crop",
        "crop_box": {"x": 656, "y": 0, "width": 608, "height": 1080},
        "output_width": 1080,
        "output_height": 1920,
        "output_aspect_ratio": "9:16",
        "black_bar_detected": False,
        "stretch_detected": False,
        "frame_fill_ratio": 1.0,
        "start_sec": 0.0,
        "end_sec": 2.0,
    }


class VerticalOutputGuardTests(unittest.TestCase):
    def setUp(self):
        self.guard = VerticalOutputGuard()

    def test_final_container_non_9x16_fails(self):
        result = self.guard.validate_final_container({"width": 640, "height": 480, "display_aspect_ratio": "4:3", "sample_aspect_ratio": "1:1", "orientation": "landscape"})
        self.assertFalse(result["pass"])
        self.assertIn("invalid_container_size", result["failures"])

    def test_qc_draft_must_stay_true_9x16(self):
        good = self.guard.validate_final_container({"width": 540, "height": 960, "display_aspect_ratio": "9:16", "sample_aspect_ratio": "1:1", "orientation": "portrait"}, qc_draft=True)
        bad = self.guard.validate_final_container({"width": 640, "height": 480, "display_aspect_ratio": "4:3", "sample_aspect_ratio": "1:1", "orientation": "landscape"}, qc_draft=True)
        self.assertTrue(good["pass"])
        self.assertFalse(bad["pass"])

    def test_final_container_pass_but_horizontal_inset_segment_fails(self):
        manifest = {
            "variant_id": "known_failure_fixture",
            "final_container": {"width": 1080, "height": 1920, "display_aspect_ratio": "9:16", "sample_aspect_ratio": "1:1", "orientation": "portrait"},
            "segments": [
                _good_segment("hook"),
                {
                    **_good_segment("bad_mid"),
                    "fit_policy": "inset",
                    "crop_box": {"x": 0, "y": 0, "width": 1920, "height": 1080},
                    "frame_fill_ratio": 0.56,
                    "time_range": [2.0, 4.5],
                },
            ],
        }
        report = self.guard.build_vertical_compliance_report(manifest)
        self.assertTrue(report["final_container_pass"])
        self.assertEqual(report["segments_failed"], 1)
        self.assertEqual(report["failed_segment_ids"], ["bad_mid"])
        self.assertTrue(report["auto_replacement_required"])
        self.assertFalse(report["publish_allowed"])

    def test_black_bars_fail(self):
        segment = {**_good_segment(), "black_bar_detected": True}
        result = self.guard.validate_segment_plan(segment)
        self.assertEqual(result["segment_gate_result"], "fail")
        self.assertIn("black_bar_detected", result["failures"])

    def test_stretch_fails(self):
        segment = {**_good_segment(), "fit_policy": "stretch", "stretch_detected": True}
        result = self.guard.validate_segment_plan(segment)
        self.assertEqual(result["segment_gate_result"], "fail")
        self.assertIn("stretch_detected", result["failures"])

    def test_unsafe_crop_enters_semantic_pending_hold(self):
        segment = {**_good_segment(), "semantic_crop_risk": True}
        result = self.guard.validate_segment_plan(segment)
        self.assertEqual(result["segment_gate_result"], "hold")
        self.assertIn("semantic_crop_pending", result["warnings"])

    def test_failed_segment_replacement_recommendation_and_hold_after_three(self):
        replace = self.guard.recommend_replacement({"segment_id": "s1", "replacement_attempts": 2})
        hold = self.guard.recommend_replacement({"segment_id": "s1", "replacement_attempts": 3})
        self.assertEqual(replace["action"], "replace_segment")
        self.assertEqual(hold["action"], "hold_variant")

    def test_boundary_frame_sampling_points(self):
        samples = self.guard.sample_segment_boundary_frames("video.mp4", {"segments": [_good_segment("s1")]})
        labels = {item["label"] for item in samples}
        self.assertIn("start_plus_0_1", labels)
        self.assertIn("midpoint", labels)
        self.assertIn("end_minus_0_1", labels)
        self.assertIn("transition_before", labels)
        self.assertIn("transition_after", labels)

    def test_manifest_file_fixture_is_supported(self):
        with tempfile.TemporaryDirectory() as tmp:
            path = Path(tmp) / "fixture.json"
            path.write_text(
                json.dumps(
                    {
                        "variant_id": "file_fixture",
                        "final_container": {"width": 1080, "height": 1920, "display_aspect_ratio": "9:16", "sample_aspect_ratio": "1:1", "orientation": "portrait"},
                        "segments": [_good_segment()],
                    }
                ),
                encoding="utf-8",
            )
            report = self.guard.build_vertical_compliance_report(path)
            self.assertTrue(report["publish_allowed"])

    def test_shortage_report(self):
        report = build_shortage_report(target_count=12, passed_count=9, held_variants=["V03"])
        self.assertEqual(report["status"], "shortage")
        self.assertEqual(report["shortage_count"], 3)


if __name__ == "__main__":
    unittest.main()
