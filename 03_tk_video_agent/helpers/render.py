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
AUDIO_EXTENSIONS = (".mp3", ".wav", ".m4a")


def run_render(
    project_root: Path | str | None = None,
    timeline_path: Path | str | None = None,
    material_pack_path: Path | str | None = None,
    output_dir: Path | str | None = None,
    media_root: Path | str | None = None,
    report_root: Path | str | None = None,
    voiceover_dir: Path | str | None = None,
    report_dir: Path | str | None = None,
) -> dict[str, Any]:
    """Render a minimal review video from timeline source material."""
    root = Path(project_root) if project_root is not None else Path(__file__).resolve().parents[1]
    source_timeline_path = Path(timeline_path) if timeline_path is not None else root / "outputs" / "timelines" / "timeline.json"
    source_material_pack_path = Path(material_pack_path) if material_pack_path is not None else root / "outputs" / "material_pack" / "material_pack.json"
    destination = Path(output_dir) if output_dir is not None else root / "outputs" / "renders"
    source_root = Path(media_root) if media_root is not None else root
    relative_root = Path(report_root) if report_root is not None else root
    reports_destination = Path(report_dir) if report_dir is not None else root / "outputs" / "reports"
    candidate_voiceover_dir = Path(voiceover_dir) if voiceover_dir is not None else source_root / "assets" / "voiceovers"
    destination.mkdir(parents=True, exist_ok=True)
    reports_destination.mkdir(parents=True, exist_ok=True)

    report_path = destination / "render_report.md"
    date_stamp = datetime.now().strftime("%Y%m%d")
    voiceover_path = find_voiceover(candidate_voiceover_dir)
    voiceover_status = "present" if voiceover_path else "missing"
    render_mode = "voiceover" if voiceover_path else "muted_preview"
    final_path = destination / (f"final_voiceover_{date_stamp}.mp4" if voiceover_path else f"muted_visual_preview_{date_stamp}.mp4")
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
        "source_audio_muted": True,
        "subtitle_burned": False,
        "voiceover_status": voiceover_status,
        "voiceover_path": _safe_relative(voiceover_path, relative_root) if voiceover_path else "",
        "render_mode": render_mode,
        "message": "",
    }

    if not ffmpeg_path:
        report["message"] = "ffmpeg was not found in PATH. Install or expose ffmpeg before rendering."
        write_render_report(report_path, report)
        _write_product_reports(reports_destination, report, relative_root)
        return {"success": False, "final_path": final_path, "report_path": report_path, "report": report}

    source_path = _resolve_first_existing_video(source_root, source_materials)
    if source_path is None:
        report["message"] = "No existing mp4 source material referenced by timeline."
        write_render_report(report_path, report)
        _write_product_reports(reports_destination, report, relative_root)
        return {"success": False, "final_path": final_path, "report_path": report_path, "report": report}

    command = build_ffmpeg_command(ffmpeg_path, source_path, final_path, total_duration, voiceover_path)
    report["ffmpeg_command_summary"] = summarize_command(command, relative_root)

    try:
        completed = subprocess.run(command, capture_output=True, text=True, check=False)
    except OSError as exc:
        report["message"] = f"ffmpeg execution failed: {exc}"
        write_render_report(report_path, report)
        _write_product_reports(reports_destination, report, relative_root)
        return {"success": False, "final_path": final_path, "report_path": report_path, "report": report}

    if completed.returncode != 0:
        report["message"] = f"ffmpeg failed with exit code {completed.returncode}: {completed.stderr[-1000:]}"
        write_render_report(report_path, report)
        _write_product_reports(reports_destination, report, relative_root)
        return {"success": False, "final_path": final_path, "report_path": report_path, "report": report}

    report["status"] = "success"
    report["message"] = "Rendered final voiceover video." if voiceover_path else "Rendered muted visual preview. Voiceover is still missing."
    write_render_report(report_path, report)
    _write_product_reports(reports_destination, report, relative_root)
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


def find_voiceover(voiceover_dir: Path) -> Path | None:
    """Return the first local voiceover audio file, if present."""
    if not voiceover_dir.exists():
        return None
    candidates = sorted(path for path in voiceover_dir.rglob("*") if path.is_file() and path.suffix.lower() in AUDIO_EXTENSIONS)
    return candidates[0] if candidates else None


