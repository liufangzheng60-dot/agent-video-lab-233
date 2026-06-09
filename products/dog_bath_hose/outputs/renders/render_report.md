# Render Report

- 生成时间: `2026-05-24T13:40:52.967293+00:00`
- 状态: `success`
- Timeline: `outputs/timelines/timeline.json`
- Material pack: `outputs/material_pack/material_pack.json`
- 输出文件: `outputs/renders/final_voiceover_20260524.mp4`
- 总时长: `15.0` 秒
- ffmpeg 可用: `True`
- source_audio_muted: `True`
- subtitle_burned: `False`
- voiceover_status: `present`
- voiceover_path: `assets/voiceovers/dog_bath_hose_blue_voiceover_20260524_v001.mp3.mp3`
- render_mode: `voiceover`
- 消息: Rendered final voiceover video.

## 输入素材

- `assets/raw_videos/dog_bath_hose_shower_spray_001.mp4.mp4`

## 风险

- 未发现渲染前基础风险。

## ffmpeg 命令摘要

```text
C:\Users\43871\AppData\Local\Microsoft\WinGet\Links\ffmpeg.EXE -y -stream_loop -1 -i assets/raw_videos/dog_bath_hose_shower_spray_001.mp4.mp4 -i assets/voiceovers/dog_bath_hose_blue_voiceover_20260524_v001.mp3.mp3 -t 15.000 -vf scale=720:1280:force_original_aspect_ratio=decrease,pad=720:1280:(ow-iw)/2:(oh-ih)/2,setsar=1 -r 30 -map 0:v:0 -map 1:a:0 -c:v libx264 -preset veryfast -pix_fmt yuv420p -c:a aac -shortest outputs/renders/final_voiceover_20260524.mp4
```

## 边界

- 本阶段只做最小可审片渲染。
- 原视频背景音轨默认静音。
- 默认不烧字幕。
- 不做 AI 视觉理解、转录、自动发布或 UI。
