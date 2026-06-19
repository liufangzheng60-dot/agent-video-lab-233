import subprocess
import tempfile
import unittest
from pathlib import Path

from helpers.phase_guard import ALLOW, BLOCK, OWNER_REVIEW_REQUIRED, evaluate_phase_action


class CodexProjectContractTests(unittest.TestCase):
    def setUp(self):
        self.repo_root = Path(__file__).resolve().parents[2]

    def test_agents_md_exists_and_contains_safety_lines(self):
        text = (self.repo_root / "AGENTS.md").read_text(encoding="utf-8")
        required = [
            "Project Mission",
            "Autonomous Authority",
            "Mandatory Owner Gates",
            "Owner Review Packet",
            "GPT Consultation Boundary",
            "Execution Loop",
            "Session Resume",
            "Single-Writer Data Isolation",
            "Videos, images, audio, raw videos",
            "TikTok 9:16 output rule",
            "Never use `git add .`",
        ]
        for item in required:
            self.assertIn(item, text)

    def test_ordinary_code_change_is_allowed(self):
        result = evaluate_phase_action({"type": "ordinary_code_change", "files": ["03_tk_video_agent/helpers/x.py"]})
        self.assertEqual(result["result"], ALLOW)

    def test_hard_rule_change_requires_owner_review(self):
        result = evaluate_phase_action({"type": "hard_rule_change", "rule": "HR_NO_AUTO_PUBLISH"})
        self.assertEqual(result["result"], OWNER_REVIEW_REQUIRED)
        self.assertEqual(result["checkpoint_type"], "GATE_HARD_RULE_CHANGE")

    def test_real_vlm_enablement_requires_owner_review(self):
        result = evaluate_phase_action({"type": "ordinary_code_change", "enable_real_vlm": True})
        self.assertEqual(result["result"], OWNER_REVIEW_REQUIRED)
        self.assertEqual(result["checkpoint_type"], "GATE_EXTERNAL_PROVIDER_ENABLE")

    def test_first_real_batch2_twelve_variant_launch_requires_owner_review(self):
        result = evaluate_phase_action({"type": "ordinary_code_change", "real_batch2": True, "variants": 12})
        self.assertEqual(result["result"], OWNER_REVIEW_REQUIRED)
        self.assertEqual(result["checkpoint_type"], "GATE_REAL_BATCH_LAUNCH")

    def test_first_real_twelve_video_generation_requires_owner_review(self):
        result = evaluate_phase_action({"type": "ordinary_code_change", "generate_real_videos": True, "variants": 12})
        self.assertEqual(result["result"], OWNER_REVIEW_REQUIRED)
        self.assertEqual(result["checkpoint_type"], "GATE_REAL_BATCH_LAUNCH")

    def test_staged_media_blocks(self):
        result = evaluate_phase_action({"type": "ordinary_code_change", "prohibited_staged_files": ["video.mp4"]})
        self.assertEqual(result["result"], BLOCK)

    def test_auto_publish_blocks(self):
        result = evaluate_phase_action({"type": "auto_publish"})
        self.assertEqual(result["result"], BLOCK)

    def test_raw_video_delete_blocks_but_quarantine_plan_allows(self):
        blocked = evaluate_phase_action({"type": "raw_video_delete"})
        allowed = evaluate_phase_action({"type": "ordinary_code_change", "quarantine_plan": True})
        self.assertEqual(blocked["result"], BLOCK)
        self.assertEqual(allowed["result"], ALLOW)

    def test_git_guard_reports_staged_media_as_block_input(self):
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            subprocess.run(["git", "init"], cwd=root, check=True, capture_output=True)
            (root / "video.mp4").write_text("fake", encoding="utf-8")
            subprocess.run(["git", "add", "video.mp4"], cwd=root, check=True, capture_output=True)
            staged = subprocess.run(["git", "diff", "--cached", "--name-only"], cwd=root, check=True, capture_output=True, text=True).stdout.strip()
            result = evaluate_phase_action({"type": "ordinary_code_change", "prohibited_staged_files": [staged]})
            self.assertEqual(result["result"], BLOCK)


if __name__ == "__main__":
    unittest.main()
