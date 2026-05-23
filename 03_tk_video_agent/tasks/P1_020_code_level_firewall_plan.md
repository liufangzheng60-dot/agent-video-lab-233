# P1-020 Code-Level Firewall Plan

Date: 2026-05-23

## Goal

Plan a minimal code-level firewall for the current TikTok Shop product video MVP workflow.

This is plan only. No firewall code is implemented in this task.

## Collaboration Protocol

### Codex = Builder

- Writes code, tests, templates, and execution reports after user approval.
- Must generate a review package after implementing key code.
- Must not approve its own code as final.

### Claude = Reviewer

- Reviews diffs, checks risks, challenges assumptions, and identifies possible regressions.
- May recommend changes, but cannot approve final acceptance.

### User = Owner

- Makes final decisions.
- Approves whether a change is accepted, revised, reverted, or deferred.

## Core Rule

AI cannot self-approve.

Any critical code-level firewall implementation must pass through:

```text
Codex builds -> Codex produces review package -> Claude reviews -> User decides
```

## First-Version Scope

The first firewall should solve real risks in the current commercial loop, not become a complex permission system.

Planned functions:

- `validate_product_path`
- `validate_experiment_path`
- `assert_allowed_write_path`
- `assert_do_not_touch_path`
- `generate_preflight_report`
- `generate_firewall_violation_report`

## Risks To Cover

1. AI writes to the wrong directory.
2. Different `product_slug` folders contaminate each other.
3. Different `sku_slug` or `batch_id` experiment records get mixed.
4. Core strategy files such as `control_console/` are modified without authorization.
5. One module failure blocks unrelated modules or the whole project.

## Planned Function Responsibilities

### validate_product_path

Purpose:

- Confirm that a path belongs to the expected `products/{product_slug}/` root.
- Reject attempts to write into another product folder.

Risk addressed:

- Wrong directory writes.
- Cross-product contamination.

### validate_experiment_path

Purpose:

- Confirm that a path belongs to the expected `experiments/{product_slug}/{sku_slug}/{batch_id}/` root.
- Reject attempts to write into another product, SKU, or batch experiment folder.

Risk addressed:

- Cross-SKU contamination.
- Cross-batch contamination.

### assert_allowed_write_path

Purpose:

- Check that a module writes only under approved output roots.
- Use simple allowlist checks before file creation.

Risk addressed:

- AI writes outside intended outputs.
- Business data lands in untracked locations.

### assert_do_not_touch_path

Purpose:

- Block writes to protected paths unless a task explicitly approves those paths.

Initial denylist:

- `control_console/`
- `00_references/`
- `products/*/assets/`
- `products/*/product_brief.md`
- `experiments/*/*/*/` after manual data entry
- reviewed or published final videos

Risk addressed:

- Strategy tampering.
- Source asset mutation.
- Experiment record corruption.

### generate_preflight_report

Purpose:

- Produce a small report before a risky write task begins.
- List module, intended inputs, intended outputs, allowlist, denylist, and expected generated files.

Risk addressed:

- Hidden path assumptions.
- Unclear write boundaries.

### generate_firewall_violation_report

Purpose:

- Write a clear report when a path validation fails.
- Include blocked path, expected root, module name, reason, and suggested safe next step.

Risk addressed:

- Module failure causing confusion or full project stop.
- Silent failed writes.

## Allowlist Pattern

Product-scoped modules should write only to their own outputs:

```text
products/{product_slug}/outputs/{module_output}/
```

Experiment modules should write only to their own batch:

```text
experiments/{product_slug}/{sku_slug}/{batch_id}/
```

Project journal tasks may append only to explicitly approved journal paths:

```text
project_journal/{area}/
```

## Denylist Pattern

Default protected paths:

```text
control_console/
00_references/
products/*/assets/
products/*/product_brief.md
experiments/*/*/*/
```

Exceptions require explicit user approval in the task.

## Failure Policy

Firewall violations should fail only the current module operation.

They should not stop unrelated modules or invalidate the whole workspace. The module should emit a violation report and return a clear failure message.

## Review Package Requirement

Every critical Codex implementation must include:

1. Modified file list.
2. New function list.
3. Risk solved by each function.
4. Allowlist paths.
5. Denylist paths.
6. Test coverage summary.
7. Whether old command compatibility is affected.
8. Whether business generation flow is changed.
9. `git diff --stat` summary.
10. Questions for Reviewer to focus on.

## Suggested Test Plan

- Product path accepts expected `product_slug`.
- Product path rejects another `product_slug`.
- Experiment path accepts expected product/SKU/batch.
- Experiment path rejects another SKU or batch.
- Denylist blocks `control_console/`.
- Denylist blocks `products/*/assets/`.
- Violation report is generated without external API calls.
- Existing global commands continue to pass tests.

## Not In Scope

- No complex role-based access system.
- No OS-level permissions.
- No external authorization service.
- No automatic Git hooks.
- No video generation.
- No ffmpeg.
- No external API calls.
- No dependency installation.

## Recommended Next Task

`P1_021_code_level_firewall_implementation`

Only start after the user approves implementation.
