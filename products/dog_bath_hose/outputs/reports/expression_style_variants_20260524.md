# dog_bath_hose / blue Expression Style Variants

Date: 2026-05-24

Product: dog_bath_hose
SKU: blue
Batch: batch_20260524_expression_style

## Control Variable

The only primary test variable in this batch is `expression_style`.

Controlled items:

- Product: unchanged.
- Source footage and visual skeleton: unchanged.
- CTA direction: unchanged.
- Subtitles: not added.
- Source video background audio: muted.
- Voiceover delivery: English only.

This batch must not change the visual structure at the same time, otherwise the result cannot isolate whether expression style affects retention, clicks, or conversion.

## Variant Table

| variant_id | style_type | profanity_level | bleep_required | platform_risk | core_angle | control_variable | hook_line | cta_line | target_metric |
|---|---|---|---|---|---|---|---|---|---|
| v001_baseline_direct | baseline_direct | none | false | low | Direct scene pain | expression_style | Muddy paws after a walk? | Make bath time easier at home. | product_clicks |
| v002_slang_lowbrow | slang_lowbrow | mild | false | medium | Casual lowbrow mess talk | expression_style | Your dog just dragged the whole yard inside. | Keep the mess out of the house. | 3_second_retention |
| v003_profanity_bleeped_shock | profanity_bleeped_shock | high | true | high | Shock hook for early stop | expression_style | Holy sh*t, those paws are a mess. | Clean it up before your floor pays for it. | 2_second_retention |
| v004_chaos_pain | chaos_pain | none | false | medium | Bathroom chaos and water mess | expression_style | Bath time should not turn into water everywhere. | Rinse fast and keep the chaos down. | completion_rate |
| v005_convenience_easy | convenience_easy | none | false | low | Calm home convenience | expression_style | Quick rinses are easier when the hose is ready. | Make everyday cleanup easier. | product_clicks |

## Variant Details

### v001_baseline_direct

- variant_id: v001_baseline_direct
- style_type: baseline_direct
- profanity_level: none
- bleep_required: false
- platform_risk: low
- core_angle: Directly connects muddy paws to dirty floors and a faster home rinse.
- control_variable: expression_style
- hook_line: Muddy paws after a walk?
- full_voiceover_script: Muddy paws after a walk? Use the blue dog bath hose for a faster rinse at home. Keep dirty floors and bath time mess under control.
- cta_line: Make bath time easier at home.
- business_purpose: Establish a clean baseline that tests the product promise without extra emotional styling.
- target_metric: product_clicks
- first_principles_reason: The scene word "muddy paws" creates immediate recognition, the pain word "dirty floors" names the cleanup cost, and the practical rinse promise connects the product to a clear purchase reason.
- expected_user_response: The viewer understands the use case quickly and clicks if they already need a dog cleanup tool.
- risk_note: Low creative risk, but may not create enough interruption in the first two seconds.

### v002_slang_lowbrow

- variant_id: v002_slang_lowbrow
- style_type: slang_lowbrow
- profanity_level: mild
- bleep_required: false
- platform_risk: medium
- core_angle: Casual, blunt, lower-funnel language about a messy dog dragging dirt inside.
- control_variable: expression_style
- hook_line: Your dog just dragged the whole yard inside.
- full_voiceover_script: Your dog just dragged the whole yard inside. Muddy paws, dirty floor, bath time mess. Snap on the blue hose and rinse that mess before it spreads.
- cta_line: Keep the mess out of the house.
- business_purpose: Test whether casual lowbrow phrasing makes the hook feel more native to TikTok and improves early retention.
- target_metric: 3_second_retention
- first_principles_reason: Slang and blunt imagery make the pain feel immediate. The viewer sees the familiar problem first, then gets a simple product action that lowers cleanup effort.
- expected_user_response: The viewer may feel the line sounds more like a real owner complaint than a polished ad.
- risk_note: Medium risk because informal phrasing may reduce premium perception for some buyers.

### v003_profanity_bleeped_shock

