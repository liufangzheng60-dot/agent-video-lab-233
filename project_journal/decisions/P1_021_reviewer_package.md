# P1-021 Reviewer Package For Claude

Date: 2026-05-23

## 1. P1-021 Goal

Implement the first standalone code-level firewall module and `firewall-check` command without integrating the firewall into existing business generation flows.

This is a preflight and validation layer only.

## 2. Files For Reviewer

- `03_tk_video_agent/main.py`
- `03_tk_video_agent/helpers/firewall.py`
- `03_tk_video_agent/tests/test_firewall.py`
- `03_tk_video_agent/tasks/P1_021_code_level_firewall.md`
- `project_journal/errors/firewall_preflight_dog_bath_hose_blue_batch_20260520_v001_v005.md`

## 3. New Functions

- `validate_product_path`
- `validate_experiment_path`
- `assert_allowed_write_path`
- `assert_do_not_touch_path`
- `generate_preflight_report`
- `generate_firewall_violation_report`
- `run_firewall_check`

## 4. Function Review Notes

### validate_product_path

- Input: `repo_root`, `product_slug`, `candidate_path`
- Output: resolved `Path` or `FirewallViolationError`
- Purpose: ensure a candidate path stays under `products/{product_slug}/`
- Boundary: prevents cross-product contamination and rejects paths outside `repo_root`

### validate_experiment_path

- Input: `repo_root`, `product_slug`, `sku_slug`, `batch_id`, `candidate_path`
- Output: resolved `Path` or `FirewallViolationError`
- Purpose: ensure a path stays under `experiments/{product_slug}/{sku_slug}/{batch_id}/`
- Boundary: prevents cross-product, cross-SKU, and cross-batch contamination

### assert_allowed_write_path

- Input: `repo_root`, `candidate_path`, `allowed_roots`
- Output: resolved `Path` or `FirewallViolationError`
- Purpose: ensure a write target is inside explicit allowlist roots
- Boundary: rejects unapproved roots and paths outside `repo_root`

### assert_do_not_touch_path

- Input: `repo_root`, `candidate_path`, optional `protected_roots`
- Output: resolved `Path` or `FirewallViolationError`
- Purpose: block protected directories and product source files
- Boundary: protects `control_console/`, `00_references/`, `products/*/assets/`, and `products/*/product_brief.md`

### generate_preflight_report

- Input: `repo_root`, `product_slug`, `sku_slug`, `batch_id`, optional `output_dir`
- Output: dict with report path, allowlist, denylist
- Purpose: create a preflight-only report before risky writes
- Boundary: reports are written to `project_journal/errors/`, not `control_console/`

### generate_firewall_violation_report

- Input: `repo_root`, `FirewallViolation`, optional `output_dir`
- Output: report `Path`
- Purpose: create a clear violation report
- Boundary: dangerous writes should stop and leave a trace

### run_firewall_check

- Input: `repo_root`, `product_slug`, `sku_slug`, `batch_id`
- Output: dict with status, preflight report path, and optional violation report
- Purpose: standalone CLI preflight check
- Boundary: does not run or modify business generation commands

## 5. Allowlist Paths

```text
products/{product_slug}/outputs/
experiments/{product_slug}/{sku_slug}/{batch_id}/
project_journal/errors/
```

## 6. Denylist Paths

```text
control_console/
00_references/
products/*/assets/
products/*/product_brief.md
```

P1-021A patch: wildcard denylist patterns are enforced with explicit pattern matching, not by passing wildcard strings to `Path.relative_to()`.

## 7. Current Test Coverage

`03_tk_video_agent/tests/test_firewall.py` covers:

- Product can write to its own outputs.
- Product cannot write to another product folder.
- Real product output path `products/dog_bath_hose/outputs/test.md` is allowed.
- Real product assets path `products/dog_bath_hose/assets/raw_videos/test.mp4` is denied.
- Real product brief path `products/dog_bath_hose/product_brief.md` is denied.
- Product root write `products/dog_bath_hose/test.md` is denied by allowlist.
- Path traversal from `dog_bath_hose` to `pet_nail_trimmer` is denied.
- Relative `repo_root` input still validates correctly.
- Absolute paths outside `repo_root` are denied.
- `control_console/` is protected.
- Experiment can write to its own batch.
- Experiment cannot write to another batch.
- Violation report generation.
- Preflight report generation and preflight-only wording.
- `run_firewall_check` creates a preflight report.
- Existing business command names remain present in `main.py`.

