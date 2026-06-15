# Asset Readiness Report

- product_slug: `dog_stairs_v1`
- sku_slug: `khaki`
- raw_videos_status: `missing`
- product_images_status: `missing`
- scripts_status: `missing`
- reference_videos_status: `missing`
- voiceovers_status: `missing`
- pipeline_status: `blocked_before_render`

## Blocking Reason

- `products/dog_stairs_v1/assets/raw_videos/` has no actual source video files yet.
- Per current business rule, product-level render was not started.

## Required Next Action

- Put at least one real source clip under `products/dog_stairs_v1/assets/raw_videos/`.
- Then run:
  - `python main.py inventory --product dog_stairs_v1`
  - `python main.py material-pack --product dog_stairs_v1`
  - `python main.py edit-strategy --product dog_stairs_v1`
  - `python main.py timeline --product dog_stairs_v1`
  - `python main.py render --product dog_stairs_v1`

## Standard Material Drop Zones

- Raw product videos: `products/dog_stairs_v1/assets/raw_videos/`
- Product images: `products/dog_stairs_v1/assets/product_images/`
- Script drafts: `products/dog_stairs_v1/assets/scripts/`
- Reference videos: `products/dog_stairs_v1/assets/reference_videos/`
- Voiceover audio: `products/dog_stairs_v1/assets/voiceovers/`
