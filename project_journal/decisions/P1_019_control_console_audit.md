# P1-019 Control Console Audit

Date: 2026-05-22

## 1. Overall Conclusion

`pass_with_warnings`

The current `control_console/`, `project_journal/`, and `scenario_keyword_mining/` documents are aligned with the user's core strategy:

- The user is explicitly defined as the highest decision maker.
- Models are treated as bounded execution or research modules.
- `control_console/` is read-only by default.
- Product, SKU, batch, and module boundaries are documented.
- Reference mining is framed as scene, pain, emotion, Hook hypothesis, demo logic, and business reasoning extraction, not direct imitation.

No strategy tampering or explicit model overreach was found.

## 2. Strategy Tampering

Result: `not_found`

No audited file appears to replace, weaken, or bypass the user's approved strategy.

Evidence:

- `00_MASTER_CONTROL.md` states that no model, helper script, or automation module may override product strategy, publish decisions, data firewall rules, or scope boundaries without explicit user approval.
- `01_ACTIVE_SPRINT.md` correctly focuses the current sprint on `dog_bath_hose / blue`.
- `03_DATA_FIREWALL_POLICY.md` preserves product and batch isolation.

## 3. Overreach Expressions

Result: `not_found`

No audited file gives Codex, Claude, Seedance, Audio API, or Reference Mining authority to make final business decisions, publish automatically, rewrite strategy, or cross-write data without approval.

The model role contracts describe execution, critique, generation, or mining boundaries, not autonomous control.

## 4. Boundary Ambiguity

Result: `found_minor_warnings_patched_in_P1_019A`

Warnings:

1. `03_tk_video_agent/README.md` contained an older sentence in the inventory section saying only `inventory` supports `--product`. Status: `fixed_in_P1_019A`.
2. `scenario_keyword_mining/dog_bath_hose_hook_hypotheses.csv` included `business_purpose` and `target_metric`, but did not include a dedicated `first_principles_reason` column. Status: `fixed_in_P1_019A`.
3. The firewall is currently document-level. It defines intended write boundaries, but helper code does not yet enforce all boundaries with centralized path validation. Status: `open_for_P1_020`.

## 5. Need Revision

Result: `yes_code_level_firewall_still_recommended`

The two documentation/template warnings from P1-019 have been patched. The remaining recommended revision is to plan and implement a minimal code-level firewall before more models or modules start writing files.

## 6. Recommended Revision List

1. README product-scoped command wording no longer says only `inventory` supports `--product`. Status: `fixed_in_P1_019A`.
2. The dog bath hose hook hypothesis CSV now includes `first_principles_reason`. Status: `fixed_in_P1_019A`.
3. Add code-level path guards for product, SKU, batch, and output directory boundaries. Status: `recommended_next`.
4. Add tests that assert product-scoped commands cannot write outside their assigned product workspace. Status: `recommended_next`.
5. Add a version/date/batch naming rule for future scenario keyword mining files when they become batch-specific. Status: `later`.
6. Keep `control_console/` read-only by default, and require explicit user approval for every future control update. Status: `ongoing`.

## 7. Code-Level Firewall Recommendation

Result: `recommended`

The project should move from document-level firewall to code-level firewall.

Recommended next technical step:

- Create a small path validation helper that resolves target paths and rejects writes outside approved roots.
- Use it first in product-scoped commands and experiment template generation.
- Keep the implementation minimal and covered by `unittest`.

This should be done as a separate implementation task, not silently mixed into unrelated product work.

## 8. Audit Checklist

- User is highest decision maker: `pass`
- Codex, Claude, Seedance, Audio API, and Reference Mining are bounded modules: `pass`
- No AI can bypass the user for final decisions: `pass`
- `control_console/` default read-only: `pass`
- Different `product_slug` folders cannot cross-write by policy: `pass`
- Different experiment batches cannot cross-write by policy: `pass`
- Reference mining is limited to scene/pain/emotion/Hook/business logic extraction: `pass`
- Reference copying is forbidden: `pass`
- One module failure does not stop the whole project: `pass`
- README product-scoped command wording patched: `pass`
- Hook hypothesis CSV includes first-principles reason: `pass`
- Future code-level firewall need is clear: `pass_with_warning`

## 8A. P1-019A Patch Note

Date: 2026-05-23

The two concrete P1-019 audit warnings were patched:

1. README now reflects the current product-scoped command state: `inventory`, `material-pack`, `edit-strategy`, and `timeline` support `--product`, while product-scoped `render` is in validation.
2. `scenario_keyword_mining/dog_bath_hose_hook_hypotheses.csv` now includes `first_principles_reason` for every Hook hypothesis.

No `control_console/`, `products/`, or `experiments/` files were modified in this patch.

## 9. Next Step

Recommended next task:

`P1_020_code_level_firewall_plan_only`

Goal:

Plan a minimal code-level firewall before allowing more models or product pipelines to write into shared workspace areas.

Do not implement it inside this audit task.
