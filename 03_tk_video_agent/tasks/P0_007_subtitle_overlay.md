# P0-007 Subtitle Overlay

## Goal

Generate time-aligned SRT subtitles from the existing timeline and burn them into `final.mp4`.

## Inputs

- `outputs/renders/final.mp4`
- `outputs/timelines/timeline.json`
- `outputs/edit_strategy/edit_strategy.json`
- `inputs/product_briefs/`

## Outputs

- `outputs/subtitles/subtitles.srt`
- `outputs/subtitles/subtitle_plan.md`
- `outputs/renders/final_subtitled.mp4`

## Command

```bash
python main.py subtitles
```

## Scope

- Uses timeline start/end/caption fields.
- Uses edit strategy captions as fallback.
- Reads product briefs as supporting copy context.
- Uses local ffmpeg from PATH to burn subtitles.
- Does not do AI visual understanding.
- Does not transcribe video.
- Does not call external APIs.
- Does not install dependencies.
- Does not publish to TikTok.

English-only subtitle rule:

- Final `subtitles.srt` and `final_subtitled.mp4` subtitles must be English-only.
- If timeline or edit strategy already provides an English caption, that caption is used first.
- Chinese captions or Chinese product brief text are never copied into SRT output.
- If no usable English caption exists, the command uses fixed English fallback captions by segment.
- This command does not translate text and does not call external APIs.
