"""US market output contract and Edge-TTS preflight helpers for P12E."""

from __future__ import annotations

import importlib.metadata
import json
import re
from dataclasses import asdict, dataclass, field
from pathlib import Path
from typing import Any


EN_US_VOICE_WHITELIST = {
    "en-US-AvaNeural",
    "en-US-AndrewNeural",
    "en-US-JennyNeural",
    "en-US-GuyNeural",
    "en-US-EmmaNeural",
    "en-US-BrianNeural",
}


@dataclass(frozen=True)
class MarketOutputContract:
    market: str = "US"
    script_language: str = "en-US"
    spoken_language: str = "en-US"
    voice_locale: str = "en-US"
    subtitle_language: str = "en-US"
    fallback_to_system_default: bool = False
    allow_windows_sapi_fallback: bool = False
    allowed_voices: tuple[str, ...] = field(default_factory=lambda: tuple(sorted(EN_US_VOICE_WHITELIST)))

    def to_dict(self) -> dict[str, Any]:
        payload = asdict(self)
        payload["allowed_voices"] = list(self.allowed_voices)
        return payload


def default_us_market_contract() -> MarketOutputContract:
    return MarketOutputContract()


def contains_cjk_characters(text: str) -> bool:
    return bool(re.search(r"[\u3400-\u4dbf\u4e00-\u9fff\uf900-\ufaff]", text or ""))


def edge_tts_installation_status() -> dict[str, Any]:
    try:
        version = importlib.metadata.version("edge-tts")
    except importlib.metadata.PackageNotFoundError:
        return {"provider": "edge-tts", "provider_available": False, "version": None}
    return {"provider": "edge-tts", "provider_available": True, "version": version}


def validate_tts_preflight(
    *,
    script_text: str,
    selected_voice: str,
    contract: MarketOutputContract | None = None,
    installed_status: dict[str, Any] | None = None,
) -> dict[str, Any]:
    """Validate the commercial TTS contract without calling a network provider."""
    active_contract = contract or default_us_market_contract()
    status = installed_status or edge_tts_installation_status()
    cjk = contains_cjk_characters(script_text)
    voice_locale = selected_voice.split("-", 2)[0] + "-" + selected_voice.split("-", 2)[1] if selected_voice.count("-") >= 2 else "unknown"
    failures: list[str] = []
    if not status["provider_available"]:
        failures.append("edge_tts_unavailable")
    if selected_voice not in active_contract.allowed_voices:
        failures.append("voice_not_whitelisted")
    if voice_locale != active_contract.voice_locale:
        failures.append("voice_locale_not_en_us")
    if cjk:
        failures.append("script_contains_cjk_characters")
    if active_contract.fallback_to_system_default or active_contract.allow_windows_sapi_fallback:
        failures.append("fallback_must_be_disabled")
    return {
        "provider_available": status["provider_available"],
        "provider_version": status.get("version"),
        "selected_voice": selected_voice,
        "voice_locale": voice_locale,
        "script_locale": active_contract.script_language,
        "contains_cjk_characters": cjk,
        "fallback_disabled": not active_contract.fallback_to_system_default and not active_contract.allow_windows_sapi_fallback,
        "allow_windows_sapi_fallback": active_contract.allow_windows_sapi_fallback,
        "preflight_result": "pass" if not failures else "fail",
        "audio_status": "ready" if not failures else "blocked",
        "variant_status": "ready" if not failures else "hold",
        "failures": failures,
        "contract": active_contract.to_dict(),
    }


def build_audio_metadata_manifest(
    *,
    audio_duration_ms: int,
    codec: str,
    sample_rate: int,
    channels: int,
    voice: str,
    contract: MarketOutputContract | None = None,
) -> dict[str, Any]:
    active_contract = contract or default_us_market_contract()
    return {
        "audio_duration_ms": audio_duration_ms,
        "codec": codec,
        "sample_rate": sample_rate,
        "channels": channels,
        "provider": "edge-tts",
        "voice": voice,
        "locale": active_contract.voice_locale,
        "fallback_to_system_default": False,
        "allow_windows_sapi_fallback": False,
    }


def write_market_contract(path: Path | str, contract: MarketOutputContract | None = None) -> Path:
    output = Path(path)
    output.parent.mkdir(parents=True, exist_ok=True)
    output.write_text(json.dumps((contract or default_us_market_contract()).to_dict(), indent=2, ensure_ascii=False) + "\n", encoding="utf-8")
    return output
