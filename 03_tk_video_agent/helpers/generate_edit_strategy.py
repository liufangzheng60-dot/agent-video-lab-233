"""Generate a TikTok product video edit strategy from a material pack."""

from __future__ import annotations

import json
from datetime import datetime, timezone
from pathlib import Path
from typing import Any


SEGMENT_BLUEPRINTS = (
    {
        "segment_name": "hook",
        "purpose": "Stop the scroll by showing the cost or pain point immediately.",
        "target_duration": "0-2s",
        "recommended_material_role": "product_brief_or_script",
        "caption_direction": "Stop paying $20+ for nail trims.",
        "execution_note": "Use the strongest pain-point line from the product brief as opening text. Pair with the clearest product or demo visual available.",
    },
    {
        "segment_name": "problem",
        "purpose": "Make the viewer recognize the grooming pain or cost problem.",
        "target_duration": "2-4s",
        "recommended_material_role": "demo_or_source_clip",
        "caption_direction": "Pet nail trims are stressful and expensive.",
        "execution_note": "Use source video moments that show pet handling, grooming setup, or the need for safer trimming.",
    },
    {
        "segment_name": "demo",
        "purpose": "Show the product mechanism or use case clearly.",
        "target_duration": "4-9s",
        "recommended_material_role": "demo_or_source_clip",
        "caption_direction": "LED light helps you see the quick before cutting.",
        "execution_note": "Prioritize close-up product operation. If using the 720x960 source clip, crop or rebuild to 9:16 before final timeline work.",
    },
    {
        "segment_name": "proof",
        "purpose": "Give the viewer confidence that the product is safer, quieter, or easier.",
        "target_duration": "9-12s",
        "recommended_material_role": "product_reference_image",
        "caption_direction": "Safer, easier, cheaper at home.",
        "execution_note": "Use product image as a stable proof visual if no dedicated proof clip exists. Keep text short and benefit-led.",
    },
    {
        "segment_name": "cta",
        "purpose": "Tell the viewer what to do next.",
        "target_duration": "12-15s",
        "recommended_material_role": "product_brief_or_script",
        "caption_direction": "Grab yours below.",
        "execution_note": "End with TikTok Shop-oriented CTA text. Do not publish automatically; this is only strategy output.",
    },
)


def run_edit_strategy(
    project_root: Path | str | None = None,
    pack_path: Path | str | None = None,
    output_dir: Path | str | None = None,
    report_root: Path | str | None = None,
) -> dict[str, Any]:
    """Read material_pack.json and write edit strategy reports."""
    root = Path(project_root) if project_root is not None else Path(__file__).resolve().parents[1]
    source_pack_path = Path(pack_path) if pack_path is not None else root / "outputs" / "material_pack" / "material_pack.json"
    destination = Path(output_dir) if output_dir is not None else root / "outputs" / "edit_strategy"
    relative_root = Path(report_root) if report_root is not None else root
    destination.mkdir(parents=True, exist_ok=True)

    material_pack = _read_material_pack(source_pack_path)
    materials = material_pack.get("materials", [])
    missing_materials = _build_missing_materials(material_pack, materials)
    risk_flags = _build_risk_flags(material_pack, materials)
    strategy_segments = [_build_segment(segment, materials) for segment in SEGMENT_BLUEPRINTS]
    material_usage = _build_material_usage(materials)

    edit_strategy = {
        "generated_at": datetime.now(timezone.utc).isoformat(),
        "source_material_pack": _safe_relative(source_pack_path, relative_root),
        "video_goal": "Create a 7-15 second TikTok product short that turns the product brief and available source materials into a clear hook, problem, demo, proof, and CTA flow.",
        "target_duration_seconds": {"min": 7, "max": 15},
        "strategy_segments": strategy_segments,
        "material_usage": material_usage,
        "risk_flags": risk_flags,
        "missing_materials": missing_materials,
        "next_step": "Use this strategy to plan a structured timeline. Do not render or edit video in P0_003.",
    }

    json_path = destination / "edit_strategy.json"
    markdown_path = destination / "edit_strategy.md"
    json_path.write_text(json.dumps(edit_strategy, ensure_ascii=False, indent=2), encoding="utf-8")
    markdown_path.write_text(_render_markdown(edit_strategy, material_pack), encoding="utf-8")
    return {"edit_strategy": edit_strategy, "json_path": json_path, "markdown_path": markdown_path}


def _read_material_pack(pack_path: Path) -> dict[str, Any]:
    if not pack_path.exists():
        raise FileNotFoundError(f"material pack not found: {pack_path}")
    return json.loads(pack_path.read_text(encoding="utf-8"))


def _build_segment(blueprint: dict[str, str], materials: list[dict[str, Any]]) -> dict[str, Any]:
    role = blueprint["recommended_material_role"]
    matching = [item["relative_path"] for item in materials if item.get("suggested_role") == role]
    segment = dict(blueprint)
    segment["available_materials"] = matching
    if not matching:
        segment["execution_note"] += f" Missing role: {role}."
    return segment


