# P12B Agent Factory Runtime Harness

P12B adds the first Runtime Agent skeleton for high-throughput review-pack production. It is intentionally dry-run only.

## Commands

```bash
python main.py agent-preflight --product dog_stairs_v1 --sku khaki --material-batch batch_20260617_001 --variants 12
python main.py agent-produce-review-pack-dry-run --product dog_stairs_v1 --sku khaki --material-batch batch_20260617_001 --variants 12
python main.py owner-firewall --product dog_stairs_v1 --sku khaki --material-batch batch_20260617_001 --decision-file owner_firewall_decisions.template.json --dry-run
```

## Outputs

Outputs are written under:

```text
products/<product>/outputs/agent_factory/<material_batch>/
```

P12B writes state, reports, policy files, and Owner decision templates only. It does not generate video, call Gemini, synthesize TTS, delete files, or publish.

## Runtime State

`agent_state.json` and `dry_run_agent_state.json` include product, SKU, material batch, requested variants, current stage, stage status, hard-rule results, media guard results, VLM QC results, Owner firewall status, output paths, failed variants, rerun history, final review pack path, and timestamps.

## Safety Boundaries

- Raw videos are immutable local assets.
- `products/**/inputs/raw_videos/**` and `products/**/outputs/**` must stay ignored.
- Media files, spreadsheets, and `.env` files must not be staged.
- VLM is a QC sidecar only and cannot bypass hard rules or Owner decisions.
- Owner Firewall is the final decision layer.
