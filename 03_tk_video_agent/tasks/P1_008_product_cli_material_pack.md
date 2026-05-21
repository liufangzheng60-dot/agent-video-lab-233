# P1-008 Product CLI Material Pack

## Goal

Add product-scoped material pack generation:

```bash
python main.py material-pack --product pet_nail_trimmer
```

## Product Inputs

```text
products/pet_nail_trimmer/outputs/material_inventory/material_inventory.json
products/pet_nail_trimmer/product_brief.md
products/pet_nail_trimmer/assets/scripts/
```

The product brief is the primary product document. `assets/scripts/*.txt` and `assets/scripts/*.md` are optional script supplements.

## Product Outputs

```text
products/pet_nail_trimmer/outputs/material_pack/material_pack.json
products/pet_nail_trimmer/outputs/material_pack/material_pack.md
```

## Compatibility

The old global command remains supported:

```bash
python main.py material-pack
```

It still reads:

```text
03_tk_video_agent/outputs/material_inventory/material_inventory.json
03_tk_video_agent/inputs/product_briefs/
```

And writes:

```text
03_tk_video_agent/outputs/material_pack/
```

## Scope

- Only `material-pack` is added to the product-aware CLI in this slice.
- No old files are moved.
- No edit-strategy, timeline, render, subtitles, or batch-variants behavior is changed.
- No video generation.
- No external API calls.
- No dependency installation.
