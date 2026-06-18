# GitHub Sync And Laptop Handoff

## Desktop Safe Push

1. Confirm `.gitignore` protects media, outputs, raw videos, audio, images, spreadsheets, logs, and `.env`.
2. Run `git status --short`.
3. Never run `git add .`.
4. Selectively add safe files only: docs, scripts, tests, `.gitignore`, `.env.example`, requirements.
5. Confirm staged files do not include `products/*/outputs`, `raw_videos`, media, `.xlsx`, `.env`, or secrets.
6. Commit with an intentional message.
7. Push to `origin main`.

## Laptop Clone

```powershell
git clone <repo-url>
cd agent-video-lab-233\03_tk_video_agent
```

## Python Environment

```powershell
py -3 -m venv .venv
.\.venv\Scripts\Activate.ps1
python -m pip install --upgrade pip
pip install -r requirements.txt
```

## ffmpeg

Install ffmpeg and ensure `ffmpeg -version` and `ffprobe -version` work in PowerShell.

## Node / npm

Node is not required for the current Python CLI path unless future UI tooling is added.

## Edge-TTS

Install only if running voiceover stages:

```powershell
pip install edge-tts
```

## Gemini API Key

Copy `.env.example` to `.env` and put the real key in `.env` only. Do not commit `.env`.

## Smoke Test

```powershell
python main.py --help
python -m unittest discover -s tests -p "test_*.py"
```

If full tests need local media, run the smoke subset documented in `scripts/smoke_test_laptop.ps1`.

## Raw Videos

Git does not sync `outputs` or `raw_videos`. Manually copy raw videos to the laptop or mount an external drive.

## Verify Ignore Rules

```powershell
git check-ignore -v ..\products\dog_stairs_v1\outputs\
git check-ignore -v ..\products\dog_stairs_v1\inputs\raw_videos\
```

Do not commit generated videos, contact sheets, audio, screenshots, outputs, or raw material.
