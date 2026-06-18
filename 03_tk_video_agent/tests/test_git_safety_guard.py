import subprocess
import tempfile
import unittest
from pathlib import Path

from helpers.git_safety_guard import is_prohibited_path, run_git_safety_guard


class GitSafetyGuardTests(unittest.TestCase):
    def test_path_patterns_block_media_outputs_raw_and_env(self):
        blocked = [
            "products/dog_stairs_v1/outputs/x.json",
            "products/dog_stairs_v1/inputs/raw_videos/batch/a.mp4",
            "clip.mov",
            "image.jpg",
            "sound.wav",
            "sheet.xlsx",
            ".env",
        ]
        for path in blocked:
            self.assertTrue(is_prohibited_path(path), path)
        self.assertFalse(is_prohibited_path("03_tk_video_agent/helpers/agent_state.py"))

    def test_staged_media_is_reported(self):
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            subprocess.run(["git", "init"], cwd=root, check=True, capture_output=True)
            (root / "video.mp4").write_text("fake", encoding="utf-8")
            subprocess.run(["git", "add", "video.mp4"], cwd=root, check=True, capture_output=True)
            report = run_git_safety_guard(root)
            self.assertEqual(report["status"], "fail")
            self.assertEqual(report["prohibited_staged_files"], ["video.mp4"])


if __name__ == "__main__":
    unittest.main()
