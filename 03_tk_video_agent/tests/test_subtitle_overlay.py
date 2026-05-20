"""Tests for subtitle generation and overlay workflow."""

from __future__ import annotations

import json
import tempfile
import unittest
from pathlib import Path
from unittest.mock import patch

from helpers.subtitle_overlay import (
    build_subtitles,
    contains_chinese,
    format_srt_time,
    render_srt,
    run_subtitles,
)


class SubtitleOverlayTests(unittest.TestCase):
    def setUp(self) -> None:
        self.temp_dir = tempfile.TemporaryDirectory()
        self.project_root = Path(self.temp_dir.name)
        (self.project_root / "outputs" / "timelines").mkdir(parents=True, exist_ok=True)
        (self.project_root / "outputs" / "edit_strategy").mkdir(parents=True, exist_ok=True)
        (self.project_root / "outputs" / "renders").mkdir(parents=True, exist_ok=True)
        (self.project_root / "inputs" / "product_briefs").mkdir(parents=True, exist_ok=True)
        self.write_inputs()

    def tearDown(self) -> None:
        self.temp_dir.cleanup()

    def write_inputs(self) -> None:
        timeline = {
            "segments": [
                {"start": 0.0, "end": 2.0, "segment_name": "hook", "caption": "Stop paying $20+ for nail trims."},
                {"start": 2.0, "end": 4.0, "segment_name": "problem", "caption": "Pet nail trims are stressful and expensive."},
                {"start": 4.0, "end": 9.0, "segment_name": "demo", "caption": "LED light helps you see the quick before cutting."},
                {"start": 9.0, "end": 12.0, "segment_name": "proof", "caption": "Safer, easier, cheaper at home."},
                {"start": 12.0, "end": 15.0, "segment_name": "cta", "caption": "Grab yours below."},
            ]
        }
        edit_strategy = {"strategy_segments": []}
        (self.project_root / "outputs" / "timelines" / "timeline.json").write_text(json.dumps(timeline), encoding="utf-8")
        (self.project_root / "outputs" / "edit_strategy" / "edit_strategy.json").write_text(json.dumps(edit_strategy), encoding="utf-8")
        (self.project_root / "outputs" / "renders" / "final.mp4").write_bytes(b"fake video")
        (self.project_root / "inputs" / "product_briefs" / "brief.txt").write_text("Brief text", encoding="utf-8")

    def test_generates_srt_from_timeline(self) -> None:
        timeline = json.loads((self.project_root / "outputs" / "timelines" / "timeline.json").read_text(encoding="utf-8"))
        subtitles = build_subtitles(timeline)
        srt = render_srt(subtitles)

        self.assertIn("1\n00:00:00,000 --> 00:00:02,000", srt)
        self.assertIn("Stop paying $20+", srt)

    def test_srt_time_format_is_correct(self) -> None:
        self.assertEqual(format_srt_time(65.432), "00:01:05,432")

    @patch("helpers.subtitle_overlay.which", return_value=None)
    def test_generates_subtitle_plan_when_ffmpeg_missing(self, _mock_which: object) -> None:
        result = run_subtitles(self.project_root)

        self.assertFalse(result["success"])
        self.assertTrue(result["srt_path"].exists())
        self.assertTrue(result["plan_path"].exists())
        self.assertIn("ffmpeg was not found", result["report"]["message"])

    @patch("helpers.subtitle_overlay.which", return_value=None)
    def test_subtitle_plan_contains_timing_table(self, _mock_which: object) -> None:
        result = run_subtitles(self.project_root)
        content = result["plan_path"].read_text(encoding="utf-8")

        self.assertIn("Subtitle Plan", content)
        self.assertIn("00:00:00,000 --> 00:00:02,000", content)

    def test_chinese_product_brief_does_not_create_chinese_subtitles(self) -> None:
        timeline = {"segments": [{"start": 0, "end": 2, "segment_name": "hook", "caption": ""}]}
        edit_strategy = {"strategy_segments": []}
        subtitles = build_subtitles(timeline, edit_strategy, "这是中文脚本，不应该进入字幕。")
        srt = render_srt(subtitles)

        self.assertIn("Stop guessing. Make pet nail trimming easier.", srt)
        self.assertFalse(contains_chinese(srt))
        self.assertEqual(subtitles[0]["source"], "english_fallback_template")

    def test_srt_output_contains_no_chinese_characters(self) -> None:
        timeline = {
            "segments": [
                {"start": 0, "end": 2, "segment_name": "hook", "caption": "中文痛点字幕"},
                {"start": 2, "end": 4, "segment_name": "problem", "caption": "English caption"},
            ]
        }
        subtitles = build_subtitles(timeline)
        srt = render_srt(subtitles)

        self.assertFalse(contains_chinese(srt))
        self.assertIn("English caption", srt)

    def test_english_fallback_captions_generate_for_all_segments(self) -> None:
        timeline = {
            "segments": [
                {"start": 0, "end": 2, "segment_name": "hook", "caption": "中文"},
                {"start": 2, "end": 4, "segment_name": "problem", "caption": "中文"},
                {"start": 4, "end": 9, "segment_name": "demo", "caption": "中文"},
                {"start": 9, "end": 12, "segment_name": "proof", "caption": "中文"},
                {"start": 12, "end": 15, "segment_name": "cta", "caption": "中文"},
            ]
        }
        subtitles = build_subtitles(timeline)
        texts = [item["text"] for item in subtitles]

        self.assertEqual(texts[0], "Stop guessing. Make pet nail trimming easier.")
        self.assertEqual(texts[-1], "Make grooming easier at home.")
        self.assertTrue(all(item["source"] == "english_fallback_template" for item in subtitles))

    def test_no_external_api_dependency(self) -> None:
        timeline = json.loads((self.project_root / "outputs" / "timelines" / "timeline.json").read_text(encoding="utf-8"))
        subtitles = build_subtitles(timeline)

        self.assertEqual(len(subtitles), 5)


if __name__ == "__main__":
    unittest.main()
