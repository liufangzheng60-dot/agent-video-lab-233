import unittest
from pathlib import Path


class P12AuditDocsExistTests(unittest.TestCase):
    def setUp(self):
        self.agent_root = Path(__file__).resolve().parents[1]

    def test_required_p12_audit_docs_exist(self):
        required = [
            "docs/p12_refactor_audit/CLI_CHAIN_REVERSE_AUDIT.md",
            "docs/p12_refactor_audit/HELPERS_REVERSE_AUDIT.md",
            "docs/p12_refactor_audit/RULES_REVERSE_AUDIT.md",
            "docs/p12_refactor_audit/00_EXECUTIVE_SUMMARY.md",
            "docs/p12_refactor_audit/01_HARD_RULES_INVENTORY.md",
            "docs/p12_refactor_audit/02_GENERAL_RULES_TO_OPTIMIZE.md",
            "docs/p12_refactor_audit/03_REDUNDANT_RULES_TO_DELETE_LATER.md",
            "docs/p12_refactor_audit/04_RUNTIME_FRICTION_REPORT.md",
            "docs/p12_refactor_audit/05_P12_AGENT_FACTORY_BLUEPRINT.md",
            "docs/p12_refactor_audit/06_VLM_QC_GATE_SPEC.md",
            "docs/p12_refactor_audit/07_AGENT_STATE_AND_FIREWALL_SPEC.md",
            "docs/p12_refactor_audit/08_GITHUB_SYNC_AND_LAPTOP_HANDOFF.md",
            "docs/P11_FINAL_STATUS_AND_LIMITATIONS.md",
        ]
        for relative in required:
            self.assertTrue((self.agent_root / relative).exists(), relative)


if __name__ == "__main__":
    unittest.main()
