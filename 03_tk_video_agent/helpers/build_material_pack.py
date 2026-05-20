"""Build an Agent-readable material pack from local inventory outputs."""

from __future__ import annotations

import json
from datetime import datetime, timezone
from pathlib import Path
from typing import Any


ROLE_BY_BUCKET = {
    "raw_videos": "demo_or_source_clip",
    "product_images": "product_reference_image",
    "product_briefs": "product_brief_or_script",
    "reference_videos": "reference_clip",
    "ai_generated_clips": "ai_generated_clip",
}

REQUIRED_BUCKETS = ("raw_videos", "product_images", "product_briefs")
BRIEF_EXTENSIONS = {".txt", ".md"}
NINE_BY_SIXTEEN = 9 / 16
ASPECT_RATIO_TOLERANCE = 0.05


def run_material_pack(project_root: Path | str | None = None) -> dict[str, Any]:
    """Read inventory and product briefs, then write material pack reports."""
    root = Path(project_root) if project_root is not None else Path(__file__).resolve().parents[1]
    inventory_path = root / "outputs" / "material_inventory" / "material_inventory.json"
    brief_dir = root / "inputs" / "product_briefs"
    output_dir = root / "outputs" / "material_pack"
    output_dir.mkdir(parents=True, exist_ok=True)

    inventory = _read_inventory(inventory_path)
    product_briefs = _read_product_briefs(root, brief_dir)
    materials = [_build_material(item) for item in inventory.get("files", [])]
    missing_materials = _find_missing_materials(materials)
    risk_flags = _collect_risk_flags(materials, missing_materials)

    material_pack = {
        "generated_at": datetime.now(timezone.utc).isoformat(),
        "inventory_source": inventory_path.relative_to(root).as_posix(),
        "inventory_generated_at": inventory.get("generated_at"),
        "material_count": len(materials),
        "product_briefs": product_briefs,
        "materials": materials,
        "missing_materials": missing_materials,
        "risk_flags": risk_flags,
    }

    json_path = output_dir / "material_pack.json"
    markdown_path = output_dir / "material_pack.md"
    json_path.write_text(json.dumps(material_pack, ensure_ascii=False, indent=2), encoding="utf-8")
    markdown_path.write_text(_render_markdown(material_pack), encoding="utf-8")
    return {"material_pack": material_pack, "json_path": json_path, "markdown_path": markdown_path}


def _read_inventory(inventory_path: Path) -> dict[str, Any]:
    if not inventory_path.exists():
        raise FileNotFoundError(f"material inventory not found: {inventory_path}")
    return json.loads(inventory_path.read_text(encoding="utf-8"))


def _read_product_briefs(root: Path, brief_dir: Path) -> list[dict[str, Any]]:
    if not brief_dir.exists():
        return []

    briefs: list[dict[str, Any]] = []
    for path in sorted(p for p in brief_dir.rglob("*") if p.is_file() and p.suffix.lower() in BRIEF_EXTENSIONS):
        content = path.read_text(encoding="utf-8", errors="replace")
        briefs.append(
            {
                "file_name": path.name,
                "relative_path": str(path.relative_to(root)).replace("\\", "/"),
                "extension": path.suffix.lower(),
                "content": content,
                "summary": _summarize_text(content),
            }
        )
    return briefs


def _build_material(item: dict[str, Any]) -> dict[str, Any]:
    source_bucket = item.get("source_bucket", "")
    material = {
        "file_name": item.get("file_name"),
        "relative_path": item.get("relative_path"),
        "material_type": item.get("material_type"),
        "extension": item.get("extension"),
        "file_size_bytes": item.get("file_size_bytes"),
        "source_bucket": source_bucket,
        "duration_seconds": item.get("duration_seconds"),
        "width": item.get("width"),
        "height": item.get("height"),
        "has_audio": item.get("has_audio"),
        "suggested_role": ROLE_BY_BUCKET.get(source_bucket, "supporting_material"),
        "risk_flags": list(item.get("risk_flags") or []),
        "notes": list(item.get("notes") or []),
    }

    if material["material_type"] == "video":
        _add_video_risks(material)
    return material


