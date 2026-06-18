import tempfile
import unittest
from pathlib import Path

from helpers.owner_firewall import evaluate_owner_firewall, run_owner_firewall, write_decision_template


class OwnerFirewallTests(unittest.TestCase):
    def test_supported_actions_pass_in_dry_run(self):
        result = evaluate_owner_firewall({"actions": [{"action": "force_rerun_variant", "variant_ids": ["V01"]}]}, dry_run=True)
        self.assertEqual(result["status"], "pass")
        self.assertTrue(result["dry_run"])

    def test_unknown_action_fails(self):
        result = evaluate_owner_firewall({"actions": [{"action": "publish_now"}]}, dry_run=True)
        self.assertEqual(result["status"], "fail")
        self.assertEqual(result["violations"][0]["error"], "unsupported_action")

    def test_run_owner_firewall_writes_audit_outputs(self):
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            decision_file = write_decision_template(root / "owner_firewall_decisions.template.json", 2)
            result = run_owner_firewall(
                decision_file,
                root / "owner_firewall_audit_log.md",
                root / "owner_firewall_result.json",
                product="dog_stairs_v1",
                sku="khaki",
                material_batch="batch_20260617_001",
                dry_run=True,
            )
            self.assertEqual(result["status"], "pass")
            self.assertTrue((root / "owner_firewall_audit_log.md").exists())
            self.assertTrue((root / "owner_firewall_result.json").exists())


if __name__ == "__main__":
    unittest.main()
