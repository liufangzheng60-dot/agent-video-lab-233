# P12B Owner Firewall User Guide

The Owner Firewall reads an Owner decision JSON and validates the requested actions. In P12B it is dry-run only.

## Supported Actions

- `approve_all`
- `approve_selected`
- `force_reject`
- `force_delete_candidate`
- `force_rerun_variant`
- `force_stop_pipeline`
- `force_override_vlm`
- `force_write_negative_example`

## Dry-Run Command

```bash
python main.py owner-firewall --product dog_stairs_v1 --sku khaki --material-batch batch_20260617_001 --decision-file owner_firewall_decisions.template.json --dry-run
```

If `--decision-file` is a filename, the CLI first looks inside:

```text
products/<product>/outputs/agent_factory/<material_batch>/
```

## Guarantees

P12B Owner Firewall does not delete files, render videos, call VLM, generate TTS, modify raw videos, publish, or modify Git. It writes:

- `owner_firewall_audit_log.md`
- `owner_firewall_result.json`

All real destructive or publish-related behavior remains blocked until a later Owner-approved phase.
