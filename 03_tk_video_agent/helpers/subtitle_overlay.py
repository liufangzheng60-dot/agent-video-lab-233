"""Generate English-only SRT subtitles and burn them into the review video."""

from __future__ import annotations

import json
import re
import subprocess
from datetime import datetime, timezone
from pathlib import Path
from shutil import which
from typing import Any


ENGLISH_FALLBACK_CAPTIONS = {
    "hook": "Stop guessing. Make pet nail trimming easier.",
    "problem": "Nervous pets make nail trimming stressful.",
    "demo": "Use the light to see clearly before trimming.",
    "proof": "Trim and smooth for a safer finish.",
    "cta": "Make grooming easier at home.",
}

CHINESE_RE = re.compile(r"[\u3400-\u4dbf\u4e00-\u9fff\uf900-\ufaff]")
ASCII_LETTER_RE = re.compile(r"[A-Za-z]")


def run_subtitles(project_root: Path | str | None = None) -> dict[str, Any]:
    """Create subtitles.srt, subtitle_plan.md, and a subtitled review video."""
    root = Path(project_root) if project_root is not None else Path(__file__).resolve().parents[1]
    final_path = root / "outputs" / "renders" / "final.mp4"
    timeline_path = root / "outputs" / "timelines" / "timeline.json"
    strategy_path = root / "outputs" / "edit_strategy" / "edit_strategy.json"
    brief_dir = root / "inputs" / "product_briefs"
    output_dir = root / "outputs" / "subtitles"
    output_dir.mkdir(parents=True, exist_ok=True)

    srt_path = output_dir / "subtitles.srt"
    plan_path = output_dir / "subtitle_plan.md"
    subtitled_path = root / "outputs" / "renders" / "final_subtitled.mp4"

    timeline = read_json(timeline_path)
    edit_strategy = read_json(strategy_path) if strategy_path.exists() else {}
    product_briefs = read_product_briefs(brief_dir)
    subtitles = build_subtitles(timeline, edit_strategy, product_briefs)
    srt_path.write_text(render_srt(subtitles), encoding="utf-8")

    ffmpeg_path = which("ffmpeg")
    report = {
        "generated_at": datetime.now(timezone.utc).isoformat(),
        "status": "failed",
        "final_input": final_path.relative_to(root).as_posix(),
        "srt_output": srt_path.relative_to(root).as_posix(),
        "subtitled_output": subtitled_path.relative_to(root).as_posix(),
        "subtitle_count": len(subtitles),
        "english_only": not contains_chinese(render_srt(subtitles)),
        "ffmpeg_found": bool(ffmpeg_path),
        "ffmpeg_command_summary": "",
        "message": "",
        "subtitles": subtitles,
    }

    if not ffmpeg_path:
        report["message"] = "ffmpeg was not found in PATH. subtitles.srt was generated, but video burn-in was skipped."
        write_subtitle_plan(plan_path, report)
        return {"success": False, "srt_path": srt_path, "plan_path": plan_path, "subtitled_path": subtitled_path, "report": report}

    if not final_path.exists():
        report["message"] = f"final.mp4 not found: {final_path}"
        write_subtitle_plan(plan_path, report)
        return {"success": False, "srt_path": srt_path, "plan_path": plan_path, "subtitled_path": subtitled_path, "report": report}

    command = build_ffmpeg_command(ffmpeg_path, final_path, srt_path, subtitled_path)
    report["ffmpeg_command_summary"] = summarize_command(command, root)
    completed = subprocess.run(command, capture_output=True, text=True, check=False)
    if completed.returncode != 0:
        report["message"] = f"ffmpeg subtitle burn-in failed with exit code {completed.returncode}: {completed.stderr[-1000:]}"
        write_subtitle_plan(plan_path, report)
        return {"success": False, "srt_path": srt_path, "plan_path": plan_path, "subtitled_path": subtitled_path, "report": report}

    report["status"] = "success"
    report["message"] = "Generated final_subtitled.mp4 with English-only subtitles for manual review."
    write_subtitle_plan(plan_path, report)
    return {"success": True, "srt_path": srt_path, "plan_path": plan_path, "subtitled_path": subtitled_path, "report": report}


def read_json(path: Path) -> dict[str, Any]:
    if not path.exists():
        raise FileNotFoundError(f"required input not found: {path}")
    return json.loads(path.read_text(encoding="utf-8"))


def read_product_briefs(brief_dir: Path) -> str:
    if not brief_dir.exists():
        return ""
    chunks = []
    for path in sorted(p for p in brief_dir.rglob("*") if p.is_file() and p.suffix.lower() in {".txt", ".md"}):
        chunks.append(path.read_text(encoding="utf-8", errors="replace"))
    return "\n\n".join(chunks)


