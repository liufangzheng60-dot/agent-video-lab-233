# Expression Style Batch Brief

Product: dog_bath_hose
SKU: blue
Batch: batch_20260524_expression_style
Date: 2026-05-24

## Fill-In Instructions

Use this folder to manually track the expression_style A/B test for dog_bath_hose / blue. If a value is unavailable, write `NA`.

## Test Goal

Test whether English voiceover expression style changes early retention, product clicks, completion rate, or conversion.

## Primary Control Variable

Only change:

- expression_style

Do not change in this batch:

- Product.
- Source footage.
- Visual skeleton.
- CTA direction.
- Subtitle policy.
- Source audio mute policy.

## Variants

- v001_baseline_direct
- v002_slang_lowbrow
- v003_profanity_bleeped_shock
- v004_chaos_pain
- v005_convenience_easy

## Risk Note

v003 is a high_risk_test_variant. It exists to test whether a crude shock hook improves the first two seconds of attention. It may increase early retention while hurting trust, product clicks, or conversion. Use bleeped or character-masked wording only.

## Data Rule

Record data at the same checkpoints for every variant. Missing data should be entered as `NA`.
