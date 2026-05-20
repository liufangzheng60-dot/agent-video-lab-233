# P0-006 Manual Review Setup

## Goal

Prepare a structured manual review form for the generated `final.mp4`.

## Inputs

- `outputs/renders/final.mp4`
- `outputs/renders/render_report.md`

## Output

- `outputs/reports/manual_review.md`

## Review Checklist

The review form asks the user to check:

- Whether playback works.
- Whether the video is vertical 9:16.
- Whether the image is distorted.
- Whether the subject is clear.
- Whether pacing is acceptable.
- Whether it feels like a TikTok product video.
- The biggest current problem.
- The smallest next improvement.

## Scope

- Does not modify render logic.
- Does not re-render `final.mp4`.
- Does not call ffmpeg.
- Does not call external APIs.
- Does not install dependencies.
- Does not do AI visual understanding.
