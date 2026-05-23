"""Tests for manual experiment racing templates."""

from __future__ import annotations

import csv
import tempfile
import unittest
from pathlib import Path

from helpers.experiment_racing import PERFORMANCE_FIELDS, TEMPLATE_FILES, VARIANTS_FIELDS, run_experiment_init


class ExperimentRacingTests(unittest.TestCase):
    def setUp(self) -> None:
        self.temp_dir = tempfile.TemporaryDirectory()
        self.repo_root = Path(self.temp_dir.name)

    def tearDown(self) -> None:
        self.temp_dir.cleanup()

    def test_experiment_init_creates_isolated_product_sku_batch_directory(self) -> None:
        result = run_experiment_init(self.repo_root, "pet_nail_trimmer", "default_sku", "batch_20260520_v002_v006")

        self.assertEqual(
            result["batch_dir"],
            self.repo_root / "experiments" / "pet_nail_trimmer" / "default_sku" / "batch_20260520_v002_v006",
        )
        self.assertTrue(result["batch_dir"].exists())

    def test_all_five_template_files_exist(self) -> None:
        result = run_experiment_init(self.repo_root, "pet_nail_trimmer", "default_sku", "batch_20260520_v002_v006")

        for name in TEMPLATE_FILES:
            self.assertTrue((result["batch_dir"] / name).exists())

    def test_variants_csv_header_is_correct(self) -> None:
        result = run_experiment_init(self.repo_root, "pet_nail_trimmer", "default_sku", "batch_20260520_v002_v006")

        with (result["batch_dir"] / "01_variants.csv").open("r", encoding="utf-8-sig", newline="") as file:
            rows = list(csv.reader(file))
        self.assertEqual(rows[0], VARIANTS_FIELDS)

    def test_performance_log_csv_header_is_correct(self) -> None:
        result = run_experiment_init(self.repo_root, "pet_nail_trimmer", "default_sku", "batch_20260520_v002_v006")

        with (result["batch_dir"] / "02_performance_log.csv").open("r", encoding="utf-8-sig", newline="") as file:
            rows = list(csv.reader(file))
        self.assertEqual(rows[0], PERFORMANCE_FIELDS)

    def test_markdown_files_contain_manual_fill_instructions(self) -> None:
        result = run_experiment_init(self.repo_root, "pet_nail_trimmer", "default_sku", "batch_20260520_v002_v006")

        for name in ("00_batch_brief.md", "03_racing_decision.md", "04_next_iteration.md"):
            content = (result["batch_dir"] / name).read_text(encoding="utf-8")
            self.assertIn("填写说明", content)
            self.assertIn("NA", content)

    def test_no_external_api_dependency(self) -> None:
        result = run_experiment_init(self.repo_root, "pet_nail_trimmer", "default_sku", "batch_20260520_v002_v006")

        self.assertEqual(result["product_slug"], "pet_nail_trimmer")


if __name__ == "__main__":
    unittest.main()
