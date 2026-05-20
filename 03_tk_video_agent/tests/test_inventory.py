"""Tests for local material inventory generation."""

from __future__ import annotations

import json
import tempfile
import unittest
from pathlib import Path
from unittest.mock import patch

from helpers.inventory import SOURCE_BUCKETS, run_inventory


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


if __name__ == "__main__":
    unittest.main()
