"""Minimal Zhipu GLM-4.6V calibration adapter for P12H.

The adapter is deliberately narrow. It does not run Golden Pilot, does not
upload raw videos or audio, and refuses real requests when API-key or package
confirmation gates are not satisfied.
"""

from __future__ import annotations

import importlib.metadata
import hashlib
import json
import os
from dataclasses import asdict, dataclass
from pathlib import Path
from typing import Any, Mapping

from helpers.agent_state import utc_now_iso
from helpers.vlm_qc_gate import SEMANTIC_LABEL_SCHEMA_VERSION, build_semantic_vlm_cache_key


ZHIPU_PROVIDER = "zhipu"
ZHIPU_MODEL = "glm-4.6v"
ZHIPU_BASE_URL = "https://open.bigmodel.cn/api/paas/v4/"
ZAI_KEY_ENV_VAR = "ZAI_API_KEY"
ZAI_KEY_FINGERPRINT_ENV_VAR = "ZAI_KEY_FINGERPRINT_EXPECTED"
ZHIPU_SINGLE_KEY_SOURCE_INVARIANT = {
    "provider": ZHIPU_PROVIDER,
    "model": ZHIPU_MODEL,
    "key_source": ZAI_KEY_ENV_VAR,
    "base_url": ZHIPU_BASE_URL,
    "credential_fallback": False,
    "model_fallback": False,
    "provider_fallback": False,
}


@dataclass(frozen=True)
class ZhipuCalibrationConfig:
    provider: str = ZHIPU_PROVIDER
    model: str = ZHIPU_MODEL
    base_url: str = ZHIPU_BASE_URL
    upload_audio: bool = False
    cache_enabled: bool = True
    request_timeout_sec: int = 180
    max_retry_per_request: int = 1
    max_successful_calibration_calls: int = 3
    max_total_request_attempts: int = 6
    stream: bool = False
    do_sample: bool = False
    thinking_type: str = "disabled"

    def to_dict(self) -> dict[str, Any]:
        return asdict(self)


def inspect_zhipu_environment(env: Mapping[str, str] | None = None) -> dict[str, Any]:
    active_env = os.environ if env is None else env
    zai_key = active_env.get(ZAI_KEY_ENV_VAR) or ""
    return {
        "python_key_status": {
            ZAI_KEY_ENV_VAR: _key_status(zai_key),
            "selected_env_var": ZAI_KEY_ENV_VAR if zai_key else None,
            "credential_fallback": False,
        },
        "sdk_status": inspect_zai_sdk(),
        "legacy_zhipuai_status": inspect_legacy_zhipuai(),
        "single_key_source_invariant": ZHIPU_SINGLE_KEY_SOURCE_INVARIANT,
        "api_key_available": bool(zai_key),
    }


def verify_zai_key_fingerprint(env: Mapping[str, str] | None = None) -> dict[str, Any]:
    active_env = os.environ if env is None else env
    key = active_env.get(ZAI_KEY_ENV_VAR) or ""
    expected = active_env.get(ZAI_KEY_FINGERPRINT_ENV_VAR) or ""
    actual = hashlib.sha256(key.encode("utf-8")).hexdigest() if key else ""
    return {
        "zai_api_key_exists": bool(key),
        "zai_api_key_length": len(key),
        "expected_fingerprint_exists": bool(expected),
        "fingerprint_matches": bool(key and expected and actual == expected.lower()),
        "secret_value_logged": False,
    }


def inspect_zai_sdk() -> dict[str, Any]:
    try:
        version = importlib.metadata.version("zai-sdk")
    except importlib.metadata.PackageNotFoundError:
        return {"name": "zai-sdk", "installed": False, "version": None, "client_importable": False}
    try:
        from zai import ZhipuAiClient  # noqa: F401

        importable = True
    except Exception:
        importable = False
    return {"name": "zai-sdk", "installed": True, "version": version, "client_importable": importable}


