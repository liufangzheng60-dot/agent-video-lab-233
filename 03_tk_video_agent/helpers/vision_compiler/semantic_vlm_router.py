"""Zhipu GLM-4.6V semantic routing for P12W."""

from __future__ import annotations

import base64
import json
import os
import re
from pathlib import Path
from typing import Any


PROVIDER = "zhipu"
MODEL = "glm-4.6v"


def parse_json_response(text: str) -> dict[str, Any]:
    text = text.strip()
    try:
        return json.loads(text)
    except Exception:
        match = re.search(r"\{.*\}", text, flags=re.S)
        if match:
            try:
                return json.loads(match.group(0))
            except Exception:
                pass
    return {"parse_error": True, "raw_response": text}


def usage_dict(usage: Any) -> dict[str, Any]:
    if usage is None:
        return {}
    if hasattr(usage, "model_dump"):
        return usage.model_dump()
    if hasattr(usage, "dict"):
        return usage.dict()
    return dict(getattr(usage, "__dict__", {}))


class ZhipuRouter:
    def __init__(self, *, enabled: bool = True) -> None:
        self.enabled = enabled
        self.calls: list[dict[str, Any]] = []
        self.total_tokens = 0
        if enabled:
            api_key = os.environ.get("ZHIPU_API_KEY")
            if not api_key:
                raise RuntimeError("ZHIPU_API_KEY is required; no fallback env var is allowed")
            from zai import ZhipuAiClient

            self.client = ZhipuAiClient(api_key=api_key, timeout=180, max_retries=0)
        else:
            self.client = None

    def text_json(self, request_id: str, prompt: str, *, max_tokens: int = 900) -> dict[str, Any]:
        if not self.enabled:
            result = {"provider": PROVIDER, "requested_model": MODEL, "response_model": MODEL, "request_id": request_id, "parsed": {"offline": True}, "usage": {"total_tokens": 0}}
            self.calls.append(result)
            return result
        response = self.client.chat.completions.create(
            model=MODEL,
            request_id=request_id,
            messages=[{"role": "user", "content": prompt}],
            do_sample=False,
            stream=False,
            max_tokens=max_tokens,
            thinking={"type": "disabled"},
        )
        return self._record(request_id, response)

    def image_json(self, request_id: str, prompt: str, image_path: Path | str, *, max_tokens: int = 900) -> dict[str, Any]:
        if not self.enabled:
            result = {"provider": PROVIDER, "requested_model": MODEL, "response_model": MODEL, "request_id": request_id, "image": str(image_path), "parsed": {"offline": True}, "usage": {"total_tokens": 0}}
            self.calls.append(result)
            return result
        b64 = base64.b64encode(Path(image_path).read_bytes()).decode("ascii")
        response = self.client.chat.completions.create(
            model=MODEL,
            request_id=request_id,
            messages=[{"role": "user", "content": [{"type": "text", "text": prompt}, {"type": "image_url", "image_url": {"url": "data:image/jpeg;base64," + b64}}]}],
            do_sample=False,
            stream=False,
            max_tokens=max_tokens,
            thinking={"type": "disabled"},
        )
        result = self._record(request_id, response)
        result["image"] = str(image_path)
        return result

    def _record(self, request_id: str, response: Any) -> dict[str, Any]:
        response_model = getattr(response, "model", None)
        if response_model != MODEL:
            raise RuntimeError(f"Zhipu response model mismatch: {response_model}")
        content = response.choices[0].message.content
        usage = usage_dict(getattr(response, "usage", None))
        result = {
            "provider": PROVIDER,
            "requested_model": MODEL,
            "response_model": response_model,
            "request_id": request_id,
            "content": content,
            "parsed": parse_json_response(content),
            "usage": usage,
        }
        self.total_tokens += int(usage.get("total_tokens", 0) or 0)
        self.calls.append(result)
        return result
