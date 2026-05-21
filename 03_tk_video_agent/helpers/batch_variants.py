"""Batch-generate English subtitle variants and burn them into review videos."""

from __future__ import annotations

import re
import subprocess
from datetime import datetime, timezone
from pathlib import Path
from shutil import which
from typing import Any

from helpers.subtitle_overlay import (
    build_ffmpeg_command,
    contains_chinese,
    read_json,
    render_srt,
)


VARIANTS = [
    {
        "version": "v002",
        "key": "cost_hook",
        "label": "Cost Hook",
        "captions": {
            "hook": "Stop paying $20+ for nail trims.",
            "problem": "At-home trims can save repeat visits.",
            "demo": "Use the light before every careful clip.",
            "proof": "Trim and smooth with more confidence.",
            "cta": "Try easier grooming at home.",
        },
        "caption_option": "Save on repeat nail trims with a simple LED grooming tool made for careful at-home touchups.",
        "hashtags": "#petsoftiktok #doggrooming #petgrooming #tiktokshop #dogmom",
    },
    {
        "version": "v003",
        "key": "stress_hook",
        "label": "Stress Hook",
        "captions": {
            "hook": "Nail trims do not have to be stressful.",
            "problem": "Nervous pets make grooming harder.",
            "demo": "Go slow and use the LED guide.",
            "proof": "A calmer setup helps every trim.",
            "cta": "Make grooming feel easier.",
        },
        "caption_option": "For pets that get nervous during nail trims, a clearer view and slower pace can make grooming feel easier.",
        "hashtags": "#dogsoftiktok #petcare #doggroomingtips #tiktokmademebuyit #tiktokshopfinds",
    },
    {
        "version": "v004",
        "key": "led_safety_hook",
        "label": "Safety / LED Hook",
        "captions": {
            "hook": "LED light helps you see clearly.",
            "problem": "Guessing makes nail trims harder.",
            "demo": "Check the nail before you trim.",
            "proof": "Better visibility means better control.",
            "cta": "Upgrade your grooming routine.",
        },
        "caption_option": "The built-in LED light helps you see more clearly before trimming, so at-home grooming feels less intimidating.",
        "hashtags": "#petnailtrimmer #petcaretips #doggrooming #tiktokshop #petparents",
    },
    {
        "version": "v005",
        "key": "home_grooming_hook",
        "label": "At-home Grooming Hook",
        "captions": {
            "hook": "Easier grooming at home.",
            "problem": "Nail care piles up fast.",
            "demo": "Trim, smooth, and keep it simple.",
            "proof": "Small touchups fit your routine.",
            "cta": "Keep grooming simple at home.",
        },
        "caption_option": "A simple at-home grooming helper for pet parents who want nail care to feel less complicated.",
        "hashtags": "#athomegrooming #petparents #dogmomlife #petgrooming #tiktokshop",
    },
    {
        "version": "v006",
        "key": "fast_demo_hook",
        "label": "Fast Demo Hook",
        "captions": {
            "hook": "Clip, smooth, done.",
            "problem": "Skip the overthinking.",
            "demo": "Use the light, trim, then smooth.",
            "proof": "Quick touchups can stay simple.",
            "cta": "See it in TikTok Shop.",
        },
        "caption_option": "Clip, smooth, done. A quick look at an LED pet nail trimmer for simple at-home touchups.",
        "hashtags": "#tiktokshopfinds #petsoftiktok #doggrooming #petnailcare #dogmom",
    },
]

DATE_RE = re.compile(r"^\d{8}$")


