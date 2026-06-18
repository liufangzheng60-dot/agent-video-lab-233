# Helpers Reverse Audit

## hard_rule_core

| module | reason |
| --- | --- |
| `color_fidelity_guard.py` | Enforces controlled-SDR / HDR / color metadata safety. |
| `global_conflict_registry.py` | Prevents repeated hook/window reuse across variants. |
| `negative_hook_memory.py` | Persists rejected hook patterns and Owner negative examples. |
| `render_manifest_preflight.py` | Validates controlled-SDR render manifests before P11C. |
| `audio_fit_guard.py` | Prevents unusable voiceover duration fits. |
| `visual_stream_copy_guard.py` | Ensures P11D audio mux does not visually reencode masters. |
| `firewall.py` | Path/safety firewall utility. |

## runtime_candidate

| module | future role |
| --- | --- |
| `batch_material_intake.py` | `ingest_materials`. |
| `material_capability_index.py` | material capability indexing. |
| `tag_review_workspace.py` | manual tag workspace until VLM-assisted tagging exists. |
| `folder_tag_collector.py` | `collect_tags`. |
| `batch_variant_matrix_planner.py` | `generate_matrix`. |
| `hook_preview_pack.py` | preview/review pack builder. |
| `batch_diversity_metric.py` | diversity scoring. |
| `p11c_visual_master_renderer.py` | `render_visual_masters`. |
| `p11d_voiceover_pipeline.py` | `produce_voiceover`. |
| `p11e_publish_candidate_builder.py` | `build_publish_candidates`. |
| `publish_metadata_builder.py` | title/caption/metadata sidecar generation. |
| `tts_provider.py` | provider abstraction for voiceover generation. |
| `owner_decision_lock.py` | Owner Firewall persistence. |

## general_rule_candidate

| module | optimization direction |
| --- | --- |
| `ab_strategy_planner.py` | Make strategy scoring configurable and data-aware. |
| `variant_planner.py` | Merge into matrix planner/harness. |
| `video_difference_score.py` | Add body/proof/CTA diversity, not only hook difference. |
| `variant_quality_gate.py` | Keep as quality signal, not hard truth. |
| `hook_quality_guard.py` | Add VLM-assisted checks for human hand/clutter/product visibility. |
| `semantic_dedup_guard.py` | Expand beyond clip_id uniqueness into visual intent. |
| `duplicate_risk.py` | Fold into global conflict registry and batch diversity metrics. |
| `creative_strategy.py` | Keep as strategy helper, not runtime brain. |
| `variant_voiceover.py` | Keep P10 compatibility, but P12 should prefer `p11d_voiceover_pipeline.py`. |

## legacy_patch

| module | why legacy patch |
| --- | --- |
| `hook_preview_repair.py` | P11B2/B3/B4 preview accident repair. Keep diagnostic only. |
| `visual_fidelity_guard.py` | Pre-HDR visual fidelity guard; superseded by color fidelity guard for HDR/10-bit cases. |
| `hook_replacement_planner.py` | P11B6 replacement flow; useful logic but should become auto-replacement stage. |
| `hook_visual_review.py` | P10B2 manual hook review pack. |
| `variant_renderer.py` | P10C wrapper; P11C renderer is the controlled-SDR path. |
| `variant_render_review.py` | P10 review artifact helper. |
| `publish_pack.py`, `publish_candidate_pack.py` | P9/P10 publish pack builders; superseded by P11E-style candidate builder. |

## delete_candidate

These are not deleted in P12A. They need Owner approval and a compatibility check first.

| module | reason |
| --- | --- |
| `subtitle_overlay.py` | Subtitle burn-in is not a default production path. |
| `transcribe.py` | Whisper/transcription is out of current runtime path. |
| `self_eval.py` | Local heuristic self-eval is weaker than explicit gates plus Owner/VLM review. |
| `make_timeline.py` | Potential overlap with `generate_timeline.py`. |
| `render.py` | First-MVP renderer; superseded by controlled-SDR renderer for production. |

## unknown

| module | note |
| --- | --- |
| `extract_keyframes.py` | Likely useful utility; classify after checking current callers. |
| `product_workspace.py` | Utility, likely keep. |
| `inventory.py`, `build_material_pack.py`, `generate_edit_strategy.py`, `generate_timeline.py` | Legacy MVP foundation; preserve until P12 harness proves replacement. |
| `actual_render.py`, `shot_matcher.py` | Core legacy chain; do not modify in P12A. |
