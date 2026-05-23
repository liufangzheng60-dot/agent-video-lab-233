"""Tests for control console, project journal, and scenario keyword templates."""

from __future__ import annotations

import unittest
from pathlib import Path


REPO_ROOT = Path(__file__).resolve().parents[2]


class ControlConsoleStructureTests(unittest.TestCase):
    def test_control_console_core_files_exist(self) -> None:
        for name in (
            "00_MASTER_CONTROL.md",
            "01_ACTIVE_SPRINT.md",
            "02_MODEL_ROLE_CONTRACTS.md",
            "03_DATA_FIREWALL_POLICY.md",
            "04_MODULE_REGISTRY.yaml",
            "05_DECISION_LOG.md",
            "06_DO_NOT_TOUCH.md",
            "07_NEXT_ACTION_QUEUE.md",
        ):
            self.assertTrue((REPO_ROOT / "control_console" / name).exists(), name)

    def test_project_journal_core_directories_exist(self) -> None:
        for name in ("build_log", "decisions", "errors", "changelog"):
            self.assertTrue((REPO_ROOT / "project_journal" / name).is_dir(), name)
            self.assertTrue((REPO_ROOT / "project_journal" / name / "README.md").exists(), name)

    def test_scenario_keyword_mining_core_files_exist(self) -> None:
        for name in (
            "README.md",
            "dog_bath_hose_scene_keywords.md",
            "dog_bath_hose_hook_hypotheses.csv",
        ):
            self.assertTrue((REPO_ROOT / "scenario_keyword_mining" / name).exists(), name)

    def test_module_registry_exists(self) -> None:
        self.assertTrue((REPO_ROOT / "control_console" / "04_MODULE_REGISTRY.yaml").exists())

    def test_no_external_api_dependency(self) -> None:
        content = (REPO_ROOT / "scenario_keyword_mining" / "README.md").read_text(encoding="utf-8")
        self.assertIn("Do not copy reference video captions", content)


if __name__ == "__main__":
    unittest.main()
