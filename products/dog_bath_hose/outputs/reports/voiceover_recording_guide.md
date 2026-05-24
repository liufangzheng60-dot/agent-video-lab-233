# Dog Bath Hose Voiceover Recording Guide

## Goal

Create one English voiceover file for the `dog_bath_hose / blue` product video.

Do not use this project to generate audio automatically. Record manually or use an external tool outside this workflow, then place the finished file into the product voiceover folder.

## Where To Put The Audio

Save the finished `.mp3`, `.wav`, or `.m4a` file here:

```text
products/dog_bath_hose/assets/voiceovers/
```

Recommended filename:

```text
dog_bath_hose_blue_voiceover_20260524_v001.mp3
```

## Recording Rules

- Language: English only.
- Length target: 7-15 seconds.
- Tone: clear, friendly, practical, TikTok Shop US style.
- Do not overclaim safety or medical benefits.
- Do not copy reference video captions, music, or creator phrasing.
- Keep the line natural enough to match a home pet-care demo.

## Suggested Read

Use one of the three versions in:

```text
products/dog_bath_hose/outputs/reports/voiceover_script_20260524.md
```

## Recommended Audio Specs

- Format: `.mp3` preferred
- Voice: natural spoken English
- Volume: loud enough to hear over a silent source video
- Background music: none for the first test
- Silence trimming: remove long silence at the start and end

## After Recording

After placing the audio file in `assets/voiceovers/`, run:

```bash
cd 03_tk_video_agent
python main.py render --product dog_bath_hose
```

Expected output:

```text
products/dog_bath_hose/outputs/renders/final_voiceover_YYYYMMDD.mp4
```

The source video audio will remain muted, subtitles will not be burned, and the voiceover will be mixed in.
