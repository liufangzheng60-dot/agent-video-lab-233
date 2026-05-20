"""Local material inventory helpers.

This module only inspects local files. It does not call external APIs, edit
videos, transcribe media, or perform AI-based visual understanding.
"""

from __future__ import annotations

import json
import mimetypes
import subprocess
from datetime import datetime, timezone
from pathlib import Path
from shutil import which
from typing import Any


SOURCE_BUCKETS = (
    "product_images",
    "raw_videos",
    "ai_generated_clips",
    "product_briefs",
    "reference_videos",
)

IMAGE_EXTENSIONS = {".jpg", ".jpeg", ".png", ".webp", ".gif", ".bmp", ".tiff"}
VIDEO_EXTENSIONS = {".mp4", ".mov", ".mkv", ".avi", ".webm", ".m4v"}
AUDIO_EXTENSIONS = {".mp3", ".wav", ".m4a", ".aac", ".flac", ".ogg"}
DOCUMENT_EXTENSIONS = {".md", ".txt", ".pdf", ".doc", ".docx", ".csv", ".json", ".yaml", ".yml"}


def run_inventory(project_root: Path | str | None = None) -> dict[str, Any]:
    """Scan default input buckets and write inventory reports."""
    root = Path(project_root) if project_root is not None else Path(__file__).resolve().parents[1]
    input_root = root / "inputs"
    output_dir = root / "outputs" / "material_inventory"
    output_dir.mkdir(parents=True, exist_ok=True)

    ffprobe_path = which("ffprobe")
    generated_at = datetime.now(timezone.utc).isoformat()
    files = _scan_files(root, input_root, ffprobe_path)

    inventory = {
        "generated_at": generated_at,
        "input_root": str(input_root.relative_to(root)),
        "file_count": len(files),
        "files": files,
    }

    json_path = output_dir / "material_inventory.json"
    markdown_path = output_dir / "material_inventory.md"
    json_path.write_text(json.dumps(inventory, ensure_ascii=False, indent=2), encoding="utf-8")
    markdown_path.write_text(_render_markdown(inventory), encoding="utf-8")
    return {"inventory": inventory, "json_path": json_path, "markdown_path": markdown_path}


def _scan_files(root: Path, input_root: Path, ffprobe_path: str | None) -> list[dict[str, Any]]:
    items: list[dict[str, Any]] = []
    for bucket in SOURCE_BUCKETS:
        bucket_dir = input_root / bucket
        if not bucket_dir.exists():
            continue
        for path in sorted(p for p in bucket_dir.rglob("*") if p.is_file() and p.name != ".gitkeep"):
            items.append(_build_file_record(root, path, bucket, ffprobe_path))
    return items


def _build_file_record(root: Path, path: Path, source_bucket: str, ffprobe_path: str | None) -> dict[str, Any]:
    material_type = _detect_material_type(path)
    risk_flags: list[str] = []
    notes: list[str] = []
    duration_seconds = None
    width = None
    height = None
    has_audio = None

    if material_type in {"video", "audio"}:
        if ffprobe_path:
            metadata = _probe_media(path, ffprobe_path)
            duration_seconds = metadata["duration_seconds"]
            width = metadata["width"]
            height = metadata["height"]
            has_audio = metadata["has_audio"]
            risk_flags.extend(metadata["risk_flags"])
            notes.extend(metadata["notes"])
        else:
            risk_flags.append("ffprobe_unavailable")
            notes.append("ffprobe is not available; media duration and stream metadata were not collected.")

    return {
        "file_name": path.name,
        "relative_path": str(path.relative_to(root)).replace("\\", "/"),
        "material_type": material_type,
        "extension": path.suffix.lower(),
        "file_size_bytes": path.stat().st_size,
        "source_bucket": source_bucket,
        "duration_seconds": duration_seconds,
        "width": width,
        "height": height,
        "has_audio": has_audio,
        "risk_flags": risk_flags,
        "notes": notes,
    }


def _detect_material_type(path: Path) -> str:
    extension = path.suffix.lower()
    if extension in IMAGE_EXTENSIONS:
        return "image"
    if extension in VIDEO_EXTENSIONS:
        return "video"
    if extension in AUDIO_EXTENSIONS:
        return "audio"
    if extension in DOCUMENT_EXTENSIONS:
        return "document"

    mime_type, _ = mimetypes.guess_type(path.name)
    if mime_type:
        return mime_type.split("/", 1)[0]
    return "unknown"


