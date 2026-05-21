# P1-011 Product CLI Render

## Goal

Add product-scoped minimal render:

```bash
python main.py render --product pet_nail_trimmer
```

## Product Inputs

```text
products/pet_nail_trimmer/outputs/timelines/timeline.json
products/pet_nail_trimmer/outputs/material_pack/material_pack.json
products/pet_nail_trimmer/assets/raw_videos/
```

## Product Outputs

```text
products/pet_nail_trimmer/outputs/renders/final.mp4
products/pet_nail_trimmer/outputs/renders/render_report.md
```

## Compatibility

The old global command remains supported:

```bash
python main.py render
```

It still reads:

```text
03_tk_video_agent/outputs/timelines/timeline.json
03_tk_video_agent/outputs/material_pack/material_pack.json
03_tk_video_agent/inputs/raw_videos/
```

And writes:

```text
03_tk_video_agent/outputs/renders/
```

## Scope

- Only `render` is added to the product-aware CLI in this slice.
- No old files are moved.
- Product render only resolves videos inside the product workspace.
- No inventory, material-pack, edit-strategy, timeline, subtitles, or batch-variants behavior is changed.
- ffmpeg may be used if available.
- No dependency installation.
- No external API calls.
- No automatic TikTok publishing.