def build_subtitles(timeline: dict[str, Any], edit_strategy: dict[str, Any] | None = None, product_briefs: str = "") -> list[dict[str, Any]]:
    """Build English-only subtitle rows from timeline and strategy captions."""
    strategy_by_name = {
        segment.get("segment_name"): segment
        for segment in (edit_strategy or {}).get("strategy_segments", [])
    }
    subtitles = []
    for index, segment in enumerate(timeline.get("segments", []), start=1):
        name = segment.get("segment_name", "")
        caption, source = choose_english_caption(segment, strategy_by_name.get(name, {}), product_briefs)
        subtitles.append(
            {
                "index": index,
                "start": float(segment.get("start") or 0),
                "end": float(segment.get("end") or 0),
                "segment_name": name,
                "text": caption,
                "source": source,
            }
        )
    return subtitles


def choose_english_caption(segment: dict[str, Any], strategy_segment: dict[str, Any], product_briefs: str = "") -> tuple[str, str]:
    name = str(segment.get("segment_name") or "")
    timeline_caption = clean_caption(segment.get("caption") or "")
    if is_english_caption(timeline_caption):
        return shorten_caption(timeline_caption), "timeline_caption"

    strategy_caption = clean_caption(strategy_segment.get("caption_direction") or "")
    if is_english_caption(strategy_caption):
        return shorten_caption(strategy_caption), "edit_strategy_caption"

    # Product briefs are intentionally not copied into subtitles unless an English
    # caption has already been curated into timeline/edit_strategy. This prevents
    # Chinese scripts from leaking into final SRT output without translation.
    return ENGLISH_FALLBACK_CAPTIONS.get(name, "Watch this product in action."), "english_fallback_template"


def contains_chinese(value: str) -> bool:
    return bool(CHINESE_RE.search(value))


def is_english_caption(value: str) -> bool:
    value = clean_caption(value)
    return bool(value) and not contains_chinese(value) and bool(ASCII_LETTER_RE.search(value))


def clean_caption(value: str) -> str:
    return " ".join(str(value).replace("\n", " ").split())


def shorten_caption(value: str, max_chars: int = 42) -> str:
    if len(value) <= max_chars:
        return value
    words = value.split()
    result = []
    for word in words:
        candidate = " ".join(result + [word])
        if len(candidate) > max_chars:
            break
        result.append(word)
    return " ".join(result) if result else value[:max_chars].rstrip()


def render_srt(subtitles: list[dict[str, Any]]) -> str:
    blocks = []
    for item in subtitles:
        blocks.append(
            "\n".join(
                [
                    str(item["index"]),
                    f"{format_srt_time(item['start'])} --> {format_srt_time(item['end'])}",
                    item["text"],
                ]
            )
        )
    return "\n\n".join(blocks) + "\n"


def format_srt_time(seconds: float) -> str:
    millis = int(round(seconds * 1000))
    hours, remainder = divmod(millis, 3_600_000)
    minutes, remainder = divmod(remainder, 60_000)
    secs, ms = divmod(remainder, 1000)
    return f"{hours:02}:{minutes:02}:{secs:02},{ms:03}"


def build_ffmpeg_command(ffmpeg_path: str, final_path: Path, srt_path: Path, subtitled_path: Path) -> list[str]:
    subtitles_filter = f"subtitles=filename='{escape_filter_path(srt_path)}':force_style='FontSize=18,Outline=2,Shadow=1,Alignment=2,MarginV=90'"
    return [
        ffmpeg_path,
        "-y",
        "-i",
        str(final_path),
        "-vf",
        subtitles_filter,
        "-c:a",
        "copy",
        str(subtitled_path),
    ]


def escape_filter_path(path: Path) -> str:
    value = path.resolve().as_posix().replace(":", "\\:")
    return value.replace("'", "\\'")


def write_subtitle_plan(plan_path: Path, report: dict[str, Any]) -> None:
    lines = [
        "# Subtitle Plan",
        "",
        f"- Generated at: `{report['generated_at']}`",
        f"- Status: `{report['status']}`",
        f"- Input video: `{report['final_input']}`",
        f"- SRT output: `{report['srt_output']}`",
        f"- Subtitled video output: `{report['subtitled_output']}`",
        f"- Subtitle count: `{report['subtitle_count']}`",
        f"- English only: `{report['english_only']}`",
        f"- ffmpeg found: `{report['ffmpeg_found']}`",
        f"- Message: {report['message']}",
        "",
        "## Subtitle Timing Table",
        "",
        "| # | Time | Segment | Text | Source |",
        "| --- | --- | --- | --- | --- |",
    ]
    for item in report["subtitles"]:
        lines.append(
            f"| {item['index']} | {format_srt_time(item['start'])} --> {format_srt_time(item['end'])} | {item['segment_name']} | {item['text']} | {item['source']} |"
        )
    lines.extend(["", "## ffmpeg Command Summary", ""])
    lines.append(f"```text\n{report['ffmpeg_command_summary'] or '(not executed)'}\n```")
    lines.extend(["", "## Boundaries", ""])
    lines.append("- This stage only generates English-only subtitle files and burns them into the existing final.mp4.")
    lines.append("- No AI visual understanding, video transcription, external API calls, translation, or automatic publishing.")
    plan_path.write_text("\n".join(lines) + "\n", encoding="utf-8")


def summarize_command(command: list[str], root: Path) -> str:
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
