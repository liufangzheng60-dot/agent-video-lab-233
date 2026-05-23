# Next Action Queue

## Active Queue

1. Wait for manual Reviewer check of `P1_021_code_level_firewall`.
2. User decides one of: `commit`, `patch`, or `rollback`.
3. User places dog bath hose blue SKU assets into `products/dog_bath_hose/assets/`.
4. Run product-level inventory for `dog_bath_hose`.
5. Generate product-level material pack.
6. Generate product-level edit strategy.
7. Generate product-level timeline.
8. Render product-level review video only after source mp4 exists.
9. Continue subtitles and batch variants only after product-level render succeeds.

## Multimodel Review Policy

- Codex = Builder.
- Claude = Reviewer.
- User = Owner.
- AI cannot self-approve.
- Do not connect Claude API now.
- Use Claude Web or App manually for the first review cycles.
- Consider `P2_claude_reviewer_api_module` only after 3-5 stable manual review cycles.

## Report Compression Policy

The project folder is the source of truth. Codex reports should stay compact in chat and store full detail in `project_journal/` or task files.

Low-risk tasks should use summary mode only. Medium-risk tasks should use summary plus Review Package path. High-risk tasks may use full reports.

Daily Codex summary fields:

- Task name.
- Execution result.
- Modified files.
- New files.
- Generated files.
- Boundary status.
- Business logic changed.
- API called.
- Video generated.
- Dependencies installed.
- Test status.
- Key risks.
- Next recommendation.
- Suggested commit.
- Review Package path.

High-risk tasks that may justify a full chat report:

- Firewall integration into business flows.
- Multi-model API integration.
- Modifying `control_console/`.
- Modifying core strategy.
- Batch deleting or moving files.
- Modifying the overall `products/` or `experiments/` structure.
- Connecting OpenAI, Claude, or Seedance APIs.
- Modifying core render logic.
- Automatic TikTok publishing.

Claude reviews should stay compact:

- `pass` / `pass_with_warnings` / `fail`.
- Must-fix items.
- Optional improvements.
- Whether commit is allowed.

## Parking Lot

- Product-level `subtitles --product`.
- Product-level `batch-variants --product`.
- Clip library and keyframe extraction.
