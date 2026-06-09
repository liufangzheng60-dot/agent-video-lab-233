# v003 Follow-Up Batch Plan

Date: 2026-05-24

Product: dog_bath_hose
SKU: blue
Source batch: batch_20260524_expression_style
Follow-up batch: batch_20260524_v003_followup

## Current Signal

v003_profanity_bleeped_shock is not a winner.

Current 12h data:

- views: 2121
- avg_watch_time: 3.3s
- completion_rate: 2.89%
- attention_signal: positive
- retention_signal: negative
- completion_signal: weak
- decision_status: not_winner_yet

## First Principles Read

The crude shock hook appears to create enough interruption to earn attention, but the next seconds do not sustain product interest. The next test should not make the language even harsher. It should test whether the hook can hand off faster to visible proof, product action, and a clearer demo.

## Control Variable

This follow-up tests hook carry-through and expression style only.

Do not change:

- Product.
- CTA direction.
- Basic source material skeleton.
- Language: English.
- Subtitle policy: no subtitles.
- Source video audio policy: original source audio muted.
- Output style: voiceover only.

## Follow-Up Variants

### v003A_profanity_shorter_demo

- variant_id: v003A_profanity_shorter_demo
- style_type: profanity_bleeped_shock_short_demo
- core_angle: Keep shock hook, shorten the setup, and enter the demo faster.
- hook_line: Holy sh*t, those paws are a mess.
- full_voiceover_script: Holy sh*t, those paws are a mess. Quick rinse, less floor cleanup. Snap on the blue hose and wash the mud off fast.
- duration_target: 7-10 seconds
- business_purpose: Test whether the shock hook can retain more viewers when the product action arrives immediately.
- target_metric: avg_watch_time
- first_principles_reason: If attention is already positive but watch time is weak, the bottleneck is likely the handoff after the hook. A shorter demo path reduces friction between emotional interruption and product proof.
- expected_user_response: Viewers who stop for the shock line should see the rinse action before they bounce.
- risk_note: High-risk language remains bleeped or character-masked. It may still reduce trust or product clicks.

### v003B_profanity_visual_first

- variant_id: v003B_profanity_visual_first
- style_type: profanity_bleeped_shock_visual_first
- core_angle: Keep shock hook, but force the first second to show muddy paws, dirty floor, or rinse action.
- hook_line: What the h*ll happened to those paws?
- full_voiceover_script: What the h*ll happened to those paws? Show the mud, rinse it fast, and keep that dirty water off the floor.
- duration_target: 8-11 seconds
- business_purpose: Test whether visual proof in the first second makes the crude hook feel relevant instead of random.
- target_metric: first_3_second_hold
- first_principles_reason: Strong language can create attention, but the visual must instantly justify the emotion. Showing muddy paws or rinse action first links the shock to a concrete product problem.
- expected_user_response: Viewers should understand the messy scene faster and stay long enough to see the product use case.
- risk_note: Still a high-risk test variant. Do not publish uncensored profanity by default.

### v002_slang_lowbrow_control

- variant_id: v002_slang_lowbrow_control
- style_type: slang_lowbrow_control
- core_angle: Keep casual lowbrow tone without strong profanity to test whether retention can improve with less trust damage.
- hook_line: Your dog just dragged the whole yard inside.
- full_voiceover_script: Your dog just dragged the whole yard inside. Muddy paws, dirty floor, bath time mess. Grab the blue hose and rinse it before the mess spreads.
- duration_target: 9-12 seconds
- business_purpose: Compare strong shock against a lower-risk casual expression style.
- target_metric: product_clicks
- first_principles_reason: If v003 gets attention but weak conversion signals, a less aggressive style may preserve relevance while lowering trust loss.
- expected_user_response: Viewers may perceive it as more natural and less jarring while still recognizing the same problem.
- risk_note: Medium risk. It may get less early attention than v003 but produce better click intent.

## Decision Rule

Do not declare a winner from this plan. The next decision requires comparable published data across v003A, v003B, and v002_control.

## Next Manual Step

Create or record voiceover audio for each variant, keep the same visual skeleton where possible, publish manually, then enter checkpoint data through `experiment-record`.