def _add_video_risks(material: dict[str, Any]) -> None:
    width = material.get("width")
    height = material.get("height")
    if not width or not height:
        _append_unique(material["risk_flags"], "missing_video_dimensions")
        return

    ratio = width / height
    if abs(ratio - NINE_BY_SIXTEEN) > ASPECT_RATIO_TOLERANCE:
        _append_unique(material["risk_flags"], "aspect_ratio_not_9_16")
        material["notes"].append(f"Video aspect ratio is {width}:{height}, not close to 9:16.")


def _find_missing_materials(materials: list[dict[str, Any]]) -> list[str]:
    present_buckets = {item["source_bucket"] for item in materials}
    return [bucket for bucket in REQUIRED_BUCKETS if bucket not in present_buckets]


def _collect_risk_flags(materials: list[dict[str, Any]], missing_materials: list[str]) -> list[str]:
    flags: list[str] = []
    for missing in missing_materials:
        flags.append(f"missing_{missing}")
    for item in materials:
        for flag in item.get("risk_flags", []):
            _append_unique(flags, flag)
    return flags


def _append_unique(items: list[str], value: str) -> None:
    if value not in items:
        items.append(value)


def _summarize_text(content: str, max_chars: int = 500) -> str:
    collapsed = " ".join(content.split())
    if len(collapsed) <= max_chars:
        return collapsed
    return collapsed[: max_chars - 3] + "..."


def _render_markdown(material_pack: dict[str, Any]) -> str:
    materials = material_pack["materials"]
    product_briefs = material_pack["product_briefs"]
    lines = [
        "# Material Pack",
        "",
        f"- 生成时间: `{material_pack['generated_at']}`",
        f"- 素材总数: `{material_pack['material_count']}`",
        f"- Inventory 来源: `{material_pack['inventory_source']}`",
        "",
        "## 素材总览",
        "",
    ]
    lines.extend(_render_overview(materials))
    lines.extend(["", "## 产品 brief 摘要", ""])

    if not product_briefs:
        lines.append("- 未读取到产品 brief。")
    else:
        for brief in product_briefs:
            lines.append(f"### {brief['file_name']}")
            lines.append(brief["summary"] or "(empty brief)")
            lines.append("")

    lines.extend(["## 素材角色表", ""])
    if not materials:
        lines.append("当前没有素材可分配角色。")
    else:
        lines.extend(
            [
                "| File | Bucket | Type | Role | Duration | Resolution | Risks |",
                "| --- | --- | --- | --- | ---: | --- | --- |",
            ]
        )
        for item in materials:
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
                        item["suggested_role"],
                        str(item["duration_seconds"]) if item["duration_seconds"] is not None else "-",
                        resolution,
                        ", ".join(item["risk_flags"]) if item["risk_flags"] else "-",
                    ]
                )
                + " |"
            )

    lines.extend(["", "## 风险提示", ""])
    if material_pack["risk_flags"]:
        for flag in material_pack["risk_flags"]:
            lines.append(f"- `{flag}`")
    else:
        lines.append("- 未发现素材包层面的基础风险。")

    lines.extend(["", "## 缺失素材提示", ""])
    if material_pack["missing_materials"]:
        for bucket in material_pack["missing_materials"]:
            lines.append(f"- 缺少 `{bucket}` 素材。")
    else:
        lines.append("- 必需素材桶已具备：raw_videos、product_images、product_briefs。")

    lines.extend(["", "## 下一步建议", ""])
    lines.append("- 基于素材包进入 P0_003_edit_strategy，生成剪辑策略。")
    lines.append("- 暂不进行转录、剪辑、渲染或外部 API 调用。")
    return "\n".join(lines) + "\n"


def _render_overview(materials: list[dict[str, Any]]) -> list[str]:
    if not materials:
        return ["- 当前没有素材。"]

    counts: dict[str, int] = {}
    for item in materials:
        bucket = item["source_bucket"]
        counts[bucket] = counts.get(bucket, 0) + 1
    return [f"- `{bucket}`: {count}" for bucket, count in sorted(counts.items())]

