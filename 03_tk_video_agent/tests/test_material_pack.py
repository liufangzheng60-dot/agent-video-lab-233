"""Tests for material pack generation."""

from __future__ import annotations

import json
import tempfile
import unittest
from pathlib import Path

from helpers.build_material_pack import run_material_pack


class MaterialPackTests(unittest.TestCase):
    def setUp(self) -> None:
        self.temp_dir = tempfile.TemporaryDirectory()
        self.project_root = Path(self.temp_dir.name)
        (self.project_root / "outputs" / "material_inventory").mkdir(parents=True, exist_ok=True)
        (self.project_root / "inputs" / "product_briefs").mkdir(parents=True, exist_ok=True)

    def tearDown(self) -> None:
        self.temp_dir.cleanup()

    def write_inventory(self) -> None:
        inventory = {
            "generated_at": "2026-05-20T00:00:00+00:00",
            "input_root": "inputs",
            "file_count": 3,
            "files": [
                {
                    "file_name": "clip.mp4",
                    "relative_path": "inputs/raw_videos/clip.mp4",
                    "material_type": "video",
                    "extension": ".mp4",
                    "file_size_bytes": 100,
                    "source_bucket": "raw_videos",
                    "duration_seconds": 38.566667,
                    "width": 720,
                    "height": 960,
                    "has_audio": True,
                    "risk_flags": [],
                    "notes": [],
                },
                {
                    "file_name": "product.jpg",
                    "relative_path": "inputs/product_images/product.jpg",
                    "material_type": "image",
                    "extension": ".jpg",
                    "file_size_bytes": 200,
                    "source_bucket": "product_images",
                    "duration_seconds": None,
                    "width": None,
                    "height": None,
                    "has_audio": None,
                    "risk_flags": [],
                    "notes": [],
                },
                {
                    "file_name": "brief.txt",
                    "relative_path": "inputs/product_briefs/brief.txt",
                    "material_type": "document",
                    "extension": ".txt",
                    "file_size_bytes": 50,
                    "source_bucket": "product_briefs",
                    "duration_seconds": None,
                    "width": None,
                    "height": None,
                    "has_audio": None,
                    "risk_flags": [],
                    "notes": [],
                },
            ],
        }
        inventory_path = self.project_root / "outputs" / "material_inventory" / "material_inventory.json"
        inventory_path.write_text(json.dumps(inventory), encoding="utf-8")

    def test_generates_material_pack_from_inventory(self) -> None:
        self.write_inventory()
        (self.project_root / "inputs" / "product_briefs" / "brief.txt").write_text("Quiet pet trimmer script", encoding="utf-8")

        result = run_material_pack(self.project_root)

        self.assertTrue(result["json_path"].exists())
        self.assertTrue(result["markdown_path"].exists())
        self.assertEqual(result["material_pack"]["material_count"], 3)

    def test_reads_product_brief_documents(self) -> None:
        self.write_inventory()
        (self.project_root / "inputs" / "product_briefs" / "brief.md").write_text("# Product\nGentle trimming", encoding="utf-8")

        result = run_material_pack(self.project_root)
        briefs = result["material_pack"]["product_briefs"]

        self.assertEqual(len(briefs), 1)
        self.assertIn("Gentle trimming", briefs[0]["content"])
        self.assertIn("Gentle trimming", briefs[0]["summary"])

    def test_marks_720x960_video_as_not_9_16(self) -> None:
        self.write_inventory()

        result = run_material_pack(self.project_root)
        video = next(item for item in result["material_pack"]["materials"] if item["material_type"] == "video")

        self.assertEqual(video["suggested_role"], "demo_or_source_clip")
        self.assertIn("aspect_ratio_not_9_16", video["risk_flags"])
        self.assertIn("aspect_ratio_not_9_16", result["material_pack"]["risk_flags"])

    def test_no_external_api_dependency(self) -> None:
        self.write_inventory()

        result = run_material_pack(self.project_root)

        self.assertEqual(result["material_pack"]["inventory_source"], "outputs/material_inventory/material_inventory.json")


if __name__ == "__main__":
    unittest.main()
