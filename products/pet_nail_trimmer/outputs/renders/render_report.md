# Render Report

- 生成时间: `2026-05-21T13:58:35.803236+00:00`
- 状态: `success`
- Timeline: `outputs/timelines/timeline.json`
- Material pack: `outputs/material_pack/material_pack.json`
- 输出文件: `outputs/renders/final.mp4`
- 总时长: `15.0` 秒
- ffmpeg 可用: `True`
- 消息: Rendered final.mp4 for manual review.

## 输入素材

- `assets/raw_videos/462a80716c45b93a3449f6c007244ebb.mp4`

## 风险

- `missing_product_images`
- `aspect_ratio_not_9_16`
- `needs_9_16_crop_or_rebuild`

## ffmpeg 命令摘要

```text
C:\Users\43871\AppData\Local\Microsoft\WinGet\Links\ffmpeg.EXE -y -stream_loop -1 -i assets/raw_videos/462a80716c45b93a3449f6c007244ebb.mp4 -t 15.000 -vf scale=720:1280:force_original_aspect_ratio=decrease,pad=720:1280:(ow-iw)/2:(oh-ih)/2,setsar=1 -r 30 -c:v libx264 -preset veryfast -pix_fmt yuv420p -c:a aac -shortest outputs/renders/final.mp4
```

## 边界

- 本阶段只做最小可审片渲染。
- 不做 AI 视觉理解、转录、自动发布或 UI。
