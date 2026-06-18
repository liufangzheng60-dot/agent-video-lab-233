import subprocess
import unittest
from pathlib import Path


class GitignoreHygieneTests(unittest.TestCase):
    def setUp(self):
        self.repo_root = Path(__file__).resolve().parents[2]
        self.gitignore = self.repo_root / ".gitignore"
        self.text = self.gitignore.read_text(encoding="utf-8")

    def test_required_patterns_exist(self):
        self.assertTrue(self.gitignore.exists())
        required = [
            "products/*/outputs/",
            "products/*/inputs/raw_videos/",
            "*.mp4",
            "*.jpg",
            "*.wav",
            ".env",
        ]
        for pattern in required:
            self.assertIn(pattern, self.text)

    def test_env_example_is_not_blocked_by_gitignore(self):
        self.assertIn("!.env.example", self.text)
        self.assertIn("!**/.env.example", self.text)
        result = subprocess.run(
            ["git", "check-ignore", "03_tk_video_agent/.env.example"],
            cwd=self.repo_root,
            capture_output=True,
            text=True,
            check=False,
        )
        self.assertNotEqual(result.returncode, 0, result.stdout + result.stderr)

    def test_docs_do_not_contain_obvious_real_api_key(self):
        docs_root = self.repo_root / "03_tk_video_agent" / "docs"
        suspicious_markers = ["AI" + "za", "sk" + "-", "ghp" + "_", "xoxb" + "-"]
        for path in docs_root.rglob("*.md"):
            text = path.read_text(encoding="utf-8", errors="ignore")
            for marker in suspicious_markers:
                self.assertNotIn(marker, text, f"{marker} found in {path}")


if __name__ == "__main__":
    unittest.main()
