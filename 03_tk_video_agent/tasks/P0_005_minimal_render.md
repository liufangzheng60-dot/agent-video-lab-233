# P0-005 Minimal Render

## Goal

Render a minimal reviewable `final.mp4` from `timeline.json` and existing raw mp4 material.

## Inputs

- `outputs/timelines/timeline.json`
- `outputs/material_pack/material_pack.json`
- `inputs/raw_videos/`

## Outputs

- `outputs/renders/final.mp4`
- `outputs/renders/render_report.md`

## Command

```bash
python main.py render
```

## Scope

- Uses ffmpeg from local PATH.
- Does not install ffmpeg or Python dependencies.
- Reuses referenced source mp4 material to produce a 9:16 review video.
- Uses scale and pad to output 720x1280 when safe cropping is not guaranteed.
- Records aspect-ratio risks in the render report.
- Does not do AI visual understanding.
- Does not transcribe video.
- Does not call external APIs.
- Does not create UI or publish to TikTok.
