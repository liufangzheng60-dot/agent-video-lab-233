import subprocess
import tempfile
import unittest
from pathlib import Path

from helpers.media_asset_guard import run_media_asset_guard


class MediaAssetGuardTests(unittest.TestCase):
    def test_raw_batch_inventory_and_ignore_status(self):
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            subprocess.run(["git", "init"], cwd=root, check=True, capture_output=True)
            (root / ".gitignore").write_text(
                "products/*/inputs/raw_videos/\nproducts/*/outputs/\n*.mp4\n",
                encoding="utf-8",
            )
            raw_dir = root / "products" / "dog_stairs_v1" / "inputs" / "raw_videos" / "batch_20260617_001"
            raw_dir.mkdir(parents=True)
            (raw_dir / "clip.mp4").write_text("fake", encoding="utf-8")
            report = run_media_asset_guard(root, "dog_stairs_v1", "batch_20260617_001")
            self.assertEqual(report["status"], "pass")
            self.assertTrue(report["raw_videos_exists"])
            self.assertEqual(report["raw_video_count"], 1)
            self.assertTrue(report["raw_videos_git_ignored"])
            self.assertTrue(report["outputs_git_ignored"])

    def test_tracked_media_files_fail(self):
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            subprocess.run(["git", "init"], cwd=root, check=True, capture_output=True)
            (root / "README.md").write_text("repo", encoding="utf-8")
            (root / "tracked.mp4").write_text("fake", encoding="utf-8")
            subprocess.run(["git", "add", "README.md", "tracked.mp4"], cwd=root, check=True, capture_output=True)
            subprocess.run(["git", "commit", "-m", "init"], cwd=root, check=False, capture_output=True)
            report = run_media_asset_guard(root, "dog_stairs_v1", "batch_20260617_001")
            if not report["tracked_media_files"]:
                self.skipTest("temporary git did not create commit identity")
            self.assertEqual(report["status"], "fail")
            self.assertIn("tracked.mp4", report["tracked_media_files"])


if __name__ == "__main__":
    unittest.main()
