# P1-025 Dog Bath Hose Voiceover Script

Date: 2026-05-24

## Goal

Generate English voiceover scripts and manual recording guidance for `dog_bath_hose / blue`.

## Outputs

```text
products/dog_bath_hose/outputs/reports/voiceover_script_20260524.md
products/dog_bath_hose/outputs/reports/voiceover_recording_guide.md
products/dog_bath_hose/outputs/reports/voiceover_plan.md
```

## Rules

- English voiceover only.
- 7-15 second TikTok Shop product video target.
- Use scene and pain words: muddy paws, dirty floor, bath time mess, quick rinse, water everywhere.
- Do not copy reference captions, music, or footage.
- Do not call Audio API.
- Do not generate audio.
- Do not generate video.
- Do not run ffmpeg.

## Script Variants

- v001 scene pain version
- v002 quick clean version
- v003 easier home version

Each variant includes:

- `voiceover_text`
- `estimated_duration_seconds`
- `business_purpose`
- `target_metric`
- `first_principles_reason`
