"""Tests for contact sheet generation from clip manifests."""

from __future__ import annotations

import csv
import tempfile
import unittest
from pathlib import Path
from unittest.mock import patch

from helpers.contact_sheet import build_contact_sheet_command, run_contact_sheet


class ContactSheetTests(unittest.TestCase):
    def setUp(self) -> None:
        self.temp_dir = tempfile.TemporaryDirectory()
        self.repo_root = Path(self.temp_dir.name) / "repo"
        self.output_dir = self.repo_root / "products" / "dog_stairs_v1" / "outputs" / "material_batches" / "batch_20260615_001"
        self.output_dir.mkdir(parents=True, exist_ok=True)
        self.manifest_path = self.output_dir / "clip_manifest.csv"

    def tearDown(self) -> None:
        self.temp_dir.cleanup()

    def write_manifest(self, rows: list[dict[str, str]]) -> None:
        fieldnames = [
            "clip_id",
            "product_slug",
            "sku_slug",
            "material_batch_id",
            "original_filename",
            "relative_path",
            "absolute_path",
            "extension",
            "file_size_bytes",
            "checksum_sha256",
            "duration_sec",
            "width",
            "height",
            "fps",
            "has_audio",
            "orientation",
            "source_bucket",
            "created_at",
            "analysis_status",
            "notes",
        ]
        with self.manifest_path.open("w", encoding="utf-8-sig", newline="") as file:
            writer = csv.DictWriter(file, fieldnames=fieldnames)
            writer.writeheader()
            writer.writerows(rows)

    def test_manifest_missing_raises_clear_error(self) -> None:
        with self.assertRaises(FileNotFoundError):
            run_contact_sheet(self.repo_root, "dog_stairs_v1", "khaki", "batch_20260615_001")

    @patch("helpers.contact_sheet.which", return_value=None)
    def test_empty_manifest_generates_zero_contact_sheets_without_error(self, _mock_which: object) -> None:
        self.write_manifest([])

        result = run_contact_sheet(self.repo_root, "dog_stairs_v1", "khaki", "batch_20260615_001")

        self.assertEqual(result["report"]["total_manifest_clips"], 0)
        self.assertEqual(result["report"]["generated_contact_sheets"], 0)
        self.assertEqual(result["report"]["failed_contact_sheets"], 0)
        self.assertTrue(result["report_path"].exists())

    @patch("helpers.contact_sheet.which", return_value=None)
    def test_ffmpeg_missing_does_not_crash(self, _mock_which: object) -> None:
        source = self.repo_root / "products" / "dog_stairs_v1" / "assets" / "raw_videos" / "batch_20260615_001" / "clip.mp4"
        source.parent.mkdir(parents=True, exist_ok=True)
        source.write_bytes(b"x")
        self.write_manifest(
            [
                {
                    "clip_id": "DOG_STAIRS_V1_KHAKI_B20260615_001_C001",
                    "product_slug": "dog_stairs_v1",
                    "sku_slug": "khaki",
                    "material_batch_id": "batch_20260615_001",
                    "original_filename": "clip.mp4",
                    "relative_path": "products/dog_stairs_v1/assets/raw_videos/batch_20260615_001/clip.mp4",
                    "absolute_path": str(source.resolve()),
                    "extension": ".mp4",
                    "file_size_bytes": "1",
                    "checksum_sha256": "x",
                    "duration_sec": "10",
                    "width": "720",
                    "height": "1280",
                    "fps": "30",
                    "has_audio": "false",
                    "orientation": "vertical",
                    "source_bucket": "raw_videos_batch",
                    "created_at": "2026-06-15T00:00:00+00:00",
                    "analysis_status": "untagged",
                    "notes": "",
                }
            ]
        )

        result = run_contact_sheet(self.repo_root, "dog_stairs_v1", "khaki", "batch_20260615_001")

        self.assertFalse(result["report"]["ffmpeg_available"])
        self.assertEqual(result["report"]["generated_contact_sheets"], 0)
        self.assertEqual(result["report"]["failed_contact_sheets"], 1)
        self.assertIn("ffmpeg_unavailable", result["report"]["warnings"])

    @patch("helpers.contact_sheet.which", return_value="ffmpeg")
    @patch("helpers.contact_sheet.subprocess.run")
    def test_ffmpeg_failure_is_reported_without_crash(self, mock_run: object, _mock_which: object) -> None:
        source = self.repo_root / "products" / "dog_stairs_v1" / "assets" / "raw_videos" / "batch_20260615_001" / "clip.mp4"
        source.parent.mkdir(parents=True, exist_ok=True)
        source.write_bytes(b"x")
        self.write_manifest(
            [
                {
                    "clip_id": "DOG_STAIRS_V1_KHAKI_B20260615_001_C001",
                    "product_slug": "dog_stairs_v1",
                    "sku_slug": "khaki",
                    "material_batch_id": "batch_20260615_001",
                    "original_filename": "clip.mp4",
                    "relative_path": "products/dog_stairs_v1/assets/raw_videos/batch_20260615_001/clip.mp4",
                    "absolute_path": str(source.resolve()),
                    "extension": ".mp4",
                    "file_size_bytes": "1",
                    "checksum_sha256": "x",
                    "duration_sec": "10",
                    "width": "720",
                    "height": "1280",
                    "fps": "30",
                    "has_audio": "false",
                    "orientation": "vertical",
                    "source_bucket": "raw_videos_batch",
                    "created_at": "2026-06-15T00:00:00+00:00",
                    "analysis_status": "untagged",
                    "notes": "",
                }
            ]
        )
        mock_run.return_value.returncode = 1
        mock_run.return_value.stderr = "failed"

        result = run_contact_sheet(self.repo_root, "dog_stairs_v1", "khaki", "batch_20260615_001")

        self.assertEqual(result["report"]["generated_contact_sheets"], 0)
        self.assertEqual(result["report"]["failed_contact_sheets"], 1)
        self.assertIn("ffmpeg_failed:DOG_STAIRS_V1_KHAKI_B20260615_001_C001", result["report"]["warnings"])

    def test_build_contact_sheet_command_contains_tile_output(self) -> None:
        command = build_contact_sheet_command("ffmpeg", Path("input.mp4"), Path("out.jpg"), "12", frame_count=6)

        self.assertIn("tile=3x2", command[command.index("-vf") + 1])
        self.assertIn("fps=0.500000", command[command.index("-vf") + 1])


if __name__ == "__main__":
    unittest.main()
