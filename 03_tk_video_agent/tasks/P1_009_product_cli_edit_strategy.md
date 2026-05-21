# P1-009 Product CLI Edit Strategy

## Goal

Add product-scoped edit strategy generation:

```bash
python main.py edit-strategy --product pet_nail_trimmer
```

## Product Input

```text
products/pet_nail_trimmer/outputs/material_pack/material_pack.json
```

## Product Outputs

```text
products/pet_nail_trimmer/outputs/edit_strategy/edit_strategy.json
products/pet_nail_trimmer/outputs/edit_strategy/edit_strategy.md
```

## Compatibility

The old global command remains supported:

```bash
python main.py edit-strategy
```

It still reads:

```text
03_tk_video_agent/outputs/material_pack/material_pack.json
```

And writes:

```text
03_tk_video_agent/outputs/edit_strategy/
```

## Scope

- Only `edit-strategy` is added to the product-aware CLI in this slice.
- No old files are moved.
- No inventory, material-pack, timeline, render, subtitles, or batch-variants behavior is changed.
- No video generation.
- No external API calls.
- No dependency installation.