def _build_material_usage(materials: list[dict[str, Any]]) -> list[dict[str, Any]]:
    usage = []
    for item in materials:
        usage.append(
            {
                "relative_path": item.get("relative_path"),
                "source_bucket": item.get("source_bucket"),
                "material_type": item.get("material_type"),
                "suggested_role": item.get("suggested_role"),
                "recommended_use": _recommended_use_for_role(item.get("suggested_role")),
                "risk_flags": item.get("risk_flags", []),
            }
        )
    return usage


def _recommended_use_for_role(role: str | None) -> str:
    if role == "demo_or_source_clip":
        return "Use for problem, demo, and motion context. Crop or rebuild to vertical if aspect ratio risk exists."
    if role == "product_reference_image":
        return "Use as product clarity or proof visual when video detail is insufficient."
    if role == "product_brief_or_script":
        return "Use for hook wording, captions, CTA, and message constraints."
    if role == "reference_clip":
        return "Use only as style or pacing reference, not as final owned footage."
    if role == "ai_generated_clip":
        return "Use as supplemental visual if it supports the product claim."
    return "Use as supporting context after manual review."


def _build_missing_materials(material_pack: dict[str, Any], materials: list[dict[str, Any]]) -> list[str]:
    missing = list(material_pack.get("missing_materials", []))
    roles = {item.get("suggested_role") for item in materials}
    required_roles = {"demo_or_source_clip", "product_reference_image", "product_brief_or_script"}
    for role in sorted(required_roles - roles):
        missing.append(f"missing_role_{role}")
    return _unique(missing)


def _build_risk_flags(material_pack: dict[str, Any], materials: list[dict[str, Any]]) -> list[str]:
    flags = list(material_pack.get("risk_flags", []))
    for item in materials:
        for flag in item.get("risk_flags", []):
            flags.append(flag)
        if item.get("material_type") == "video" and "aspect_ratio_not_9_16" in item.get("risk_flags", []):
            flags.append("needs_9_16_crop_or_rebuild")
    return _unique(flags)


def _unique(items: list[str]) -> list[str]:
    seen = set()
    result = []
    for item in items:
        if item not in seen:
            result.append(item)
            seen.add(item)
    return result


def _safe_relative(path: Path, root: Path) -> str:
    try:
        return path.relative_to(root).as_posix()
    except ValueError:
        return path.as_posix()


def _render_markdown(edit_strategy: dict[str, Any], material_pack: dict[str, Any]) -> str:
    lines = [
        "# Edit Strategy",
        "",
        "## 目标视频类型",
        "",
        "TikTok 商品短视频，目标时长 7-15 秒，结构为 hook -> problem -> demo -> proof -> cta。",
        "",
        "## 素材概览",
        "",
        f"- 素材包来源: `{edit_strategy['source_material_pack']}`",
        f"- 素材数量: `{material_pack.get('material_count', len(material_pack.get('materials', [])))}`",
        f"- 产品 brief 数量: `{len(material_pack.get('product_briefs', []))}`",
        "",
        "## 7-15 秒剪辑结构",
        "",
        "| Segment | Duration | Purpose | Role | Caption | Execution |",
        "| --- | --- | --- | --- | --- | --- |",
    ]
    for segment in edit_strategy["strategy_segments"]:
        lines.append(
            "| "
            + " | ".join(
                [
                    segment["segment_name"],
                    segment["target_duration"],
                    segment["purpose"],
                    segment["recommended_material_role"],
                    segment["caption_direction"],
                    segment["execution_note"],
                ]
            )
            + " |"
        )

    lines.extend(["", "## 每段使用什么素材", ""])
    for segment in edit_strategy["strategy_segments"]:
        materials = segment.get("available_materials") or ["缺少匹配素材"]
        lines.append(f"- `{segment['segment_name']}` 使用 `{segment['recommended_material_role']}`: {', '.join(materials)}")

    lines.extend(["", "## 风险提示", ""])
    if edit_strategy["risk_flags"]:
        for flag in edit_strategy["risk_flags"]:
            lines.append(f"- `{flag}`")
        if "aspect_ratio_not_9_16" in edit_strategy["risk_flags"]:
            lines.append("- 当前视频素材不是接近 9:16，后续时间轴阶段需要裁切或重构为 9:16。")
    else:
        lines.append("- 未发现策略层面的基础风险。")

    lines.extend(["", "## 缺失素材", ""])
    if edit_strategy["missing_materials"]:
        for item in edit_strategy["missing_materials"]:
            lines.append(f"- `{item}`")
    else:
        lines.append("- 当前 hook/problem/demo/proof/cta 策略所需基础角色齐备。")

    lines.extend(["", "## 下一步建议", ""])
    lines.append("- 进入 P0_004_timeline_plan_only，规划 JSON 时间轴结构。")
    lines.append("- 本阶段不剪辑、不渲染、不调用外部 API。")
    return "\n".join(lines) + "\n"
