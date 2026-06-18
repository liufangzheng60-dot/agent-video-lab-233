# CLI Chain Reverse Audit

## Scope

This audit reviews `03_tk_video_agent/main.py` before P12. The current entrypoint is a large CLI toolbox, not a runtime agent. It contains legacy MVP commands, P10/P11 production commands, repair commands, review-pack commands, and low-level utility commands.

## P10 / P11 Stage Commands

- `audit-material-diversity`: P10A material diversity and hook planning audit. Keep as historical audit and strategy reference.
- `plan-variants`: P10B approved A/B/C hook variant planning. Candidate to fold into P12 matrix generation.
- `build-hook-review-pack`: P10B2 hook preview pack. Candidate to fold into P12 visual review pack generation.
- `render-approved-variants`: P10C B/C visual rendering. Superseded by P11C controlled-SDR visual master flow.
- `add-variant-voiceover`: P10D/P10D2 B/C voiceover. Superseded by P11D batch voiceover flow.
- `prepare-final-publish-candidates`: P10E final B/C publish pack. Superseded by P11E publish candidate builder.
- `intake-material-batch`: P11A material intake. Runtime candidate for P12 `ingest_materials`.
- `prepare-tag-review-workspace`: P11A2 tag workspace. Runtime candidate, but P12 should reduce manual folder dragging over time.
- `collect-folder-tags`: P11A2 tag collector. Runtime candidate for `collect_tags`.
- `plan-batch-variant-matrix`: P11B level-1 matrix planning. Runtime candidate for `generate_matrix`.
- `repair-hook-preview-pack`, `repair-hook-preview-visual-fidelity`, `audit-color-fidelity-and-build-safe-previews`: P11B2/B3/B4 accident-repair commands. Keep for diagnostics, do not expose as normal daily production steps.
- `lock-owner-color-decision`: P11B4D owner color lock. Keep concept as hard rule, fold runtime validation into harness.
- `replan-hooks-after-owner-review`: P11B6 replacement planning. Runtime candidate for `auto_replace_failed_variants`.
- `lock-owner-replacement-decisions`: P11B7 owner decision lock. Runtime candidate for Owner Firewall persistence.
- `render-approved-visual-masters`: P11C controlled-SDR visual masters. Runtime candidate for `render_visual_masters`.
- `produce-voiceover-review-pack`: P11D three-block voiceover review pack. Runtime candidate for `produce_voiceover`.
- `build-publish-candidates`: P11E publish candidate pack. Runtime candidate for `build_publish_candidates`.

## Debug / Legacy Commands

- `inventory`, `material-pack`, `edit-strategy`, `timeline`, `render`: first MVP building blocks. Keep as low-level debug utilities only.
- `material-batch`, `contact-sheet`, `tag-review-init`, `tag-from-folders`: early batch/tagging utilities. Superseded by P11A/P11A2 names but useful for debugging.
- `script-pack-inspect`, `script-pack-parse`: spreadsheet/script parsing utilities. Keep low-level.
- `shot-match`, `shot-match-v002`, `render-preflight`, `render-preflight-v002`, `actual-render`, `actual-render-v002`, `batch-render-scripts`: P9/P10 render chain commands. Keep for legacy reruns, but P12 should wrap rendering behind a harness.
- `openai-tts-poc`, `edge-tts-poc`, `edge-tts-segment-align`, `edge-tts-three-block`: TTS experiments. Keep only as provider/debug commands; P12 should use one voiceover stage.
- `render-review-pack`, `render-review-pack-v002`, `creative-diagnose-assets`, `creative-strategy-v002`: manual review/debug commands.
- `subtitles`, `batch-variants`: legacy subtitle-burned commands; should not be default P12 path.
- `experiment-init`, `experiment-record`: manual experiment tracking. P12 should write structured run state instead.
- `firewall-check`: keep as safety utility.

## Commands To Merge Into P12 `agent-produce-review-pack`

- `intake-material-batch`
- `collect-folder-tags`
- `plan-batch-variant-matrix`
- `render-approved-visual-masters`
- `produce-voiceover-review-pack`
- `build-publish-candidates`
- Owner decision lock behavior from `lock-owner-replacement-decisions`
- Hard-rule validation from color pipeline, conflict registry, negative memory, stream copy, and duration checks.

## Low-Level Commands To Preserve

- `firewall-check`
- `script-pack-inspect`
- `script-pack-parse`
- `contact-sheet`
- `render-review-pack`
- TTS provider POC commands for isolated debugging.

## Reverse-Audit Conclusion

The CLI is functional but overexposed. P12 should keep low-level commands for diagnosis while adding a runtime harness that owns state transitions, hard-rule checks, VLM QC, auto replacement, Owner Firewall decisions, and final review pack generation.
