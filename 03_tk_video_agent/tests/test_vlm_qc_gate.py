import os
import unittest

from helpers.vlm_qc_gate import VLM_QC_SCHEMA, audit_video_via_vlm, compress_to_qc_draft


class VlmQcGateTests(unittest.TestCase):
    def test_missing_key_returns_hold_without_api_call(self):
        old_value = os.environ.pop("GEMINI_API_KEY", None)
        try:
            result = audit_video_via_vlm("V01", "candidate.mp4", dry_run=True)
        finally:
            if old_value is not None:
                os.environ["GEMINI_API_KEY"] = old_value
        self.assertEqual(result["decision"], "hold")
        self.assertIn("missing_gemini_api_key", result["risk_flags"])
        self.assertEqual(set(VLM_QC_SCHEMA["required"]), set(result.keys()))

    def test_compress_to_qc_draft_is_dry_run_plan(self):
        plan = compress_to_qc_draft("source.mp4", "qc_draft.mp4")
        self.assertTrue(plan["dry_run"])
        self.assertEqual(plan["status"], "planned")


if __name__ == "__main__":
    unittest.main()
