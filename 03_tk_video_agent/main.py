"""Command line entry point for the TikTok product video agent."""

from __future__ import annotations

import argparse
from pathlib import Path

from helpers.batch_variants import run_batch_variants
from helpers.build_material_pack import run_material_pack
from helpers.experiment_racing import run_experiment_init
from helpers.generate_edit_strategy import run_edit_strategy
from helpers.generate_timeline import run_timeline
from helpers.inventory import PRODUCT_ASSET_BUCKETS, run_inventory
from helpers.product_workspace import repo_root_from_agent_root, require_product_workspace
from helpers.render import run_render
from helpers.subtitle_overlay import run_subtitles


def main() -> None:
    parser = argparse.ArgumentParser(description="TikTok product video agent utilities.")
    subparsers = parser.add_subparsers(dest="command")
    inventory_parser = subparsers.add_parser("inventory", help="Scan local input materials and write inventory reports.")
    inventory_parser.add_argument("--product", help="Optional product slug for product-scoped inventory.")
    material_pack_parser = subparsers.add_parser("material-pack", help="Build an Agent-readable material pack from inventory outputs.")
    material_pack_parser.add_argument("--product", help="Optional product slug for product-scoped material pack.")
    edit_strategy_parser = subparsers.add_parser("edit-strategy", help="Generate a TikTok product video edit strategy from a material pack.")
    edit_strategy_parser.add_argument("--product", help="Optional product slug for product-scoped edit strategy.")
    timeline_parser = subparsers.add_parser("timeline", help="Generate timeline JSON and CapCut CSV from edit strategy outputs.")
    timeline_parser.add_argument("--product", help="Optional product slug for product-scoped timeline.")
    render_parser = subparsers.add_parser("render", help="Render a minimal reviewable final.mp4 using ffmpeg.")
    render_parser.add_argument("--product", help="Optional product slug for product-scoped render.")
    subparsers.add_parser("subtitles", help="Generate SRT subtitles and burn them into final.mp4.")
    subparsers.add_parser("batch-variants", help="Generate v002-v006 subtitle-burned A/B test videos.")
    experiment_parser = subparsers.add_parser("experiment-init", help="Create manual A/B experiment templates.")
    experiment_parser.add_argument("--product", required=True, help="Product slug for experiment isolation.")
    experiment_parser.add_argument("--sku", required=True, help="SKU slug for experiment isolation.")
    experiment_parser.add_argument("--batch", required=True, help="Batch ID, for example batch_20260520_v002_v006.")

    args = parser.parse_args()
    project_root = Path(__file__).resolve().parent

    if args.command == "inventory":
        try:
            if args.product:
                repo_root = repo_root_from_agent_root(project_root)
                workspace = require_product_workspace(repo_root, args.product)
                result = run_inventory(
                    project_root=project_root,
                    input_root=workspace.assets,
                    output_dir=workspace.outputs / "material_inventory",
                    source_buckets=PRODUCT_ASSET_BUCKETS,
                    report_root=workspace.root,
                )
            else:
                result = run_inventory(project_root)
        except FileNotFoundError as exc:
            print(f"Inventory failed: {exc}")
            raise SystemExit(1) from exc

        inventory = result["inventory"]
        print(f"Material inventory generated: {inventory['file_count']} files")
        print(f"JSON: {result['json_path']}")
        print(f"Markdown: {result['markdown_path']}")
        return

    if args.command == "material-pack":
        try:
            if args.product:
                repo_root = repo_root_from_agent_root(project_root)
                workspace = require_product_workspace(repo_root, args.product)
                result = run_material_pack(
                    project_root=project_root,
                    inventory_path=workspace.outputs / "material_inventory" / "material_inventory.json",
                    brief_sources=[workspace.product_brief, workspace.assets / "scripts"],
                    output_dir=workspace.outputs / "material_pack",
                    report_root=workspace.root,
                )
            else:
                result = run_material_pack(project_root)
        except FileNotFoundError as exc:
            print(f"Material pack failed: {exc}")
            raise SystemExit(1) from exc

        material_pack = result["material_pack"]
        print(f"Material pack generated: {material_pack['material_count']} materials")
        print(f"JSON: {result['json_path']}")
        print(f"Markdown: {result['markdown_path']}")
        return

    if args.command == "edit-strategy":
        try:
            if args.product:
                repo_root = repo_root_from_agent_root(project_root)
                workspace = require_product_workspace(repo_root, args.product)
                result = run_edit_strategy(
                    project_root=project_root,
                    pack_path=workspace.outputs / "material_pack" / "material_pack.json",
                    output_dir=workspace.outputs / "edit_strategy",
                    report_root=workspace.root,
                )
            else:
                result = run_edit_strategy(project_root)
        except FileNotFoundError as exc:
            print(f"Edit strategy failed: {exc}")
            raise SystemExit(1) from exc

        edit_strategy = result["edit_strategy"]
        print(f"Edit strategy generated: {len(edit_strategy['strategy_segments'])} segments")
        print(f"JSON: {result['json_path']}")
        print(f"Markdown: {result['markdown_path']}")
        return

    if args.command == "timeline":
        try:
            if args.product:
                repo_root = repo_root_from_agent_root(project_root)
                workspace = require_product_workspace(repo_root, args.product)
                result = run_timeline(
                    project_root=project_root,
                    strategy_path=workspace.outputs / "edit_strategy" / "edit_strategy.json",
                    material_pack_path=workspace.outputs / "material_pack" / "material_pack.json",
                    output_dir=workspace.outputs / "timelines",
                    report_root=workspace.root,
                )
            else:
                result = run_timeline(project_root)
        except FileNotFoundError as exc:
            print(f"Timeline failed: {exc}")
            raise SystemExit(1) from exc

        timeline = result["timeline"]
        print(f"Timeline generated: {len(timeline['segments'])} segments, {timeline['target_duration_seconds']} seconds")
        print(f"JSON: {result['json_path']}")
        print(f"CSV: {result['csv_path']}")
        return

    if args.command == "render":
        try:
            if args.product:
                repo_root = repo_root_from_agent_root(project_root)
                workspace = require_product_workspace(repo_root, args.product)
                result = run_render(
                    project_root=project_root,
                    timeline_path=workspace.outputs / "timelines" / "timeline.json",
                    material_pack_path=workspace.outputs / "material_pack" / "material_pack.json",
                    output_dir=workspace.outputs / "renders",
                    media_root=workspace.root,
                    report_root=workspace.root,
                )
            else:
                result = run_render(project_root)
        except FileNotFoundError as exc:
            print(f"Render failed: {exc}")
            raise SystemExit(1) from exc

        report = result["report"]
        print(f"Render status: {report['status']}")
        print(f"Final: {result['final_path']}")
        print(f"Report: {result['report_path']}")
        print(report["message"])
        return

    if args.command == "subtitles":
        result = run_subtitles(project_root)
        report = result["report"]
        print(f"Subtitle status: {report['status']}")
        print(f"SRT: {result['srt_path']}")
        print(f"Plan: {result['plan_path']}")
        print(f"Video: {result['subtitled_path']}")
        print(report["message"])
        return

    if args.command == "batch-variants":
        result = run_batch_variants(project_root)
        success_count = sum(1 for item in result["results"] if item["status"] == "success")
        print(f"Batch variants generated: {success_count}/{len(result['results'])} videos")
        print(f"Publish plan: {result['publish_plan_path']}")
        print(f"Feedback template: {result['feedback_path']}")
        for item in result["results"]:
            print(f"{item['version']} {item['key']}: {item['status']} - {item['output_path']}")
        return

    if args.command == "experiment-init":
        repo_root = repo_root_from_agent_root(project_root)
        result = run_experiment_init(repo_root, args.product, args.sku, args.batch)
        print(f"Experiment templates generated: {result['batch_dir']}")
        for path in result["files"].values():
            print(f"- {path}")
        return

    parser.print_help()


if __name__ == "__main__":
    main()
