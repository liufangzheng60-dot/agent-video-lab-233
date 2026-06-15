"""Helpers for batch-based raw material intake and manifest generation."""

from __future__ import annotations

import csv
import hashlib
import json
import subprocess
from datetime import datetime, timezone
from pathlib import Path
from shutil import which
from typing import Any


VIDEO_EXTENSIONS = {".mp4", ".mov", ".m4v", ".avi", ".mkv", ".webm"}
MANIFEST_FIELDS = [
    "clip_id",
    "product_slug",
    "sku_slug",
    "material_batch_id",
    "original_filename",
    "relative_path",
    "absolute_path",
    "extension",
    "file_size_bytes",
    "checksum_sha256",
    "duration_sec",
    "width",
    "height",
    "fps",
    "has_audio",
    "orientation",
    "source_bucket",
    "created_at",
    "analysis_status",
    "notes",
]
TAGS_TEMPLATE_FIELDS = [
    "clip_id",
    "scene_tag",
    "usable_start_sec",
    "usable_end_sec",
    "quality_score",
    "hook_candidate",
    "demo_candidate",
    "proof_candidate",
    "cta_candidate",
    "risk_flags",
    "manual_notes",
]


def run_material_batch(
    repo_root: Path | str,
    product_slug: str,
    sku_slug: str,
    material_batch_id: str,
) -> dict[str, Any]:
    """Generate batch-scoped clip manifests and manual tagging templates."""
    root = Path(repo_root)
    input_dir = root / "products" / product_slug / "assets" / "raw_videos" / material_batch_id
    output_dir = root / "products" / product_slug / "outputs" / "material_batches" / material_batch_id
    input_dir.mkdir(parents=True, exist_ok=True)
    output_dir.mkdir(parents=True, exist_ok=True)

    ffprobe_path = which("ffprobe")
    generated_at = datetime.now(timezone.utc).isoformat()
    clips = _scan_batch_clips(
        repo_root=root,
        input_dir=input_dir,
        product_slug=product_slug,
        sku_slug=sku_slug,
        material_batch_id=material_batch_id,
        generated_at=generated_at,
        ffprobe_path=ffprobe_path,
    )

    manifest_csv_path = output_dir / "clip_manifest.csv"
    manifest_json_path = output_dir / "clip_manifest.json"
    tags_template_path = output_dir / "clip_tags_template.csv"
    report_path = output_dir / "batch_asset_report.md"

    _write_manifest_csv(manifest_csv_path, clips)
    _write_manifest_json(manifest_json_path, clips, product_slug, sku_slug, material_batch_id, input_dir, generated_at, bool(ffprobe_path))
    _write_tags_template(tags_template_path, clips)

    warnings = _collect_warnings(clips, bool(ffprobe_path))
    report = {
        "product_slug": product_slug,
        "sku_slug": sku_slug,
        "material_batch_id": material_batch_id,
        "input_dir": _safe_relative(input_dir, root),
        "output_dir": _safe_relative(output_dir, root),
        "total_video_files": len(clips),
        "total_size_mb": round(sum(int(item["file_size_bytes"]) for item in clips) / (1024 * 1024), 3),
        "ffprobe_available": bool(ffprobe_path),
        "manifest_csv_path": _safe_relative(manifest_csv_path, root),
        "manifest_json_path": _safe_relative(manifest_json_path, root),
        "clip_tags_template_path": _safe_relative(tags_template_path, root),
        "warnings": warnings,
        "next_step_for_user": _build_next_step(len(clips)),
    }
    report_path.write_text(_render_batch_asset_report(report), encoding="utf-8")

    return {
        "clips": clips,
        "report": report,
        "input_dir": input_dir,
        "output_dir": output_dir,
        "manifest_csv_path": manifest_csv_path,
        "manifest_json_path": manifest_json_path,
        "clip_tags_template_path": tags_template_path,
        "report_path": report_path,
    }


