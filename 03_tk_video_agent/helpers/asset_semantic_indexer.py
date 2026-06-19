"""Deterministic P12E asset semantic indexing skeleton.

The indexer never writes into raw_videos and never physically cuts source media
while building candidate windows. Media proxies are represented as deterministic
plans unless a later owner-approved stage explicitly renders them into outputs.
"""

from __future__ import annotations

import hashlib
import json
from dataclasses import asdict, dataclass
from pathlib import Path
from typing import Any


DEFAULT_WINDOW_MS = 2500
MIN_WINDOW_MS = 1500
MAX_WINDOW_MS = 4000
MAX_WINDOWS_PER_CLIP = 8


@dataclass(frozen=True)
class CandidateWindow:
    clip_id: str
    source_path: str
    source_filename: str
    start_ms: int
    end_ms: int
    duration_ms: int
    scene_boundary_source: str
    source_width: int | None
    source_height: int | None
    source_orientation: str
    sample_aspect_ratio: str | None
    display_aspect_ratio: str | None
    safe_vertical_crop_candidate: bool
    content_hash: str
    proxy_path: str
    contact_sheet_path: str
    generation_reason: str
    risk_flags: tuple[str, ...]

    def to_dict(self) -> dict[str, Any]:
        payload = asdict(self)
        payload["risk_flags"] = list(self.risk_flags)
        return payload


def generate_candidate_windows(
    inventory_items: list[dict[str, Any]],
    output_dir: Path | str,
    *,
    max_windows_per_clip: int = MAX_WINDOWS_PER_CLIP,
) -> list[dict[str, Any]]:
    """Build deterministic candidate windows from inventory metadata."""
    out = Path(output_dir)
    windows: list[CandidateWindow] = []
    for item in sorted(inventory_items, key=lambda row: (str(row.get("filename", "")).lower(), str(row.get("absolute_path", "")).lower())):
        if item.get("probe_status") != "pass":
            continue
        duration_ms = max(0, int(round(float(item.get("duration_sec") or 0) * 1000)))
        if duration_ms <= 0:
            continue
        clip_windows = _windows_for_duration(duration_ms, max_windows_per_clip=max_windows_per_clip)
        for start_ms, end_ms, reason in clip_windows:
            content_hash = _stable_window_hash(item, start_ms, end_ms)
            proxy = out / "semantic_index" / "video_proxies" / f"{item['clip_id']}_{start_ms}_{end_ms}.mp4"
            contact = out / "semantic_index" / "contact_sheets" / f"{item['clip_id']}_{start_ms}_{end_ms}.jpg"
            width = _as_int(item.get("width"))
            height = _as_int(item.get("height"))
            safe_crop = bool(width and height and height > 0 and width > 0)
            risk_flags: list[str] = []
            if not safe_crop:
                risk_flags.append("missing_dimensions")
            windows.append(
                CandidateWindow(
                    clip_id=str(item["clip_id"]),
                    source_path=str(item["absolute_path"]),
                    source_filename=str(item["filename"]),
                    start_ms=start_ms,
                    end_ms=end_ms,
                    duration_ms=end_ms - start_ms,
                    scene_boundary_source="fixed_window補充" if reason == "fixed" else "scene_candidate",
                    source_width=width,
                    source_height=height,
                    source_orientation=str(item.get("orientation") or "unknown"),
                    sample_aspect_ratio=item.get("sample_aspect_ratio"),
                    display_aspect_ratio=item.get("display_aspect_ratio"),
                    safe_vertical_crop_candidate=safe_crop,
                    content_hash=content_hash,
                    proxy_path=str(proxy),
                    contact_sheet_path=str(contact),
                    generation_reason=reason,
                    risk_flags=tuple(risk_flags),
                )
            )
    return [window.to_dict() for window in windows]


def build_keyframe_strip_plan(window: dict[str, Any], output_dir: Path | str) -> dict[str, Any]:
    samples = _sample_times(window["start_ms"], window["end_ms"])
    output = Path(output_dir) / "semantic_index" / "contact_sheets" / f"{window['clip_id']}_{window['start_ms']}_{window['end_ms']}.jpg"
    return {
        "window_id": _window_id(window),
        "input_source_path": window["source_path"],
        "sample_times_ms": samples,
        "timestamp_overlay": True,
        "low_resolution": True,
        "uses_ocr": False,
        "output_path": str(output),
        "writes_to_raw_videos": False,
        "status": "planned",
    }


