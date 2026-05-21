"""Minimal ffmpeg render helpers for reviewable TikTok video output."""

from __future__ import annotations

import json
import subprocess
from datetime import datetime, timezone
from pathlib import Path
from shutil import which
from typing import Any


TARGET_WIDTH = 720
TARGET_HEIGHT = 1280
VIDEO_EXTENSIONS = (".mp4", ".mov", ".mkv", ".avi", ".webm", ".m4v")


def run_render(
    project_root: Path | str | None = None,
    timeline_path: Path | str | None = None,
    material_pack_path: Path | str | None = None,
    output_dir: Path | str | None = None,
    media_root: Path | str | None = None,
    report_root: Path | str | None = None,
) -> dict[str, Any]:
    """Render a minimal review video from timeline source material."""
    root = Path(project_root) if project_root is not None else Path(__file__).resolve().parents[1]
    source_timeline_path = Path(timeline_path) if timeline_path is not None else root / "outputs" / "timelines" / "timeline.json"
    source_material_pack_path = Path(material_pack_path) if material_pack_path is not None else root / "outputs" / "material_pack" / "material_pack.json"
    destination = Path(output_dir) if output_dir is not None else root / "outputs" / "renders"
    source_root = Path(media_root) if media_root is not None else root
    relative_root = Path(report_root) if report_root is not None else root
    destination.mkdir(parents=True, exist_ok=True)

    final_path = destination / "final.mp4"
    report_path = destination / "render_report.md"
    timeline = read_timeline(source_timeline_path)
    material_pack = _read_json(source_material_pack_path) if source_material_pack_path.exists() else {}
    source_materials = parse_video_source_materials(timeline)
    total_duration = float(timeline.get("target_duration_seconds") or _sum_segment_durations(timeline))
    risk_flags = _collect_risk_flags(timeline, material_pack)
    ffmpeg_path = which("ffmpeg")

    report: dict[str, Any] = {
        "generated_at": datetime.now(timezone.utc).isoformat(),
        "status": "failed",
        "timeline_path": _safe_relative(source_timeline_path, relative_root),
        "material_pack_path": _safe_relative(source_material_pack_path, relative_root),
        "output_path": _safe_relative(final_path, relative_root),
        "total_duration_seconds": total_duration,
        "source_materials": source_materials,
        "risk_flags": risk_flags,
        "ffmpeg_found": bool(ffmpeg_path),
        "ffmpeg_command_summary": "",
        "message": "",
    }

    if not ffmpeg_path:
        report["message"] = "ffmpeg was not found in PATH. Install or expose ffmpeg before rendering."
        write_render_report(report_path, report)
        return {"success": False, "final_path": final_path, "report_path": report_path, "report": report}

    source_path = _resolve_first_existing_video(source_root, source_materials)
    if source_path is None:
        report["message"] = "No existing mp4 source material referenced by timeline."
        write_render_report(report_path, report)
        return {"success": False, "final_path": final_path, "report_path": report_path, "report": report}

    command = build_ffmpeg_command(ffmpeg_path, source_path, final_path, total_duration)
    report["ffmpeg_command_summary"] = summarize_command(command, relative_root)

    try:
        completed = subprocess.run(command, capture_output=True, text=True, check=False)
    except OSError as exc:
        report["message"] = f"ffmpeg execution failed: {exc}"
        write_render_report(report_path, report)
        return {"success": False, "final_path": final_path, "report_path": report_path, "report": report}

    if completed.returncode != 0:
        report["message"] = f"ffmpeg failed with exit code {completed.returncode}: {completed.stderr[-1000:]}"
        write_render_report(report_path, report)
        return {"success": False, "final_path": final_path, "report_path": report_path, "report": report}

    report["status"] = "success"
    report["message"] = "Rendered final.mp4 for manual review."
    write_render_report(report_path, report)
    return {"success": True, "final_path": final_path, "report_path": report_path, "report": report}


def read_timeline(timeline_path: Path) -> dict[str, Any]:
    """Read timeline JSON from disk."""
    if not timeline_path.exists():
        raise FileNotFoundError(f"timeline not found: {timeline_path}")
    return json.loads(timeline_path.read_text(encoding="utf-8"))


