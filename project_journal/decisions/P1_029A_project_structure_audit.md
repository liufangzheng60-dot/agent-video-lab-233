# P1_029A Project Structure Audit And Simplification Plan

Date: 2026-05-25

## Overall Conclusion

manageable_with_warnings

The project is still healthy enough to continue the dog_bath_hose business line. The main risk is not technical disorder yet; it is record duplication across `tasks/`, `products/*/outputs/reports/`, `experiments/`, `project_journal/`, and chat summaries.

No deletion or file move is recommended as an immediate action. The next step should be to enforce stricter source-of-truth rules and reduce new file creation.

## Directory Responsibilities

### 03_tk_video_agent/

Unique responsibility: code, tests, CLI entry points, helper modules, task notes, and legacy global demo compatibility.

Must keep:

- `main.py`
- `helpers/`
- `tests/`
- `README.md`

Shrink rule:

- `tasks/` should stop receiving a new file for every low-risk documentation task.
- Add task files only for code changes, high-risk policy changes, or reviewer-required packages.

### products/

Unique responsibility: product-scoped business production line.

Must keep:

- Product assets.
- Product-specific pipeline outputs.
- Product-specific reports needed for production decisions.

Source of truth:

- For product artifacts, `products/product_slug/` is the primary source.
- For dog_bath_hose output status, use `products/dog_bath_hose/outputs/`.

Risk:

- `outputs/reports/` can grow quickly if every thought becomes a report.
- Keep only decision-useful reports, not duplicate task summaries.

### experiments/

Unique responsibility: product/SKU/batch performance tracking and racing decisions.

Must keep:

- `01_variants.csv`
- `02_performance_log.csv`
- `03_racing_decision.md`
- analysis files generated from user-entered data

Source of truth:

- Performance metrics live only in `experiments/.../02_performance_log.csv`.
- Winner/loser decisions live only in `experiments/.../03_racing_decision.md`.

Risk:

- Parallel summaries in product reports can drift from experiment CSVs.

### project_journal/

Unique responsibility: meta-decisions, audits, reviewer results, and system-level policy history.

Must keep:

- decisions that affect workflow, architecture, review protocol, or data governance
- error reports that explain blocked or risky execution

Shrink rule:

- Do not duplicate product performance data here.
- Link or reference experiment paths instead of copying tables.

### control_console/

Unique responsibility: top-level governance, role contracts, data firewall policy, and do-not-touch rules.

Must keep:

- Read-only governance by default.

Risk:

- Should not become a daily task log.
- Should only change with explicit user approval.

### scenario_keyword_mining/

Unique responsibility: scene words, pain words, hook hypotheses, and reference-safe business logic.

Must keep:

- Keyword and hook hypothesis templates that inform creative direction.

Shrink rule:

- Do not record actual publish data here.
- Do not duplicate experiment winners here.

### 05_final_outputs/

Unique responsibility: legacy/global baseline publish packs and final artifacts from the first MVP loop.

Current status:

- Useful as global_demo baseline archive.
- Not the primary production line after product-scoped workspace adoption.

Shrink rule:

- Do not add new dog_bath_hose production records here unless explicitly archiving a final approved asset.

## Core Directories To Keep

- `03_tk_video_agent/`
- `products/`
- `experiments/`
- `project_journal/decisions/`
- `control_console/`

## Directories To Keep But Shrink

- `03_tk_video_agent/tasks/`
- `products/*/outputs/reports/`
- `project_journal/errors/`
- `05_final_outputs/`

## Directories With Complexity Risk

- `03_tk_video_agent/tasks/`: too many per-stage task files for low-risk work.
- `products/dog_bath_hose/outputs/reports/`: can duplicate experiment findings.
- `experiments/*/*/*/analysis/`: useful, but should stay data-derived and compact.
- `project_journal/decisions/`: should remain for architecture and workflow, not daily output logs.

## Duplicate Information Risks

Same fact currently appears or may appear in multiple places:

- Variant scripts: product reports, experiment variants CSV, and task files.
- Performance conclusions: analysis report, racing decision, README, and chat summary.
- Pipeline status: product reports, task files, and README.
- Governance rules: control_console, project_journal, and README.

## Source Of Truth Rules

1. Code behavior source of truth: `03_tk_video_agent/helpers/`, `main.py`, and tests.
2. Product asset and generated artifact source of truth: `products/product_slug/`.
3. Experiment variant source of truth: `experiments/product/sku/batch/01_variants.csv`.
4. Performance metric source of truth: `experiments/product/sku/batch/02_performance_log.csv`.
5. Winner or loser source of truth: `experiments/product/sku/batch/03_racing_decision.md`.
6. System policy source of truth: `control_console/`.
7. Architecture and audit source of truth: `project_journal/decisions/`.
8. README role: navigation and usage summary only, not full report storage.

## Future File Creation Rules

Create new files only when one of these is true:

- A command needs a new helper or test file.
- A product artifact is generated for production use.
- A new experiment batch is created.
- A decision affects future workflow or safety.
- A reviewer package is required for high-risk work.

Do not create new files for:

- Routine command success summaries.
- Low-risk task completion logs.
- Repeating the same performance data in another format.
- Chat-only decisions that are already captured in the batch decision file.

## Reports To Compress

Compress these to short summaries:

- Render status updates after the policy is stable.
- Voiceover planning updates after the script path is clear.
- Experiment analysis after it is already recorded in `analysis/`.
- Task completion summaries for docs-only changes.

Keep detailed reports for:

- New code path behavior.
- Firewall or path-safety work.
- Review packages.
- Unexpected errors.
- Batch racing decisions after real data is complete.

## Simplification Recommendations

1. Stop adding a `tasks/P*.md` file for every low-risk documentation-only task.
2. Use `experiments/.../03_racing_decision.md` as the only place for winner/loser decisions.
3. Keep `README.md` as a navigation layer; avoid copying full business analysis into it.
4. Treat `products/*/outputs/reports/` as product production reports, not a general notebook.
5. Treat `project_journal/decisions/` as architecture and governance history, not task transcripts.
6. Keep `05_final_outputs/` as legacy/global baseline archive unless explicitly publishing a final approved artifact.
7. Before creating a file, ask: "Is this a new source of truth, or just another copy?"

## Delete Recommendation

Default: no deletion now.

Reason: The current files still document a fast-moving MVP path. Deleting during active experimentation may create avoidable confusion. The better first move is to stop adding duplicate records and let future work consolidate around source-of-truth paths.

## Return To Business Line?

Yes. The project may return to the dog_bath_hose business line after this audit.

Recommended next business action:

- Continue v003 follow-up execution using the existing experiment batch.
- Record new TikTok metrics through `experiment-record`.
- Avoid creating new task files unless code or policy changes require them.
