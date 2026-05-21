# P1-006 Product Workspace Structure

## Goal

Upgrade the project from a single-product demo layout toward product-level isolation while keeping the existing global flow compatible.

## Product Workspace Structure

```text
products/product_slug/
├── product_brief.md
├── assets/
│   ├── raw_videos/
│   ├── product_images/
│   ├── ai_generated_clips/
│   ├── reference_videos/
│   └── scripts/
├── outputs/
│   ├── material_inventory/
│   ├── material_pack/
│   ├── edit_strategy/
│   ├── timelines/
│   ├── subtitles/
│   ├── renders/
│   └── reports/
└── publish/
    ├── publish_records/
    └── performance_feedback/
```

## Example Product

Created example workspace:

```text
products/pet_nail_trimmer/
```

## Compatibility

The existing global flow remains supported:

```text
03_tk_video_agent/inputs/
03_tk_video_agent/outputs/
```

No old files were moved. Current commands continue to work without `--product`.

## Future CLI Target

Future commands should support product-level execution:

```bash
python main.py inventory --product pet_nail_trimmer
python main.py material-pack --product pet_nail_trimmer
python main.py edit-strategy --product pet_nail_trimmer
python main.py timeline --product pet_nail_trimmer
python main.py render --product pet_nail_trimmer
python main.py subtitles --product pet_nail_trimmer
python main.py batch-variants --product pet_nail_trimmer
```

## Future Direction

The long-term direction is a compliant, differentiated TikTok Shop content production system:

```text
multiple source materials
-> automatic keyframe extraction
-> clip library
-> multiple Hook timelines
-> batch rendering
-> performance feedback selects winner
```

The goal is to generate compliant, differentiated, non-duplicate TikTok Shop product video variants. Do not define the goal as avoiding or evading platform algorithms.

## Scope

- Structure and documentation only.
- No new video generation.
- No rendering.
- No AI visual understanding.
- No frame extraction.
- No external API calls.
- No dependency installation.
- No GitHub push.
