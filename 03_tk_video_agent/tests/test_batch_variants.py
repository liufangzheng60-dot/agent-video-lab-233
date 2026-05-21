"""Tests for batch variant generation."""

from __future__ import annotations

import json
import tempfile
import unittest
from pathlib import Path
from unittest.mock import patch

from helpers.batch_variants import (
    build_variant_subtitles,
    get_variant_configs,
    render_feedback_template,
    render_publish_plan,
    run_batch_variants,
)
from helpers.subtitle_overlay import contains_chinese, render_srt


class BatchVariantsTests(unittest.TestCase):
    def setUp(self) -> None:
        self.temp_dir = tempfile.TemporaryDirectory()
        self.project_root = Path(self.temp_dir.name) / "03_tk_video_agent"
        self.repo_root = self.project_root.parent
        (self.project_root / "outputs" / "renders").mkdir(parents=True, exist_ok=True)
        (self.project_root / "outputs" / "timelines").mkdir(parents=True, exist_ok=True)
        (self.project_root / "outputs" / "edit_strategy").mkdir(parents=True, exist_ok=True)
        (self.repo_root / "05_final_outputs" / "publish_records").mkdir(parents=True, exist_ok=True)
        (self.repo_root / "05_final_outputs" / "performance_feedback").mkdir(parents=True, exist_ok=True)
        self.write_inputs()

    def tearDown(self) -> None:
        self.temp_dir.cleanup()

    def write_inputs(self) -> None:
        timeline = {
            "target_duration_seconds": 15.0,
            "segments": [
                {"start": 0, "end": 2, "segment_name": "hook", "caption": "baseline hook"},
                {"start": 2, "end": 4, "segment_name": "problem", "caption": "baseline problem"},
                {"start": 4, "end": 9, "segment_name": "demo", "caption": "baseline demo"},
                {"start": 9, "end": 12, "segment_name": "proof", "caption": "baseline proof"},
                {"start": 12, "end": 15, "segment_name": "cta", "caption": "baseline cta"},
            ],
        }
        edit_strategy = {"strategy_segments": []}
        (self.project_root / "outputs" / "timelines" / "timeline.json").write_text(json.dumps(timeline), encoding="utf-8")
        (self.project_root / "outputs" / "edit_strategy" / "edit_strategy.json").write_text(json.dumps(edit_strategy), encoding="utf-8")
        (self.project_root / "outputs" / "renders" / "final.mp4").write_bytes(b"fake video")

    def test_generates_five_variant_configs(self) -> None:
        configs = get_variant_configs()

        self.assertEqual(len(configs), 5)
        self.assertEqual([item["version"] for item in configs], ["v002", "v003", "v004", "v005", "v006"])

    def test_each_variant_has_english_subtitles(self) -> None:
        timeline = json.loads((self.project_root / "outputs" / "timelines" / "timeline.json").read_text(encoding="utf-8"))

        for variant in get_variant_configs():
            srt = render_srt(build_variant_subtitles(timeline, variant))
            self.assertIn("00:00:00,000", srt)
            self.assertFalse(contains_chinese(srt))

    def test_subtitles_do_not_contain_chinese_characters(self) -> None:
        timeline = {"segments": [{"start": 0, "end": 2, "segment_name": "hook", "caption": "中文"}]}
        srt = render_srt(build_variant_subtitles(timeline, get_variant_configs()[0]))

        self.assertFalse(contains_chinese(srt))

    def test_can_generate_batch_publish_plan(self) -> None:
        results = [{"version": "v002", "key": "cost_hook", "label": "Cost Hook", "output_path": "x.mp4", "srt_path": "x.srt", "status": "success"}]
        plan = render_publish_plan(results)

        self.assertIn("Batch Publish Plan", plan)
        self.assertIn("Cost Hook", plan)

    def test_can_generate_batch_feedback_template(self) -> None:
        results = [{"version": "v002", "key": "cost_hook", "label": "Cost Hook", "output_path": "x.mp4", "srt_path": "x.srt", "status": "success"}]
        feedback = render_feedback_template(results)

        self.assertIn("Batch Feedback", feedback)
        self.assertIn("1h", feedback)
        self.assertIn("48h", feedback)

    @patch("helpers.batch_variants.which", return_value=None)
    def test_no_external_api_dependency(self, _mock_which: object) -> None:
        result = run_batch_variants(self.project_root)

        self.assertFalse(result["ffmpeg_found"])
        self.assertTrue(result["publish_plan_path"].exists())
        self.assertTrue(result["feedback_path"].exists())


if __name__ == "__main__":
    unittest.main()
