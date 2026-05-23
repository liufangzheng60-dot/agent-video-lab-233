# P1-016 Start New SKU: dog_bath_hose / blue

## Goal

Create a new product-level workspace and manual A/B experiment batch for:

- Product slug: `dog_bath_hose`
- SKU slug: `blue`
- Batch: `batch_20260520_v001_v005`

## Product Workspace

```text
products/dog_bath_hose/
├── product_brief.md
├── assets/
│   ├── raw_videos/
│   ├── product_images/
│   ├── ai_generated_clips/
│   ├── reference_videos/
│   └── scripts/
├── outputs/
│   ├── material_inventory/
│   ├── material_pack/
│   ├── edit_strategy/
│   ├── timelines/
│   ├── subtitles/
│   ├── renders/
│   └── reports/
└── publish/
    ├── publish_records/
    └── performance_feedback/
```

## Experiment Batch

```text
experiments/dog_bath_hose/blue/batch_20260520_v001_v005/
├── 00_batch_brief.md
├── 01_variants.csv
├── 02_performance_log.csv
├── 03_racing_decision.md
└── 04_next_iteration.md
```

## User Next Step

Place detailed product description and scripts as `.txt` or `.md` files under:

```text
products/dog_bath_hose/assets/scripts/
```

Place raw videos, images, AI clips, and references in their matching product asset directories.

## Scope

- No old `pet_nail_trimmer` files were moved.
- No old batch was deleted.
- No video generation.
- No ffmpeg.
- No automatic TikTok publishing.
- No external API calls.
- No dependency installation.