def _scan_batch_clips(
    repo_root: Path,
    input_dir: Path,
    product_slug: str,
    sku_slug: str,
    material_batch_id: str,
    generated_at: str,
    ffprobe_path: str | None,
) -> list[dict[str, str]]:
    clips: list[dict[str, str]] = []
    batch_code = _normalize_batch_code(material_batch_id)
    prefix = f"{_slug_code(product_slug)}_{_slug_code(sku_slug)}_{batch_code}"
    video_paths = [
        path
        for path in sorted(input_dir.iterdir(), key=lambda item: item.name.lower())
        if path_is_supported_video(path)
    ]

    for index, path in enumerate(video_paths, start=1):
        metadata = probe_video_metadata(path, ffprobe_path)
        clip_id = f"{prefix}_C{index:03d}"
        clips.append(
            {
                "clip_id": clip_id,
                "product_slug": product_slug,
                "sku_slug": sku_slug,
                "material_batch_id": material_batch_id,
                "original_filename": path.name,
                "relative_path": _safe_relative(path, repo_root),
                "absolute_path": str(path.resolve()),
                "extension": path.suffix.lower(),
                "file_size_bytes": str(path.stat().st_size),
                "checksum_sha256": compute_sha256(path),
                "duration_sec": metadata["duration_sec"],
                "width": metadata["width"],
                "height": metadata["height"],
                "fps": metadata["fps"],
                "has_audio": metadata["has_audio"],
                "orientation": infer_orientation(metadata["width"], metadata["height"]),
                "source_bucket": "raw_videos_batch",
                "created_at": generated_at,
                "analysis_status": "untagged",
                "notes": metadata["notes"],
            }
        )
    return clips


def path_is_supported_video(path: Path) -> bool:
    """Return True when the path is a supported top-level batch video file."""
    return path.name != ".gitkeep" and path.suffix.lower() in VIDEO_EXTENSIONS


def compute_sha256(path: Path) -> str:
    """Compute SHA256 for a local file."""
    digest = hashlib.sha256()
    with path.open("rb") as file:
        for chunk in iter(lambda: file.read(1024 * 1024), b""):
            digest.update(chunk)
    return digest.hexdigest()


def probe_video_metadata(path: Path, ffprobe_path: str | None) -> dict[str, str]:
    """Collect media metadata with ffprobe when available, else return NA values."""
    unknown = {
        "duration_sec": "NA",
        "width": "NA",
        "height": "NA",
        "fps": "NA",
        "has_audio": "NA",
        "notes": "",
    }
    if not ffprobe_path:
        return {**unknown, "notes": "ffprobe_unavailable"}

    command = [
        ffprobe_path,
        "-v",
        "error",
        "-show_entries",
        "format=duration:stream=codec_type,width,height,r_frame_rate",
        "-of",
        "json",
        str(path),
    ]
    try:
        completed = subprocess.run(command, capture_output=True, text=True, check=True, timeout=20)
        payload = json.loads(completed.stdout or "{}")
    except (subprocess.SubprocessError, json.JSONDecodeError, OSError, RuntimeError) as exc:
        return {**unknown, "notes": f"ffprobe_failed:{exc.__class__.__name__}"}

    streams = payload.get("streams", [])
    video_stream = next((stream for stream in streams if stream.get("codec_type") == "video"), {})
    duration = _format_decimal(payload.get("format", {}).get("duration"))
    width = _format_int(video_stream.get("width"))
    height = _format_int(video_stream.get("height"))
    fps = _format_fps(video_stream.get("r_frame_rate"))
    has_audio = "true" if any(stream.get("codec_type") == "audio" for stream in streams) else "false"
    return {
        "duration_sec": duration,
        "width": width,
        "height": height,
        "fps": fps,
        "has_audio": has_audio,
        "notes": "",
    }


def infer_orientation(width: str, height: str) -> str:
    """Return vertical, horizontal, square, or unknown from width and height strings."""
    try:
        width_value = int(width)
        height_value = int(height)
    except (TypeError, ValueError):
        return "unknown"
    if width_value <= 0 or height_value <= 0:
        return "unknown"
    if width_value == height_value:
        return "square"
    if height_value > width_value:
        return "vertical"
    return "horizontal"


def build_clip_tags_rows(clips: list[dict[str, str]]) -> list[dict[str, str]]:
    """Build one manual tag template row per clip."""
    rows: list[dict[str, str]] = []
    for clip in clips:
        rows.append(
            {
                "clip_id": clip["clip_id"],
                "scene_tag": "",
                "usable_start_sec": "0",
                "usable_end_sec": "" if clip["duration_sec"] == "NA" else clip["duration_sec"],
                "quality_score": "",
                "hook_candidate": "false",
                "demo_candidate": "false",
                "proof_candidate": "false",
                "cta_candidate": "false",
                "risk_flags": "",
                "manual_notes": "",
            }
        )
    return rows


