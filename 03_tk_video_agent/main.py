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
    run_p12e_semantic_compiler_preflight,
    run_p12h_zhipu_calibration_preflight,
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
from helpers.p12d_preflight import run_p12d_asset_ready_preflight
from helpers.p12d_three_variant_runner import run_three_variant_validation
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
    project_resume_parser.add_argument("--execute", action="store_true", help="Execute an approved resume path when implemented; currently remains owner-gated.")
    vertical_audit_parser = subparsers.add_parser("vertical-output-audit", help="Audit true 9:16 final and segment output compliance without modifying video.")
    vertical_audit_parser.add_argument("--product", required=True, help="Product slug for product-scoped runtime.")
    vertical_audit_parser.add_argument("--sku", required=True, help="SKU slug for runtime state.")
    vertical_audit_parser.add_argument("--material-batch", required=True, help="Material batch ID, for example batch_20260617_001.")
    vertical_audit_parser.add_argument("--input", required=True, help="Video path or JSON manifest path to audit.")
    p12d_parser = subparsers.add_parser("p12d-preflight", help="运行 P12D 素材就绪预检，并停在 Owner 选择界面。")
    p12d_parser.add_argument("--product", required=True, help="Product slug.")
    p12d_parser.add_argument("--sku", required=True, help="SKU slug.")
    p12d_parser.add_argument("--material-batch", required=True, help="Material batch ID.")
    p12d_three_parser = subparsers.add_parser("p12d-run-three-variant", help="执行 Owner 已批准的 P12D 三条真实视频小批验证。")
    p12d_three_parser.add_argument("--product", required=True, help="Product slug.")
    p12d_three_parser.add_argument("--sku", required=True, help="SKU slug.")
    p12d_three_parser.add_argument("--material-batch", required=True, help="Material batch ID.")
    p12e_parser = subparsers.add_parser("p12e-preflight", help="运行 P12E 三段式语义编译器预检，并停在真实 VLM Owner Gate。")
    p12e_parser.add_argument("--product", required=True, help="Product slug.")
    p12e_parser.add_argument("--sku", required=True, help="SKU slug.")
    p12e_parser.add_argument("--material-batch", required=True, help="Material batch ID.")
    p12h_parser = subparsers.add_parser("p12h-calibration", help="运行 P12H Comet 只读审计与智谱 glm-4.6v Calibration 门禁预检。")
    p12h_parser.add_argument("--product", required=True, help="Product slug.")
    p12h_parser.add_argument("--sku", required=True, help="SKU slug.")
    p12h_parser.add_argument("--material-batch", required=True, help="Material batch ID.")

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

    if args.command == "p12d-preflight":
        repo_root = repo_root_from_agent_root(project_root)
        result = run_p12d_asset_ready_preflight(repo_root, args.product, args.sku, args.material_batch)
        if result["status"] == "asset_shortage":
            count = result["raw_video_count"]
            print("OWNER_ACTION_REQUIRED")
            print(f"当前原片数量：{count}")
            print("最低要求：50")
            print(f"缺口数量：{50 - count}")
            print(f"目标目录：{result['raw_dir']}")
            print("已完成检查：Git Safety、Media Asset Guard、原片数量统计")
            print("请选择：")
            print("A. 补充原片至 50 条后重新检查")
            print("B. 用当前数量做 3 条缩减版 Preflight，不真实渲染")
            print("C. 指定新的素材目录")
            print("D. 停止")
            print("Codex 推荐：选择 A")
            print("推荐理由：当前目标是 12 条真实批次 Preflight，少于 50 条会导致替换池和矩阵差异化失真。")
            return
        if result["status"] == "git_safety_blocked":
            print("Git 安全检查失败：已阻止继续真实生产。")
            print(result)
            raise SystemExit(1)
        if result["status"] == "resource_safety_blocked":
            benchmark = result["benchmark"]
            resource = result["resource_report"]
            print("OWNER_REVIEW_REQUIRED")
            print("检查点类型：GATE_RESOURCE_SAFETY_OVERRIDE")
            print("当前资源数据：两素材 benchmark 未通过，真实 Batch 仍被阻止。")
            print(f"首次 benchmark：{benchmark.get('first_attempt', benchmark)}")
            print(f"降级后 benchmark：{benchmark if benchmark.get('first_attempt') else '未发生降级或降级未执行'}")
            print(f"CPU P95：{benchmark.get('cpu_p95')}")
            print(f"内存 P95：{benchmark.get('memory_p95')}")
            print(f"可用磁盘：{resource.get('disk_free_gb')} GB")
            print(f"供电状态：{resource.get('power_status')}")
            print("请选择：")
            print("A. 分批运行")
            print("B. 进一步降低 QC draft 规格")
            print("C. 更换设备")
            print("D. 停止")
            print("Codex 推荐：A")
            print("推荐理由：不提高并发、不放宽 9:16，优先用更小批次降低资源风险。")
            return
        if result["status"] == "owner_review_required":
            checkpoint = result["checkpoint"]
            benchmark = result["benchmark"]
            resource = result["resource_report"]
            real_plan = result["real_plan"]
            print("OWNER_REVIEW_REQUIRED")
            print(f"检查点编号：{checkpoint['checkpoint_id']}")
            print(f"当前目标：{checkpoint['current_goal']}")
            print(f"原片数量：{result['raw_video_count']}")
            print(f"素材盘点结果：ffprobe 通过 {result['inventory']['probe_pass_count']} / {result['inventory']['raw_video_count']}")
            print(f"资源基准结果：{benchmark.get('result')}")
            print(f"CPU P95：{benchmark.get('cpu_p95')}")
            print(f"内存 P95：{benchmark.get('memory_p95')}")
            print(f"可用磁盘：{resource.get('disk_free_gb')} GB")
            print(f"供电状态：{resource.get('power_status')}")
            print(f"9:16 回归结果：{result['vertical_report'].get('result')}")
            print(f"可规划 Variant 数量：{real_plan.get('planned_variants')}")
            print(f"矩阵差异化结果：{real_plan.get('diversity_policy', {}).get('result')}")
            print(f"替换池结果：候选 {real_plan.get('planned_variants')} 条计划已生成")
            print(f"预计运行时长：{real_plan.get('estimated_runtime')}")
            print(f"预计磁盘增长：{real_plan.get('estimated_disk_growth')}")
            print("是否使用真实 VLM：否")
            print("是否自动发布：否")
            print(f"主要风险：{'; '.join(checkpoint['main_risks'])}")
            print("请选择一个方案：")
            print("A. 批准正式运行 12 条本地 Batch2 视频")
            print("B. 先运行 3 条真实视频小批验证")
            print("C. 修订计划后重新 Preflight")
            print("D. 停止")
            print("Codex 推荐方案：B")
            print("推荐理由：先用 3 条真实视频验证资源、9:16 与替换闭环，可以降低第一次真实批量运行的时间和风险。")
            print("Owner 可直接回复：选择 A / 选择 B / 选择 C，并补充修改要求 / 选择 D")
            return

    if args.command == "p12d-run-three-variant":
        repo_root = repo_root_from_agent_root(project_root)
        result = run_three_variant_validation(repo_root, args.product, args.sku, args.material_batch)
        if result["status"] != "owner_review_required":
            print(f"三条真实视频验证未完成：{result}")
            raise SystemExit(1)
        summary = result["summary"]
        print("OWNER_REVIEW_REQUIRED")
        print("检查点类型：GATE_THREE_VARIANT_VALIDATION_REVIEW")
        print(f"3 条视频输出目录：{summary['output_dir']}")
        print(f"成功、Hold、失败数量：{summary['success_count']} / {summary['hold_count']} / {summary['failed_count']}")
        print(f"每条实际运行时长：{ {item['variant_id']: item['elapsed_sec'] for item in summary['variant_results']} }")
        print(f"CPU P50 / P95：{summary['cpu_p50']} / {summary['cpu_p95']}")
        print(f"内存 P50 / P95：{summary['memory_p50']} / {summary['memory_p95']}")
        print(f"磁盘增长：{summary['disk_growth_bytes']} bytes")
        print(f"9:16 最终容器结果：通过 {summary['final_container_pass_count']} / 3")
        print(f"Segment-level 审计结果：失败 segment 数 {summary['segment_failed_count']}")
        print(f"横屏嵌套、黑边、拉伸失败数量：{summary['horizontal_inset_failures']} / {summary['black_bar_failures']} / {summary['stretch_failures']}")
        print(f"自动替换次数：{summary['auto_replacement_count']}")
        print(f"Hook / Body / Proof / CTA 重复率：{summary['hook_repeat_rate']} / {summary['body_repeat_rate']} / {summary['proof_repeat_rate']} / {summary['cta_repeat_rate']}")
        print(f"Body Structure 数量：{summary['body_structure_count']}")
        print(f"音频生成结果：成功 {summary['audio_success_count']} / 3")
        print(f"Video Stream Copy 结果：成功 {summary['video_stream_copy_success_count']} / 3")
        print(f"Git 媒体数量：{summary['git_media_count']}")
        print(f"raw_videos 修改数量：{summary['raw_videos_modified_count']}")
        print(f"关键问题：{'; '.join(summary['main_risks'])}")
        print("继续剩余 9 条的可选方案：")
        print("A. 批准继续剩余 9 条")
        print("B. 先人工审查这 3 条，再修订计划")
        print("C. 停止")
        print("Codex 推荐：B")
        return

    if args.command == "p12e-preflight":
        repo_root = repo_root_from_agent_root(project_root)
        result = run_p12e_semantic_compiler_preflight(repo_root, args.product, args.sku, args.material_batch)
        if result["status"] != "owner_review_required":
            print(f"P12E 预检被阻止：{result}")
            raise SystemExit(1)
        checkpoint = result["checkpoint"]
        estimate = result["vlm_estimate"]
        tts = result["tts_preflight"]
        print("OWNER_REVIEW_REQUIRED")
        print(f"检查点编号：{checkpoint['checkpoint_id']}")
        print(f"检查点类型：{checkpoint['checkpoint_type']}")
        print(f"当前目标：{checkpoint['current_goal']}")
        print("已完成架构：美区英文输出合同、资产候选窗口索引、两级 VLM Schema/缓存/预算估算、三段式 Story Compiler")
        print(f"旧自由 Planner 冻结状态：{checkpoint['old_free_planner_frozen']}")
        print(f"P12D 负面样本登记结果：{len(checkpoint['p12d_negative_samples'])} 条")
        print(f"Edge-TTS 安装结果：{result['edge_status']}")
        print(f"可用 en-US Voice：{tts['contract']['allowed_voices']}")
        print(f"最终选择 Voice：{checkpoint['selected_voice']}")
        print(f"SAPI 静默回退状态：已禁止，allow_windows_sapi_fallback={tts['allow_windows_sapi_fallback']}")
        print(f"美区输出合同结果：{tts['preflight_result']}")
        print(f"候选窗口数量：{result['candidate_window_count']}")
        print(f"Golden Pilot 候选原片数量：{result['golden_pilot_source_count']}")
        print(f"Pass 1 预计请求数：{estimate['pass1_estimated_requests']}")
        print(f"Pass 2 最大请求数：{estimate['pass2_max_requests']}")
        print(f"预计上传关键帧数量：{estimate['estimated_keyframe_uploads']}")
        print(f"预计上传短视频数量：{estimate['estimated_video_proxy_uploads']}")
        print(f"是否上传音频：{estimate['upload_audio']}")
        print(f"预计输入 Token：{estimate['estimated_input_tokens']}")
        print(f"预计输出 Token：{estimate['estimated_output_tokens']}")
        print(f"预计费用区间：{estimate['estimated_cost_range']}")
        print(f"推荐 Provider：{estimate['provider']}")
        print(f"推荐 Model：{estimate['model']}（真实调用前必须由配置和账号可用模型确认）")
        print(f"推荐 media_resolution：{estimate['media_resolution']}")
        print(f"max_calls：{estimate['max_calls']}")
        print(f"max_budget：{estimate['max_budget']}")
        print(f"缓存策略：cache_enabled={estimate['cache_enabled']}，同缓存键成功后不重复上传或收费调用")
        print("上传的数据：低分辨率关键帧条带；仅对低置信度或动作 shortlist 上传短视频代理")
        print("不上传的数据：完整原片、原片音频、高分辨率母文件、与 Golden Pilot 无关素材")
        print(f"主要风险：{'; '.join(checkpoint['main_risks'])}")
        print("测试结果：见本次 Codex 最终摘要")
        print("回归测试结果：见本次 Codex 最终摘要")
        print("Git 提交：见本次 Codex 最终摘要")
        print("Git 推送结果：见本次 Codex 最终摘要")
        print("请选择：")
        print("A. 批准 Golden Pilot 的关键帧粗标签和必要短视频复核")
        print("B. 只批准关键帧粗标签")
        print("C. 不启用 VLM，停止自动语义剪辑方向")
        print("D. 修订 Provider、Model、预算或上传范围")
        print("Codex 推荐方案：A")
        print("推荐理由：Pass 1 控制成本获取粗标签，Pass 2 只覆盖动作完整性和低置信度 shortlist，能避免再次无语义乱剪。")
        print("Owner 可以直接回复：选择 A / 选择 B / 选择 C / 选择 D，并补充修改要求")
        return

    if args.command == "p12h-calibration":
        repo_root = repo_root_from_agent_root(project_root)
        result = run_p12h_zhipu_calibration_preflight(repo_root, args.product, args.sku, args.material_batch)
        if result["status"] != "owner_review_required":
            print(f"P12H 被阻止：{result}")
            raise SystemExit(1)
        checkpoint = result["checkpoint"]
        package = result["package_report"]
        env = result["env_report"]
        plan = result["request_plan"]
        paths = checkpoint["report_paths"]
        print("OWNER_REVIEW_REQUIRED")
        print(f"检查点编号：{checkpoint['checkpoint_id']}")
        print(f"实际Provider：{checkpoint['actual_provider']}")
        print(f"实际Model：{checkpoint['actual_model']}")
        print(f"API端点：{checkpoint['api_endpoint']}")
        print(f"SDK名称和版本：{env['sdk_status']}")
        print(f"API Key状态：{env['python_key_status']}")
        print(f"Comet克隆结果：{checkpoint['comet_clone_result']}")
        print(f"Comet参考审计结果：{checkpoint['comet_reference_audit_result']}")
        print("Comet是否被安装或接入：否")
        print(f"资源包名称：{package['resource_pack_name']}")
        print(f"资源包有效期：{package['package_expiration']}")
        print(f"资源包是否覆盖glm-4.6v：{package['glm_4_6v_included']}")
        print(f"图片Token是否覆盖：{package['image_tokens_included']}")
        print(f"视频Token是否覆盖：{package['video_tokens_included']}")
        print(f"套餐外现金扣费风险：{package['cash_charge_possible']}")
        print(f"Calibration样本数量：{plan['planned_request_count']}")
        print("图片调用成功/失败：0 / 0，因 API Key 或资源包门禁未满足，未调用")
        print("视频调用成功/失败：0 / 0，因 API Key 或资源包门禁未满足，未调用")
        print("Function Call可用性：未探测")
        print("最终结构化输出策略：未调用前保持候选策略，优先 Function Call，失败后 JSON-only Prompt")
        print("Schema成功率：0.0，未执行真实 Calibration")
        print("产品状态识别结果：未执行")
        print("狗使用动作识别结果：未执行")
        print("动作完整性判断结果：未执行")
        print("脚本角色判断结果：未执行")
        print("缓存测试结果：已生成 cache_key 计划，未产生真实调用")
        print("输入Token：0")
        print("输出Token：0")
        print("视觉Token：0")
        print("视频Token：0")
        print("资源包扣减：未执行")
        print("现金费用：0")
        print("平均请求延迟：未执行")
        print("失败和重试次数：0")
        print("主要问题：缺少 ZAI_API_KEY/ZHIPUAI_API_KEY；资源包覆盖和现金扣费风险需要 Owner 在智谱控制台确认")
        print(f"报告路径：{paths}")
        print("请选择：")
        print("A. Calibration通过，批准glm-4.6v运行完整Golden Pilot标签")
        print("B. 只批准glm-4.6v运行Pass 1关键帧标签")
        print("C. 修订Prompt或Schema后重新Calibration")
        print("D. 修改视频代理输入方式后重新Calibration")
        print("E. 停止智谱VLM方向")
        print("Codex 推荐：先不要选择 A/B；请先在本机设置 ZAI_API_KEY，并在智谱控制台确认资源包覆盖和套餐外现金扣费风险，再重新运行 Calibration。")
        print("安全设置示例：$env:ZAI_API_KEY = \"在本机填写，不要发送到对话中\"")
        return

    parser.print_help()


if __name__ == "__main__":
    main()
