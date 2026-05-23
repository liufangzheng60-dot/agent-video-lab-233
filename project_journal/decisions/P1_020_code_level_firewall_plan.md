# P1-020 Code-Level Firewall Plan Decision

Date: 2026-05-23

## Decision

Plan a minimal code-level firewall before allowing more product pipelines or model roles to write into shared workspace areas.

## Owner / Builder / Reviewer Protocol

- User = Owner and final decision maker.
- Codex = Builder and implementation reporter.
- Claude = Reviewer for diff review, risk checks, and challenge questions.

AI cannot self-approve.

Approved review sequence for critical code changes:

```text
Codex builds -> Codex produces review package -> Claude reviews -> User decides
```

## Why This Matters

The project is now multi-product, multi-SKU, multi-batch, and multi-model. The main risk is no longer only whether code runs. The main risk is whether an AI module writes into the wrong business context.

## First-Version Firewall Scope

The first implementation should stay small and practical:

- `validate_product_path`
- `validate_experiment_path`
- `assert_allowed_write_path`
- `assert_do_not_touch_path`
- `generate_preflight_report`
- `generate_firewall_violation_report`

## Risks Covered

1. AI writes to the wrong directory.
2. Different `product_slug` folders contaminate each other.
3. Different `sku_slug` or `batch_id` experiment records get mixed.
4. Core strategy files such as `control_console/` are modified without authorization.
5. A single module failure stops unrelated work.

## Commercial Boundary

This firewall is not a complex permission system. It protects the active commercial MVP loop:

```text
product assets -> inventory -> material pack -> strategy -> timeline -> render -> subtitles -> batch variants -> experiment data
```

## Required Review Package

Every critical Builder implementation must include:

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

## Proposed Allowlist

```text
products/{product_slug}/outputs/
experiments/{product_slug}/{sku_slug}/{batch_id}/
project_journal/{approved_area}/
```

## Proposed Denylist

```text
control_console/
00_references/
products/*/assets/
products/*/product_brief.md
experiments/*/*/*/ after manual data entry
reviewed or published final videos
```

## Next Step

Prepare `P1_021_code_level_firewall_implementation` only after explicit user approval.

The implementation should include focused unit tests and should not change business generation behavior unless explicitly approved.
