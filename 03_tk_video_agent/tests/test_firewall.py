"""Tests for standalone code-level firewall helpers."""

from __future__ import annotations

import tempfile
import unittest
from pathlib import Path

from helpers.firewall import (
    FirewallViolation,
    FirewallViolationError,
    assert_allowed_write_path,
    assert_do_not_touch_path,
    generate_firewall_violation_report,
    generate_preflight_report,
    run_firewall_check,
    validate_experiment_path,
    validate_product_path,
)


class FirewallTests(unittest.TestCase):
    def setUp(self) -> None:
        self.temp_dir = tempfile.TemporaryDirectory()
        self.repo_root = Path(self.temp_dir.name)

    def tearDown(self) -> None:
        self.temp_dir.cleanup()

    def test_product_can_write_to_own_outputs(self) -> None:
        path = self.repo_root / "products" / "dog_bath_hose" / "outputs" / "renders" / "final.mp4"

        result = validate_product_path(self.repo_root, "dog_bath_hose", path)
        allowed = assert_allowed_write_path(self.repo_root, path, [self.repo_root / "products" / "dog_bath_hose" / "outputs"])

        self.assertEqual(result, path)
        self.assertEqual(allowed, path)

    def test_real_product_output_path_is_allowed(self) -> None:
        path = self.repo_root / "products" / "dog_bath_hose" / "outputs" / "test.md"

        result = assert_allowed_write_path(self.repo_root, path, [self.repo_root / "products" / "dog_bath_hose" / "outputs"])

        self.assertEqual(result, path)

    def test_product_cannot_write_to_other_product(self) -> None:
        path = self.repo_root / "products" / "pet_nail_trimmer" / "outputs" / "renders" / "final.mp4"

        with self.assertRaises(FirewallViolationError) as error:
            validate_product_path(self.repo_root, "dog_bath_hose", path)

        self.assertEqual(error.exception.violation.rule, "product_path_scope")

    def test_other_product_output_path_is_denied_for_active_product(self) -> None:
        path = self.repo_root / "products" / "pet_nail_trimmer" / "outputs" / "test.md"

        with self.assertRaises(FirewallViolationError) as error:
            validate_product_path(self.repo_root, "dog_bath_hose", path)

        self.assertEqual(error.exception.violation.rule, "product_path_scope")

    def test_product_path_traversal_to_other_product_is_denied(self) -> None:
        path = self.repo_root / "products" / "dog_bath_hose" / ".." / "pet_nail_trimmer" / "outputs" / "test.md"

        with self.assertRaises(FirewallViolationError) as error:
            validate_product_path(self.repo_root, "dog_bath_hose", path)

        self.assertEqual(error.exception.violation.rule, "product_path_scope")

    def test_outside_repo_absolute_path_is_denied(self) -> None:
        path = self.repo_root.parent / "outside.md"

        with self.assertRaises(FirewallViolationError) as error:
            assert_do_not_touch_path(self.repo_root, path)

        self.assertEqual(error.exception.violation.rule, "outside_repo_root")

    def test_control_console_is_protected(self) -> None:
        path = self.repo_root / "control_console" / "00_MASTER_CONTROL.md"

        with self.assertRaises(FirewallViolationError) as error:
            assert_do_not_touch_path(self.repo_root, path)

        self.assertEqual(error.exception.violation.rule, "do_not_touch_path")

    def test_real_product_assets_path_is_denied(self) -> None:
        path = self.repo_root / "products" / "dog_bath_hose" / "assets" / "raw_videos" / "test.mp4"

        with self.assertRaises(FirewallViolationError) as error:
            assert_do_not_touch_path(self.repo_root, path)

        self.assertEqual(error.exception.violation.rule, "do_not_touch_product_assets")

    def test_real_product_brief_path_is_denied(self) -> None:
        path = self.repo_root / "products" / "dog_bath_hose" / "product_brief.md"

        with self.assertRaises(FirewallViolationError) as error:
            assert_do_not_touch_path(self.repo_root, path)

        self.assertEqual(error.exception.violation.rule, "do_not_touch_product_brief")

    def test_product_root_write_is_denied_by_allowlist(self) -> None:
        path = self.repo_root / "products" / "dog_bath_hose" / "test.md"

        with self.assertRaises(FirewallViolationError) as error:
            assert_allowed_write_path(self.repo_root, path, [self.repo_root / "products" / "dog_bath_hose" / "outputs"])

        self.assertEqual(error.exception.violation.rule, "allowed_write_path")

    def test_experiment_can_write_to_own_batch(self) -> None:
        path = self.repo_root / "experiments" / "dog_bath_hose" / "blue" / "batch_20260520_v001_v005" / "01_variants.csv"

        result = validate_experiment_path(self.repo_root, "dog_bath_hose", "blue", "batch_20260520_v001_v005", path)

        self.assertEqual(result, path)

    def test_experiment_cannot_write_to_other_batch(self) -> None:
        path = self.repo_root / "experiments" / "dog_bath_hose" / "blue" / "batch_20260521_v006_v010" / "01_variants.csv"

        with self.assertRaises(FirewallViolationError) as error:
            validate_experiment_path(self.repo_root, "dog_bath_hose", "blue", "batch_20260520_v001_v005", path)

        self.assertEqual(error.exception.violation.rule, "experiment_batch_scope")

    def test_violation_report_can_be_generated(self) -> None:
        violation = FirewallViolation(
            path="control_console/00_MASTER_CONTROL.md",
            rule="do_not_touch_path",
            reason="control console is protected",
            suggested_action="request user approval",
        )

        report_path = generate_firewall_violation_report(self.repo_root, violation)

        self.assertTrue(report_path.exists())
        self.assertIn("control_console/00_MASTER_CONTROL.md", report_path.read_text(encoding="utf-8"))

    def test_preflight_report_can_be_generated(self) -> None:
        result = generate_preflight_report(self.repo_root, "dog_bath_hose", "blue", "batch_20260520_v001_v005")

        self.assertTrue(result["report_path"].exists())
        content = result["report_path"].read_text(encoding="utf-8")
        self.assertIn("products/dog_bath_hose/outputs", content)
        self.assertIn("Preflight-only", content)

    def test_relative_repo_root_still_validates_correctly(self) -> None:
        with tempfile.TemporaryDirectory(dir=Path.cwd()) as temp_dir:
            absolute_root = Path(temp_dir).resolve()
            relative_root = absolute_root.relative_to(Path.cwd())
            path = Path("products") / "dog_bath_hose" / "outputs" / "test.md"
            result = validate_product_path(relative_root, "dog_bath_hose", path)

        self.assertEqual(result, absolute_root / "products" / "dog_bath_hose" / "outputs" / "test.md")

    def test_firewall_check_generates_preflight_without_business_flow(self) -> None:
        result = run_firewall_check(self.repo_root, "dog_bath_hose", "blue", "batch_20260520_v001_v005")

        self.assertEqual(result["status"], "pass")
        self.assertTrue(result["preflight_report"].exists())

    def test_old_business_command_registration_is_unchanged(self) -> None:
        main_py = Path(__file__).resolve().parents[1] / "main.py"
        content = main_py.read_text(encoding="utf-8")

        for command in ("inventory", "material-pack", "edit-strategy", "timeline", "render", "subtitles", "batch-variants"):
            self.assertIn(command, content)

    def test_no_external_api_dependency(self) -> None:
        path = self.repo_root / "products" / "dog_bath_hose" / "assets" / "raw_videos" / "source.mp4"

        with self.assertRaises(FirewallViolationError) as error:
            assert_do_not_touch_path(self.repo_root, path)

        self.assertEqual(error.exception.violation.rule, "do_not_touch_product_assets")


if __name__ == "__main__":
    unittest.main()
