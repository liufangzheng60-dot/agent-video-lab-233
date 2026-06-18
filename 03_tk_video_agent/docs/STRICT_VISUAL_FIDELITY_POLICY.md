# Strict Visual Fidelity Policy

## Visual Fidelity Red Lines

- Do not change exposure.
- Do not change brightness.
- Do not change contrast.
- Do not change saturation.
- Do not sharpen.
- Do not beautify.
- Do not use AI enhancement.
- Do not denoise.
- Do not auto-correct color.
- Do not change the original material look to make it "clearer".
- Preview / review pack media must stay as close as possible to the source material.

## Allowed ffmpeg Operations

- Trim a time window.
- Transcode to H.264.
- Convert to `yuv420p` for Windows compatibility.
- Use `movflags +faststart`.
- Minimally fix odd width or height when required.
- Mute preview audio with `-an`.
- Extract frames for contact sheets.

## Forbidden ffmpeg Filters

Do not use or introduce:

- `eq`
- `curves`
- `unsharp`
- `smartblur`
- `hqdn3d`
- `colorbalance`
- `hue`
- `lut`
- `lutrgb`
- `lutyuv`
- `tonemap`
- `normalize`
- `sharpen`
- `contrast`
- `brightness`
- `saturation`
- `gamma`
- `zscale` unless explicitly justified
- scale flags that visibly sharpen the image
- any filter named `enhance`, `denoise`, `sharpen`, or `auto`

## Preview Generation Principles

- Prefer no scale.
- Prefer preserving source width and height.
- If width or height is odd, apply only minimal pad or minimal crop to even dimensions.
- Use `format=yuv420p` only for player compatibility.
- Do not adjust picture aesthetics.
- Preview is an Owner review asset, not a beautification stage.

## Quality Gate

Every preview generation must write `visual_fidelity_audit.json` with:

- `ffmpeg_filter_chain`
- `contains_forbidden_filter`
- `source_width`
- `source_height`
- `output_width`
- `output_height`
- `source_pix_fmt`
- `output_pix_fmt`
- `source_color_range`
- `output_color_range`
- `scale_used`
- `scale_reason`
- `suspected_visual_change`
- `visual_fidelity_gate_result`

If `contains_forbidden_filter=true`, the task fails.
If `suspected_visual_change=true`, the preview cannot be used for Owner review.
If exposure change cannot be judged automatically, the report must say so and must not pretend the visual look was artistically approved.

## HDR / 10-bit / Color Metadata Fidelity Rules

1. Visual fidelity forbids not only visible filters, but also undeclared bit-depth, color-transfer, or colorspace conversion.
2. `yuv420p10le`, 10-bit, HDR, HLG, PQ, and Dolby Vision source material must not be converted directly to bare `yuv420p` and marked `visual_fidelity_pass`.
3. If `10-bit -> 8-bit` conversion occurs, the system must generate before/after frame comparison and set `requires_owner_color_review=true`.
4. If `source color_transfer` and `output color_transfer` differ, the system must set `suspected_visual_change=true` or `requires_owner_color_review=true`.
5. If `source color_primaries`, `color_space`, or `color_range` differs from output, the result must enter `color_fidelity_review`.
6. `visual_fidelity_gate` must check color metadata and sample frame comparison, not only filter chains.
7. For HDR / 10-bit source material, preview status can only be one of:
   - `pass_source_like`
   - `pass_controlled_sdr_with_owner_review`
   - `hold_color_review`
   - `reject_visual_fidelity`
8. Any unexplained exposure, sharpness, saturation, contrast, or texture change must block P11C.
9. Hook Preview / Review Pack is not a beautification stage; do not sacrifice source look to make material "clearer".
10. Future full rendering must reuse the same `color_fidelity_guard`.
