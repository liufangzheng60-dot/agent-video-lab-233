# P12 Agent Factory Blueprint

## Future Main Command

```bash
python main.py agent-produce-review-pack --product dog_stairs_v1 --sku khaki --material-batch batch_xxx --variants 12
```

## Internal State Machine

1. `ingest_materials`
2. `collect_tags`
3. `generate_matrix`
4. `hard_rule_filter`
5. `render_qc_drafts`
6. `vlm_qc_gate`
7. `auto_replace_failed_variants`
8. `render_visual_masters`
9. `produce_voiceover`
10. `owner_firewall`
11. `build_publish_candidates`

## P12 Goals

- One command generates 12 ordinary testable review-pack videos.
- VLM performs automatic first-pass QC.
- Owner only makes final firewall decisions.
- Owner no longer reviews text plans.
- Prompt glue is removed from runtime.
- P11 accident-repair commands are not daily production steps.
- The system optimizes throughput of ordinary videos, not single-video polish.

## Owner Firewall Actions

- `approve_all`
- `approve_selected`
- `force_reject`
- `force_delete_candidate`
- `force_rerun_variant`
- `force_stop_pipeline`
- `force_override_vlm`
- `force_write_negative_example`

## VLM Allowed

- quality gate
- visual scoring
- repetition detection
- human hand / clutter warning
- product visibility check
- body overlap warning
- audio naturalness warning

## VLM Forbidden

- directly modifying timeline
- directly deleting files
- bypassing hard rules
- auto publishing
- overriding Owner decisions
- modifying raw assets
- modifying Git