def build_video_proxy_plan(window: dict[str, Any], output_dir: Path | str, *, reason: str) -> dict[str, Any]:
    duration_ms = min(4000, max(0, int(window["end_ms"]) - int(window["start_ms"])))
    output = Path(output_dir) / "semantic_index" / "video_proxies" / f"{window['clip_id']}_{window['start_ms']}_{window['end_ms']}_proxy.mp4"
    return {
        "window_id": _window_id(window),
        "input_source_path": window["source_path"],
        "start_ms": window["start_ms"],
        "end_ms": window["end_ms"],
        "duration_ms": duration_ms,
        "resolution": "360x640",
        "fps": 6,
        "include_audio": False,
        "output_path": str(output),
        "cache_reusable": True,
        "deterministic_name": True,
        "generation_reason": reason,
        "writes_to_raw_videos": False,
        "status": "planned_on_demand",
    }


def write_semantic_index(output_dir: Path | str, windows: list[dict[str, Any]]) -> dict[str, Path]:
    out = Path(output_dir)
    index_dir = out / "semantic_index"
    index_dir.mkdir(parents=True, exist_ok=True)
    payload = {"schema_version": "p12e_asset_semantic_index_v1", "candidate_window_count": len(windows), "windows": windows}
    json_path = index_dir / "candidate_windows.json"
    json_path.write_text(json.dumps(payload, indent=2, ensure_ascii=False) + "\n", encoding="utf-8")
    report_path = index_dir / "candidate_windows_report.md"
    report_path.write_text(
        "\n".join([
            "# P12E 资产候选窗口索引",
            "",
            f"- 候选窗口数量：{len(windows)}",
            "- 原片目录未写入 sidecar、缓存或缩略图。",
            "- 场景切点只作为候选边界，不提供语义结论。",
        ]) + "\n",
        encoding="utf-8",
    )
    return {"json": json_path, "report": report_path}


def select_golden_pilot_source_clips(inventory_items: list[dict[str, Any]], *, target_min: int = 10, target_max: int = 15) -> list[dict[str, Any]]:
    passed = [item for item in inventory_items if item.get("probe_status") == "pass"]
    ordered = sorted(passed, key=lambda row: (str(row.get("filename", "")).lower(), str(row.get("absolute_path", "")).lower()))
    limit = min(target_max, max(0, len(ordered)))
    if limit >= target_min:
        return ordered[:limit]
    return ordered


def _windows_for_duration(duration_ms: int, *, max_windows_per_clip: int) -> list[tuple[int, int, str]]:
    if duration_ms <= MAX_WINDOW_MS:
        return [(0, max(MIN_WINDOW_MS, duration_ms), "complete_short_clip")]
    windows: list[tuple[int, int, str]] = []
    step = DEFAULT_WINDOW_MS
    start = 0
    while start < duration_ms and len(windows) < max_windows_per_clip:
        end = min(duration_ms, start + step)
        if end - start >= MIN_WINDOW_MS:
            windows.append((start, end, "fixed"))
        start += step
    return windows


def _sample_times(start_ms: int, end_ms: int) -> list[int]:
    duration = max(0, end_ms - start_ms)
    offsets = [0.0, 0.25, 0.5, 0.75, 1.0]
    return [start_ms + int(round(duration * offset)) for offset in offsets]


def _stable_window_hash(item: dict[str, Any], start_ms: int, end_ms: int) -> str:
    basis = "|".join([
        str(item.get("absolute_path")),
        str(item.get("size_bytes")),
        str(item.get("modified_time")),
        str(start_ms),
        str(end_ms),
    ])
    return hashlib.sha1(basis.encode("utf-8")).hexdigest()[:16]


def _window_id(window: dict[str, Any]) -> str:
    return f"{window['clip_id']}:{window['start_ms']}-{window['end_ms']}"


def _as_int(value: Any) -> int | None:
    try:
        if value is None:
            return None
        return int(value)
    except (TypeError, ValueError):
        return None
