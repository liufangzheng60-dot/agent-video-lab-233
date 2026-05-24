# Voiceover Plan

- Voiceover script: `products/dog_bath_hose/outputs/reports/voiceover_script_20260524.md`
- Recording guide: `products/dog_bath_hose/outputs/reports/voiceover_recording_guide.md`
- Recommended filename: `dog_bath_hose_blue_voiceover_20260524_v001.mp3`
- Source audio muted: `True`
- Subtitle burned: `False`

## Rule

- Final dog_bath_hose videos should use muted source video audio.
- Final dog_bath_hose videos should not burn subtitles by default.
- If a voiceover mp3, wav, or m4a exists, mix that voiceover into the final video.
- If voiceover is missing, generate only a muted visual preview and do not label it as final voiceover output.

## Manual Recording Action

- Choose one script version.
- Record or externally generate English voiceover audio.
- Save the `.mp3`, `.wav`, or `.m4a` file under `products/dog_bath_hose/assets/voiceovers/`.
- Re-run `python main.py render --product dog_bath_hose`.
