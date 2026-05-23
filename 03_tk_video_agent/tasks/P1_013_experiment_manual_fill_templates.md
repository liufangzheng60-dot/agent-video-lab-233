# P1-013 Experiment Manual Fill Templates

## Goal

Create isolated, manual-fill A/B testing templates for each product, SKU, and batch:

```bash
python main.py experiment-init --product pet_nail_trimmer --sku default_sku --batch batch_20260520_v002_v006
```

## Directory Pattern

```text
experiments/product_slug/sku_slug/batch_YYYYMMDD_vXXX_vYYY/
```

Example:

```text
experiments/pet_nail_trimmer/default_sku/batch_20260520_v002_v006/
```

## Generated Files

```text
00_batch_brief.md
01_variants.csv
02_performance_log.csv
03_racing_decision.md
04_next_iteration.md
```

## Manual Fill Rule

- All missing or unavailable values should be entered as `NA`.
- CSV files include headers only by default.
- Markdown files include fill-in instructions.
- The templates are for manual publishing records, performance logging, racing decisions, and next iteration planning.

## Scope

- No video generation.
- No automatic TikTok publishing.
- No external API calls.
- No dependency installation.
- No GitHub push handling.
