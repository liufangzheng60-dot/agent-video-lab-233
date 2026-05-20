"""Tests for timeline generation."""

from __future__ import annotations

import csv
import json
import tempfile
import unittest
from pathlib import Path

from helpers.generate_timeline import run_timeline


class TimelineTests(unittest.TestCase):
    def setUp(self) -> None:
        self.temp_dir = tempfile.TemporaryDirectory()
        self.project_root = Path(self.temp_dir.name)
        (self.project_root / "outputs" / "edit_strategy").mkdir(parents=True, exist_ok=True)
        (self.project_root / "outputs" / "material_pack").mkdir(parents=True, exist_ok=True)
        self.write_inputs()

    def tearDown(self) -> None:
        self.temp_dir.cleanup()

    def write_inputs(self) -> None:
        edit_strategy = {
            "generated_at": "2026-05-20T00:00:00+00:00",
            "source_material_pack": "outputs/material_pack/material_pack.json",
            "video_goal": "Create a 7-15 second TikTok product short.",
            "target_duration_seconds": {"min": 7, "max": 15},
            "strategy_segments": [
                self.segment("hook", "product_brief_or_script", "inputs/product_briefs/brief.txt"),
                self.segment("problem", "demo_or_source_clip", "inputs/raw_videos/clip.mp4"),
                self.segment("demo", "demo_or_source_clip", "inputs/raw_videos/clip.mp4"),
                self.segment("proof", "product_reference_image", "inputs/product_images/product.jpg"),
                self.segment("cta", "product_brief_or_script", "inputs/product_briefs/brief.txt"),
            ],
            "material_usage": [],
            "risk_flags": ["aspect_ratio_not_9_16", "needs_9_16_crop_or_rebuild"],
            "missing_materials": [],
            "next_step": "Generate timeline.",
        }
        material_pack = {
            "generated_at": "2026-05-20T00:00:00+00:00",
            "material_count": 3,
            "materials": [],
            "missing_materials": [],
            "risk_flags": ["aspect_ratio_not_9_16"],
        }
        (self.project_root / "outputs" / "edit_strategy" / "edit_strategy.json").write_text(json.dumps(edit_strategy), encoding="utf-8")
        (self.project_root / "outputs" / "material_pack" / "material_pack.json").write_text(json.dumps(material_pack), encoding="utf-8")

    def segment(self, name: str, role: str, material: str) -> dict[str, object]:
        return {
            "segment_name": name,
            "purpose": f"{name} purpose",
            "target_duration": "0-2s",
            "recommended_material_role": role,
            "caption_direction": f"{name} caption",
            "execution_note": f"{name} note",
            "available_materials": [material],
        }

    def test_generates_timeline_json_from_edit_strategy(self) -> None:
        result = run_timeline(self.project_root)

        self.assertTrue(result["json_path"].exists())
        self.assertEqual(result["timeline"]["source_edit_strategy"], "outputs/edit_strategy/edit_strategy.json")

    def test_generates_capcut_timeline_csv(self) -> None:
        result = run_timeline(self.project_root)

        self.assertTrue(result["csv_path"].exists())
        with result["csv_path"].open("r", encoding="utf-8-sig", newline="") as file:
            rows = list(csv.DictReader(file))
        self.assertEqual(rows[0]["segment_name"], "hook")
        self.assertIn("editing_note", rows[0])

    def test_timeline_contains_required_segments(self) -> None:
        result = run_timeline(self.project_root)
        names = [segment["segment_name"] for segment in result["timeline"]["segments"]]

        self.assertEqual(names, ["hook", "problem", "demo", "proof", "cta"])

    def test_total_duration_is_between_7_and_15_seconds(self) -> None:
        result = run_timeline(self.project_root)
        total = result["timeline"]["target_duration_seconds"]

        self.assertGreaterEqual(total, 7)
        self.assertLessEqual(total, 15)

    def test_non_9_16_risk_is_preserved(self) -> None:
        result = run_timeline(self.project_root)
        timeline = result["timeline"]
        video_segments = [segment for segment in timeline["segments"] if segment["source_material"].endswith(".mp4")]

        self.assertIn("needs_9_16_crop_or_rebuild", timeline["risk_flags"])
        self.assertTrue(any("needs_9_16_crop_or_rebuild" in segment["risk_flags"] for segment in video_segments))

    def test_no_external_api_dependency(self) -> None:
        result = run_timeline(self.project_root)

        self.assertIn("No video editing", result["timeline"]["notes"][1])


if __name__ == "__main__":
    unittest.main()