Latest expected validation:

```text
python -m unittest discover -s tests
OK
```

## 8. Uncovered Risks

- The firewall is not yet integrated into business generation commands.
- It does not yet protect every file write in helper modules.
- It does not yet detect whether an experiment batch already contains manually entered data.
- It does not yet inspect Git staged vs unstaged state.
- It does not yet enforce date/version naming.
- It does not yet parse or validate YAML registry rules from `control_console/04_MODULE_REGISTRY.yaml`.
- Symlink behavior has not been separately tested.

## 9. Path Traversal Risk Notes

Implementation notes:

- `repo_root` is resolved in all major validators.
- Candidate paths are resolved before scope checks.
- Paths outside `repo_root` are rejected with `outside_repo_root`.
- Ancestry checks use resolved `Path.relative_to()`.
- Wildcard protected patterns use `fnmatchcase` on resolved repo-relative POSIX paths.

Reviewer should check:

- Whether `Path.resolve()` behavior is acceptable for this local Windows workspace.
- Whether symlink handling should become an explicit follow-up test.
- Whether broad allowlist roots are acceptable before integration into business flows.

## 10. Windows Path Handling Notes

The project runs on Windows PowerShell.

Reviewer should check:

- Drive-letter absolute paths outside the repo are rejected.
- Backslash and forward slash display differences do not affect enforcement.
- Case-insensitive Windows filesystem behavior does not create a practical bypass for current use.

## 11. Old Command Compatibility

Expected: no behavioral change to existing business commands.

`main.py` only adds:

```bash
python main.py firewall-check --product dog_bath_hose --sku blue --batch batch_20260520_v001_v005
```

Existing business commands are not rewired:

- `inventory`
- `material-pack`
- `edit-strategy`
- `timeline`
- `render`
- `subtitles`
- `batch-variants`
- `experiment-init`

## 12. Business Flow Impact

Expected: no business generation flow change.

The firewall is standalone and does not yet block or alter inventory, material-pack, edit-strategy, timeline, render, subtitles, or batch-variants.

## 13. Reviewer Must Check

1. Is `validate_product_path` safe against path traversal and absolute paths?
2. Is `validate_experiment_path` strict enough for product/SKU/batch isolation?
3. Is `assert_allowed_write_path` safe when allowlist contains broad roots?
4. Is `assert_do_not_touch_path` too broad, too narrow, or missing key protected paths?
5. Are wildcard protected patterns now implemented correctly?
6. Is writing reports to `project_journal/errors/` acceptable for preflight and violation reports?
7. Does `run_firewall_check` make it clear that this is preflight-only and not production enforcement?
8. Are Windows path semantics handled safely enough for this workspace?
9. Are tests sufficient before commit, or is another patch required?

## 14. Requested Claude Output Format

Claude should output exactly:

```text
总体结论：pass / pass_with_warnings / fail
必须修复项：
可选优化项：
是否允许 commit：
是否允许进入 P1_022：
```

## 15. P1-021A Patch Summary

Claude Reviewer warning status: patched.

Patched items:

1. Denylist wildcard matching for `products/*/assets/`.
2. Denylist wildcard matching for `products/*/product_brief.md`.
3. Repo-root resolution and outside-root denial.
4. Path traversal denial tests.
5. Preflight-only wording in generated preflight reports.

Business flow remains unchanged. The firewall is still standalone.

## 16. P1-021B Second Reviewer Result

Reviewer result: `pass_with_warnings`

Must-fix items: none.

Commit allowed: yes.

P1_022 allowed: yes, but only as `firewall_integration_plan_only`.

Remaining warnings:

- Symlink behavior is not separately tested.
- `fnmatchcase` case sensitivity on Windows is a future optional hardening point.
- Firewall is still standalone and not integrated into business commands.
