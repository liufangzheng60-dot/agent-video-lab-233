# P1-007 Product CLI Inventory

## Goal

Add the first product-scoped CLI slice by supporting:

```bash
python main.py inventory --product pet_nail_trimmer
```

This scans the product workspace assets and writes inventory outputs under the same product workspace.

## Product Input

```text
products/pet_nail_trimmer/assets/
├── raw_videos/
├── product_images/
├── ai_generated_clips/
├── reference_videos/
└── scripts/
```

## Product Output

```text
products/pet_nail_trimmer/outputs/material_inventory/
├── material_inventory.json
└── material_inventory.md
```

## Compatibility

The old global command remains supported:

```bash
python main.py inventory
```

It still scans:

```text
03_tk_video_agent/inputs/
```

And writes:

```text
03_tk_video_agent/outputs/material_inventory/
```

## Scope

- Only `inventory` supports `--product` in this slice.
- No old files are moved.
- No other commands are changed.
- No video generation.
- No external API calls.
- No dependency installation.