def parse_video_source_materials(timeline: dict[str, Any]) -> list[str]:
    """Return unique video source paths referenced by timeline segments."""
    sources: list[str] = []
    for segment in timeline.get("segments", []):
        source = str(segment.get("source_material") or "")
        if source.lower().endswith(VIDEO_EXTENSIONS) and source not in sources:
            sources.append(source)
    return sources


def build_ffmpeg_command(ffmpeg_path: str, source_path: Path, final_path: Path, duration: float) -> list[str]:
    """Build the minimal ffmpeg command without executing it."""
    video_filter = (
        f"scale={TARGET_WIDTH}:{TARGET_HEIGHT}:force_original_aspect_ratio=decrease,"
        f"pad={TARGET_WIDTH}:{TARGET_HEIGHT}:(ow-iw)/2:(oh-ih)/2,setsar=1"
    )
    return [
        ffmpeg_path,
        "-y",
        "-stream_loop",
        "-1",
        "-i",
        str(source_path),
        "-t",
        f"{duration:.3f}",
        "-vf",
        video_filter,
        "-r",
        "30",
        "-c:v",
        "libx264",
        "-preset",
        "veryfast",
        "-pix_fmt",
        "yuv420p",
        "-c:a",
        "aac",
        "-shortest",
        str(final_path),
    ]


def write_render_report(report_path: Path, report: dict[str, Any]) -> None:
    """Write a Markdown render report."""
    lines = [
        "# Render Report",
        "",
        f"- 生成时间: `{report['generated_at']}`",
        f"- 状态: `{report['status']}`",
        f"- Timeline: `{report['timeline_path']}`",
        f"- Material pack: `{report['material_pack_path']}`",
        f"- 输出文件: `{report['output_path']}`",
        f"- 总时长: `{report['total_duration_seconds']}` 秒",
        f"- ffmpeg 可用: `{report['ffmpeg_found']}`",
        f"- 消息: {report['message']}",
        "",
        "## 输入素材",
        "",
    ]
    if report["source_materials"]:
        for source in report["source_materials"]:
            lines.append(f"- `{source}`")
    else:
        lines.append("- 未找到 timeline 引用的 mp4 素材。")

    lines.extend(["", "## 风险", ""])
    if report["risk_flags"]:
        for flag in report["risk_flags"]:
            lines.append(f"- `{flag}`")
    else:
        lines.append("- 未发现渲染前基础风险。")

    lines.extend(["", "## ffmpeg 命令摘要", ""])
    lines.append(f"```text\n{report['ffmpeg_command_summary'] or '(not executed)'}\n```")
    lines.extend(["", "## 边界", ""])
    lines.append("- 本阶段只做最小可审片渲染。")
    lines.append("- 不做 AI 视觉理解、转录、自动发布或 UI。")
    report_path.write_text("\n".join(lines) + "\n", encoding="utf-8")


def summarize_command(command: list[str], root: Path) -> str:
    """Return a readable command summary with project-relative paths where possible."""
    parts = []
    for part in command:
        try:
            path = Path(part)
            if path.is_absolute():
                parts.append(path.relative_to(root).as_posix())
            else:
                parts.append(part)
        except (ValueError, OSError):
            parts.append(part)
    return " ".join(parts)


def _read_json(path: Path) -> dict[str, Any]:
    return json.loads(path.read_text(encoding="utf-8"))


def _sum_segment_durations(timeline: dict[str, Any]) -> float:
    return float(sum(float(segment.get("duration") or 0) for segment in timeline.get("segments", [])))


def _collect_risk_flags(timeline: dict[str, Any], material_pack: dict[str, Any]) -> list[str]:
    flags: list[str] = []
    for source in (timeline.get("risk_flags", []), material_pack.get("risk_flags", [])):
        for flag in source:
            if flag not in flags:
                flags.append(flag)
    for segment in timeline.get("segments", []):
        for flag in segment.get("risk_flags", []):
            if flag not in flags:
                flags.append(flag)
    return flags


def _resolve_first_existing_video(root: Path, source_materials: list[str]) -> Path | None:
    for source in source_materials:
        path = root / source
        if path.exists() and path.is_file():
            return path
    return None


def _safe_relative(path: Path, root: Path) -> str:
    try:
        return path.relative_to(root).as_posix()
    except ValueError:
        return path.as_posix()
