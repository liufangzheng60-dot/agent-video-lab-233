# P1-024 Dog Bath Hose Voiceover-Only Pipeline

Date: 2026-05-24

## Goal

Run the product-level `dog_bath_hose / blue` pipeline with a voiceover-only final video rule.

## Product

- Product slug: `dog_bath_hose`
- SKU slug: `blue`

## Voiceover-Only Render Policy

- Source video background audio must be muted.
- Subtitles must not be burned by default.
- If `products/dog_bath_hose/assets/voiceovers/` contains `.mp3`, `.wav`, or `.m4a`, render `final_voiceover_YYYYMMDD.mp4`.
- If voiceover audio is missing, render only `muted_visual_preview_YYYYMMDD.mp4` and write `voiceover_plan.md`.
- Do not label a muted preview as a final voiceover video.

## Product-Level Commands

```bash
python main.py inventory --product dog_bath_hose
python main.py material-pack --product dog_bath_hose
python main.py edit-strategy --product dog_bath_hose
python main.py timeline --product dog_bath_hose
python main.py render --product dog_bath_hose
python -m unittest discover -s tests
```

## Expected Reports

```text
products/dog_bath_hose/outputs/reports/asset_readiness_report.md
products/dog_bath_hose/outputs/reports/voiceover_plan.md
products/dog_bath_hose/outputs/reports/business_pipeline_report.md
products/dog_bath_hose/outputs/renders/render_report.md
```

## Required Render Report Fields

- `source_audio_muted=true`
- `subtitle_burned=false`
- `voiceover_status=present` or `missing`

## Scope

- No external API calls.
- No automatic TikTok publishing.
- No subtitle burn.
- No original source background audio in final output.
- No control console changes.
- No experiments changes.
- No pet_nail_trimmer changes.
- No P1-022 firewall integration.
