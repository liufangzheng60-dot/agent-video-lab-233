"""Manual A/B experiment template generation helpers."""

from __future__ import annotations

import csv
from datetime import datetime, timezone
from pathlib import Path
from typing import Any


VARIANTS_FIELDS = [
    "video_id",
    "variant_name",
    "hook_type",
    "core_test_variable",
    "generated_video_path",
    "generated_date",
    "caption_summary",
    "hashtag_set",
    "publish_status",
    "publish_datetime",
    "tiktok_url",
    "notes",
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
    "traffic_note",
    "comment_note",
    "issue_note",
]

TEMPLATE_FILES = (
    "00_batch_brief.md",
    "01_variants.csv",
    "02_performance_log.csv",
    "03_racing_decision.md",
    "04_next_iteration.md",
)


def run_experiment_init(
    repo_root: Path | str,
    product_slug: str,
    sku_slug: str,
    batch_id: str,
) -> dict[str, Any]:
    """Create manual-fill templates for one isolated product/SKU/batch experiment."""
    root = Path(repo_root)
    batch_dir = root / "experiments" / product_slug / sku_slug / batch_id
    batch_dir.mkdir(parents=True, exist_ok=True)

    generated_at = datetime.now(timezone.utc).isoformat()
    files = {
        "batch_brief": batch_dir / "00_batch_brief.md",
        "variants": batch_dir / "01_variants.csv",
        "performance_log": batch_dir / "02_performance_log.csv",
        "racing_decision": batch_dir / "03_racing_decision.md",
        "next_iteration": batch_dir / "04_next_iteration.md",
    }

    files["batch_brief"].write_text(
        _render_batch_brief(product_slug, sku_slug, batch_id, generated_at),
        encoding="utf-8",
    )
    _write_csv_header(files["variants"], VARIANTS_FIELDS)
    _write_csv_header(files["performance_log"], PERFORMANCE_FIELDS)
    files["racing_decision"].write_text(_render_racing_decision(), encoding="utf-8")
    files["next_iteration"].write_text(_render_next_iteration(), encoding="utf-8")

    return {
        "batch_dir": batch_dir,
        "files": files,
        "product_slug": product_slug,
        "sku_slug": sku_slug,
        "batch_id": batch_id,
    }


def _write_csv_header(path: Path, fields: list[str]) -> None:
    with path.open("w", encoding="utf-8-sig", newline="") as file:
        writer = csv.writer(file)
        writer.writerow(fields)


def _render_batch_brief(product_slug: str, sku_slug: str, batch_id: str, generated_at: str) -> str:
    return (
        "# Experiment Batch Brief\n\n"
        "## 填写说明\n\n"
        "- 本文件用于记录一个产品、一个 SKU、一个批次的 A/B 测试背景。\n"
        "- 所有缺失或暂未记录的数据统一填写 `NA`。\n"
        "- 本批次只记录手动发布与人工回填数据，不自动发布 TikTok。\n\n"
        "## Batch Identity\n\n"
        f"- Product: `{product_slug}`\n"
        f"- SKU: `{sku_slug}`\n"
        f"- Batch: `{batch_id}`\n"
        f"- Template generated at: `{generated_at}`\n\n"
        "## Test Goal\n\n"
        "- 本批要验证什么 Hook、字幕、CTA、节奏或素材变量：NA\n\n"
        "## Source Assets\n\n"
        "- Video source path(s): NA\n"
        "- Subtitle source path(s): NA\n"
        "- Publish plan path: NA\n\n"
        "## Notes\n\n"
        "- NA\n"
    )


def _render_racing_decision() -> str:
    fields = [
        "本批 winner",
        "本批 loser",
        "是否需要更多数据",
        "最佳 Hook 方向",
        "最差 Hook 方向",
        "主要成功原因",
        "主要失败原因",
        "下一轮应该收敛什么",
        "下一轮应该发散什么",
        "最终决策",
        "下一步动作",
    ]
    return _render_manual_markdown("Experiment Racing Decision", fields)


def _render_next_iteration() -> str:
    fields = [
        "下一批 batch_id",
        "下一批版本范围",
        "保留什么",
        "删除什么",
        "新增什么",
        "下一轮核心变量",
        "下一轮视频数量",
        "下一轮优先 Hook",
        "下一轮禁止重复的问题",
    ]
    return _render_manual_markdown("Next Iteration Plan", fields)


def _render_manual_markdown(title: str, fields: list[str]) -> str:
    lines = [
        f"# {title}",
        "",
        "## 填写说明",
        "",
        "- 请在发布数据回收后手动填写本文件。",
        "- 所有缺失或暂未记录的数据统一填写 `NA`。",
        "- 不要在本文件中粘贴敏感账号凭证或平台后台隐私信息。",
        "",
    ]
    for field in fields:
        lines.extend([f"## {field}", "", "NA", ""])
    return "\n".join(lines)
