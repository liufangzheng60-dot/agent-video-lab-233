# P0-004 Timeline Generation

## Goal

Generate executable planning timeline files from `edit_strategy.json` and `material_pack.json` without editing or rendering video.

## Inputs

- `outputs/edit_strategy/edit_strategy.json`
- `outputs/material_pack/material_pack.json`

## Outputs

- `outputs/timelines/timeline.json`
- `outputs/timelines/capcut_timeline.csv`

## Command

```bash
python main.py timeline
```

## Scope

- Builds a 7-15 second short video timeline.
- Includes hook, problem, demo, proof, and CTA segments.
- Preserves `needs_9_16_crop_or_rebuild` risk for non-9:16 video materials.
- Writes CSV fields for manual CapCut recreation.
- Does not call ffmpeg.
- Does not edit or render video.
- Does not generate `final.mp4`.
- Does not call external APIs.
- Does not install dependencies.
