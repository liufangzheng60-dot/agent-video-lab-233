# VLM QC Gate Spec

This spec defines a future VLM sidecar. It does not connect to a real API in P12A.

## QC Draft Rules

- Generate 480p previews.
- Use 5-6 fps.
- Use low bitrate.
- Target 1-3 MB.
- Drafts are temporary QC assets and must not be committed.

## Input

- `visual_master_controlled_sdr.mp4`
- `voiced_review.mp4`
- or generated `qc_draft.mp4`

## Output JSON Schema

```json
{
  "variant_id": "...",
  "hook_has_reason": true,
  "human_hand_problem": false,
  "clutter_problem": false,
  "product_visible": true,
  "feature_destroyed_by_crop": false,
  "body_too_repetitive": true,
  "audio_natural": true,
  "decision": "approve|hold|reject",
  "risk_flags": [],
  "notes": "..."
}
```

## Timeout / Retry / Hold Policy

- Use bounded timeout per variant.
- Retry once for transient provider failure.
- If VLM fails, do not crash the whole system; mark variant `hold` with `risk_flags`.
- If VLM returns `hold`, route to Owner; do not auto-fail.

## Secrets

- No API key in repo.
- `.env.example` may only contain `GEMINI_API_KEY=your_gemini_api_key_here`.
- Real keys live only in local `.env`.

## Boundaries

VLM may act only as Quality Gate, visual first-pass reviewer, and reverse QC gateway.

VLM must not:

- bypass hard rules
- directly modify timeline
- delete files
- auto publish
- modify raw assets
- modify Git
