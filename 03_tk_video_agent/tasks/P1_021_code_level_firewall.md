# P1-021 Code-Level Firewall Implementation

Date: 2026-05-23

## Goal

Implement the first standalone code-level firewall module and preflight command without integrating it into all business generation flows.

## Added Command

```bash
python main.py firewall-check --product dog_bath_hose --sku blue --batch batch_20260520_v001_v005
```

## Added Helper

```text
helpers/firewall.py
```

## Implemented Functions

- `validate_product_path`
- `validate_experiment_path`
- `assert_allowed_write_path`
- `assert_do_not_touch_path`
- `generate_preflight_report`
- `generate_firewall_violation_report`
- `run_firewall_check`

## P1-021A Reviewer Patch

Reviewer result: `pass_with_warnings`

Patched warnings:

- Protected product asset paths now use explicit wildcard pattern matching rather than relying on `Path.relative_to()` with wildcard text.
- `products/*/assets/` protects real paths such as `products/dog_bath_hose/assets/raw_videos/test.mp4`.
- `products/*/product_brief.md` protects real paths such as `products/dog_bath_hose/product_brief.md`.
- All major validators resolve `repo_root` and candidate paths before checks.
- Paths resolving outside `repo_root` are denied.
- Preflight report clearly states it is preflight-only and not integrated into production business commands.

## First-Version Boundaries

Allow product-scoped writes only under the active product outputs:

```text
products/{product_slug}/outputs/
```

Allow experiment writes only under the active product/SKU/batch:

```text
experiments/{product_slug}/{sku_slug}/{batch_id}/
```

Protect by default:

```text
control_console/
00_references/
products/*/assets/
products/*/product_brief.md
```

These wildcard patterns are enforced in code with explicit pattern matching.

## Reports

Preflight and violation reports are written under:

```text
project_journal/errors/
```

They are never written under `control_console/`.

## Scope

- Standalone firewall only.
- Existing business generation commands are not rewired.
- No video generation.
- No ffmpeg call.
- No external API call.
- No dependency installation.
- No GitHub push handling.

## P1-021B Second Reviewer Result

Reviewer result: `pass_with_warnings`

Must-fix items: none.

Commit allowed: yes.

Allowed next step: `P1_022_firewall_integration_plan_only` only.

Remaining warnings:

- Symlink behavior is not separately tested; track as future hardening.
- `fnmatchcase` is case-sensitive while Windows filesystems are commonly case-insensitive; track as optional future optimization.
- Firewall remains standalone and does not protect business commands yet.
