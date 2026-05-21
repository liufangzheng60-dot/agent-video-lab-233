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

    def test_legacy_material_pack_output_path_remains_default(self) -> None:
        self.write_inventory()

        result = run_material_pack(self.project_root)

        self.assertEqual(result["json_path"], self.project_root / "outputs" / "material_pack" / "material_pack.json")
        self.assertEqual(result["markdown_path"], self.project_root / "outputs" / "material_pack" / "material_pack.md")

    def test_product_material_pack_writes_to_product_outputs_and_reads_sources(self) -> None:
        product_root = self.project_root / "products" / "pet_nail_trimmer"
        inventory_dir = product_root / "outputs" / "material_inventory"
        output_dir = product_root / "outputs" / "material_pack"
        scripts_dir = product_root / "assets" / "scripts"
        inventory_dir.mkdir(parents=True, exist_ok=True)
        scripts_dir.mkdir(parents=True, exist_ok=True)
        inventory = {
            "generated_at": "2026-05-21T00:00:00+00:00",
            "input_root": "assets",
            "file_count": 1,
            "files": [
                {
                    "file_name": "script.txt",
                    "relative_path": "assets/scripts/script.txt",
                    "material_type": "document",
                    "extension": ".txt",
                    "file_size_bytes": 10,
                    "source_bucket": "scripts",
                    "duration_seconds": None,
                    "width": None,
                    "height": None,
                    "has_audio": None,
                    "risk_flags": [],
                    "notes": [],
                }
            ],
        }
        inventory_path = inventory_dir / "material_inventory.json"
        inventory_path.write_text(json.dumps(inventory), encoding="utf-8")
        (product_root / "product_brief.md").write_text("# Pet Nail Trimmer\nLED grooming angle", encoding="utf-8")
        (scripts_dir / "script.txt").write_text("Clip, smooth, done.", encoding="utf-8")

        result = run_material_pack(
            project_root=self.project_root / "03_tk_video_agent",
            inventory_path=inventory_path,
            brief_sources=[product_root / "product_brief.md", scripts_dir],
            output_dir=output_dir,
            report_root=product_root,
        )
        brief_paths = [brief["relative_path"] for brief in result["material_pack"]["product_briefs"]]
        material = result["material_pack"]["materials"][0]

        self.assertEqual(result["json_path"], output_dir / "material_pack.json")
        self.assertEqual(result["markdown_path"], output_dir / "material_pack.md")
        self.assertEqual(result["material_pack"]["inventory_source"], "outputs/material_inventory/material_inventory.json")
        self.assertIn("product_brief.md", brief_paths)
        self.assertIn("assets/scripts/script.txt", brief_paths)
        self.assertEqual(material["suggested_role"], "product_brief_or_script")


if __name__ == "__main__":
    unittest.main()
