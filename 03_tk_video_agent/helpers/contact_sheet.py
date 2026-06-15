"""Helpers for contact sheet generation from material batch manifests."""

from __future__ import annotations

import csv
import subprocess
from pathlib import Path
from shutil import which
from typing import Any


DEFAULT_FRAME_COUNT = 6


def run_contact_sheet(
    repo_root: Path | str,
    product_slug: str,
    sku_slug: str,
    material_batch_id: str,
) -> dict[str, Any]:
    """Generate one jpg contact sheet per manifest clip."""
    root = Path(repo_root)
    output_dir = root / "products" / product_slug / "outputs" / "material_batches" / material_batch_id
    manifest_csv_path = output_dir / "clip_manifest.csv"
    if not manifest_csv_path.exists():
        raise FileNotFoundError(f"clip manifest not found: {manifest_csv_path}")

    contact_sheets_dir = output_dir / "contact_sheets"
    contact_sheets_dir.mkdir(parents=True, exist_ok=True)
    ffmpeg_path = which("ffmpeg")
    rows = _read_manifest_csv(manifest_csv_path)

    generated_count = 0
    failed_count = 0
    warnings: list[str] = []

    if not ffmpeg_path:
        warnings.append("ffmpeg_unavailable")
    for row in rows:
        if not ffmpeg_path:
            failed_count += 1
            continue
        output_path = contact_sheets_dir / f"{row['clip_id']}_contact_sheet.jpg"
        command = build_contact_sheet_command(
            ffmpeg_path=ffmpeg_path,
            source_path=Path(row["absolute_path"]),
            output_path=output_path,
            duration_sec=row.get("duration_sec", "NA"),
            frame_count=DEFAULT_FRAME_COUNT,
        )
        try:
            completed = subprocess.run(command, capture_output=True, text=True, check=False)
        except OSError:
            failed_count += 1
            warnings.append(f"ffmpeg_os_error:{row['clip_id']}")
            continue
        if completed.returncode != 0:
            failed_count += 1
            warnings.append(f"ffmpeg_failed:{row['clip_id']}")
            continue
        generated_count += 1

    report = {
        "product_slug": product_slug,
        "sku_slug": sku_slug,
        "material_batch_id": material_batch_id,
        "manifest_csv_path": _safe_relative(manifest_csv_path, root),
        "contact_sheets_dir": _safe_relative(contact_sheets_dir, root),
        "total_manifest_clips": len(rows),
        "generated_contact_sheets": generated_count,
        "failed_contact_sheets": failed_count,
        "ffmpeg_available": bool(ffmpeg_path),
        "warnings": warnings,
        "next_step_for_user": _next_step_for_user(len(rows), generated_count, bool(ffmpeg_path)),
    }
    report_path = output_dir / "contact_sheet_report.md"
    report_path.write_text(_render_contact_sheet_report(report), encoding="utf-8")
    return {
        "rows": rows,
        "report": report,
        "report_path": report_path,
        "contact_sheets_dir": contact_sheets_dir,
    }


def build_contact_sheet_command(
    ffmpeg_path: str,
    source_path: Path,
    output_path: Path,
    duration_sec: str,
    frame_count: int = DEFAULT_FRAME_COUNT,
) -> list[str]:
    """Build the ffmpeg command for one contact sheet jpg."""
    fps_filter = _build_fps_filter(duration_sec, frame_count)
    vf = f"{fps_filter},scale=320:-1,tile=3x2"
    return [
        ffmpeg_path,
        "-y",
        "-i",
        str(source_path),
        "-frames:v",
        "1",
        "-q:v",
        "2",
        "-vf",
        vf,
        str(output_path),
    ]


def _read_manifest_csv(path: Path) -> list[dict[str, str]]:
    with path.open("r", encoding="utf-8-sig", newline="") as file:
        return list(csv.DictReader(file))


def _build_fps_filter(duration_sec: str, frame_count: int) -> str:
    try:
        duration = float(duration_sec)
        if duration > 0:
            return f"fps={frame_count / duration:.6f}"
    except (TypeError, ValueError):
        pass
    return "fps=1"


def _next_step_for_user(total_clips: int, generated_count: int, ffmpeg_available: bool) -> str:
    if total_clips == 0:
        return "Add source videos to the batch folder, run material-batch again, then rerun contact-sheet."
    if not ffmpeg_available:
        return "Install or expose ffmpeg in PATH, then rerun contact-sheet."
    if generated_count == total_clips:
        return "Review the generated contact sheets and fill clip_tags_template.csv."
    return "Inspect contact_sheet_report.md, fix failed clips, then rerun contact-sheet."


def _render_contact_sheet_report(report: dict[str, Any]) -> str:
    lines = [
        "# Contact Sheet Report",
        "",
        f"- product_slug: `{report['product_slug']}`",
        f"- sku_slug: `{report['sku_slug']}`",
        f"- material_batch_id: `{report['material_batch_id']}`",
        f"- manifest_csv_path: `{report['manifest_csv_path']}`",
        f"- contact_sheets_dir: `{report['contact_sheets_dir']}`",
        f"- total_manifest_clips: `{report['total_manifest_clips']}`",
        f"- generated_contact_sheets: `{report['generated_contact_sheets']}`",
        f"- failed_contact_sheets: `{report['failed_contact_sheets']}`",
        f"- ffmpeg_available: `{report['ffmpeg_available']}`",
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


def _safe_relative(path: Path, root: Path) -> str:
    try:
        return path.relative_to(root).as_posix()
    except ValueError:
        return path.as_posix()
