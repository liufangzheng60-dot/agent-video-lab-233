"""Generate timeline files from edit strategy and material pack outputs."""

from __future__ import annotations

import csv
import json
from datetime import datetime, timezone
from pathlib import Path
from typing import Any


SEGMENT_DURATIONS = {
    "hook": 2.0,
    "problem": 2.0,
    "demo": 5.0,
    "proof": 3.0,
    "cta": 3.0,
}

CSV_FIELDS = [
    "start",
    "end",
    "duration",
    "segment_name",
    "purpose",
    "source_material",
    "caption",
    "editing_note",
    "risk_flags",
]

VIDEO_EXTENSIONS = (".mp4", ".mov", ".mkv", ".avi", ".webm", ".m4v")


def run_timeline(
    project_root: Path | str | None = None,
    strategy_path: Path | str | None = None,
    material_pack_path: Path | str | None = None,
    output_dir: Path | str | None = None,
    report_root: Path | str | None = None,
) -> dict[str, Any]:
    """Read strategy and material pack, then write timeline JSON and CSV."""
    root = Path(project_root) if project_root is not None else Path(__file__).resolve().parents[1]
    source_strategy_path = Path(strategy_path) if strategy_path is not None else root / "outputs" / "edit_strategy" / "edit_strategy.json"
    source_material_pack_path = Path(material_pack_path) if material_pack_path is not None else root / "outputs" / "material_pack" / "material_pack.json"
    destination = Path(output_dir) if output_dir is not None else root / "outputs" / "timelines"
    relative_root = Path(report_root) if report_root is not None else root
    destination.mkdir(parents=True, exist_ok=True)

    edit_strategy = _read_json(source_strategy_path)
    material_pack = _read_json(source_material_pack_path)
    segments = _build_timeline_segments(edit_strategy)
    missing_materials = _unique(list(edit_strategy.get("missing_materials", [])) + list(material_pack.get("missing_materials", [])))
    risk_flags = _unique(list(edit_strategy.get("risk_flags", [])) + list(material_pack.get("risk_flags", [])))

    timeline = {
        "generated_at": datetime.now(timezone.utc).isoformat(),
        "source_edit_strategy": _safe_relative(source_strategy_path, relative_root),
        "source_material_pack": _safe_relative(source_material_pack_path, relative_root),
        "target_duration_seconds": _round_time(sum(item["duration"] for item in segments)),
        "segments": segments,
        "missing_materials": missing_materials,
        "risk_flags": risk_flags,
        "notes": [
            "Timeline is for planning and manual CapCut recreation only.",
            "No video editing, rendering, ffmpeg, or external API calls are performed in P0_004.",
        ],
    }

    json_path = destination / "timeline.json"
    csv_path = destination / "capcut_timeline.csv"
    json_path.write_text(json.dumps(timeline, ensure_ascii=False, indent=2), encoding="utf-8")
    _write_csv(csv_path, segments)
    return {"timeline": timeline, "json_path": json_path, "csv_path": csv_path}


def _read_json(path: Path) -> dict[str, Any]:
    if not path.exists():
        raise FileNotFoundError(f"required input not found: {path}")
    return json.loads(path.read_text(encoding="utf-8"))


def _build_timeline_segments(edit_strategy: dict[str, Any]) -> list[dict[str, Any]]:
    timeline_segments: list[dict[str, Any]] = []
    cursor = 0.0
    strategy_risks = list(edit_strategy.get("risk_flags", []))

    for strategy_segment in edit_strategy.get("strategy_segments", []):
        name = strategy_segment["segment_name"]
        duration = SEGMENT_DURATIONS.get(name, 2.0)
        start = cursor
        end = cursor + duration
        cursor = end
        available = strategy_segment.get("available_materials") or []
        source_material = available[0] if available else ""
        segment_risks = _segment_risks(strategy_risks, source_material)

        timeline_segments.append(
            {
                "start": _round_time(start),
                "end": _round_time(end),
                "duration": _round_time(duration),
                "segment_name": name,
                "purpose": strategy_segment.get("purpose", ""),
                "source_material": source_material,
                "caption": strategy_segment.get("caption_direction", ""),
                "editing_note": strategy_segment.get("execution_note", ""),
                "risk_flags": segment_risks,
            }
        )

    return timeline_segments


def _segment_risks(strategy_risks: list[str], source_material: str) -> list[str]:
    risks: list[str] = []
    if source_material.lower().endswith(VIDEO_EXTENSIONS):
        for flag in ("aspect_ratio_not_9_16", "needs_9_16_crop_or_rebuild"):
            if flag in strategy_risks:
                risks.append(flag)
    return risks


def _write_csv(csv_path: Path, segments: list[dict[str, Any]]) -> None:
    with csv_path.open("w", encoding="utf-8-sig", newline="") as file:
        writer = csv.DictWriter(file, fieldnames=CSV_FIELDS)
        writer.writeheader()
        for segment in segments:
            row = dict(segment)
            row["risk_flags"] = ";".join(segment.get("risk_flags", []))
            writer.writerow({field: row.get(field, "") for field in CSV_FIELDS})


def _unique(items: list[str]) -> list[str]:
    seen = set()
    result = []
    for item in items:
        if item not in seen:
            result.append(item)
            seen.add(item)
    return result


def _round_time(value: float) -> float:
    return round(value, 3)


def _safe_relative(path: Path, root: Path) -> str:
    try:
        return path.relative_to(root).as_posix()
    except ValueError:
        return path.as_posix()
