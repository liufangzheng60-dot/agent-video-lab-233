"""Tests for local material inventory generation."""

from __future__ import annotations

import json
import tempfile
import unittest
from pathlib import Path
from unittest.mock import patch

from helpers.inventory import PRODUCT_ASSET_BUCKETS, SOURCE_BUCKETS, run_inventory


class InventoryTests(unittest.TestCase):
    def setUp(self) -> None:
        self.temp_dir = tempfile.TemporaryDirectory()
        self.project_root = Path(self.temp_dir.name)
        for bucket in SOURCE_BUCKETS:
            (self.project_root / "inputs" / bucket).mkdir(parents=True, exist_ok=True)

    def tearDown(self) -> None:
        self.temp_dir.cleanup()

    @patch("helpers.inventory.which", return_value=None)
    def test_empty_inputs_generate_json_and_markdown(self, _mock_which: object) -> None:
        result = run_inventory(self.project_root)

        self.assertTrue(result["json_path"].exists())
        self.assertTrue(result["markdown_path"].exists())
        self.assertEqual(result["inventory"]["file_count"], 0)
        self.assertEqual(result["inventory"]["files"], [])
        self.assertIn("当前没有素材", result["markdown_path"].read_text(encoding="utf-8"))

    @patch("helpers.inventory.which", return_value=None)
    def test_regular_file_records_name_extension_size_and_bucket(self, _mock_which: object) -> None:
        file_path = self.project_root / "inputs" / "product_briefs" / "brief.md"
        file_path.write_text("hello", encoding="utf-8")

        result = run_inventory(self.project_root)
        data = json.loads(result["json_path"].read_text(encoding="utf-8"))
        item = data["files"][0]

        self.assertEqual(data["file_count"], 1)
        self.assertEqual(item["file_name"], "brief.md")
        self.assertEqual(item["extension"], ".md")
        self.assertEqual(item["file_size_bytes"], 5)
        self.assertEqual(item["source_bucket"], "product_briefs")
        self.assertEqual(item["material_type"], "document")

    @patch("helpers.inventory.which", return_value=None)
    def test_ffprobe_is_not_required_for_basic_inventory(self, _mock_which: object) -> None:
        file_path = self.project_root / "inputs" / "raw_videos" / "clip.mp4"
        file_path.write_bytes(b"not a real video")

        result = run_inventory(self.project_root)
        item = result["inventory"]["files"][0]

        self.assertIsNone(item["duration_seconds"])
        self.assertIsNone(item["width"])
        self.assertIsNone(item["height"])
        self.assertIsNone(item["has_audio"])
        self.assertIn("ffprobe_unavailable", item["risk_flags"])

    @patch("helpers.inventory.which", return_value=None)
    def test_legacy_inventory_output_path_remains_default(self, _mock_which: object) -> None:
        result = run_inventory(self.project_root)

        self.assertEqual(result["json_path"], self.project_root / "outputs" / "material_inventory" / "material_inventory.json")
        self.assertEqual(
            result["markdown_path"],
            self.project_root / "outputs" / "material_inventory" / "material_inventory.md",
        )

    @patch("helpers.inventory.which", return_value=None)
    def test_product_inventory_writes_to_product_outputs(self, _mock_which: object) -> None:
        product_root = self.project_root / "products" / "pet_nail_trimmer"
        assets_root = product_root / "assets"
        output_dir = product_root / "outputs" / "material_inventory"
        for bucket in PRODUCT_ASSET_BUCKETS:
            (assets_root / bucket).mkdir(parents=True, exist_ok=True)
        script_path = assets_root / "scripts" / "script.txt"
        script_path.write_text("short product script", encoding="utf-8")

        result = run_inventory(
            project_root=self.project_root / "03_tk_video_agent",
            input_root=assets_root,
            output_dir=output_dir,
            source_buckets=PRODUCT_ASSET_BUCKETS,
            report_root=product_root,
        )
        item = result["inventory"]["files"][0]

        self.assertEqual(result["json_path"], output_dir / "material_inventory.json")
        self.assertEqual(result["markdown_path"], output_dir / "material_inventory.md")
        self.assertEqual(result["inventory"]["input_root"], "assets")
        self.assertEqual(item["relative_path"], "assets/scripts/script.txt")
        self.assertEqual(item["source_bucket"], "scripts")
        self.assertEqual(item["material_type"], "document")


if __name__ == "__main__":
    unittest.main()