def _write_manifest_csv(path: Path, clips: list[dict[str, str]]) -> None:
    with path.open("w", encoding="utf-8-sig", newline="") as file:
        writer = csv.DictWriter(file, fieldnames=MANIFEST_FIELDS)
        writer.writeheader()
        writer.writerows(clips)


def _write_manifest_json(
    path: Path,
    clips: list[dict[str, str]],
    product_slug: str,
    sku_slug: str,
    material_batch_id: str,
    input_dir: Path,
    generated_at: str,
    ffprobe_available: bool,
) -> None:
    payload = {
        "generated_at": generated_at,
        "product_slug": product_slug,
        "sku_slug": sku_slug,
        "material_batch_id": material_batch_id,
        "input_dir": str(input_dir),
        "ffprobe_available": ffprobe_available,
        "clips": clips,
    }
    path.write_text(json.dumps(payload, ensure_ascii=False, indent=2), encoding="utf-8")


def _write_tags_template(path: Path, clips: list[dict[str, str]]) -> None:
    rows = build_clip_tags_rows(clips)
    with path.open("w", encoding="utf-8-sig", newline="") as file:
        writer = csv.DictWriter(file, fieldnames=TAGS_TEMPLATE_FIELDS)
        writer.writeheader()
        writer.writerows(rows)


def _collect_warnings(clips: list[dict[str, str]], ffprobe_available: bool) -> list[str]:
    warnings: list[str] = []
    if not clips:
        warnings.append("no_video_files_found")
    if not ffprobe_available:
        warnings.append("ffprobe_unavailable")
    elif any(clip["notes"].startswith("ffprobe_failed") for clip in clips):
        warnings.append("ffprobe_failed_for_some_files")
    return warnings


def _build_next_step(total_video_files: int) -> str:
    if total_video_files == 0:
        return "Put raw source videos into the batch folder, then rerun material-batch."
    return "Review clip_tags_template.csv and fill manual clip tags before timeline design."


def _render_batch_asset_report(report: dict[str, Any]) -> str:
    lines = [
        "# Batch Asset Report",
        "",
        f"- product_slug: `{report['product_slug']}`",
        f"- sku_slug: `{report['sku_slug']}`",
        f"- material_batch_id: `{report['material_batch_id']}`",
        f"- input_dir: `{report['input_dir']}`",
        f"- output_dir: `{report['output_dir']}`",
        f"- total_video_files: `{report['total_video_files']}`",
        f"- total_size_mb: `{report['total_size_mb']}`",
        f"- ffprobe_available: `{report['ffprobe_available']}`",
        f"- manifest_csv_path: `{report['manifest_csv_path']}`",
        f"- manifest_json_path: `{report['manifest_json_path']}`",
        f"- clip_tags_template_path: `{report['clip_tags_template_path']}`",
        "",
        "## warnings",
        "",
    ]
    if report["warnings"]:
        lines.extend(f"- `{item}`" for item in report["warnings"])
    else:
        lines.append("- none")
    lines.extend(
        [
            "",
            "## next_step_for_user",
            "",
            f"- {report['next_step_for_user']}",
        ]
    )
    return "\n".join(lines) + "\n"


def _normalize_batch_code(material_batch_id: str) -> str:
    suffix = material_batch_id
    if suffix.lower().startswith("batch_"):
        suffix = suffix[6:]
    return f"B{suffix.upper()}"


def _slug_code(value: str) -> str:
    return "".join(char if char.isalnum() else "_" for char in value.upper())


def _format_decimal(value: Any) -> str:
    try:
        if value in (None, ""):
            return "NA"
        return f"{float(value):.3f}".rstrip("0").rstrip(".")
    except (TypeError, ValueError):
        return "NA"


def _format_int(value: Any) -> str:
    try:
        if value in (None, ""):
            return "NA"
        return str(int(value))
    except (TypeError, ValueError):
        return "NA"


def _format_fps(value: Any) -> str:
    if not value:
        return "NA"
    try:
        if isinstance(value, str) and "/" in value:
            left, right = value.split("/", 1)
            fps_value = float(left) / float(right)
        else:
            fps_value = float(value)
        return f"{fps_value:.3f}".rstrip("0").rstrip(".")
    except (TypeError, ValueError, ZeroDivisionError):
        return "NA"


def _safe_relative(path: Path, root: Path) -> str:
    try:
        return path.relative_to(root).as_posix()
    except ValueError:
        return path.as_posix()
