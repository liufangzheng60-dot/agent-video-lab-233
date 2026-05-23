# P1-023 Codex Report Compression Policy

Date: 2026-05-23

## Decision

The project folder is the source of truth. Chat responses should be compact by default, while complete task records, review packages, and detailed policies should be stored in `project_journal/` or task files.

## Default Output Rule

Codex should not output long complete reports in chat unless the task is a high-risk node.

## Risk Levels

### Low Risk

Use summary mode only.

Examples:

- Documentation-only updates.
- Template additions.
- Read-only audits with a written report file.
- Small non-business-code metadata updates.

### Medium Risk

Use summary plus Review Package path.

Examples:

- Standalone helper modules.
- New tests.
- New commands that do not change business generation flow.
- Policy implementation not yet integrated into production commands.

### High Risk

Full report is allowed.

High-risk tasks include:

- Firewall integration into business flows.
- Multi-model API integration.
- Modifying `control_console/`.
- Modifying core strategy.
- Batch deleting or moving files.
- Modifying the overall `products/` or `experiments/` structure.
- Connecting OpenAI, Claude, or Seedance APIs.
- Modifying core render logic.
- Automatic TikTok publishing.

## Daily Summary Fields

Chat summaries should include:

- Task name.
- Execution result.
- Modified files.
- New files.
- Generated files.
- Boundary status.
- Whether business logic changed.
- Whether any API was called.
- Whether any video was generated.
- Whether dependencies were installed.
- Test result.
- Key risk.
- Next recommendation.
- Suggested commit.
- Review Package path.

## Full Report Storage

Complete reports should be written to one of:

- `project_journal/decisions/`
- `project_journal/build_log/`
- `project_journal/errors/`
- `03_tk_video_agent/tasks/`

## Token Control Principle

Spend tokens on decisions, risk, and next actions. Store detail in files. Keep chat useful, small, and reviewable.