- variant_id: v003_profanity_bleeped_shock
- style_type: profanity_bleeped_shock
- profanity_level: high
- bleep_required: true
- platform_risk: high
- core_angle: Deliberately crude and high-friction shock hook to test first-second stopping power.
- control_variable: expression_style
- hook_line: Holy sh*t, those paws are a mess.
- full_voiceover_script: Holy sh*t, those paws are a mess. What the h*ll happened outside? Rinse the mud off fast with the blue dog bath hose before your floor gets wrecked.
- cta_line: Clean it up before your floor pays for it.
- business_purpose: This is not vulgarity for its own sake. It tests whether a stronger emotional jolt can lift the first two seconds of attention when the visual starts with mess.
- target_metric: 2_second_retention
- first_principles_reason: The opening uses shock and surprise to interrupt scrolling, then immediately ties the emotion to muddy paws, water everywhere, and a fast rinse solution. The commercial question is whether more attention compensates for higher brand and platform risk.
- expected_user_response: Some viewers may stop because the hook feels raw and chaotic; others may bounce or distrust the product because the tone feels too aggressive.
- risk_note: high_risk_test_variant. It may increase views or early hold while lowering conversion, trust, or platform suitability. Use bleeped or character-masked wording only; do not publish fully uncensored profanity by default.

### v004_chaos_pain

- variant_id: v004_chaos_pain
- style_type: chaos_pain
- profanity_level: none
- bleep_required: false
- platform_risk: medium
- core_angle: Emphasizes bath time mess, water everywhere, and stress reduction.
- control_variable: expression_style
- hook_line: Bath time should not turn into water everywhere.
- full_voiceover_script: Bath time should not turn into water everywhere. Use the blue dog bath hose for a quick rinse on muddy paws and messy fur, without turning cleanup into another job.
- cta_line: Rinse fast and keep the chaos down.
- business_purpose: Test whether naming the whole messy scene improves completion and product relevance.
- target_metric: completion_rate
- first_principles_reason: The viewer is not only buying a hose; they are buying less chaos. This framing links the product to emotional relief and lower household cleanup effort.
- expected_user_response: The viewer may keep watching because the problem feels familiar and the promise is practical.
- risk_note: Medium risk because a broader chaos angle may be less punchy than a direct cost or shock hook.

### v005_convenience_easy

- variant_id: v005_convenience_easy
- style_type: convenience_easy
- profanity_level: none
- bleep_required: false
- platform_risk: low
- core_angle: Calm convenience, fast home cleanup, less friction.
- control_variable: expression_style
- hook_line: Quick rinses are easier when the hose is ready.
- full_voiceover_script: Quick rinses are easier when the hose is ready. Muddy paws, messy fur, quick cleanup. The blue dog bath hose helps make everyday grooming simpler at home.
- cta_line: Make everyday cleanup easier.
- business_purpose: Test whether a softer convenience style improves clicks from practical buyers who dislike aggressive ad language.
- target_metric: product_clicks
- first_principles_reason: Convenience framing reduces perceived effort. The product becomes a simple home routine upgrade rather than a dramatic problem fix.
- expected_user_response: The viewer may respond with lower early shock but higher trust and purchase intent.
- risk_note: Low risk, but it may underperform on first-second retention compared with stronger hooks.

## Business Logic

- v003 is intentionally preserved as a high-risk test variant. Its purpose is to test whether strong emotional shock improves the first two seconds of attention, not to make the brand vulgar by default.
- v003 may lift early views or retention while reducing trust, product clicks, or conversion.
- This batch must keep the visual skeleton and CTA direction stable so the result can be attributed to `expression_style`.
- These scripts are not reference-video copies. They use scene words, pain words, emotion triggers, and commercial logic specific to the dog bath hose.

## Recommended Manual Use

1. Select one voiceover script per version.
2. Record or externally generate audio manually.
3. Save audio under `products/dog_bath_hose/assets/voiceovers/`.
4. Keep filenames tied to variant IDs and date.
5. Do not publish v003 without bleeping or character-masking profanity.