def _probe_media(path: Path, ffprobe_path: str) -> dict[str, Any]:
    command = [
        ffprobe_path,
        "-v",
        "error",
        "-show_entries",
        "format=duration:stream=codec_type,width,height",
        "-of",
        "json",
        str(path),
    ]
    try:
        completed = subprocess.run(command, capture_output=True, text=True, check=True, timeout=15)
        data = json.loads(completed.stdout or "{}")
    except (subprocess.SubprocessError, json.JSONDecodeError) as exc:
        return {
            "duration_seconds": None,
            "width": None,
            "height": None,
            "has_audio": None,
            "risk_flags": ["ffprobe_failed"],
            "notes": [f"ffprobe failed: {exc}"],
        }

    streams = data.get("streams", [])
    video_stream = next((stream for stream in streams if stream.get("codec_type") == "video"), {})
    has_audio = any(stream.get("codec_type") == "audio" for stream in streams)
    duration = data.get("format", {}).get("duration")

    return {
        "duration_seconds": _parse_float(duration),
        "width": video_stream.get("width"),
        "height": video_stream.get("height"),
        "has_audio": has_audio,
        "risk_flags": [],
        "notes": [],
    }


def _parse_float(value: Any) -> float | None:
    try:
        return None if value is None else float(value)
    except (TypeError, ValueError):
        return None


def _render_markdown(inventory: dict[str, Any]) -> str:
    files = inventory["files"]
    bucket_counts = _count_by(files, "source_bucket")
    type_counts = _count_by(files, "material_type")
    risk_rows = [item for item in files if item["risk_flags"]]

    lines = [
        "# Material Inventory",
        "",
        f"- 生成时间: `{inventory['generated_at']}`",
        f"- 输入目录: `{inventory['input_root']}`",
        f"- 素材总数: `{inventory['file_count']}`",
        "",
        "## 按素材桶统计",
        "",
    ]
    lines.extend(_render_counts(bucket_counts))
    lines.extend(["", "## 按素材类型统计", ""])
    lines.extend(_render_counts(type_counts))
    lines.extend(["", "## 素材明细表", ""])

    if not files:
        lines.append("当前没有素材。请将图片、视频、AI 生成片段、产品 brief 或参考视频放入 `inputs/` 对应目录。")
    else:
        lines.extend(
            [
                "| File | Bucket | Type | Extension | Size Bytes | Duration | Resolution | Has Audio | Risks |",
                "| --- | --- | --- | --- | ---: | ---: | --- | --- | --- |",
            ]
        )
        for item in files:
            resolution = "-"
            if item["width"] is not None and item["height"] is not None:
                resolution = f"{item['width']}x{item['height']}"
            lines.append(
                "| "
                + " | ".join(
                    [
                        item["relative_path"],
                        item["source_bucket"],
                        item["material_type"],
                        item["extension"] or "-",
                        str(item["file_size_bytes"]),
                        str(item["duration_seconds"]) if item["duration_seconds"] is not None else "-",
                        resolution,
                        str(item["has_audio"]) if item["has_audio"] is not None else "-",
                        ", ".join(item["risk_flags"]) if item["risk_flags"] else "-",
                    ]
                )
                + " |"
            )

    lines.extend(["", "## 风险提示", ""])
    if not files:
        lines.append("- 当前没有素材，无法进入剪辑策略阶段。")
    elif risk_rows:
        for item in risk_rows:
            lines.append(f"- `{item['relative_path']}`: {', '.join(item['risk_flags'])}")
    else:
        lines.append("- 未发现基础盘点风险。")

    lines.extend(["", "## 下一步建议", ""])
    if not files:
        lines.append("- 先补充至少一个商品 brief 和一组图片或视频素材。")
    else:
        lines.append("- 人工检查素材明细，确认是否具备 Hook、产品展示、使用场景和证明素材。")
        lines.append("- 进入 material pack 设计阶段，定义后续剪辑策略需要的标准输入。")

    return "\n".join(lines) + "\n"


def _count_by(files: list[dict[str, Any]], key: str) -> dict[str, int]:
    counts: dict[str, int] = {}
    for item in files:
        value = item[key]
        counts[value] = counts.get(value, 0) + 1
    return counts


def _render_counts(counts: dict[str, int]) -> list[str]:
    if not counts:
        return ["- 当前没有素材。"]
    return [f"- `{key}`: {value}" for key, value in sorted(counts.items())]
