# Next Action Queue

## Active Queue

1. User places dog bath hose blue SKU assets into `products/dog_bath_hose/assets/`.
2. Run product-level inventory for `dog_bath_hose`.
3. Generate product-level material pack.
4. Generate product-level edit strategy.
5. Generate product-level timeline.
6. Render product-level review video only after source mp4 exists.
7. Continue subtitles and batch variants only after product-level render succeeds.

## Parking Lot

- Product-level `subtitles --product`.
- Product-level `batch-variants --product`.
- Clip library and keyframe extraction.
