"""Tests for edit strategy generation."""

from __future__ import annotations

import json
import tempfile
import unittest
from pathlib import Path

from helpers.generate_edit_strategy import run_edit_strategy


class EditStrategyTests(unittest.TestCase):
    def setUp(self) -> None:
        self.temp_dir = tempfile.TemporaryDirectory()
        self.project_root = Path(self.temp_dir.name)
        (self.project_root / "outputs" / "material_pack").mkdir(parents=True, exist_ok=True)
        self.write_material_pack()

    def tearDown(self) -> None:
        self.temp_dir.cleanup()

    def write_material_pack(self) -> None:
        material_pack = {
            "generated_at": "2026-05-20T00:00:00+00:00",
            "inventory_source": "outputs/material_inventory/material_inventory.json",
            "inventory_generated_at": "2026-05-20T00:00:00+00:00",
            "material_count": 3,
            "product_briefs": [
                {
                    "file_name": "brief.txt",
                    "relative_path": "inputs/product_briefs/brief.txt",
                    "extension": ".txt",
                    "content": "Stop paying $20+ for nail trims. LED clipper shows the quick.",
                    "summary": "Stop paying $20+ for nail trims. LED clipper shows the quick.",
                }
            ],
            "materials": [
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
                    "suggested_role": "demo_or_source_clip",
                    "risk_flags": ["aspect_ratio_not_9_16"],
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
                    "suggested_role": "product_reference_image",
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
                    "suggested_role": "product_brief_or_script",
                    "risk_flags": [],
                    "notes": [],
                },
            ],
            "missing_materials": [],
            "risk_flags": ["aspect_ratio_not_9_16"],
        }
        pack_path = self.project_root / "outputs" / "material_pack" / "material_pack.json"
        pack_path.write_text(json.dumps(material_pack), encoding="utf-8")

    def test_generates_edit_strategy_from_material_pack(self) -> None:
        result = run_edit_strategy(self.project_root)

        self.assertTrue(result["json_path"].exists())
        self.assertTrue(result["markdown_path"].exists())
        self.assertEqual(result["edit_strategy"]["source_material_pack"], "outputs/material_pack/material_pack.json")

    def test_output_contains_required_segments(self) -> None:
        result = run_edit_strategy(self.project_root)
        names = [segment["segment_name"] for segment in result["edit_strategy"]["strategy_segments"]]

        self.assertEqual(names, ["hook", "problem", "demo", "proof", "cta"])

    def test_non_9_16_risk_enters_risk_flags(self) -> None:
        result = run_edit_strategy(self.project_root)

        self.assertIn("aspect_ratio_not_9_16", result["edit_strategy"]["risk_flags"])
        self.assertIn("needs_9_16_crop_or_rebuild", result["edit_strategy"]["risk_flags"])

    def test_no_external_api_dependency(self) -> None:
        result = run_edit_strategy(self.project_root)

        self.assertEqual(result["edit_strategy"]["target_duration_seconds"], {"min": 7, "max": 15})

    def test_legacy_edit_strategy_output_path_remains_default(self) -> None:
        result = run_edit_strategy(self.project_root)

        self.assertEqual(result["json_path"], self.project_root / "outputs" / "edit_strategy" / "edit_strategy.json")
        self.assertEqual(result["markdown_path"], self.project_root / "outputs" / "edit_strategy" / "edit_strategy.md")

    def test_product_edit_strategy_writes_to_product_outputs(self) -> None:
        product_root = self.project_root / "products" / "pet_nail_trimmer"
        pack_dir = product_root / "outputs" / "material_pack"
        output_dir = product_root / "outputs" / "edit_strategy"
        pack_dir.mkdir(parents=True, exist_ok=True)
        pack_path = pack_dir / "material_pack.json"
        source_pack = json.loads((self.project_root / "outputs" / "material_pack" / "material_pack.json").read_text(encoding="utf-8"))
        source_pack["inventory_source"] = "outputs/material_inventory/material_inventory.json"
        pack_path.write_text(json.dumps(source_pack), encoding="utf-8")

        result = run_edit_strategy(
            project_root=self.project_root / "03_tk_video_agent",
            pack_path=pack_path,
            output_dir=output_dir,
            report_root=product_root,
        )

        self.assertEqual(result["json_path"], output_dir / "edit_strategy.json")
        self.assertEqual(result["markdown_path"], output_dir / "edit_strategy.md")
        self.assertEqual(result["edit_strategy"]["source_material_pack"], "outputs/material_pack/material_pack.json")


if __name__ == "__main__":
    unittest.main()
