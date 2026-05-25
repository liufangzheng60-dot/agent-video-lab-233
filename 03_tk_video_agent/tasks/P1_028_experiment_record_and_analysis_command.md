# P1_028 Experiment Record And Analysis Command

Date: 2026-05-25

## Goal

Add a minimal `experiment-record` command that reads user-filled TikTok metric markdown, updates the experiment performance CSV, and writes a basic analysis report.

## Command

```bash
python main.py experiment-record --product dog_bath_hose --sku blue --batch batch_20260524_expression_style --input manual_inputs/v003_12h_20260524.md
```

## Boundary

- User manually fills raw TikTok data.
- The system parses key:value markdown.
- Missing values remain `NA`.
- The system does not fetch, infer, or guess missing data.
- The system does not declare a winner.
- Final racing decisions require user review.

## Outputs

- `experiments/dog_bath_hose/blue/batch_20260524_expression_style/02_performance_log.csv`
- `experiments/dog_bath_hose/blue/batch_20260524_expression_style/analysis/v003_12h_analysis.md`
- `experiments/dog_bath_hose/blue/batch_20260524_expression_style/03_racing_decision.md`

## Not Done

- No TikTok API.
- No external API.
- No automatic data scraping.
- No audio or video generation.
- No ffmpeg.
- No render change.
- No firewall change.
- No automatic winner decision.
