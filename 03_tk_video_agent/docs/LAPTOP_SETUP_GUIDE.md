# Laptop Setup Guide

## Clone

```powershell
git clone <repo-url>
cd agent-video-lab-233\03_tk_video_agent
```

## Create Python Environment

```powershell
python -m venv .venv
.\.venv\Scripts\Activate.ps1
python -m pip install --upgrade pip
pip install -r requirements.txt
```

## Install ffmpeg

Install ffmpeg for Windows and confirm:

```powershell
ffmpeg -version
ffprobe -version
```

## Configure `.env`

```powershell
Copy-Item .env.example .env
```

Put real secrets only in `.env`. Do not commit `.env`.

## Verify

```powershell
python main.py --help
.\scripts\smoke_test_laptop.ps1
```

## Raw Videos

Raw videos and outputs are intentionally not synced by Git. Copy raw videos manually from the desktop or mount an external drive. Keep the same product batch path when possible.

## Avoid Committing Outputs

Before any commit:

```powershell
git status --short
git check-ignore -v ..\products\dog_stairs_v1\outputs\
git check-ignore -v ..\products\dog_stairs_v1\inputs\raw_videos\
```

Do not commit generated videos, images, audio, spreadsheets, outputs, `.env`, or raw media.

## Common Errors

- `ffmpeg not found`: install ffmpeg and add it to PATH.
- `main.py --help` fails: activate `.venv` and install requirements.
- raw videos missing: copy media manually; Git intentionally excludes them.
- API key missing: copy `.env.example` to `.env` and fill local values.
