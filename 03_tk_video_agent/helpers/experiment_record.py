"""Manual experiment performance recording and analysis helpers."""

from __future__ import annotations

import csv
from pathlib import Path
from typing import Any


INPUT_FIELDS = [
    "video_id",
    "checkpoint",
    "views",
    "likes",
    "comments",
    "shares",
    "saves",
    "product_clicks",
    "orders",
    "revenue",
    "avg_watch_time",
    "completion_rate",
    "new_followers",
    "traffic_note",
    "comment_note",
    "issue_note",
]

PERFORMANCE_FIELDS = [
    "record_time",
    "checkpoint",
    "video_id",
    "views",
    "likes",
    "comments",
    "shares",
    "saves",
    "product_clicks",
    "orders",
    "revenue",
    "avg_watch_time",
    "completion_rate",
    "new_followers",
    "traffic_note",
    "comment_note",
    "issue_note",
]


def parse_manual_input(path: Path | str) -> dict[str, str]:
    """Parse a simple key:value markdown file without guessing missing values."""
    input_path = Path(path)
    data: dict[str, str] = {}
    for line in input_path.read_text(encoding="utf-8").splitlines():
        stripped = line.strip()
        if not stripped or stripped.startswith("#") or ":" not in stripped:
            continue
        key, value = stripped.split(":", 1)
        data[key.strip()] = value.strip() or "NA"

    for field in INPUT_FIELDS:
        data.setdefault(field, "NA")
    return data


def run_experiment_record(
    repo_root: Path | str,
    product_slug: str,
    sku_slug: str,
    batch_id: str,
    input_path: Path | str,
) -> dict[str, Any]:
    """Record one manual TikTok data snapshot and generate a lightweight analysis."""
    root = Path(repo_root)
    batch_dir = root / "experiments" / product_slug / sku_slug / batch_id
    if not batch_dir.exists():
        raise FileNotFoundError(f"Experiment batch not found: experiments/{product_slug}/{sku_slug}/{batch_id}")

    manual_inputs = batch_dir / "manual_inputs"
    analysis_dir = batch_dir / "analysis"
    manual_inputs.mkdir(parents=True, exist_ok=True)
    analysis_dir.mkdir(parents=True, exist_ok=True)

    resolved_input = Path(input_path)
    if not resolved_input.is_absolute():
        resolved_input = batch_dir / resolved_input
    if not resolved_input.exists():
        raise FileNotFoundError(f"Manual input not found: {resolved_input}")

    data = parse_manual_input(resolved_input)
    performance_log = batch_dir / "02_performance_log.csv"
    rows = upsert_performance_row(performance_log, data)
    analysis = analyze_record(data)
    analysis_path = analysis_dir / analysis_filename(data)
    analysis_path.write_text(render_analysis_report(data, analysis), encoding="utf-8")

    decision_path = batch_dir / "03_racing_decision.md"
    decision_path.write_text(render_racing_decision_update(data, analysis), encoding="utf-8")

    return {
        "batch_dir": batch_dir,
        "manual_input": resolved_input,
        "performance_log": performance_log,
        "analysis_path": analysis_path,
        "racing_decision": decision_path,
        "record": data,
        "analysis": analysis,
        "row_count": len(rows),
    }


def upsert_performance_row(path: Path | str, data: dict[str, str]) -> list[dict[str, str]]:
    """Append or update one video_id + checkpoint row in performance_log.csv."""
    csv_path = Path(path)
    rows = read_performance_rows(csv_path)
    new_row = build_performance_row(data)
    updated = False
    for index, row in enumerate(rows):
        if row.get("video_id", "NA") == new_row["video_id"] and row.get("checkpoint", "NA") == new_row["checkpoint"]:
            rows[index] = new_row
            updated = True
            break
    if not updated:
        rows.append(new_row)

    csv_path.parent.mkdir(parents=True, exist_ok=True)
    with csv_path.open("w", encoding="utf-8-sig", newline="") as file:
        writer = csv.DictWriter(file, fieldnames=PERFORMANCE_FIELDS)
        writer.writeheader()
        writer.writerows(rows)
    return rows


def read_performance_rows(path: Path) -> list[dict[str, str]]:
    if not path.exists():
        return []
    with path.open("r", encoding="utf-8-sig", newline="") as file:
        reader = csv.DictReader(file)
        rows = []
        for row in reader:
            normalized = {field: row.get(field, "NA") or "NA" for field in PERFORMANCE_FIELDS}
            if "variant_id" in row and normalized["video_id"] == "NA":
                normalized["video_id"] = row.get("variant_id") or "NA"
            rows.append(normalized)
    return rows