def inspect_legacy_zhipuai() -> dict[str, Any]:
    try:
        version = importlib.metadata.version("zhipuai")
    except importlib.metadata.PackageNotFoundError:
        return {"name": "zhipuai", "installed": False, "version": None}
    return {"name": "zhipuai", "installed": True, "version": version}


def build_package_compatibility_report() -> dict[str, Any]:
    unknown = "unknown_owner_console_check_required"
    return {
        "resource_pack_name": unknown,
        "supported_models": unknown,
        "glm_4_6v_included": unknown,
        "api_calls_included": unknown,
        "image_tokens_included": unknown,
        "video_tokens_included": unknown,
        "input_tokens_included": unknown,
        "output_tokens_included": unknown,
        "package_expiration": unknown,
        "package_tokens_before": unknown,
        "concurrency_limit": unknown,
        "qps_limit": unknown,
        "package_overage_behavior": unknown,
        "cash_charge_possible": unknown,
        "can_run_real_calibration": False,
        "blockers": [
            "无法从本地环境确认 glm-4.6v 是否被资源包覆盖。",
            "无法确认图片 Token、视频 Token、输入/输出 Token 是否抵扣资源包。",
            "无法确认套餐外现金扣费风险是否被阻断。",
        ],
        "required_owner_console_checks": [
            "确认资源包是否覆盖 glm-4.6v。",
            "确认图片和视频 Token 是否包含在资源包内。",
            "确认套餐外超额是否会产生现金扣费，以及是否可关闭。",
            "确认当前 API Key 对 glm-4.6v 有调用权限。",
        ],
    }


def build_calibration_request_plan(samples: list[dict[str, Any]], config: ZhipuCalibrationConfig | None = None) -> dict[str, Any]:
    active = config or ZhipuCalibrationConfig()
    selected = samples[: active.max_successful_calibration_calls]
    requests = []
    for index, sample in enumerate(selected, start=1):
        media_resolution = sample.get("media_resolution", "keyframe_strip_low_resolution")
        cache_key = build_semantic_vlm_cache_key(
            asset_hash=str(sample["asset_hash"]),
            window_start_ms=int(sample["start_ms"]),
            window_end_ms=int(sample["end_ms"]),
            prompt_schema_version=SEMANTIC_LABEL_SCHEMA_VERSION,
            provider=active.provider,
            model=active.model,
            media_resolution=media_resolution,
            proxy_version=str(sample.get("proxy_version", "p12h_v1")),
        )
        requests.append({
            "request_id": f"p12h_calibration_{index:02d}",
            "sample_type": sample["sample_type"],
            "clip_id": sample["clip_id"],
            "start_ms": sample["start_ms"],
            "end_ms": sample["end_ms"],
            "input_type": sample["input_type"],
            "media_resolution": media_resolution,
            "upload_audio": False,
            "cache_key": cache_key,
            "provider": active.provider,
            "model": active.model,
        })
    return {
        "config": active.to_dict(),
        "max_successful_calibration_calls": active.max_successful_calibration_calls,
        "max_total_request_attempts": active.max_total_request_attempts,
        "planned_request_count": len(requests),
        "requests": requests,
        "real_api_called": False,
    }


def atomic_write_json(path: Path | str, payload: dict[str, Any]) -> Path:
    output = Path(path)
    output.parent.mkdir(parents=True, exist_ok=True)
    tmp = output.with_name(output.name + ".tmp")
    with tmp.open("w", encoding="utf-8") as handle:
        handle.write(json.dumps(payload, indent=2, ensure_ascii=False) + "\n")
        handle.flush()
        os.fsync(handle.fileno())
    os.replace(tmp, output)
    return output


