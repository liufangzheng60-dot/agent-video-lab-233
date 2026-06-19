"""Command line entry point for the TikTok product video agent."""

from __future__ import annotations

import argparse
from pathlib import Path

from helpers.batch_variants import run_batch_variants
from helpers.agent_factory_harness import (
    run_agent_preflight,
    run_agent_produce_review_pack_dry_run,
    run_vertical_output_audit,
    run_owner_decision_apply,
    run_owner_review_packet,
    run_project_operator_status,
    run_project_resume,
)
from helpers.build_material_pack import run_material_pack
from helpers.experiment_racing import run_experiment_init
from helpers.experiment_record import run_experiment_record
from helpers.firewall import run_firewall_check
from helpers.generate_edit_strategy import run_edit_strategy
from helpers.generate_timeline import run_timeline
from helpers.inventory import PRODUCT_ASSET_BUCKETS, run_inventory
from helpers.material_batch import run_material_batch
from helpers.product_workspace import repo_root_from_agent_root, require_product_workspace
from helpers.contact_sheet import run_contact_sheet
from helpers.owner_firewall import run_owner_firewall
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
    material_batch_parser = subparsers.add_parser("material-batch", help="Create clip manifest and tag template for one raw video batch.")
    material_batch_parser.add_argument("--product", required=True, help="Product slug for product-scoped material batching.")
    material_batch_parser.add_argument("--sku", required=True, help="SKU slug for stable clip IDs.")
    material_batch_parser.add_argument("--material-batch", required=True, help="Material batch ID, for example batch_20260615_001.")
    contact_sheet_parser = subparsers.add_parser("contact-sheet", help="Generate jpg contact sheets from an existing clip manifest.")
    contact_sheet_parser.add_argument("--product", required=True, help="Product slug for product-scoped contact sheets.")
    contact_sheet_parser.add_argument("--sku", required=True, help="SKU slug for report labeling.")
    contact_sheet_parser.add_argument("--material-batch", required=True, help="Material batch ID, for example batch_20260615_001.")
    subparsers.add_parser("subtitles", help="Generate SRT subtitles and burn them into final.mp4.")
    subparsers.add_parser("batch-variants", help="Generate v002-v006 subtitle-burned A/B test videos.")
    experiment_parser = subparsers.add_parser("experiment-init", help="Create manual A/B experiment templates.")
    experiment_parser.add_argument("--product", required=True, help="Product slug for experiment isolation.")
    experiment_parser.add_argument("--sku", required=True, help="SKU slug for experiment isolation.")
    experiment_parser.add_argument("--batch", required=True, help="Batch ID, for example batch_20260520_v002_v006.")
    experiment_record_parser = subparsers.add_parser("experiment-record", help="Record manual TikTok metrics and generate analysis.")
    experiment_record_parser.add_argument("--product", required=True, help="Product slug for experiment isolation.")
    experiment_record_parser.add_argument("--sku", required=True, help="SKU slug for experiment isolation.")
    experiment_record_parser.add_argument("--batch", required=True, help="Batch ID for experiment isolation.")
    experiment_record_parser.add_argument("--input", required=True, help="Manual input markdown path relative to the batch directory.")
    firewall_parser = subparsers.add_parser("firewall-check", help="Run standalone path firewall preflight checks.")
    firewall_parser.add_argument("--product", required=True, help="Product slug for path isolation checks.")
    firewall_parser.add_argument("--sku", required=True, help="SKU slug for experiment isolation checks.")
    firewall_parser.add_argument("--batch", required=True, help="Batch ID for experiment isolation checks.")
    agent_preflight_parser = subparsers.add_parser("agent-preflight", help="Run P12 Agent Factory preflight without generating videos.")
    agent_preflight_parser.add_argument("--product", required=True, help="Product slug for product-scoped runtime.")
    agent_preflight_parser.add_argument("--sku", required=True, help="SKU slug for runtime state.")
    agent_preflight_parser.add_argument("--material-batch", required=True, help="Material batch ID, for example batch_20260617_001.")
    agent_preflight_parser.add_argument("--variants", required=True, type=int, help="Requested variant count.")
    agent_dry_run_parser = subparsers.add_parser(
        "agent-produce-review-pack-dry-run",
        help="Simulate the P12 Agent Factory state machine without rendering, TTS, or VLM calls.",
    )
    agent_dry_run_parser.add_argument("--product", required=True, help="Product slug for product-scoped runtime.")
    agent_dry_run_parser.add_argument("--sku", required=True, help="SKU slug for runtime state.")
    agent_dry_run_parser.add_argument("--material-batch", required=True, help="Material batch ID, for example batch_20260617_001.")
    agent_dry_run_parser.add_argument("--variants", required=True, type=int, help="Requested variant count.")
    owner_firewall_parser = subparsers.add_parser("owner-firewall", help="Validate Owner Firewall decisions in dry-run mode.")
    owner_firewall_parser.add_argument("--product", required=True, help="Product slug for product-scoped runtime.")
    owner_firewall_parser.add_argument("--sku", required=True, help="SKU slug for runtime state.")
    owner_firewall_parser.add_argument("--material-batch", required=True, help="Material batch ID, for example batch_20260617_001.")
    owner_firewall_parser.add_argument("--decision-file", required=True, help="Owner decision JSON path or filename in the agent output dir.")
    owner_firewall_parser.add_argument("--dry-run", action="store_true", help="Required for P12B; no destructive action is allowed.")
    operator_status_parser = subparsers.add_parser("project-operator-status", help="Show P12C autonomous Codex operator status.")
    operator_status_parser.add_argument("--product", required=True, help="Product slug for product-scoped runtime.")
    operator_status_parser.add_argument("--sku", required=True, help="SKU slug for runtime state.")
    operator_status_parser.add_argument("--material-batch", required=True, help="Material batch ID, for example batch_20260617_001.")
    owner_review_packet_parser = subparsers.add_parser("owner-review-packet", help="Print the pending Owner Review Packet if one exists.")
    owner_review_packet_parser.add_argument("--product", required=True, help="Product slug for product-scoped runtime.")
    owner_review_packet_parser.add_argument("--sku", required=True, help="SKU slug for runtime state.")
    owner_review_packet_parser.add_argument("--material-batch", required=True, help="Material batch ID, for example batch_20260617_001.")
    owner_decision_apply_parser = subparsers.add_parser("owner-decision-apply", help="Apply an explicit Owner decision to a pending checkpoint.")
    owner_decision_apply_parser.add_argument("--product", required=True, help="Product slug for product-scoped runtime.")
    owner_decision_apply_parser.add_argument("--sku", required=True, help="SKU slug for runtime state.")
    owner_decision_apply_parser.add_argument("--material-batch", required=True, help="Material batch ID, for example batch_20260617_001.")
    owner_decision_apply_parser.add_argument("--decision-file", required=True, help="Owner decision JSON path.")
    project_resume_parser = subparsers.add_parser("project-resume", help="Show the next safe resume instruction for the project operator.")
    project_resume_parser.add_argument("--product", required=True, help="Product slug for product-scoped runtime.")
    project_resume_parser.add_argument("--sku", required=True, help="SKU slug for runtime state.")
    project_resume_parser.add_argument("--material-batch", required=True, help="Material batch ID, for example batch_20260617_001.")
    vertical_audit_parser = subparsers.add_parser("vertical-output-audit", help="Audit true 9:16 final and segment output compliance without modifying video.")
    vertical_audit_parser.add_argument("--product", required=True, help="Product slug for product-scoped runtime.")
    vertical_audit_parser.add_argument("--sku", required=True, help="SKU slug for runtime state.")
    vertical_audit_parser.add_argument("--material-batch", required=True, help="Material batch ID, for example batch_20260617_001.")
    vertical_audit_parser.add_argument("--input", required=True, help="Video path or JSON manifest path to audit.")

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
                    voiceover_dir=workspace.assets / "voiceovers",
                    report_dir=workspace.outputs / "reports",
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

    if args.command == "material-batch":
        repo_root = repo_root_from_agent_root(project_root)
        result = run_material_batch(repo_root, args.product, args.sku, args.material_batch)
        report = result["report"]
        print(f"Material batch processed: {report['total_video_files']} clips")
        print(f"Manifest CSV: {result['manifest_csv_path']}")
        print(f"Manifest JSON: {result['manifest_json_path']}")
        print(f"Tags template: {result['clip_tags_template_path']}")
        print(f"Report: {result['report_path']}")
        return

    if args.command == "contact-sheet":
        try:
            repo_root = repo_root_from_agent_root(project_root)
            result = run_contact_sheet(repo_root, args.product, args.sku, args.material_batch)
        except FileNotFoundError as exc:
            print(f"Contact sheet failed: {exc}")
            raise SystemExit(1) from exc
        report = result["report"]
        print(f"Contact sheets generated: {report['generated_contact_sheets']}/{report['total_manifest_clips']}")
        print(f"Contact sheet dir: {result['contact_sheets_dir']}")
        print(f"Report: {result['report_path']}")
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

    if args.command == "experiment-record":
        try:
            repo_root = repo_root_from_agent_root(project_root)
            result = run_experiment_record(repo_root, args.product, args.sku, args.batch, args.input)
        except FileNotFoundError as exc:
            print(f"Experiment record failed: {exc}")
            raise SystemExit(1) from exc
        print(f"Experiment record updated: {result['performance_log']}")
        print(f"Analysis: {result['analysis_path']}")
        print(f"Decision status: {result['analysis']['decision_status']}")
        return

    if args.command == "firewall-check":
        repo_root = repo_root_from_agent_root(project_root)
        result = run_firewall_check(repo_root, args.product, args.sku, args.batch)
        print(f"Firewall check status: {result['status']}")
        if result["preflight_report"]:
            print(f"Preflight report: {result['preflight_report']}")
        if result["violation_report"]:
            print(f"Violation report: {result['violation_report']}")
        return

    if args.command == "agent-preflight":
        repo_root = repo_root_from_agent_root(project_root)
        result = run_agent_preflight(repo_root, args.product, args.sku, args.material_batch, args.variants)
        print(f"Agent preflight status: {result['git_report']['status']}")
        print(f"Output dir: {result['output_dir']}")
        print(f"Raw videos exist: {result['media_report']['raw_videos_exists']}")
        print(f"Raw video count: {result['media_report']['raw_video_count']}")
        print("No videos were generated.")
        return

    if args.command == "agent-produce-review-pack-dry-run":
        repo_root = repo_root_from_agent_root(project_root)
        result = run_agent_produce_review_pack_dry_run(repo_root, args.product, args.sku, args.material_batch, args.variants)
        print("Agent review pack dry-run complete.")
        print(f"Output dir: {result['output_dir']}")
        print(f"Variants planned: {len(result['variant_ids'])}")
        print("No render, TTS, VLM provider call, deletion, or publishing action was executed.")
        return

    if args.command == "owner-firewall":
        if not args.dry_run:
            print("Owner firewall failed: P12B only allows --dry-run.")
            raise SystemExit(1)
        repo_root = repo_root_from_agent_root(project_root)
        output_dir = repo_root / "products" / args.product / "outputs" / "agent_factory" / args.material_batch
        decision_path = Path(args.decision_file)
        if not decision_path.is_absolute():
            local_decision = output_dir / decision_path
            decision_path = local_decision if local_decision.exists() else Path(args.decision_file)
        result = run_owner_firewall(
            decision_file=decision_path,
            audit_log_path=output_dir / "owner_firewall_audit_log.md",
            result_path=output_dir / "owner_firewall_result.json",
            product=args.product,
            sku=args.sku,
            material_batch=args.material_batch,
            dry_run=args.dry_run,
        )
        print(f"Owner firewall dry-run status: {result['status']}")
        print(f"Audit log: {output_dir / 'owner_firewall_audit_log.md'}")
        print(f"Result: {output_dir / 'owner_firewall_result.json'}")
        return

    if args.command == "project-operator-status":
        repo_root = repo_root_from_agent_root(project_root)
        result = run_project_operator_status(repo_root, args.product, args.sku, args.material_batch)
        print(f"current_goal: {result['current_goal']}")
        print(f"active_task: {result['active_task']}")
        print(f"current_stage: {result['current_stage']}")
        print(f"git state: {result['git_state']}")
        print(f"batch2_raw_count: {result['batch2_raw_count']}")
        print(f"9x16_hard_rule_status: {result['9x16_hard_rule_status']}")
        print(f"awaiting_owner_review: {result['awaiting_owner_review']}")
        print(f"pending_checkpoint: {result['pending_checkpoint']}")
        print(f"last_owner_decision: {result['last_owner_decision']}")
        print(f"last_safe_commit: {result['last_safe_commit']}")
        print(f"next_recommended_action: {result['next_recommended_action']}")
        return

    if args.command == "owner-review-packet":
        repo_root = repo_root_from_agent_root(project_root)
        result = run_owner_review_packet(repo_root, args.product, args.sku, args.material_batch)
        print(result["packet"].rstrip())
        return

    if args.command == "owner-decision-apply":
        repo_root = repo_root_from_agent_root(project_root)
        result = run_owner_decision_apply(repo_root, args.product, args.sku, args.material_batch, Path(args.decision_file))
        if result["status"] != "pass":
            print(f"Owner decision apply failed: {result}")
            raise SystemExit(1)
        print(f"Owner decision applied: {result['resume_instruction']}")
        return

    if args.command == "project-resume":
        repo_root = repo_root_from_agent_root(project_root)
        result = run_project_resume(repo_root, args.product, args.sku, args.material_batch)
        print(f"active_task: {result['active_task']}")
        print(f"current_stage: {result['current_stage']}")
        print(f"awaiting_owner_review: {result['awaiting_owner_review']}")
        print(f"pending_checkpoint: {result['pending_checkpoint']}")
        print(f"last_owner_decision: {result['last_owner_decision']}")
        print(f"resume_instruction: {result['resume_instruction']}")
        print(f"next_safe_action: {result['next_safe_action']}")
        return

    if args.command == "vertical-output-audit":
        repo_root = repo_root_from_agent_root(project_root)
        result = run_vertical_output_audit(repo_root, args.product, args.sku, args.material_batch, Path(args.input))
        report = result["report"]
        print(f"variant_id: {report['variant_id']}")
        print(f"final_container_pass: {report['final_container_pass']}")
        print(f"segment_count: {report['segment_count']}")
        print(f"segments_failed: {report['segments_failed']}")
        print(f"failed_segment_ids: {report['failed_segment_ids']}")
        print(f"failed_time_ranges: {report['failed_time_ranges']}")
        print(f"replacement_required: {report['auto_replacement_required']}")
        print(f"publish_allowed: {report['publish_allowed']}")
        print(f"release_allowed: {report['release_allowed']}")
        print(f"report_path: {result['report_path']}")
        return

    parser.print_help()


if __name__ == "__main__":
    main()