def build_ffmpeg_command(
    ffmpeg_path: str,
    source_path: Path,
    final_path: Path,
    duration: float,
    voiceover_path: Path | None = None,
) -> list[str]:
    """Build the minimal ffmpeg command without executing it."""
    video_filter = (
        f"scale={TARGET_WIDTH}:{TARGET_HEIGHT}:force_original_aspect_ratio=decrease,"
        f"pad={TARGET_WIDTH}:{TARGET_HEIGHT}:(ow-iw)/2:(oh-ih)/2,setsar=1"
    )
    command = [
        ffmpeg_path,
        "-y",
        "-stream_loop",
        "-1",
        "-i",
        str(source_path),
    ]
    if voiceover_path:
        command.extend(["-i", str(voiceover_path)])
    command.extend(
        [
        "-t",
        f"{duration:.3f}",
        "-vf",
        video_filter,
        "-r",
        "30",
        "-map",
        "0:v:0",
    ])
    if voiceover_path:
        command.extend(["-map", "1:a:0"])
    else:
        command.append("-an")
    command.extend([
        "-c:v",
        "libx264",
        "-preset",
        "veryfast",
        "-pix_fmt",
        "yuv420p",
    ])
    if voiceover_path:
        command.extend(["-c:a", "aac"])
    command.extend([
        "-shortest",
        str(final_path),
    ])
    return command


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
        f"- source_audio_muted: `{report.get('source_audio_muted')}`",
        f"- subtitle_burned: `{report.get('subtitle_burned')}`",
        f"- voiceover_status: `{report.get('voiceover_status')}`",
        f"- voiceover_path: `{report.get('voiceover_path') or 'NA'}`",
        f"- render_mode: `{report.get('render_mode')}`",
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
    lines.append("- 原视频背景音轨默认静音。")
    lines.append("- 默认不烧字幕。")
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


def _write_product_reports(report_dir: Path, report: dict[str, Any], relative_root: Path) -> None:
    asset_report = report_dir / "asset_readiness_report.md"
    voiceover_plan = report_dir / "voiceover_plan.md"
    business_report = report_dir / "business_pipeline_report.md"
    asset_report.write_text(_render_asset_readiness_report(report), encoding="utf-8")
    voiceover_plan.write_text(_render_voiceover_plan(report), encoding="utf-8")
    business_report.write_text(_render_business_pipeline_report(report, relative_root), encoding="utf-8")


def _render_asset_readiness_report(report: dict[str, Any]) -> str:
    lines = [
        "# Asset Readiness Report",
        "",
        f"- Render status: `{report['status']}`",
        f"- Source video count: `{len(report.get('source_materials', []))}`",
        f"- Voiceover status: `{report.get('voiceover_status')}`",
        f"- Source audio muted: `{report.get('source_audio_muted')}`",
        f"- Subtitle burned: `{report.get('subtitle_burned')}`",
        "",
        "## Source Materials",
        "",
    ]
    if report.get("source_materials"):
        lines.extend(f"- `{item}`" for item in report["source_materials"])
    else:
        lines.append("- NA")
    lines.extend(["", "## Risks", ""])
    if report.get("risk_flags"):
        lines.extend(f"- `{item}`" for item in report["risk_flags"])
    else:
        lines.append("- NA")
    return "\n".join(lines) + "\n"


def _render_voiceover_plan(report: dict[str, Any]) -> str:
    lines = [
        "# Voiceover Plan",
        "",
        f"- Voiceover status: `{report.get('voiceover_status')}`",
        f"- Voiceover path: `{report.get('voiceover_path') or 'NA'}`",
        f"- Source audio muted: `{report.get('source_audio_muted')}`",
        f"- Subtitle burned: `{report.get('subtitle_burned')}`",
        "",
        "## Rule",
        "",
        "- Final dog_bath_hose videos should use muted source video audio.",
        "- Final dog_bath_hose videos should not burn subtitles by default.",
        "- If a voiceover mp3, wav, or m4a exists, mix that voiceover into the final video.",
        "- If voiceover is missing, generate only a muted visual preview and do not label it as final voiceover output.",
        "",
        "## Next Action",
        "",
    ]
    if report.get("voiceover_status") == "present":
        lines.append("- Review the generated voiceover video.")
    else:
        lines.append("- Add a voiceover `.mp3`, `.wav`, or `.m4a` under `products/dog_bath_hose/assets/voiceovers/`.")
    return "\n".join(lines) + "\n"


def _render_business_pipeline_report(report: dict[str, Any], relative_root: Path) -> str:
    lines = [
        "# Business Pipeline Report",
        "",
        f"- Generated at: `{report['generated_at']}`",
        f"- Render status: `{report['status']}`",
        f"- Output path: `{report['output_path']}`",
        f"- Source audio muted: `{report.get('source_audio_muted')}`",
        f"- Subtitle burned: `{report.get('subtitle_burned')}`",
        f"- Voiceover status: `{report.get('voiceover_status')}`",
        f"- Render mode: `{report.get('render_mode')}`",
        f"- Message: {report['message']}",
        "",
        "## Business Rule",
        "",
        "- dog_bath_hose / blue uses a voiceover-only final video policy.",
        "- Original source video background audio must not be kept.",
        "- Subtitles are not burned by default.",
        "",
        "## Current Decision",
        "",
    ]
    if report.get("voiceover_status") == "present" and report["status"] == "success":
        lines.append("- Final voiceover video is ready for manual review.")
    elif report.get("voiceover_status") == "missing":
        lines.append("- Voiceover is missing; do not treat the muted visual preview as a final voiceover video.")
    else:
        lines.append("- Render did not complete successfully; inspect render_report.md before continuing.")
    return "\n".join(lines) + "\n"


def _safe_relative(path: Path, root: Path) -> str:
    try:
        return path.relative_to(root).as_posix()
    except ValueError:
        return path.as_posix()
