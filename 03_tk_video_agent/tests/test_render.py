"""Tests for minimal render workflow."""

from __future__ import annotations

import json
import tempfile
import unittest
from pathlib import Path
from unittest.mock import patch

from helpers.render import parse_video_source_materials, read_timeline, run_render, write_render_report


class RenderTests(unittest.TestCase):
    def setUp(self) -> None:
        self.temp_dir = tempfile.TemporaryDirectory()
        self.project_root = Path(self.temp_dir.name)
        (self.project_root / "outputs" / "timelines").mkdir(parents=True, exist_ok=True)
        (self.project_root / "outputs" / "material_pack").mkdir(parents=True, exist_ok=True)
        (self.project_root / "inputs" / "raw_videos").mkdir(parents=True, exist_ok=True)
        self.write_inputs()

    def tearDown(self) -> None:
        self.temp_dir.cleanup()

    def write_inputs(self) -> None:
        timeline = {
            "generated_at": "2026-05-20T00:00:00+00:00",
            "source_edit_strategy": "outputs/edit_strategy/edit_strategy.json",
            "source_material_pack": "outputs/material_pack/material_pack.json",
            "target_duration_seconds": 15.0,
            "segments": [
                {
                    "start": 0.0,
                    "end": 2.0,
                    "duration": 2.0,
                    "segment_name": "hook",
                    "purpose": "hook",
                    "source_material": "inputs/product_briefs/brief.txt",
                    "caption": "hook caption",
                    "editing_note": "hook note",
                    "risk_flags": [],
                },
                {
                    "start": 2.0,
                    "end": 7.0,
                    "duration": 5.0,
                    "segment_name": "demo",
                    "purpose": "demo",
                    "source_material": "inputs/raw_videos/clip.mp4",
                    "caption": "demo caption",
                    "editing_note": "demo note",
                    "risk_flags": ["aspect_ratio_not_9_16", "needs_9_16_crop_or_rebuild"],
                },
            ],
            "missing_materials": [],
            "risk_flags": ["aspect_ratio_not_9_16", "needs_9_16_crop_or_rebuild"],
        }
        material_pack = {
            "generated_at": "2026-05-20T00:00:00+00:00",
            "risk_flags": ["aspect_ratio_not_9_16"],
            "missing_materials": [],
        }
        (self.project_root / "outputs" / "timelines" / "timeline.json").write_text(json.dumps(timeline), encoding="utf-8")
        (self.project_root / "outputs" / "material_pack" / "material_pack.json").write_text(json.dumps(material_pack), encoding="utf-8")
        (self.project_root / "inputs" / "raw_videos" / "clip.mp4").write_bytes(b"fake video")

    @patch("helpers.render.which", return_value=None)
    def test_ffmpeg_missing_writes_clear_failure_report(self, _mock_which: object) -> None:
        result = run_render(self.project_root)

        self.assertFalse(result["success"])
        self.assertTrue(result["report_path"].exists())
        self.assertIn("ffmpeg was not found", result["report"]["message"])
        self.assertIn("ffmpeg was not found", result["report_path"].read_text(encoding="utf-8"))

    @patch("helpers.render.which", return_value=None)
    def test_legacy_render_output_path_remains_default(self, _mock_which: object) -> None:
        result = run_render(self.project_root)

        self.assertEqual(result["final_path"], self.project_root / "outputs" / "renders" / "final.mp4")
        self.assertEqual(result["report_path"], self.project_root / "outputs" / "renders" / "render_report.md")

    @patch("helpers.render.which", return_value=None)
    def test_product_render_paths_write_to_product_outputs(self, _mock_which: object) -> None:
        product_root = self.project_root / "products" / "pet_nail_trimmer"
        timeline_dir = product_root / "outputs" / "timelines"
        pack_dir = product_root / "outputs" / "material_pack"
        output_dir = product_root / "outputs" / "renders"
        raw_video_dir = product_root / "assets" / "raw_videos"
        timeline_dir.mkdir(parents=True, exist_ok=True)
        pack_dir.mkdir(parents=True, exist_ok=True)
        raw_video_dir.mkdir(parents=True, exist_ok=True)
        timeline = read_timeline(self.project_root / "outputs" / "timelines" / "timeline.json")
        timeline["segments"][1]["source_material"] = "assets/raw_videos/clip.mp4"
        timeline["source_material_pack"] = "outputs/material_pack/material_pack.json"
        (timeline_dir / "timeline.json").write_text(json.dumps(timeline), encoding="utf-8")
        (pack_dir / "material_pack.json").write_text(
            (self.project_root / "outputs" / "material_pack" / "material_pack.json").read_text(encoding="utf-8"),
            encoding="utf-8",
        )
        (raw_video_dir / "clip.mp4").write_bytes(b"fake video")

        result = run_render(
            project_root=self.project_root / "03_tk_video_agent",
            timeline_path=timeline_dir / "timeline.json",
            material_pack_path=pack_dir / "material_pack.json",
            output_dir=output_dir,
            media_root=product_root,
            report_root=product_root,
        )

        self.assertEqual(result["final_path"], output_dir / "final.mp4")
        self.assertEqual(result["report_path"], output_dir / "render_report.md")
        self.assertTrue(result["report_path"].exists())
        self.assertEqual(result["report"]["timeline_path"], "outputs/timelines/timeline.json")
        self.assertEqual(result["report"]["output_path"], "outputs/renders/final.mp4")

    def test_can_read_timeline_json(self) -> None:
        timeline = read_timeline(self.project_root / "outputs" / "timelines" / "timeline.json")

        self.assertEqual(timeline["target_duration_seconds"], 15.0)
        self.assertEqual(timeline["segments"][1]["segment_name"], "demo")

    def test_can_parse_video_source_material(self) -> None:
        timeline = read_timeline(self.project_root / "outputs" / "timelines" / "timeline.json")
        sources = parse_video_source_materials(timeline)

        self.assertEqual(sources, ["inputs/raw_videos/clip.mp4"])

    def test_render_report_generation_is_testable(self) -> None:
        report_path = self.project_root / "outputs" / "renders" / "render_report.md"
        report_path.parent.mkdir(parents=True, exist_ok=True)
        report = {
            "generated_at": "2026-05-20T00:00:00+00:00",
            "status": "failed",
            "timeline_path": "outputs/timelines/timeline.json",
            "material_pack_path": "outputs/material_pack/material_pack.json",
            "output_path": "outputs/renders/final.mp4",
            "total_duration_seconds": 15.0,
            "source_materials": ["inputs/raw_videos/clip.mp4"],
            "risk_flags": ["needs_9_16_crop_or_rebuild"],
            "ffmpeg_found": False,
            "ffmpeg_command_summary": "",
            "message": "test message",
        }

        write_render_report(report_path, report)

        content = report_path.read_text(encoding="utf-8")
        self.assertIn("Render Report", content)
        self.assertIn("needs_9_16_crop_or_rebuild", content)

    def test_no_external_api_dependency(self) -> None:
        timeline = read_timeline(self.project_root / "outputs" / "timelines" / "timeline.json")

        self.assertIn("risk_flags", timeline)


if __name__ == "__main__":
    unittest.main()
