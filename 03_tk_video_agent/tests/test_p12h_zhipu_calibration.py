import unittest

from helpers.zhipu_vlm_adapter import (
    ZHIPU_BASE_URL,
    ZHIPU_MODEL,
    ZHIPU_PROVIDER,
    ZhipuCalibrationConfig,
    build_calibration_request_plan,
    build_package_compatibility_report,
    inspect_zai_sdk,
)


class P12HZhipuCalibrationTests(unittest.TestCase):
    def sample(self, idx=1, input_type="keyframe_strip"):
        return {
            "sample_type": f"sample_{idx}",
            "clip_id": f"clip_{idx:03d}",
            "asset_hash": f"hash_{idx}",
            "start_ms": 0,
            "end_ms": 2500,
            "input_type": input_type,
            "media_resolution": "keyframe_strip_low_resolution",
            "proxy_version": "p12h_v1",
        }

    def test_config_fixed_to_zhipu_glm46v(self):
        config = ZhipuCalibrationConfig()
        self.assertEqual(config.provider, ZHIPU_PROVIDER)
        self.assertEqual(config.model, ZHIPU_MODEL)
        self.assertEqual(config.base_url, ZHIPU_BASE_URL)
        self.assertFalse(config.upload_audio)
        self.assertFalse(config.stream)
        self.assertFalse(config.do_sample)
        self.assertEqual(config.thinking_type, "disabled")

    def test_request_plan_caps_successful_calls_to_three(self):
        samples = [self.sample(i) for i in range(1, 6)]
        plan = build_calibration_request_plan(samples)
        self.assertEqual(plan["planned_request_count"], 3)
        self.assertEqual(plan["max_successful_calibration_calls"], 3)
        self.assertEqual(plan["max_total_request_attempts"], 6)
        self.assertFalse(plan["real_api_called"])

    def test_cache_key_includes_provider_and_model(self):
        plan = build_calibration_request_plan([self.sample(1)])
        request = plan["requests"][0]
        self.assertEqual(request["provider"], "zhipu")
        self.assertEqual(request["model"], "glm-4.6v")
        self.assertEqual(len(request["cache_key"]), 64)

    def test_package_unknown_blocks_real_calibration(self):
        report = build_package_compatibility_report()
        self.assertFalse(report["can_run_real_calibration"])
        self.assertIn("unknown_owner_console_check_required", report["glm_4_6v_included"])
        self.assertTrue(report["blockers"])

    def test_zai_sdk_is_importable_after_install(self):
        status = inspect_zai_sdk()
        self.assertTrue(status["installed"])
        self.assertTrue(status["client_importable"])


if __name__ == "__main__":
    unittest.main()
