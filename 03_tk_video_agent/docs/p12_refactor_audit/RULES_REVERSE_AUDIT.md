# Rules Reverse Audit

## Config Files Found

- `03_tk_video_agent/configs/tiktok_video_rules.yaml`: early MVP rules with platform, duration, hook, product visibility, and manual review notes.
- `03_tk_video_agent/configs/product_video_scoring.yaml`
- `03_tk_video_agent/configs/project_config.yaml`

The existing YAML rules are too shallow for P12. Most P11/P12 rules currently live in docs and helper logic rather than config.

## hard_rules_to_keep

- controlled_sdr color pipeline lock.
- Prohibit source_like / P11B2 / P11B3 distorted paths from returning to production.
- global_conflict_registry.
- negative_hook_examples / negative memory.
- ffprobe duration validation.
- audio duration fit.
- video stream copy guard.
- no visual reencode after visual master.
- no subtitles unless explicitly requested.
- no auto publish.
- no `git add .`.
- raw_videos immutable.
- Owner approve/reject firewall.
- no secrets in repo.

## general_rules_to_optimize

- strategy_tag selection.
- hook ranking.
- body/proof/CTA segment selection.
- body overlap tolerance.
- voiceover rate strategy.
- title/caption generation.
- publish priority.
- VLM score threshold.
- CTA fallback policy.
- crop/profile recommendations.

## redundant_rules_to_delete_later

- Rules that require Owner to review text plans.
- Multi-layer intermediate lock/manual review steps from P11.
- P11B2/P11B3/P11B4 accident repair steps exposed as daily production flow.
- Fragile code-only heuristics that try to score TikTok feel.
- Overly fine pixel tuning rules.
- Matrix rules that only inspect the first 3 seconds and ignore body/proof/CTA.
- Repeated manifest review logic that should be machine preflight.

## Recommendation

P12 should move rules into three explicit layers: immutable hard gates, configurable quality/strategy rules, and deprecation candidates. The runtime harness should enforce hard gates automatically and expose only final review packs to Owner.
