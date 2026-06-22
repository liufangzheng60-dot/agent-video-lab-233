import hashlib
import json
import unittest

from helpers.zhipu_vlm_adapter import (
    ZHIPU_BASE_URL,
    ZHIPU_MODEL,
    ZHIPU_PROVIDER,
    ZHIPU_SINGLE_KEY_SOURCE_INVARIANT,
    inspect_zhipu_environment,
    verify_zai_key_fingerprint,
)


class SingleZhipuKeySourceTests(unittest.TestCase):
    def test_only_zai_api_key_is_selected_without_value_output(self):
        env = {"ZAI_API_KEY": "test-zai-key-value"}
        report = inspect_zhipu_environment(env)

        self.assertTrue(report["api_key_available"])
        self.assertEqual(report["python_key_status"]["selected_env_var"], "ZAI_API_KEY")
        self.assertEqual(report["python_key_status"]["ZAI_API_KEY"]["length"], len(env["ZAI_API_KEY"]))
        self.assertFalse(report["python_key_status"]["ZAI_API_KEY"]["value_logged"])
        self.assertNotIn(env["ZAI_API_KEY"], json.dumps(report))

    def test_legacy_zhipuai_key_alone_is_not_used(self):
        report = inspect_zhipu_environment({"ZHIPUAI_API_KEY": "legacy-only-key"})

        self.assertFalse(report["api_key_available"])
        self.assertIsNone(report["python_key_status"]["selected_env_var"])
        self.assertNotIn("legacy-only-key", json.dumps(report))

    def test_legacy_zhipu_key_alone_is_not_used(self):
        report = inspect_zhipu_environment({"ZHIPU_API_KEY": "legacy-only-key"})

        self.assertFalse(report["api_key_available"])
        self.assertIsNone(report["python_key_status"]["selected_env_var"])
        self.assertNotIn("legacy-only-key", json.dumps(report))

    def test_conflicting_variables_still_select_only_zai_api_key(self):
        env = {
            "ZAI_API_KEY": "official-key",
            "ZHIPUAI_API_KEY": "legacy-key",
            "ZHIPU_API_KEY": "older-key",
        }
        report = inspect_zhipu_environment(env)

        self.assertTrue(report["api_key_available"])
        self.assertEqual(report["python_key_status"]["selected_env_var"], "ZAI_API_KEY")
        self.assertFalse(report["python_key_status"]["credential_fallback"])
        self.assertNotIn("legacy-key", json.dumps(report))
        self.assertNotIn("older-key", json.dumps(report))

    def test_no_key_fails_without_fallback(self):
        report = inspect_zhipu_environment({})

        self.assertFalse(report["api_key_available"])
        self.assertIsNone(report["python_key_status"]["selected_env_var"])
        self.assertFalse(report["python_key_status"]["credential_fallback"])

    def test_provider_model_and_base_url_are_fixed(self):
        self.assertEqual(ZHIPU_PROVIDER, "zhipu")
        self.assertEqual(ZHIPU_MODEL, "glm-4.6v")
        self.assertEqual(ZHIPU_BASE_URL, "https://open.bigmodel.cn/api/paas/v4/")
        self.assertEqual(ZHIPU_SINGLE_KEY_SOURCE_INVARIANT["key_source"], "ZAI_API_KEY")
        self.assertFalse(ZHIPU_SINGLE_KEY_SOURCE_INVARIANT["credential_fallback"])
        self.assertFalse(ZHIPU_SINGLE_KEY_SOURCE_INVARIANT["provider_fallback"])
        self.assertFalse(ZHIPU_SINGLE_KEY_SOURCE_INVARIANT["model_fallback"])

    def test_fingerprint_match_and_mismatch_are_redacted(self):
        key = "test-fingerprint-key"
        fingerprint = hashlib.sha256(key.encode("utf-8")).hexdigest()

        matched = verify_zai_key_fingerprint({"ZAI_API_KEY": key, "ZAI_KEY_FINGERPRINT_EXPECTED": fingerprint})
        mismatched = verify_zai_key_fingerprint({"ZAI_API_KEY": key, "ZAI_KEY_FINGERPRINT_EXPECTED": "0" * 64})

        self.assertTrue(matched["fingerprint_matches"])
        self.assertFalse(mismatched["fingerprint_matches"])
        self.assertFalse(matched["secret_value_logged"])
        self.assertNotIn(key, json.dumps(matched))
        self.assertNotIn(key, json.dumps(mismatched))


if __name__ == "__main__":
    unittest.main()
