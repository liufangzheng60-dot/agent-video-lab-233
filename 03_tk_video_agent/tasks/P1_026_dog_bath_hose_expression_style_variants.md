# P1_026 dog_bath_hose Expression Style Variants

Date: 2026-05-24

## Goal

Create a controlled expression_style test batch for dog_bath_hose / blue.

## Scope

This task generated documentation and manual-fill experiment templates only. It did not generate audio, video, subtitles, or render outputs.

## Primary Variable

`expression_style`

## Variants

- v001_baseline_direct
- v002_slang_lowbrow
- v003_profanity_bleeped_shock
- v004_chaos_pain
- v005_convenience_easy

## Control Rules

- Keep product unchanged.
- Keep source footage and visual skeleton unchanged.
- Keep CTA direction unchanged.
- Do not burn subtitles.
- Do not keep source video background audio.
- Do not copy reference video wording, music, or material.

## High-Risk Variant Rule

v003 is intentionally retained as `high_risk_test_variant`. Its purpose is to test whether a crude shock hook improves the first two seconds of attention. It may lift early retention while reducing trust, product clicks, or conversion.

## Outputs

- `products/dog_bath_hose/outputs/reports/expression_style_variants_20260524.md`
- `experiments/dog_bath_hose/blue/batch_20260524_expression_style/00_batch_brief.md`
- `experiments/dog_bath_hose/blue/batch_20260524_expression_style/01_variants.csv`
- `experiments/dog_bath_hose/blue/batch_20260524_expression_style/02_performance_log.csv`
- `experiments/dog_bath_hose/blue/batch_20260524_expression_style/03_racing_decision.md`
- `experiments/dog_bath_hose/blue/batch_20260524_expression_style/04_next_iteration.md`

## Not Done

- No external API.
- No audio generation.
- No video generation.
- No ffmpeg.
- No render logic change.
- No firewall change.
- No TikTok publishing.
