# P1-010 Product CLI Timeline

## Goal

Add product-scoped timeline generation:

```bash
python main.py timeline --product pet_nail_trimmer
```

## Product Inputs

```text
products/pet_nail_trimmer/outputs/edit_strategy/edit_strategy.json
products/pet_nail_trimmer/outputs/material_pack/material_pack.json
```

## Product Outputs

```text
products/pet_nail_trimmer/outputs/timelines/timeline.json
products/pet_nail_trimmer/outputs/timelines/capcut_timeline.csv
```

## Compatibility

The old global command remains supported:

```bash
python main.py timeline
```

It still reads:

```text
03_tk_video_agent/outputs/edit_strategy/edit_strategy.json
03_tk_video_agent/outputs/material_pack/material_pack.json
```

And writes:

```text
03_tk_video_agent/outputs/timelines/
```

## Scope

- Only `timeline` is added to the product-aware CLI in this slice.
- No old files are moved.
- No inventory, material-pack, edit-strategy, render, subtitles, or batch-variants behavior is changed.
- No video generation.
- No ffmpeg calls.
- No external API calls.
- No dependency installation.
