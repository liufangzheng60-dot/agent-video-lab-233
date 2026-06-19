import unittest

from helpers.market_output_contract import (
    build_audio_metadata_manifest,
    contains_cjk_characters,
    default_us_market_contract,
    validate_tts_preflight,
)


class MarketOutputContractTests(unittest.TestCase):
    def test_edge_unavailable_blocks_variant_without_sapi_fallback(self):
        result = validate_tts_preflight(
            script_text="Stable steps for everyday sofa moments.",
            selected_voice="en-US-AvaNeural",
            installed_status={"provider_available": False, "version": None},
        )
        self.assertEqual(result["preflight_result"], "fail")
        self.assertEqual(result["audio_status"], "blocked")
        self.assertEqual(result["variant_status"], "hold")
        self.assertFalse(result["allow_windows_sapi_fallback"])

    def test_cjk_in_english_script_fails(self):
        self.assertTrue(contains_cjk_characters("Stable steps 给小狗使用"))
        result = validate_tts_preflight(
            script_text="Stable steps 给小狗使用",
            selected_voice="en-US-AvaNeural",
            installed_status={"provider_available": True, "version": "test"},
        )
        self.assertIn("script_contains_cjk_characters", result["failures"])

    def test_en_us_voice_required(self):
        result = validate_tts_preflight(
            script_text="Stable steps for everyday sofa moments.",
            selected_voice="zh-CN-XiaoxiaoNeural",
            installed_status={"provider_available": True, "version": "test"},
        )
        self.assertIn("voice_not_whitelisted", result["failures"])
        self.assertIn("voice_locale_not_en_us", result["failures"])

    def test_provider_voice_locale_written_to_audio_manifest(self):
        manifest = build_audio_metadata_manifest(
            audio_duration_ms=1200,
            codec="mp3",
            sample_rate=24000,
            channels=1,
            voice="en-US-AvaNeural",
            contract=default_us_market_contract(),
        )
        self.assertEqual(manifest["provider"], "edge-tts")
        self.assertEqual(manifest["voice"], "en-US-AvaNeural")
        self.assertEqual(manifest["locale"], "en-US")
        self.assertFalse(manifest["allow_windows_sapi_fallback"])


if __name__ == "__main__":
    unittest.main()