def write_blocked_calibration_reports(output_dir: Path | str, *, env_report: dict[str, Any], package_report: dict[str, Any], request_plan: dict[str, Any], comet_audit: dict[str, Any]) -> dict[str, str]:
    out = Path(output_dir)
    out.mkdir(parents=True, exist_ok=True)
    capability = {
        "provider": ZHIPU_PROVIDER,
        "model": ZHIPU_MODEL,
        "base_url": ZHIPU_BASE_URL,
        "sdk": env_report["sdk_status"],
        "api_key_status": env_report["python_key_status"],
        "real_api_called": False,
        "blockers": [] if env_report["api_key_available"] else ["ZAI_API_KEY is missing; credential fallback is forbidden and real API calls remain stopped."],
        "created_at": utc_now_iso(),
    }
    results = {
        "status": "blocked_before_real_api",
        "successful_business_calls": 0,
        "total_request_attempts": 0,
        "image_calls": {"success": 0, "fail": 0},
        "video_calls": {"success": 0, "fail": 0},
        "schema_success_rate": 0.0,
        "real_api_called": False,
        "media_uploaded": False,
        "reason": "API Key 或资源包现金扣费门禁未满足。",
    }
    schema = {"status": "not_run", "schema_version": SEMANTIC_LABEL_SCHEMA_VERSION, "validated_samples": 0, "failures": []}
    token_cost = {
        "input_tokens": 0,
        "output_tokens": 0,
        "vision_tokens": 0,
        "video_tokens": 0,
        "resource_pack_deduction": "not_run",
        "cash_cost": 0,
        "cash_charge_possible": package_report["cash_charge_possible"],
    }
    cache = {"status": "planned_not_executed", "cache_enabled": True, "cache_hit_prevented_request": False, "real_charge_saved": 0}
    review = _review_markdown(env_report, package_report, request_plan, comet_audit)
    paths = {
        "zhipu_provider_capability_report": out / "zhipu_provider_capability_report.json",
        "zhipu_package_compatibility_report": out / "zhipu_package_compatibility_report.json",
        "zhipu_calibration_requests": out / "zhipu_calibration_requests.json",
        "zhipu_calibration_results": out / "zhipu_calibration_results.json",
        "zhipu_schema_validation_report": out / "zhipu_schema_validation_report.json",
        "zhipu_token_cost_report": out / "zhipu_token_cost_report.json",
        "zhipu_cache_report": out / "zhipu_cache_report.json",
    }
    payloads = [capability, package_report, request_plan, results, schema, token_cost, cache]
    for path, payload in zip(paths.values(), payloads):
        atomic_write_json(path, payload)
    review_path = out / "zhipu_calibration_review.md"
    review_path.write_text(review, encoding="utf-8")
    paths["zhipu_calibration_review"] = review_path
    return {key: str(value) for key, value in paths.items()}


def _key_status(value: str) -> dict[str, Any]:
    if not value:
        return {"exists": False, "length": 0, "value_logged": False}
    return {"exists": True, "length": len(value), "value_logged": False}


def _review_markdown(env_report: dict[str, Any], package_report: dict[str, Any], request_plan: dict[str, Any], comet_audit: dict[str, Any]) -> str:
    lines = [
        "# P12H 智谱 GLM-4.6V Calibration 预审结果",
        "",
        "- 状态：真实 API 调用已被门禁阻止。",
        f"- SDK：{env_report['sdk_status']}",
        f"- API Key：{env_report['python_key_status']}",
        f"- 计划样本数量：{request_plan['planned_request_count']}",
        f"- Comet 审计：{comet_audit.get('status')}",
        "- 未上传完整原片、原片音频或高分辨率母文件。",
        "- 未产生真实 VLM 调用或现金费用。",
        "",
        "## 阻塞项",
    ]
    for blocker in package_report["blockers"]:
        lines.append(f"- {blocker}")
    if not env_report["api_key_available"]:
        lines.append("- 本机当前会话未设置 ZAI_API_KEY；凭证 fallback 已禁止。")
    return "\n".join(lines) + "\n"
