# P0-003 Edit Strategy

## Goal

Generate a TikTok product short video edit strategy from `material_pack.json`.

## Inputs

- `outputs/material_pack/material_pack.json`
- `outputs/material_pack/material_pack.md`

## Outputs

- `outputs/edit_strategy/edit_strategy.json`
- `outputs/edit_strategy/edit_strategy.md`

## Command

```bash
python main.py edit-strategy
```

## Scope

- Builds a 7-15 second TikTok product video strategy.
- Uses hook, problem, demo, proof, and CTA segments.
- Uses `suggested_role` from the material pack.
- Carries aspect-ratio risk into the strategy.
- Notes that non-9:16 video should be cropped or rebuilt in a later timeline stage.
- Does not do AI visual understanding.
- Does not transcribe video.
- Does not edit or render video.
- Does not call external APIs.
- Does not install dependencies.
