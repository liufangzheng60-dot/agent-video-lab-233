# Edit Strategy

## 目标视频类型

TikTok 商品短视频，目标时长 7-15 秒，结构为 hook -> problem -> demo -> proof -> cta。

## 素材概览

- 素材包来源: `outputs/material_pack/material_pack.json`
- 素材数量: `0`
- 产品 brief 数量: `1`

## 7-15 秒剪辑结构

| Segment | Duration | Purpose | Role | Caption | Execution |
| --- | --- | --- | --- | --- | --- |
| hook | 0-2s | Stop the scroll by showing the cost or pain point immediately. | product_brief_or_script | Stop paying $20+ for nail trims. | Use the strongest pain-point line from the product brief as opening text. Pair with the clearest product or demo visual available. Missing role: product_brief_or_script. |
| problem | 2-4s | Make the viewer recognize the grooming pain or cost problem. | demo_or_source_clip | Pet nail trims are stressful and expensive. | Use source video moments that show pet handling, grooming setup, or the need for safer trimming. Missing role: demo_or_source_clip. |
| demo | 4-9s | Show the product mechanism or use case clearly. | demo_or_source_clip | LED light helps you see the quick before cutting. | Prioritize close-up product operation. If using the 720x960 source clip, crop or rebuild to 9:16 before final timeline work. Missing role: demo_or_source_clip. |
| proof | 9-12s | Give the viewer confidence that the product is safer, quieter, or easier. | product_reference_image | Safer, easier, cheaper at home. | Use product image as a stable proof visual if no dedicated proof clip exists. Keep text short and benefit-led. Missing role: product_reference_image. |
| cta | 12-15s | Tell the viewer what to do next. | product_brief_or_script | Grab yours below. | End with TikTok Shop-oriented CTA text. Do not publish automatically; this is only strategy output. Missing role: product_brief_or_script. |

## 每段使用什么素材

- `hook` 使用 `product_brief_or_script`: 缺少匹配素材
- `problem` 使用 `demo_or_source_clip`: 缺少匹配素材
- `demo` 使用 `demo_or_source_clip`: 缺少匹配素材
- `proof` 使用 `product_reference_image`: 缺少匹配素材
- `cta` 使用 `product_brief_or_script`: 缺少匹配素材

## 风险提示

- `missing_raw_videos`
- `missing_product_images`

## 缺失素材

- `raw_videos`
- `product_images`
- `missing_role_demo_or_source_clip`
- `missing_role_product_brief_or_script`
- `missing_role_product_reference_image`

## 下一步建议

- 进入 P0_004_timeline_plan_only，规划 JSON 时间轴结构。
- 本阶段不剪辑、不渲染、不调用外部 API。
