"""Tests for batch-based raw material manifest generation."""

from __future__ import annotations

import csv
import json
import tempfile
import unittest
from pathlib import Path
from unittest.mock import patch

from helpers.material_batch import (
    MANIFEST_FIELDS,
    TAGS_TEMPLATE_FIELDS,
    compute_sha256,
    infer_orientation,
    path_is_supported_video,
    run_material_batch,
)


class MaterialBatchTests(unittest.TestCase):
    def setUp(self) -> None:
        self.temp_dir = tempfile.TemporaryDirectory()
        self.repo_root = Path(self.temp_dir.name) / "repo"
        self.batch_dir = self.repo_root / "products" / "dog_stairs_v1" / "assets" / "raw_videos" / "batch_20260615_001"
        self.batch_dir.mkdir(parents=True, exist_ok=True)

    def tearDown(self) -> None:
        self.temp_dir.cleanup()

    @patch("helpers.material_batch.which", return_value=None)
    def test_missing_input_dir_is_created_and_empty_outputs_are_written(self, _mock_which: object) -> None:
        repo_root = Path(self.temp_dir.name) / "repo_two"

        result = run_material_batch(repo_root, "dog_stairs_v1", "khaki", "batch_20260615_001")

        self.assertTrue(result["input_dir"].exists())
        self.assertEqual(result["clips"], [])
        self.assertTrue(result["manifest_csv_path"].exists())
        self.assertTrue(result["manifest_json_path"].exists())
        self.assertTrue(result["clip_tags_template_path"].exists())
        self.assertIn("no_video_files_found", result["report"]["warnings"])

    @patch("helpers.material_batch.which", return_value=None)
    def test_non_video_files_and_gitkeep_are_ignored(self, _mock_which: object) -> None:
        (self.batch_dir / ".gitkeep").write_text("", encoding="utf-8")
        (self.batch_dir / "notes.txt").write_text("x", encoding="utf-8")
        (self.batch_dir / "clip.mp4").write_bytes(b"video bytes")

        result = run_material_batch(self.repo_root, "dog_stairs_v1", "khaki", "batch_20260615_001")

        self.assertEqual(len(result["clips"]), 1)
        self.assertEqual(result["clips"][0]["original_filename"], "clip.mp4")

    @patch("helpers.material_batch.which", return_value=None)
    def test_stable_clip_ids_follow_sorted_filenames(self, _mock_which: object) -> None:
        (self.batch_dir / "zeta.MOV").write_bytes(b"a")
        (self.batch_dir / "alpha.mp4").write_bytes(b"b")

        result = run_material_batch(self.repo_root, "dog_stairs_v1", "khaki", "batch_20260615_001")
        clip_ids = [item["clip_id"] for item in result["clips"]]
        filenames = [item["original_filename"] for item in result["clips"]]

        self.assertEqual(filenames, ["alpha.mp4", "zeta.MOV"])
        self.assertEqual(clip_ids[0], "DOG_STAIRS_V1_KHAKI_B20260615_001_C001")
        self.assertEqual(clip_ids[1], "DOG_STAIRS_V1_KHAKI_B20260615_001_C002")

    def test_checksum_matches_file_content(self) -> None:
        path = self.batch_dir / "clip.mp4"
        path.write_bytes(b"abc123")

        self.assertEqual(
            compute_sha256(path),
            "6ca13d52ca70c883e0f0bb101e425a89e8624de51db2d2392593af6a84118090",
        )

    @patch("helpers.material_batch.which", return_value="ffprobe")
    @patch("helpers.material_batch.subprocess.run")
    def test_ffprobe_metadata_populates_manifest_fields(self, mock_run: object, _mock_which: object) -> None:
        (self.batch_dir / "clip.mp4").write_bytes(b"video bytes")
        mock_run.return_value.stdout = json.dumps(
            {
                "format": {"duration": "12.5"},
                "streams": [
                    {"codec_type": "video", "width": 720, "height": 1280, "r_frame_rate": "30000/1001"},
                    {"codec_type": "audio"},
                ],
            }
        )
        mock_run.return_value.returncode = 0

        result = run_material_batch(self.repo_root, "dog_stairs_v1", "khaki", "batch_20260615_001")
        clip = result["clips"][0]

        self.assertEqual(clip["duration_sec"], "12.5")
        self.assertEqual(clip["width"], "720")
        self.assertEqual(clip["height"], "1280")
        self.assertEqual(clip["fps"], "29.97")
        self.assertEqual(clip["has_audio"], "true")
        self.assertEqual(clip["orientation"], "vertical")

    @patch("helpers.material_batch.which", return_value="ffprobe")
    @patch("helpers.material_batch.subprocess.run", side_effect=RuntimeError("boom"))
    def test_ffprobe_failure_does_not_crash(self, _mock_run: object, _mock_which: object) -> None:
        (self.batch_dir / "clip.mp4").write_bytes(b"video bytes")

        result = run_material_batch(self.repo_root, "dog_stairs_v1", "khaki", "batch_20260615_001")
        clip = result["clips"][0]

        self.assertEqual(clip["duration_sec"], "NA")
        self.assertEqual(clip["has_audio"], "NA")
        self.assertTrue(clip["notes"].startswith("ffprobe_failed"))

    @patch("helpers.material_batch.which", return_value=None)
    def test_manifest_and_tag_template_fields_are_complete(self, _mock_which: object) -> None:
        (self.batch_dir / "clip.mp4").write_bytes(b"video bytes")

        result = run_material_batch(self.repo_root, "dog_stairs_v1", "khaki", "batch_20260615_001")

        with result["manifest_csv_path"].open("r", encoding="utf-8-sig", newline="") as file:
            manifest_reader = csv.DictReader(file)
            self.assertEqual(manifest_reader.fieldnames, MANIFEST_FIELDS)
            manifest_row = next(manifest_reader)
        with result["clip_tags_template_path"].open("r", encoding="utf-8-sig", newline="") as file:
            tags_reader = csv.DictReader(file)
            self.assertEqual(tags_reader.fieldnames, TAGS_TEMPLATE_FIELDS)
            tags_row = next(tags_reader)

        self.assertEqual(manifest_row["analysis_status"], "untagged")
        self.assertEqual(manifest_row["source_bucket"], "raw_videos_batch")
        self.assertEqual(tags_row["usable_start_sec"], "0")
        self.assertEqual(tags_row["hook_candidate"], "false")
        self.assertEqual(tags_row["demo_candidate"], "false")
        self.assertEqual(tags_row["proof_candidate"], "false")
        self.assertEqual(tags_row["cta_candidate"], "false")

    def test_supported_video_detection_and_orientation_helpers(self) -> None:
        self.assertTrue(path_is_supported_video(Path("clip.MKV")))
        self.assertFalse(path_is_supported_video(Path(".gitkeep")))
        self.assertEqual(infer_orientation("100", "100"), "square")
        self.assertEqual(infer_orientation("200", "100"), "horizontal")
        self.assertEqual(infer_orientation("NA", "100"), "unknown")


if __name__ == "__main__":
    unittest.main()
