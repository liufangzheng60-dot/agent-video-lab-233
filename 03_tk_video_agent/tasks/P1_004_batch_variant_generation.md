# P1-004 Batch Variant Generation

## Goal

Generate five English-subtitled A/B test videos for TikTok Shop US manual publishing.

## Inputs

- `outputs/renders/final.mp4`
- `outputs/timelines/timeline.json`
- `outputs/edit_strategy/edit_strategy.json`
- `inputs/product_briefs/`

## Outputs

- `outputs/renders/final_v002_cost_hook.mp4`
- `outputs/renders/final_v003_stress_hook.mp4`
- `outputs/renders/final_v004_led_safety_hook.mp4`
- `outputs/renders/final_v005_home_grooming_hook.mp4`
- `outputs/renders/final_v006_fast_demo_hook.mp4`
- `outputs/subtitles/batch_variants/`
- `../05_final_outputs/publish_records/batch_v002_to_v006_publish_plan.md`
- `../05_final_outputs/performance_feedback/batch_v002_to_v006_feedback.md`

## Command

```bash
python main.py batch-variants
```

## Scope

- Generates English subtitle variants only.
- Burns each variant onto existing `final.mp4` using local ffmpeg.
- Does not auto-publish to TikTok.
- Does not call external APIs.
- Does not install dependencies.
- Does not do AI visual understanding or transcription.