def run_batch_variants(project_root: Path | str | None = None, date_stamp: str | None = None) -> dict[str, Any]:
    """Generate five English subtitle variants and burn each into a dated video."""
    root = Path(project_root) if project_root is not None else Path(__file__).resolve().parents[1]
    stamp = date_stamp or current_date_stamp()
    validate_date_stamp(stamp)

    final_path = root / "outputs" / "renders" / "final.mp4"
    timeline_path = root / "outputs" / "timelines" / "timeline.json"
    strategy_path = root / "outputs" / "edit_strategy" / "edit_strategy.json"
    subtitle_dir = root / "outputs" / "subtitles" / "batch_variants"
    render_dir = root / "outputs" / "renders"
    publish_dir = root.parents[0] / "05_final_outputs" / "publish_records"
    feedback_dir = root.parents[0] / "05_final_outputs" / "performance_feedback"

    subtitle_dir.mkdir(parents=True, exist_ok=True)
    render_dir.mkdir(parents=True, exist_ok=True)
    publish_dir.mkdir(parents=True, exist_ok=True)
    feedback_dir.mkdir(parents=True, exist_ok=True)

    timeline = read_json(timeline_path)
    _ = read_json(strategy_path) if strategy_path.exists() else {}
    ffmpeg_path = which("ffmpeg")
    results = []

    for variant in VARIANTS:
        subtitles = build_variant_subtitles(timeline, variant)
        srt_path = subtitle_dir / build_subtitle_filename(variant, stamp)
        output_path = render_dir / build_video_filename(variant, stamp)
        srt_text = render_srt(subtitles)
        srt_path.write_text(srt_text, encoding="utf-8")

        result = {
            "version": variant["version"],
            "key": variant["key"],
            "label": variant["label"],
            "date_stamp": stamp,
            "srt_path": srt_path.relative_to(root).as_posix(),
            "output_path": output_path.relative_to(root).as_posix(),
            "english_only": not contains_chinese(srt_text),
            "status": "failed",
            "message": "",
        }

        if not ffmpeg_path:
            result["message"] = "ffmpeg was not found in PATH. SRT generated; video burn-in skipped."
        elif not final_path.exists():
            result["message"] = f"source video not found: {final_path}"
        else:
            command = build_ffmpeg_command(ffmpeg_path, final_path, srt_path, output_path)
            completed = subprocess.run(command, capture_output=True, text=True, check=False)
            if completed.returncode == 0:
                result["status"] = "success"
                result["message"] = "Variant video generated."
            else:
                result["message"] = f"ffmpeg failed with exit code {completed.returncode}: {completed.stderr[-800:]}"
        results.append(result)

    publish_plan_path = publish_dir / build_publish_plan_filename(stamp)
    feedback_path = feedback_dir / build_feedback_filename(stamp)
    publish_plan_path.write_text(render_publish_plan(results, stamp), encoding="utf-8")
    feedback_path.write_text(render_feedback_template(results, stamp), encoding="utf-8")

    return {
        "date_stamp": stamp,
        "results": results,
        "publish_plan_path": publish_plan_path,
        "feedback_path": feedback_path,
        "ffmpeg_found": bool(ffmpeg_path),
        "source_timeline": timeline_path,
        "source_edit_strategy": strategy_path,
    }


def current_date_stamp() -> str:
    """Return local date as YYYYMMDD for generated asset names."""
    return datetime.now().strftime("%Y%m%d")


def validate_date_stamp(date_stamp: str) -> None:
    if not DATE_RE.match(date_stamp):
        raise ValueError(f"date_stamp must use YYYYMMDD format: {date_stamp}")


def build_video_filename(variant: dict[str, Any], date_stamp: str) -> str:
    validate_date_stamp(date_stamp)
    return f"final_{variant['version']}_{variant['key']}_{date_stamp}.mp4"


def build_subtitle_filename(variant: dict[str, Any], date_stamp: str) -> str:
    validate_date_stamp(date_stamp)
    return f"subtitles_{variant['version']}_{variant['key']}_{date_stamp}.srt"


def build_publish_plan_filename(date_stamp: str) -> str:
    validate_date_stamp(date_stamp)
    return f"batch_v002_to_v006_publish_plan_{date_stamp}.md"


def build_feedback_filename(date_stamp: str) -> str:
    validate_date_stamp(date_stamp)
    return f"batch_v002_to_v006_feedback_{date_stamp}.md"


def build_qc_review_filename(date_stamp: str) -> str:
    validate_date_stamp(date_stamp)
    return f"batch_v002_to_v006_qc_review_{date_stamp}.md"


def get_variant_configs() -> list[dict[str, Any]]:
    """Return batch variant configuration."""
    return list(VARIANTS)


