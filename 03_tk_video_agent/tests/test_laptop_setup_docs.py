import unittest
from pathlib import Path


class LaptopSetupDocsTests(unittest.TestCase):
    def setUp(self):
        self.agent_root = Path(__file__).resolve().parents[1]

    def test_laptop_scripts_and_docs_exist(self):
        required = [
            "scripts/setup_windows_laptop.ps1",
            "scripts/verify_laptop_env.ps1",
            "scripts/smoke_test_laptop.ps1",
            "docs/LAPTOP_SETUP_GUIDE.md",
            "docs/DESKTOP_TO_LAPTOP_HANDOFF_CHECKLIST.md",
            ".env.example",
        ]
        for relative in required:
            self.assertTrue((self.agent_root / relative).exists(), relative)

    def test_env_example_only_contains_placeholders(self):
        text = (self.agent_root / ".env.example").read_text(encoding="utf-8")
        self.assertIn("GEMINI_API_KEY=your_gemini_api_key_here", text)
        self.assertIn("DO_NOT_COMMIT_THIS_FILE=true", text)
        self.assertNotIn("AI" + "za", text)


if __name__ == "__main__":
    unittest.main()
