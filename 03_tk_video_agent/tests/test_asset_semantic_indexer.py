import tempfile
import unittest
from pathlib import Path

from helpers.asset_semantic_indexer import (
    build_keyframe_strip_plan,
    build_video_proxy_plan,
    generate_candidate_windows,
    select_golden_pilot_source_clips,
)


class AssetSemanticIndexerTests(unittest.TestCase):
    def _inventory(self, raw_dir: Path):
        return [
            {
                "clip_id": "clip_001",
                "filename": "b.mp4",
                "absolute_path": str(raw_dir / "b.mp4"),
                "size_bytes": 100,
                "modified_time": "1",
                "duration_sec": 8.0,
                "width": 1920,
                "height": 1080,
                "sample_aspect_ratio": "1:1",
                "display_aspect_ratio": "16:9",
                "orientation": "landscape",
                "probe_status": "pass",
            },
            {
                "clip_id": "clip_002",
                "filename": "a.mp4",
                "absolute_path": str(raw_dir / "a.mp4"),
                "size_bytes": 100,
                "modified_time": "1",
                "duration_sec": 3.0,
                "width": 1080,
                "height": 1920,
                "sample_aspect_ratio": "1:1",
                "display_aspect_ratio": "9:16",
                "orientation": "portrait",
                "probe_status": "pass",
            },
        ]

    def test_candidate_windows_are_deterministic(self):
        with tempfile.TemporaryDirectory() as temp:
            raw_dir = Path(temp) / "raw_videos"
            out_dir = Path(temp) / "outputs"
            raw_dir.mkdir()
            first = generate_candidate_windows(self._inventory(raw_dir), out_dir)
            second = generate_candidate_windows(self._inventory(raw_dir), out_dir)
            self.assertEqual(first, second)
            self.assertEqual(first[0]["clip_id"], "clip_002")

    def test_long_clip_gets_fixed_windows_without_physical_cut(self):
        with tempfile.TemporaryDirectory() as temp:
            raw_dir = Path(temp) / "raw_videos"
            out_dir = Path(temp) / "outputs"
            raw_dir.mkdir()
            windows = generate_candidate_windows(self._inventory(raw_dir), out_dir)
            long_clip_windows = [item for item in windows if item["clip_id"] == "clip_001"]
            self.assertGreaterEqual(len(long_clip_windows), 3)
            self.assertTrue(all(item["scene_boundary_source"] in {"fixed_window補充", "scene_candidate"} for item in long_clip_windows))
            self.assertFalse(any(str(raw_dir) in item["proxy_path"] for item in windows))

    def test_keyframe_and_proxy_plans_write_to_outputs_only(self):
        with tempfile.TemporaryDirectory() as temp:
            raw_dir = Path(temp) / "raw_videos"
            out_dir = Path(temp) / "outputs"
            raw_dir.mkdir()
            window = generate_candidate_windows(self._inventory(raw_dir), out_dir)[0]
            strip = build_keyframe_strip_plan(window, out_dir)
            proxy = build_video_proxy_plan(window, out_dir, reason="low_confidence")
            self.assertFalse(strip["writes_to_raw_videos"])
            self.assertFalse(proxy["writes_to_raw_videos"])
            self.assertIn(str(out_dir), strip["output_path"])
            self.assertIn(str(out_dir), proxy["output_path"])
            self.assertEqual(len(strip["sample_times_ms"]), 5)

    def test_golden_pilot_selection_is_sorted(self):
        with tempfile.TemporaryDirectory() as temp:
            selected = select_golden_pilot_source_clips(self._inventory(Path(temp)))
            self.assertEqual([item["filename"] for item in selected], ["a.mp4", "b.mp4"])


if __name__ == "__main__":
    unittest.main()