def build_variant_subtitles(timeline: dict[str, Any], variant: dict[str, Any]) -> list[dict[str, Any]]:
    subtitles = []
    captions = variant["captions"]
    for index, segment in enumerate(timeline.get("segments", []), start=1):
        segment_name = segment.get("segment_name", "")
        text = captions.get(segment_name, "Watch this product in action.")
        subtitles.append(
            {
                "index": index,
                "start": float(segment.get("start") or 0),
                "end": float(segment.get("end") or 0),
                "segment_name": segment_name,
                "text": text,
                "source": f"{variant['key']}_template",
            }
        )
    return subtitles


def render_publish_plan(results: list[dict[str, Any]], date_stamp: str | None = None) -> str:
    stamp = date_stamp or current_date_stamp()
    validate_date_stamp(stamp)
    lines = [
        "# Batch Publish Plan v002-v006",
        "",
        f"- Date stamp: `{stamp}`",
        f"- Prepared at: `{datetime.now(timezone.utc).isoformat()}`",
        "- Boundary: manual TikTok Shop US publishing only; no automatic publishing or API calls.",
        "",
        "## Variant Summary",
        "",
        "| Version | Variant | Video | Subtitles | Status |",
        "| --- | --- | --- | --- | --- |",
    ]
    by_key = {variant["key"]: variant for variant in VARIANTS}
    for result in results:
        variant = by_key[result["key"]]
        lines.append(
            f"| {result['version']} | {variant['label']} | `{result['output_path']}` | `{result['srt_path']}` | `{result['status']}` |"
        )

    lines.extend(["", "## Caption And Hashtag Options", ""])
    for variant in VARIANTS:
        lines.extend(
            [
                f"### {variant['version']} {variant['label']}",
                "",
                variant["caption_option"],
                "",
                f"Hashtags: `{variant['hashtags']}`",
                "",
            ]
        )

    lines.extend(
        [
            "## Manual Publish Checklist",
            "",
            "| Item | Status | Notes |",
            "| --- | --- | --- |",
            "| Confirm each video opens and plays | TODO |  |",
            "| Confirm subtitles are English-only | TODO |  |",
            "| Confirm filenames include YYYYMMDD date stamp | TODO |  |",
            "| Confirm no exaggerated safety or medical claims | TODO |  |",
            "| Select TikTok account and product attachment | TODO |  |",
            "| Publish variants separately and record URLs | TODO |  |",
            "",
            "## Test Purpose",
            "",
            "- v002 tests cost-saving hook.",
            "- v003 tests stress-reduction hook.",
            "- v004 tests LED visibility hook.",
            "- v005 tests at-home grooming convenience hook.",
            "- v006 tests fast demo hook.",
        ]
    )
    return "\n".join(lines) + "\n"


def render_feedback_template(results: list[dict[str, Any]], date_stamp: str | None = None) -> str:
    stamp = date_stamp or current_date_stamp()
    validate_date_stamp(stamp)
    lines = [
        "# Batch Feedback v002-v006",
        "",
        f"- Date stamp: `{stamp}`",
        "- Record each variant after manual publishing. Compare results before deciding v007 direction.",
        "",
        "## Metrics Table",
        "",
        "| Version | Variant | Time | views | likes | comments | shares | avg_watch_time | completion_rate | product_clicks | orders | Notes |",
        "| --- | --- | --- | ---: | ---: | ---: | ---: | --- | --- | ---: | ---: | --- |",
    ]
    by_key = {variant["key"]: variant for variant in VARIANTS}
    for result in results:
        label = by_key[result["key"]]["label"]
        for time_point in ("1h", "3h", "24h", "48h"):
            lines.append(f"| {result['version']} | {label} | {time_point} | TODO | TODO | TODO | TODO | TODO | TODO | TODO | TODO |  |")

    lines.extend(
        [
            "",
            "## Iteration Rules",
            "",
            "| Signal | Next Action |",
            "| --- | --- |",
            "| Cost hook wins | Build more price-saving variants. |",
            "| Stress hook wins | Lead with pet anxiety and calmer grooming. |",
            "| LED safety hook wins | Lead with visibility and careful trimming. |",
            "| Home grooming hook wins | Lead with convenience and routine. |",
            "| Fast demo hook wins | Shorten intro and show product action earlier. |",
            "| All variants weak | Replace source material before changing advanced tooling. |",
        ]
    )
    return "\n".join(lines) + "\n"
