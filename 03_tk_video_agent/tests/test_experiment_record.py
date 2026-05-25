"""Tests for manual experiment record ingestion and analysis."""

from __future__ import annotations

import csv
import tempfile
import unittest
from pathlib import Path

from helpers.experiment_record import analyze_record, parse_manual_input, run_experiment_record, upsert_performance_row


class ExperimentRecordTests(unittest.TestCase):
    def setUp(self) -> None:
        self.temp_dir = tempfile.TemporaryDirectory()
        self.repo_root = Path(self.temp_dir.name)
        self.batch_dir = self.repo_root / "experiments" / "dog_bath_hose" / "blue" / "batch_20260524_expression_style"
        (self.batch_dir / "manual_inputs").mkdir(parents=True)
        self.input_path = self.batch_dir / "manual_inputs" / "v003_12h_20260524.md"
        self.input_path.write_text(
            "\n".join(
                [
                    "video_id: v003_profanity_bleeped_shock",
                    "checkpoint: 12h",
                    "views: 2121",
                    "likes: 6",
                    "comments: NA",
                    "shares: NA",
                    "saves: NA",
                    "product_clicks: NA",
                    "orders: NA",
                    "revenue: NA",
                    "avg_watch_time: 3.3s",
                    "completion_rate: 2.89%",
                    "new_followers: 1",
                    "traffic_note: strong_inflection_at_10h_873_views_per_hour",
                    "comment_note: NA",
                    "issue_note: attention_positive_retention_negative",
                ]
            ),
            encoding="utf-8",
        )

    def tearDown(self) -> None:
        self.temp_dir.cleanup()

    def test_key_value_markdown_can_be_parsed(self) -> None:
        data = parse_manual_input(self.input_path)

        self.assertEqual(data["video_id"], "v003_profanity_bleeped_shock")
        self.assertEqual(data["checkpoint"], "12h")
        self.assertEqual(data["views"], "2121")

    def test_na_values_are_not_guessed(self) -> None:
        data = parse_manual_input(self.input_path)

        self.assertEqual(data["comments"], "NA")
        self.assertEqual(data["orders"], "NA")

    def test_performance_log_can_append(self) -> None:
        data = parse_manual_input(self.input_path)
        rows = upsert_performance_row(self.batch_dir / "02_performance_log.csv", data)

        self.assertEqual(len(rows), 1)
        self.assertEqual(rows[0]["video_id"], "v003_profanity_bleeped_shock")

    def test_same_video_and_checkpoint_updates_instead_of_duplicates(self) -> None:
        data = parse_manual_input(self.input_path)
        log_path = self.batch_dir / "02_performance_log.csv"
        upsert_performance_row(log_path, data)
        data["views"] = "3000"
        rows = upsert_performance_row(log_path, data)

        self.assertEqual(len(rows), 1)
        with log_path.open("r", encoding="utf-8-sig", newline="") as file:
            csv_rows = list(csv.DictReader(file))
        self.assertEqual(csv_rows[0]["views"], "3000")

    def test_analysis_report_is_generated(self) -> None:
        result = run_experiment_record(
            self.repo_root,
            "dog_bath_hose",
            "blue",
            "batch_20260524_expression_style",
            "manual_inputs/v003_12h_20260524.md",
        )

        self.assertTrue(result["analysis_path"].exists())
        self.assertIn("not_winner_yet", result["analysis_path"].read_text(encoding="utf-8"))

    def test_v003_current_data_signals_are_expected(self) -> None:
        analysis = analyze_record(parse_manual_input(self.input_path))

        self.assertEqual(analysis["attention_signal"], "positive")
        self.assertEqual(analysis["retention_signal"], "negative")
        self.assertEqual(analysis["completion_signal"], "weak")
        self.assertEqual(analysis["decision_status"], "not_winner_yet")

    def test_no_external_api_dependency(self) -> None:
        data = parse_manual_input(self.input_path)

        self.assertEqual(data["traffic_note"], "strong_inflection_at_10h_873_views_per_hour")


if __name__ == "__main__":
    unittest.main()