def build_performance_row(data: dict[str, str]) -> dict[str, str]:
    row = {field: "NA" for field in PERFORMANCE_FIELDS}
    for field in INPUT_FIELDS:
        if field in row:
            row[field] = data.get(field, "NA") or "NA"
    return row


def analyze_record(data: dict[str, str]) -> dict[str, str]:
    views = parse_number(data.get("views", "NA"))
    likes = parse_number(data.get("likes", "NA"))
    avg_watch_time = parse_seconds(data.get("avg_watch_time", "NA"))
    completion_rate = parse_percent(data.get("completion_rate", "NA"))

    like_rate = "NA"
    if views is not None and views > 0 and likes is not None:
        like_rate = f"{(likes / views) * 100:.2f}%"

    attention_signal = "positive" if views is not None and views >= 2000 else "insufficient"
    retention_signal = "negative" if avg_watch_time is not None and avg_watch_time <= 4 else "unknown"
    completion_signal = "weak" if completion_rate is not None and completion_rate <= 5 else "unknown"

    return {
        "views": data.get("views", "NA"),
        "like_rate": like_rate,
        "avg_watch_time": data.get("avg_watch_time", "NA"),
        "completion_rate": data.get("completion_rate", "NA"),
        "attention_signal": attention_signal,
        "retention_signal": retention_signal,
        "completion_signal": completion_signal,
        "decision_status": "not_winner_yet",
        "next_action": "followup_test",
        "first_principles_reason": first_principles_reason(attention_signal, retention_signal, completion_signal),
    }


def parse_number(value: str) -> float | None:
    clean = value.strip()
    if not clean or clean.upper() == "NA":
        return None
    try:
        return float(clean.replace(",", ""))
    except ValueError:
        return None


def parse_seconds(value: str) -> float | None:
    clean = value.strip().lower().replace("seconds", "").replace("second", "").replace("s", "")
    return parse_number(clean)


def parse_percent(value: str) -> float | None:
    clean = value.strip().replace("%", "")
    return parse_number(clean)


def first_principles_reason(attention_signal: str, retention_signal: str, completion_signal: str) -> str:
    return (
        "The record separates attention, retention, and completion instead of declaring a winner. "
        f"Attention is {attention_signal}, retention is {retention_signal}, and completion is {completion_signal}. "
        "A variant with strong views but weak watch time may be stopping the scroll without sustaining enough product interest, "
        "so the next action is a followup test rather than a winner decision."
    )


def analysis_filename(data: dict[str, str]) -> str:
    video_id = data.get("video_id", "record")
    checkpoint = data.get("checkpoint", "checkpoint")
    version = video_id.split("_", 1)[0] if "_" in video_id else video_id
    return f"{version}_{checkpoint}_analysis.md"


def render_analysis_report(data: dict[str, str], analysis: dict[str, str]) -> str:
    lines = [
        "# Experiment Record Analysis",
        "",
        f"- video_id: {data.get('video_id', 'NA')}",
        f"- checkpoint: {data.get('checkpoint', 'NA')}",
        "",
        "## Metrics",
        "",
        f"- views: {analysis['views']}",
        f"- like_rate: {analysis['like_rate']}",
        f"- avg_watch_time: {analysis['avg_watch_time']}",
        f"- completion_rate: {analysis['completion_rate']}",
        "",
        "## Signals",
        "",
        f"- attention_signal: {analysis['attention_signal']}",
        f"- retention_signal: {analysis['retention_signal']}",
        f"- completion_signal: {analysis['completion_signal']}",
        f"- decision_status: {analysis['decision_status']}",
        f"- next_action: {analysis['next_action']}",
        "",
        "## First Principles Reason",
        "",
        analysis["first_principles_reason"],
        "",
        "## Missing Data Rule",
        "",
        "Missing values remain `NA`. No TikTok data was guessed or fetched automatically.",
        "",
    ]
    return "\n".join(lines)


def render_racing_decision_update(data: dict[str, str], analysis: dict[str, str]) -> str:
    return (
        "# Racing Decision\n\n"
        f"Batch checkpoint updated from `{data.get('video_id', 'NA')}` / `{data.get('checkpoint', 'NA')}`.\n\n"
        "## Current Decision Status\n\n"
        "not_winner_yet\n\n"
        "## Winner\n\n"
        "NA\n\n"
        "## Reason\n\n"
        f"{analysis['first_principles_reason']}\n\n"
        "## Signal Summary\n\n"
        f"- attention_signal: {analysis['attention_signal']}\n"
        f"- retention_signal: {analysis['retention_signal']}\n"
        f"- completion_signal: {analysis['completion_signal']}\n"
        f"- next_action: {analysis['next_action']}\n\n"
        "## Rule\n\n"
        "This command does not automatically declare a winner. Final decisions require user review.\n"
    )
