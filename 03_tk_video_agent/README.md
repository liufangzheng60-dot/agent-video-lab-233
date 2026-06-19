# tk_video_agent

TikTok 商品视频剪辑 Agent 的主开发区。

当前阶段目标：

- 读取一个商品案例的素材和产品 brief。
- 生成素材盘点。
- 生成剪辑策略。
- 生成自定义 `timeline.json`。
- 生成 CapCut 人工复刻用 `capcut_timeline.csv`。

当前阶段不做：

- 不自动发布 TikTok。
- 不创建 UI。
- 不调用外部 API。
- 不实现复杂业务逻辑。
- 不生成最终视频，除非进入明确的渲染任务。

## 目录

- `configs/`：项目配置、TikTok 视频规则、商品视频评分规则。
- `inputs/`：主开发区输入素材。
- `outputs/`：素材盘点、剪辑策略、时间轴、渲染结果和报告。
- `skills/`：本项目专用 Skill。
- `prompts/`：可复用 Prompt。
- `helpers/`：Python 辅助脚本。
- `tests/`：pytest 测试。
- `tasks/`：阶段任务说明。

## 本地素材盘点

运行：

```bash
python main.py inventory
```

默认扫描：

- `inputs/product_images/`
- `inputs/raw_videos/`
- `inputs/ai_generated_clips/`
- `inputs/product_briefs/`
- `inputs/reference_videos/`

默认输出：

- `outputs/material_inventory/material_inventory.json`
- `outputs/material_inventory/material_inventory.md`

第一版只做本地文件盘点。`ffprobe` 如果可用，会补充媒体时长、分辨率和音轨信息；如果不可用，程序不会中断，会在风险提示中记录 `ffprobe_unavailable`。

Product-scoped inventory is also supported:

```bash
python main.py inventory --product pet_nail_trimmer
```

This scans `../products/pet_nail_trimmer/assets/` and writes:

- `../products/pet_nail_trimmer/outputs/material_inventory/material_inventory.json`
- `../products/pet_nail_trimmer/outputs/material_inventory/material_inventory.md`

Current product-scoped commands include `inventory`, `material-pack`, `edit-strategy`, and `timeline`. Product-scoped `render` is in validation and writes a clear report when product-level source video is missing.

## 素材包生成

运行：

```bash
python main.py material-pack
```

默认输入：

- `outputs/material_inventory/material_inventory.json`
- `inputs/product_briefs/*.txt`
- `inputs/product_briefs/*.md`

默认输出：

- `outputs/material_pack/material_pack.json`
- `outputs/material_pack/material_pack.md`

Product-scoped material pack is also supported:

```bash
python main.py material-pack --product pet_nail_trimmer
```

This reads:

- `../products/pet_nail_trimmer/outputs/material_inventory/material_inventory.json`
- `../products/pet_nail_trimmer/product_brief.md`
- `../products/pet_nail_trimmer/assets/scripts/*.txt`
- `../products/pet_nail_trimmer/assets/scripts/*.md`

And writes:

- `../products/pet_nail_trimmer/outputs/material_pack/material_pack.json`
- `../products/pet_nail_trimmer/outputs/material_pack/material_pack.md`

第一版只做本地素材包整理：读取素材盘点和产品 brief，为素材分配 `suggested_role`，并添加基础风险提示。不做 AI 视觉理解、转录、剪辑、渲染或外部 API 调用。

## 剪辑策略生成

运行：

```bash
python main.py edit-strategy
```

默认输入：

- `outputs/material_pack/material_pack.json`
- `outputs/material_pack/material_pack.md`

默认输出：

- `outputs/edit_strategy/edit_strategy.json`
- `outputs/edit_strategy/edit_strategy.md`

第一版只生成 TikTok 商品短视频剪辑策略，目标时长 7-15 秒，结构为 `hook -> problem -> demo -> proof -> cta`。它会使用素材包中的 `suggested_role`，并把非 9:16 视频风险传递到策略中。本阶段不做 AI 视觉理解、转录、剪辑、渲染或外部 API 调用。

Product-scoped edit strategy is also supported:

```bash
python main.py edit-strategy --product pet_nail_trimmer
```

This reads:

- `../products/pet_nail_trimmer/outputs/material_pack/material_pack.json`

And writes:

- `../products/pet_nail_trimmer/outputs/edit_strategy/edit_strategy.json`
- `../products/pet_nail_trimmer/outputs/edit_strategy/edit_strategy.md`

## 时间轴生成

运行：

```bash
python main.py timeline
```

默认输入：

- `outputs/edit_strategy/edit_strategy.json`
- `outputs/material_pack/material_pack.json`

默认输出：

- `outputs/timelines/timeline.json`
- `outputs/timelines/capcut_timeline.csv`

第一版只生成可执行规划时间轴和 CapCut 人工复刻 CSV。它不会调用 ffmpeg，不会剪辑，不会渲染，也不会生成 `final.mp4`。

Product-scoped timeline is also supported:

```bash
python main.py timeline --product pet_nail_trimmer
```

This reads:

- `../products/pet_nail_trimmer/outputs/edit_strategy/edit_strategy.json`
- `../products/pet_nail_trimmer/outputs/material_pack/material_pack.json`

And writes:

- `../products/pet_nail_trimmer/outputs/timelines/timeline.json`
- `../products/pet_nail_trimmer/outputs/timelines/capcut_timeline.csv`

## 最小渲染

运行：

```bash
python main.py render
```

默认输入：

- `outputs/timelines/timeline.json`
- `outputs/material_pack/material_pack.json`
- `inputs/raw_videos/`

默认输出：

- `outputs/renders/final.mp4`
- `outputs/renders/render_report.md`

第一版使用本机 PATH 中的 `ffmpeg`，把 timeline 引用的 mp4 素材生成一个 9:16 可审片视频。当前采用 scale + pad 输出 720x1280，并记录非 9:16 风险。不做 AI 视觉理解、转录、自动发布或 UI。

Product-scoped render is also supported:

```bash
python main.py render --product pet_nail_trimmer
```

This reads:

- `../products/pet_nail_trimmer/outputs/timelines/timeline.json`
- `../products/pet_nail_trimmer/outputs/material_pack/material_pack.json`
- `../products/pet_nail_trimmer/assets/raw_videos/`

And writes:

- `../products/pet_nail_trimmer/outputs/renders/final.mp4`
- `../products/pet_nail_trimmer/outputs/renders/render_report.md`

If the product timeline does not reference an existing video under the product workspace, render writes a clear `render_report.md` failure instead of moving or borrowing global files.

## 人工审片

审片文件：

```text
outputs/reports/manual_review.md
```

当前审片对象：

```text
outputs/renders/final.mp4
```

请人工打开 `final.mp4`，检查播放、竖屏比例、画面变形、主体清晰度、节奏和 TikTok 商品视频观感，并把结论写入 `manual_review.md`。本步骤不重新渲染，不调用 ffmpeg。

## 字幕烧录

运行：

```bash
python main.py subtitles
```

默认输入：

- `outputs/renders/final.mp4`
- `outputs/timelines/timeline.json`
- `outputs/edit_strategy/edit_strategy.json`
- `inputs/product_briefs/`

默认输出：

- `outputs/subtitles/subtitles.srt`
- `outputs/subtitles/subtitle_plan.md`
- `outputs/renders/final_subtitled.mp4`

第一版从 timeline 的时间和 caption 生成英文短字幕，并使用本机 `ffmpeg` 烧录到现有 `final.mp4`。不做 AI 视觉理解、视频转录、外部 API 调用或自动发布。

English-only subtitle rule:

`python main.py subtitles` always writes English-only subtitles to `outputs/subtitles/subtitles.srt` and burns those English subtitles into `outputs/renders/final_subtitled.mp4`. Chinese source captions or product brief text are not copied into the SRT; fixed English fallback templates are used when needed. No translation API is called.

## Manual Publish Record And Feedback Loop

P1 starts with manual publishing records, not automatic publishing.

Templates:

```text
../05_final_outputs/publish_records/video_v001_publish_record.md
../05_final_outputs/performance_feedback/video_v001_feedback.md
```

Use `video_v001_publish_record.md` before posting to confirm the asset, caption, hashtags, product attachment, and manual publish URL. Use `video_v001_feedback.md` after posting to record 1h, 3h, 24h, and 48h performance data, then decide the smallest next iteration.

Iteration rules:

- Poor 3-second retention -> improve Hook.
- Poor product clicks -> improve subtitles and CTA.
- Poor completion -> shorten pacing.
- Comments ask product function -> strengthen demo and proof.
- Low views but good engagement -> keep structure and replace material.

## video_v001 Manual Publish Pack

Prepared files:

```text
../05_final_outputs/publish_records/video_v001_publish_pack.md
../05_final_outputs/publish_records/video_v001_caption_options.md
../05_final_outputs/performance_feedback/video_v001_feedback.md
```

Use the publish pack to manually post `outputs/renders/final_subtitled.mp4` to TikTok Shop US. No automatic publishing, external API call, video modification, or re-rendering is performed by this project step.

## Batch A/B Variant Generation

Run:

```bash
python main.py batch-variants
```

This generates five TikTok Shop US test variants from the existing `final.mp4`:

- v002 cost hook
- v003 stress hook
- v004 LED safety hook
- v005 home grooming hook
- v006 fast demo hook

Outputs include five subtitle-burned mp4 files, SRT files under `outputs/subtitles/batch_variants/`, and manual publish/feedback templates under `../05_final_outputs/`. No automatic TikTok publishing or external API calls are performed.

## Date Naming Rule For Batch Outputs

Future generated batch outputs must include a concrete `YYYYMMDD` date stamp in filenames:

- `final_v002_cost_hook_YYYYMMDD.mp4`
- `final_v003_stress_hook_YYYYMMDD.mp4`
- `final_v004_led_safety_hook_YYYYMMDD.mp4`
- `final_v005_home_grooming_hook_YYYYMMDD.mp4`
- `final_v006_fast_demo_hook_YYYYMMDD.mp4`
- `batch_v002_to_v006_publish_plan_YYYYMMDD.md`
- `batch_v002_to_v006_feedback_YYYYMMDD.md`
- `batch_v002_to_v006_qc_review_YYYYMMDD.md`

This makes publishing, feedback, and audit records easier to connect to the exact batch date.

## Experiment Racing Templates

Run:

```bash
python main.py experiment-init --product pet_nail_trimmer --sku default_sku --batch batch_20260520_v002_v006
```

This creates manual-fill templates under:

```text
../experiments/product_slug/sku_slug/batch_YYYYMMDD_vXXX_vYYY/
```

Example:

```text
../experiments/pet_nail_trimmer/default_sku/batch_20260520_v002_v006/
├── 00_batch_brief.md
├── 01_variants.csv
├── 02_performance_log.csv
├── 03_racing_decision.md
└── 04_next_iteration.md
```

Use these files to manually record each A/B test batch, compare variants, choose winners and losers, and plan the next iteration. Missing or unavailable data should be entered as `NA`. This command does not generate videos, publish to TikTok, call external APIs, or install dependencies.

## Experiment Record And Analysis

Run:

```bash
python main.py experiment-record --product dog_bath_hose --sku blue --batch batch_20260524_expression_style --input manual_inputs/v003_12h_20260524.md
```

The user is responsible for manually filling raw TikTok backend data in a key:value markdown file under the batch `manual_inputs/` folder. The command updates `02_performance_log.csv` and writes an analysis report under `analysis/`.

Rules:

- Missing values remain `NA`.
- No TikTok API or external API is called.
- No backend data is scraped automatically.
- The command may mark signals such as attention, retention, and completion, but it does not automatically declare a winner.
- Final racing decisions must be reviewed by the user.

## New SKU Test Entry: dog_bath_hose / blue

The next product-level test workspace is:

```text
../products/dog_bath_hose/
```

SKU:

```text
blue
```

Place source material here:

- `../products/dog_bath_hose/assets/raw_videos/`
- `../products/dog_bath_hose/assets/product_images/`
- `../products/dog_bath_hose/assets/scripts/`
- `../products/dog_bath_hose/assets/ai_generated_clips/`
- `../products/dog_bath_hose/assets/reference_videos/`

The first manual A/B testing batch is:

```text
../experiments/dog_bath_hose/blue/batch_20260520_v001_v005/
```

Use this batch to record v001-v005 variants, manual publish status, performance checkpoints, racing decisions, and the next iteration plan. Do not mix this product-level test with the old global demo baseline.

## Control Console And Scenario Keyword Mining

The workspace now includes governance and research templates for multi-model, multi-product, multi-SKU work:

```text
../control_console/
../project_journal/
../scenario_keyword_mining/
```

Use `control_console/` for master decisions, role contracts, data firewall policy, module registry, do-not-touch rules, and next action queue. This area is read-only by default unless the user explicitly approves a control update.

Use `project_journal/` for build logs, decisions, errors, and changelog notes.

Use `scenario_keyword_mining/` to mine scene words, pain words, emotion triggers, Hook hypotheses, demo logic, and differentiated selling points. Do not copy reference video captions, original music, original footage, creator identity, or distinctive expression.

## Codex Report Compression

The project folder is the source of truth. Complete reports should be stored in `project_journal/` or `tasks/`; chat responses should default to concise summaries.

- Low-risk tasks: summary only.
- Medium-risk tasks: summary plus Review Package path.
- High-risk tasks: full report allowed.

High-risk tasks include firewall integration into business flows, multi-model API integration, `control_console/` or core strategy changes, batch deletes or moves, major `products/` or `experiments/` structure changes, OpenAI/Claude/Seedance API connections, core render logic changes, and automatic TikTok publishing.

## Product-Level Workspace Structure

The project now supports a product-level workspace pattern while keeping the original global `inputs/` and `outputs/` flow compatible.

Example product workspace:

```text
../products/pet_nail_trimmer/
├── product_brief.md
├── assets/
│   ├── raw_videos/
│   ├── product_images/
│   ├── ai_generated_clips/
│   ├── reference_videos/
│   └── scripts/
├── outputs/
│   ├── material_inventory/
│   ├── material_pack/
│   ├── edit_strategy/
│   ├── timelines/
│   ├── subtitles/
│   ├── renders/
│   └── reports/
└── publish/
    ├── publish_records/
    └── performance_feedback/
```

Future command target:

Current product-aware commands:

```bash
python main.py inventory --product pet_nail_trimmer
python main.py material-pack --product pet_nail_trimmer
python main.py edit-strategy --product pet_nail_trimmer
python main.py timeline --product pet_nail_trimmer
```

Product-aware render validation:

```bash
python main.py render --product pet_nail_trimmer
```

## dog_bath_hose Voiceover-Only Render Policy

For `dog_bath_hose / blue`, product-level render follows a voiceover-only rule:

- Source video background audio is muted.
- Subtitles are not burned by default.
- Voiceover audio is read from `../products/dog_bath_hose/assets/voiceovers/` when a `.mp3`, `.wav`, or `.m4a` file exists.
- If voiceover exists, render writes `../products/dog_bath_hose/outputs/renders/final_voiceover_YYYYMMDD.mp4`.
- If voiceover is missing, render writes only a muted visual preview and `voiceover_plan.md`; the muted preview is not treated as a final voiceover video.

Relevant reports:

```text
../products/dog_bath_hose/outputs/renders/render_report.md
../products/dog_bath_hose/outputs/reports/asset_readiness_report.md
../products/dog_bath_hose/outputs/reports/voiceover_plan.md
../products/dog_bath_hose/outputs/reports/business_pipeline_report.md
```

Manual voiceover planning files:

```text
../products/dog_bath_hose/outputs/reports/voiceover_script_20260524.md
../products/dog_bath_hose/outputs/reports/voiceover_recording_guide.md
```

Record or externally generate the selected English voiceover, then place the `.mp3`, `.wav`, or `.m4a` file under:

```text
../products/dog_bath_hose/assets/voiceovers/
```

Recommended filename:

```text
dog_bath_hose_blue_voiceover_20260524_v001.mp3
```

## dog_bath_hose Expression Style Testing

`dog_bath_hose / blue` can run controlled English voiceover expression tests where the only primary variable is `expression_style`.

Allowed controlled expression styles include:

- `baseline_direct`
- `slang_lowbrow`
- `profanity_bleeped_shock`
- `chaos_pain`
- `convenience_easy`

Slang, lowbrow phrasing, and bleeped profanity are allowed only as isolated test variables. They must be clearly labeled with:

- `profanity_level`
- `platform_risk`
- `bleep_required`
- `first_principles_reason`

High-risk shock variants must not be mixed with normal commercial versions or treated as default brand voice. The business purpose must be explicit, such as testing whether stronger emotional shock improves first-two-second retention while accepting that it may reduce trust, product clicks, or conversion.

Current follow-up planning:

```text
../products/dog_bath_hose/outputs/reports/v003_followup_plan_20260524.md
../experiments/dog_bath_hose/blue/batch_20260524_v003_followup/
```

The v003 follow-up batch treats `v003_profanity_bleeped_shock` as an attention-positive signal, not a winner. It tests whether shorter demo handoff, visual-first proof, or a slang lowbrow control can improve retention while keeping product, CTA, source skeleton, no-subtitle policy, and muted source audio unchanged.

Future product-aware command target:

```bash
python main.py subtitles --product pet_nail_trimmer
python main.py batch-variants --product pet_nail_trimmer
```

Current commands remain compatible without `--product`. No existing files were moved.

Future matrix direction: multiple source materials -> keyframe extraction -> clip library -> multiple Hook timelines -> batch rendering -> performance feedback selects winner. The goal is compliant, differentiated, non-duplicate TikTok Shop product video variants, not algorithm evasion.

## New Product Minimal Business Pipeline: dog_stairs_v1 / khaki

This repository now also supports a fresh product workspace for `dog_stairs_v1 / khaki` under:

```text
../products/dog_stairs_v1/
../experiments/dog_stairs_v1/khaki/batch_20260615_v001/
```

Standard material drop zones:

- `../products/dog_stairs_v1/assets/raw_videos/`
- `../products/dog_stairs_v1/assets/product_images/`
- `../products/dog_stairs_v1/assets/scripts/`
- `../products/dog_stairs_v1/assets/reference_videos/`
- `../products/dog_stairs_v1/assets/voiceovers/`

When raw video material exists, run:

```bash
python main.py inventory --product dog_stairs_v1
python main.py material-pack --product dog_stairs_v1
python main.py edit-strategy --product dog_stairs_v1
python main.py timeline --product dog_stairs_v1
python main.py render --product dog_stairs_v1
```

Business rule:

- Do not auto-publish TikTok.
- Do not auto-judge winner.
- Source background audio stays muted.
- Subtitles are not burned by default.
- If a `.mp3`, `.wav`, or `.m4a` exists under `../products/dog_stairs_v1/assets/voiceovers/`, render may output `final_voiceover_YYYYMMDD.mp4`.
- If voiceover is missing, render should output only `muted_visual_preview_YYYYMMDD.mp4` and keep `voiceover_plan.md`.
- If raw video is missing, stop before render and use `asset_readiness_report.md` to tell the operator what material is still missing.

## Material Batch Contact Sheet Minimal

This project also supports a raw video batch intake flow for product workspaces.

Run:

```bash
python main.py material-batch --product dog_stairs_v1 --sku khaki --material-batch batch_20260615_001
python main.py contact-sheet --product dog_stairs_v1 --sku khaki --material-batch batch_20260615_001
```

Input folder:

```text
../products/dog_stairs_v1/assets/raw_videos/batch_20260615_001/
```

Output folder:

```text
../products/dog_stairs_v1/outputs/material_batches/batch_20260615_001/
```

`material-batch` rules:

- Keeps original filenames unchanged.
- Ignores `.gitkeep` and non-video files.
- Scans only the top level of the selected batch folder.
- Creates the input folder automatically if it does not exist.
- Writes `clip_manifest.csv`, `clip_manifest.json`, `clip_tags_template.csv`, and `batch_asset_report.md`.
- Computes stable `clip_id` values from sorted filenames.
- Computes `checksum_sha256` for every clip.
- Uses local `ffprobe` metadata when available, otherwise writes `NA` without crashing.

`contact-sheet` rules:

- Reads `clip_manifest.csv` and writes one `{clip_id}_contact_sheet.jpg` per clip under `contact_sheets/`.
- Uses local `ffmpeg` only.
- If `ffmpeg` is missing or fails, it writes `contact_sheet_report.md` without crashing the project.
- No external API, AI, automatic editing, or render pipeline is triggered by these commands.

## Folder-as-Tag Review Init

Run:

```bash
python main.py tag-review-init --product dog_stairs_v1 --sku khaki --material-batch batch_20260615_001
```

This creates:

```text
../products/dog_stairs_v1/outputs/material_batches/batch_20260615_001/tag_review/
```

Inside `tag_review/`, the system creates fixed manual review folders such as `dog_climbs_steps`, `paw_grip_closeup`, `bad_clip`, and `duplicate_clip`, plus `README_TAG_REVIEW.md`.

Manual rule:

- Copy only `contact_sheets/*.jpg` into the matching tag folders.
- Do not move raw source files from `assets/raw_videos/`.
- Do not put video files inside `tag_review/`.
- Later parsing will recover `clip_id` from jpg filenames only.

Generate `clip_tags.csv` from folder placement:

```bash
python main.py tag-from-folders --product dog_stairs_v1 --sku khaki --material-batch batch_20260615_001
```

This reads:

- `../products/dog_stairs_v1/outputs/material_batches/batch_20260615_001/clip_manifest.csv`
- `../products/dog_stairs_v1/outputs/material_batches/batch_20260615_001/tag_review/<scene_tag>/*.jpg`

And writes:

- `../products/dog_stairs_v1/outputs/material_batches/batch_20260615_001/clip_tags.csv`
- `../products/dog_stairs_v1/outputs/material_batches/batch_20260615_001/folder_tagging_report.md`

Rules:

- `clip_id` is parsed from `{clip_id}_contact_sheet.jpg`.
- Multiple tag folders for the same `clip_id` create a conflict and leave that row untagged.
- Clips absent from all tag folders keep empty `scene_tag` and `manual_notes=untagged`.
- If any video file is mistakenly placed inside `tag_review/`, the report records a warning without moving or deleting that file.

## Script Pack Inspect

Run:

```bash
python main.py script-pack-inspect --product dog_stairs_v1 --script-file script_pack.xlsx
```

This performs a read-only workbook inspection for:

```text
../products/dog_stairs_v1/assets/scripts/script_pack.xlsx
```

Outputs:

```text
../products/dog_stairs_v1/outputs/script_pack/script_pack_inspection_report.md
../products/dog_stairs_v1/outputs/script_pack/script_pack_inspection.json
```

Scope:

- Checks whether the workbook file exists.
- Reads workbook sheet names when `openpyxl` is available.
- Records each sheet's `max_row`, `max_column`, and a 1-3 row preview.
- Does not modify the xlsx file.
- If `openpyxl` is missing, writes a clear `missing_dependency_openpyxl` inspection error instead of crashing.

## Script Pack Parse By Index

Run:

```bash
python main.py script-pack-parse --product dog_stairs_v1 --script-file script_pack.xlsx
```

This parses the same workbook by fixed sheet index, not by Chinese sheet names or Chinese header text.

Sheet index map:

- `0`: `strategy_review`
- `1`: `script_overview`
- `2`: `full_timeline`
- `3`: `material_shot_list`
- `4`: `voiceover_subtitle_pack`
- `5`: `test_board`
- `6`: `forbidden_terms`
- `7`: `sources_rules`

Outputs:

- `../products/dog_stairs_v1/outputs/script_pack/sheet_map.json`
- `../products/dog_stairs_v1/outputs/script_pack/timeline_segments.csv`
- `../products/dog_stairs_v1/outputs/script_pack/shot_requirements.csv`
- `../products/dog_stairs_v1/outputs/script_pack/voiceover_lines.csv`
- `../products/dog_stairs_v1/outputs/script_pack/subtitle_lines.csv`
- `../products/dog_stairs_v1/outputs/script_pack/forbidden_claims.csv`
- `../products/dog_stairs_v1/outputs/script_pack/script_pack_parse_report.md`
- `../products/dog_stairs_v1/outputs/script_pack/script_pack_parse.json`

Scope:

- Does not modify the xlsx file.
- Does not generate timeline output for editing or rendering.
- Rows with unrecognized time ranges are preserved with `parse_status=needs_review`.
- CSV outputs use UTF-8-SIG for Windows/WPS/Excel compatibility.

## Shot Match Dry Run

Run:

```bash
python main.py shot-match --product dog_stairs_v1 --sku khaki --material-batch batch_20260615_001
```

This creates a dry-run matching plan from parsed script CSVs and manually tagged material clips. It does not render video and does not modify raw media.

Inputs:

- `../products/dog_stairs_v1/outputs/script_pack/timeline_segments.csv`
- `../products/dog_stairs_v1/outputs/script_pack/shot_requirements.csv`
- `../products/dog_stairs_v1/outputs/script_pack/voiceover_lines.csv`
- `../products/dog_stairs_v1/outputs/script_pack/subtitle_lines.csv`
- `../products/dog_stairs_v1/outputs/material_batches/batch_20260615_001/clip_manifest.csv`
- `../products/dog_stairs_v1/outputs/material_batches/batch_20260615_001/clip_tags.csv`

Outputs:

- `../products/dog_stairs_v1/outputs/shot_match/shot_match_plan.csv`
- `../products/dog_stairs_v1/outputs/shot_match/edit_decision_list.csv`
- `../products/dog_stairs_v1/outputs/shot_match/shot_match_report.md`
- `../products/dog_stairs_v1/outputs/shot_match/shot_match_summary.json`

Matching behavior:

- Uses `shot_requirements.csv` first, then falls back to `timeline_segments.csv`.
- Excludes untagged clips, `quality_score <= 1`, and `bad_clip` risk flags.
- Allows clip reuse but marks `reused_clip` in warnings.
- Reports low proof material pool as `proof_pool_low`.

## Shot Match V002

Run:

```bash
python main.py shot-match-v002 --product dog_stairs_v1 --sku khaki --material-batch batch_20260615_001 --rules products/dog_stairs_v1/outputs/creative_strategy/v002/shot_match_rules_v002.json
```

This regenerates the shot match plan using the frozen v002 creative rules. It does not render video and does not create MP4 files.

Outputs:

- `../products/dog_stairs_v1/outputs/shot_match/v002/shot_match_plan_v002.csv`
- `../products/dog_stairs_v1/outputs/shot_match/v002/edit_decision_list_v002.csv`
- `../products/dog_stairs_v1/outputs/shot_match/v002/shot_match_report_v002.md`
- `../products/dog_stairs_v1/outputs/shot_match/v002/shot_match_summary_v002.json`

V002 behavior:

- Limits per-script clip reuse according to `max_clip_reuse_per_script`.
- Penalizes `avoid_high_reuse_clip_ids`, including the v001 overused C002 clip.
- Prioritizes `dog_hesitates_jump`, `dog_climbs_steps`, and `paw_grip_closeup` in the first 3 seconds.
- Blocks `product_static_detail` and `living_room_aesthetic` from the first 3 seconds.

## Render Preflight Dry Run

Run:

```bash
python main.py render-preflight --product dog_stairs_v1 --sku khaki --material-batch batch_20260615_001
```

This validates the shot-match EDL before actual rendering. It writes a render plan only and does not create mp4 files.

Inputs:

- `../products/dog_stairs_v1/outputs/shot_match/edit_decision_list.csv`
- `../products/dog_stairs_v1/outputs/shot_match/shot_match_plan.csv`
- `../products/dog_stairs_v1/outputs/material_batches/batch_20260615_001/clip_manifest.csv`
- `../products/dog_stairs_v1/outputs/material_batches/batch_20260615_001/clip_tags.csv`

Outputs:

- `../products/dog_stairs_v1/outputs/render_preflight/render_plan.csv`
- `../products/dog_stairs_v1/outputs/render_preflight/render_plan.json`
- `../products/dog_stairs_v1/outputs/render_preflight/render_preflight_report.md`
- `../products/dog_stairs_v1/outputs/render_preflight/render_preflight_summary.json`

Checks:

- Source files exist and stay under the raw video batch folder.
- Clip start/end times are valid and clamped to manifest duration when needed.
- Short clips, high clip reuse, low proof pool, and ffmpeg availability are reported.
- Next-stage render strategy is recorded as 9:16, 1080x1920, center crop with scale-and-pad fallback.

## Render Preflight V002

Run:

```bash
python main.py render-preflight-v002 --product dog_stairs_v1 --sku khaki --material-batch batch_20260615_001 --variant v002
```

This validates the v002 shot-match EDL before actual rendering. It writes a v002 render plan only and does not create MP4 files.

Inputs:

- `../products/dog_stairs_v1/outputs/shot_match/v002/edit_decision_list_v002.csv`
- `../products/dog_stairs_v1/outputs/shot_match/v002/shot_match_plan_v002.csv`
- `../products/dog_stairs_v1/outputs/material_batches/batch_20260615_001/clip_manifest.csv`
- `../products/dog_stairs_v1/outputs/material_batches/batch_20260615_001/clip_tags.csv`

Outputs:

- `../products/dog_stairs_v1/outputs/render_preflight/v002/render_plan_v002.csv`
- `../products/dog_stairs_v1/outputs/render_preflight/v002/render_plan_v002.json`
- `../products/dog_stairs_v1/outputs/render_preflight/v002/render_preflight_report_v002.md`
- `../products/dog_stairs_v1/outputs/render_preflight/v002/render_preflight_summary_v002.json`

V002 checks:

- Confirms C002 reuse remains zero.
- Confirms V1 first 3 seconds do not use static product or pure home aesthetic scene tags.
- Enforces max per-script clip reuse reporting against the v002 limit.
- Records render strategy as mp4, 1080x1920, center crop, scale-and-pad fallback, muted original audio, and SRT-first subtitles.

## Actual Render V001

Run:

```bash
python main.py actual-render --product dog_stairs_v1 --sku khaki --material-batch batch_20260615_001 --variant v001
```

This renders the first script ID from `render_plan.csv` into a muted rough-cut MP4. It does not call APIs, does not synthesize TTS, does not upload, and does not modify raw media.

Inputs:

- `../products/dog_stairs_v1/outputs/render_preflight/render_plan.csv`
- `../products/dog_stairs_v1/outputs/render_preflight/render_plan.json`
- `../products/dog_stairs_v1/outputs/shot_match/edit_decision_list.csv`

Outputs:

- `../products/dog_stairs_v1/outputs/renders/batch_20260615_001/v001/dog_stairs_v1_khaki_batch_20260615_001_v001.mp4`
- `../products/dog_stairs_v1/outputs/renders/batch_20260615_001/v001/dog_stairs_v1_khaki_batch_20260615_001_v001.srt`
- `../products/dog_stairs_v1/outputs/renders/batch_20260615_001/v001/actual_render_report.md`
- `../products/dog_stairs_v1/outputs/renders/batch_20260615_001/v001/actual_render_summary.json`
- `../products/dog_stairs_v1/outputs/renders/batch_20260615_001/v001/ffmpeg_command.txt`

Render behavior:

- Selects only the first script ID in `render_plan.csv` when multiple script IDs exist.
- Transcodes each segment to 1080x1920, muted, then concatenates the segments.
- Tries `center_crop` first and falls back to `scale_and_pad` if rendering fails.
- Generates an external UTF-8-SIG SRT file from `burned_subtitle` or `voiceover_text`; subtitles are not burned in this step.

## Render Review Pack

Run:

```bash
python main.py render-review-pack --product dog_stairs_v1 --sku khaki --material-batch batch_20260615_001 --variant v001
```

This creates a human review pack from an existing rendered MP4. It does not render a new MP4 and does not modify the original video.

Inputs:

- `../products/dog_stairs_v1/outputs/renders/batch_20260615_001/v001/dog_stairs_v1_khaki_batch_20260615_001_v001.mp4`
- `../products/dog_stairs_v1/outputs/renders/batch_20260615_001/v001/dog_stairs_v1_khaki_batch_20260615_001_v001.srt`

Outputs:

- `../products/dog_stairs_v1/outputs/renders/batch_20260615_001/v001/review_pack/review_frames/`
- `../products/dog_stairs_v1/outputs/renders/batch_20260615_001/v001/review_pack/review_contact_sheet.jpg`
- `../products/dog_stairs_v1/outputs/renders/batch_20260615_001/v001/review_pack/render_review_checklist.md`
- `../products/dog_stairs_v1/outputs/renders/batch_20260615_001/v001/review_pack/render_review_summary.json`

Review behavior:

- Reads duration, resolution, and fps with ffprobe.
- Extracts roughly one frame per second into `review_frames/`.
- Builds a JPG contact sheet for quick human review.
- Counts SRT subtitle entries and writes a manual scoring checklist.

## Creative Asset Diagnosis

Run:

```bash
python main.py creative-diagnose-assets --product dog_stairs_v1 --sku khaki --material-batch batch_20260615_001 --variant v001
```

This records human review scores and diagnoses whether the current asset pool can support the next creative iteration. It does not run shot matching, does not render, and does not create new MP4 files.

Inputs:

- `../products/dog_stairs_v1/outputs/material_batches/batch_20260615_001/clip_tags.csv`
- `../products/dog_stairs_v1/outputs/shot_match/shot_match_plan.csv`
- `../products/dog_stairs_v1/outputs/render_preflight/render_preflight_summary.json`
- `../products/dog_stairs_v1/outputs/renders/batch_20260615_001/v001/actual_render_summary.json`
- `../products/dog_stairs_v1/outputs/renders/batch_20260615_001/v001/review_pack/render_review_summary.json`

Outputs:

- `../products/dog_stairs_v1/outputs/renders/batch_20260615_001/v001/review_pack/human_review_scores_v001.json`
- `../products/dog_stairs_v1/outputs/creative_strategy/v002/asset_capability_diagnosis.json`
- `../products/dog_stairs_v1/outputs/creative_strategy/v002/asset_capability_diagnosis.md`
- `../products/dog_stairs_v1/outputs/creative_strategy/v002/creative_diagnosis_inputs.json`

Diagnosis scope:

- Summarizes clip tags, candidate counts, scene tag distribution, and risk flags.
- Summarizes shot matching reuse, high reuse clip IDs, and segment roles.
- Converts human review scores into operational flags such as `hook_weak`, `crop_ok`, `repetition_risk`, and `proof_pool_low`.
- Missing optional summary files are reported as warnings instead of stopping the diagnosis.

## Creative Strategy V002

Run:

```bash
python main.py creative-strategy-v002 --product dog_stairs_v1 --sku khaki --material-batch batch_20260615_001 --from-variant v001 --to-variant v002
```

This converts the v001 diagnosis into a cuttable v002 script strategy and shot-match rules. It does not run shot matching, does not render, and does not create MP4 files.

Inputs:

- `../products/dog_stairs_v1/outputs/creative_strategy/v002/asset_capability_diagnosis.json`
- `../products/dog_stairs_v1/outputs/creative_strategy/v002/creative_diagnosis_inputs.json`
- `../products/dog_stairs_v1/outputs/renders/batch_20260615_001/v001/review_pack/human_review_scores_v001.json`

Outputs:

- `../products/dog_stairs_v1/outputs/creative_strategy/v002/cuttable_script_strategy_v002.json`
- `../products/dog_stairs_v1/outputs/creative_strategy/v002/cuttable_script_strategy_v002.md`
- `../products/dog_stairs_v1/outputs/creative_strategy/v002/shot_match_rules_v002.json`
- `../products/dog_stairs_v1/outputs/creative_strategy/v002/creative_strategy_report.md`

Strategy rules:

- Weak hook shifts the first 3 seconds toward `dog_hesitates_jump`, `dog_climbs_steps`, and close-up action.
- Crop remains `center_crop` when the diagnosis says crop is acceptable.
- Repetition risk limits per-script clip reuse and avoids high-reuse clips.
- Low proof pool allows proof reuse while listing next shooting priorities.

## Context Assets

Long-term project and product context now lives outside transient task reports.

- Global entrypoint: `../context_assets/SKILL.md`
- dog_stairs_v1 product entrypoint: `../products/dog_stairs_v1/strategy/SKILL.md`

For complex project or product tasks, read these context files before inferring business strategy from short prompts.

## Actual Render V002

Run:

```bash
python main.py actual-render-v002 --product dog_stairs_v1 --sku khaki --material-batch batch_20260615_001 --variant v002
```

This renders the first script_id from the v002 render preflight plan into a muted 1080x1920 MP4. It reads `render_plan_v002.csv`, writes an SRT first, and does not burn subtitles or synthesize TTS.

Outputs:

- `../products/dog_stairs_v1/outputs/renders/batch_20260615_001/v002/dog_stairs_v1_khaki_batch_20260615_001_v002.mp4`
- `../products/dog_stairs_v1/outputs/renders/batch_20260615_001/v002/dog_stairs_v1_khaki_batch_20260615_001_v002.srt`
- `../products/dog_stairs_v1/outputs/renders/batch_20260615_001/v002/actual_render_report_v002.md`
- `../products/dog_stairs_v1/outputs/renders/batch_20260615_001/v002/actual_render_summary_v002.json`
- `../products/dog_stairs_v1/outputs/renders/batch_20260615_001/v002/ffmpeg_command_v002.txt`

## Render Review Pack V002

Run:

```bash
python main.py render-review-pack-v002 --product dog_stairs_v1 --sku khaki --material-batch batch_20260615_001 --variant v002
```

This creates a review pack from the existing v002 MP4. It extracts frames, builds a review contact sheet, counts SRT subtitles, and creates a v002 human score template. It does not re-render and does not create a new MP4.

Outputs:

- `../products/dog_stairs_v1/outputs/renders/batch_20260615_001/v002/review_pack/review_frames/`
- `../products/dog_stairs_v1/outputs/renders/batch_20260615_001/v002/review_pack/review_contact_sheet.jpg`
- `../products/dog_stairs_v1/outputs/renders/batch_20260615_001/v002/review_pack/render_review_checklist_v002.md`
- `../products/dog_stairs_v1/outputs/renders/batch_20260615_001/v002/review_pack/render_review_summary_v002.json`
- `../products/dog_stairs_v1/outputs/renders/batch_20260615_001/v002/review_pack/human_review_scores_v002.json`

## Batch Render Scripts

Run:

```bash
python main.py batch-render-scripts --product dog_stairs_v1 --sku khaki --material-batch batch_20260615_001 --iteration iter002 --scripts V1,V2,V3,V4,V5
```

This renders multiple `script_id` candidates from the v002 render plan. `V1` through `V5` are script IDs, not iteration versions. Outputs are named as `script_V1_iter002` to avoid confusion with v001/v002 strategy versions.

Outputs:

- `../products/dog_stairs_v1/outputs/renders/batch_20260615_001/iter002/script_VX/dog_stairs_v1_khaki_batch_20260615_001_script_VX_iter002.mp4`
- `../products/dog_stairs_v1/outputs/renders/batch_20260615_001/iter002/script_VX/dog_stairs_v1_khaki_batch_20260615_001_script_VX_iter002.srt`
- `../products/dog_stairs_v1/outputs/renders/batch_20260615_001/iter002/script_VX/review_pack/`
- `../products/dog_stairs_v1/outputs/renders/batch_20260615_001/iter002/batch_render_summary_iter002.json`
- `../products/dog_stairs_v1/outputs/renders/batch_20260615_001/iter002/batch_render_report_iter002.md`

## OpenAI TTS POC

Run:

```bash
python main.py openai-tts-poc --product dog_stairs_v1 --sku khaki --material-batch batch_20260615_001 --iteration iter002 --scripts V1,V3 --voice marin --model gpt-4o-mini-tts --response-format wav --speed 1.08
```

This reads parsed `voiceover_lines.csv`, generates OpenAI TTS WAV files for selected script IDs, checks audio duration against the existing rendered MP4, and muxes the fitted voiceover as AAC. It does not burn subtitles, does not re-edit video, and does not use local TTS or voice cloning.

Safety:

- Requires `OPENAI_API_KEY` in the environment.
- The API key is never written to request JSON, reports, logs, or README.
- If `OPENAI_API_KEY` is missing, the command writes a safe failure summary and does not call OpenAI.

## Edge TTS POC

Run:

```bash
python main.py edge-tts-poc --product dog_stairs_v1 --sku khaki --material-batch batch_20260615_001 --iteration iter002 --scripts V1,V3 --voice en-US-JennyNeural --rate +8%
```

This reads parsed `voiceover_lines.csv`, generates edge-tts MP3 voiceovers, fits the audio duration without truncating speech, and muxes the fitted WAV as the only AAC audio track. It does not call OpenAI, does not burn subtitles, and does not re-edit video.

Outputs:

- `../products/dog_stairs_v1/outputs/renders/batch_20260615_001/iter002_tts_edge/script_VX/voiceover_raw_script_VX_iter002.mp3`
- `../products/dog_stairs_v1/outputs/renders/batch_20260615_001/iter002_tts_edge/script_VX/voiceover_fitted_script_VX_iter002.wav`
- `../products/dog_stairs_v1/outputs/renders/batch_20260615_001/iter002_tts_edge/script_VX/dog_stairs_v1_khaki_batch_20260615_001_script_VX_iter002_with_edge_tts.mp4`
- `../products/dog_stairs_v1/outputs/renders/batch_20260615_001/iter002_tts_edge/tts_batch_summary_edge_iter002.json`

## Edge TTS Segment Align

Run:

```bash
python main.py edge-tts-segment-align --product dog_stairs_v1 --sku khaki --material-batch batch_20260615_001 --iteration iter002 --scripts V1,V3 --voice en-US-JennyNeural --rate +8%
```

This generates one edge-tts clip per timeline segment, fits each segment to its own timing window, concatenates the fitted WAV segments, and muxes that full aligned voiceover onto the existing iter002 MP4. It does not re-edit video, does not burn subtitles, and does not call OpenAI.

## Edge TTS Three-Block Fast Mode

Run:

```bash
python main.py edge-tts-three-block --product dog_stairs_v1 --sku khaki --material-batch batch_20260615_001 --iteration iter002 --scripts V1,V3 --voice en-US-JennyNeural --rate +8% --fast
```

This creates a natural three-block voiceover track for each selected script: hook, demo/proof, and CTA/memory. It does not create seven segment-level clips, does not burn subtitles, does not re-edit the video, and extracts the first frame for manual visual inspection.

## Publish Candidate Pack

Run:

```bash
python main.py prepare-publish-pack --product dog_stairs_v1 --sku khaki --material-batch batch_20260615_001 --iteration iter002 --tts-mode edge_tts_three_block --scripts V1,V3
```

This copies approved three-block TTS videos and their review artifacts into a manual upload candidate pack. It verifies duration, resolution, audio stream presence, and first-frame artifacts. It does not regenerate TTS, does not mux, does not burn subtitles, and does not publish.

## Material Diversity And A/B Hook Audit

Run:

```bash
python main.py audit-material-diversity --product dog_stairs_v1 --sku khaki --material-batch batch_20260615_001 --iteration iter002 --include-publish-metrics
```

This audits clip diversity, first-3-second hook capacity, duplicate risk, and creates an Owner-reviewed A/B hook matrix. It does not render MP4, does not generate TTS, does not mux, and does not modify `shot_matcher` or `actual_render`.

## Variant Planner Hook Conflict Fuse

Run:

```bash
python main.py plan-variants --product dog_stairs_v1 --sku khaki --material-batch batch_20260615_001 --iteration iter002 --audit-id P10A_material_diversity_ab_plan --approve-variants Variant_A_Pain_Point,Variant_B_Home_Aesthetic,Variant_C_Two_In_One_Reversal --no-render
```

This creates P10B variant plans, hook-zone conflict checks, difference scores, quality gates, and a P10C render input manifest. It does not render MP4, does not generate TTS, does not burn subtitles, and does not modify `shot_matcher` or `actual_render`.

## Hook Window Visual Review Pack

Run:

```bash
python main.py build-hook-review-pack --product dog_stairs_v1 --sku khaki --material-batch batch_20260615_001 --plan-id P10B_approved_abc_hook_conflict_fuse --variants Variant_A_Pain_Point,Variant_B_Home_Aesthetic,Variant_C_Two_In_One_Reversal
```

This exports first/mid/last hook frames, a hook contact sheet, and a low-bitrate hook-window preview for Owner review. It does not render a full MP4, does not generate TTS, does not mux, does not burn subtitles, and does not apply crop/hflip/speed/freeze perturbations.

## Render Approved P10C Variants

Run:

```bash
python main.py render-approved-variants --product dog_stairs_v1 --sku khaki --material-batch batch_20260615_001 --plan-id P10B_approved_abc_hook_conflict_fuse --review-id P10B2_hook_window_visual_review_abc --variants Variant_B_Home_Aesthetic,Variant_C_Two_In_One_Reversal --no-tts --no-subtitles
```

This renders only Owner-approved P10C variants from the P10B manifest. It skips Variant_A, generates muted 1080x1920 MP4s, review contact sheets, and manual publish-test notes. It does not generate TTS, does not burn subtitles, and does not modify `shot_matcher` or `actual_render`.
### P10D approved variant voiceover

Add three-block edge-tts voiceover to approved P10C visual variants without re-editing video or burning subtitles:

```bash
python main.py add-variant-voiceover --product dog_stairs_v1 --sku khaki --material-batch batch_20260615_001 --render-id P10C_approved_variants_bc --variants Variant_B_Home_Aesthetic,Variant_C_Two_In_One_Reversal --tts-mode edge_tts_three_block --voice en-US-JennyNeural --rate +8%
```

Outputs are written under `products/dog_stairs_v1/outputs/renders/batch_20260615_001/P10D_bc_three_block_voiceover/`.

Generate a +10% rate comparison version without overwriting the +8% P10D output:

```bash
python main.py add-variant-voiceover --product dog_stairs_v1 --sku khaki --material-batch batch_20260615_001 --render-id P10C_approved_variants_bc --variants Variant_B_Home_Aesthetic,Variant_C_Two_In_One_Reversal --tts-mode edge_tts_three_block --voice en-US-JennyNeural --rate +10% --output-id P10D2_bc_three_block_voiceover_rate10
```

Prepare the final P10E publish candidate pack after Owner selects B +10% and C +8%:

```bash
python main.py prepare-final-publish-candidates --product dog_stairs_v1 --sku khaki --material-batch batch_20260615_001 --candidate-id P10E_final_bc_publish_candidates --variant-b-source P10D2_bc_three_block_voiceover_rate10 --variant-c-source P10D_bc_three_block_voiceover
```

### P11A batch-2 material intake

Create a new material batch intake workspace, contact sheets, tag review folders, and a lightweight capability audit without rendering or TTS:

```bash
python main.py intake-material-batch --product dog_stairs_v1 --sku khaki --material-batch batch_20260617_001
```

Place Batch 2 raw videos under `products/dog_stairs_v1/inputs/raw_videos/batch_20260617_001/` before running the command.

### P11A2 tag review workspace

Prepare the manual contact-sheet sorting workspace:

```bash
python main.py prepare-tag-review-workspace --product dog_stairs_v1 --sku khaki --material-batch batch_20260617_001
```

After the Owner copies contact sheets into tag folders, collect folder-as-tag results:

```bash
python main.py collect-folder-tags --product dog_stairs_v1 --sku khaki --material-batch batch_20260617_001
```

### P11B batch-2 level-1 matrix plan

Generate six Level 1 variant plans and hook-window preview assets for Owner review without rendering full videos or generating TTS:

```bash
python main.py plan-batch-variant-matrix --product dog_stairs_v1 --sku khaki --material-batch batch_20260617_001 --matrix-size 6 --plan-id P11B_level1_matrix_plan_hook_preview
```

This reads Batch 2 `clip_manifest.csv`, `clip_tags.csv`, and `tag_review_summary.json`, then writes a matrix plan, diversity reports, hook previews, and a P11C render input manifest. It does not render complete MP4s, does not generate TTS, does not burn subtitles, and does not modify `shot_matcher` or `actual_render`.

### P11B2 hook preview repair

Repair black or incompatible P11B hook preview files by regenerating hook-only previews as H.264/yuv420p MP4s:

```bash
python main.py repair-hook-preview-pack --product dog_stairs_v1 --sku khaki --material-batch batch_20260617_001 --plan-id P11B_level1_matrix_plan_hook_preview --repair-id P11B2_repaired_hook_preview_pack
```

This only repairs hook-window review assets. It does not render full videos, generate TTS, burn subtitles, or modify `shot_matcher` / `actual_render`.

Visual preview/review generation must follow [STRICT_VISUAL_FIDELITY_POLICY.md](docs/STRICT_VISUAL_FIDELITY_POLICY.md).

Regenerate hook previews with strict visual fidelity rules after any visual quality incident:

```bash
python main.py repair-hook-preview-visual-fidelity --product dog_stairs_v1 --sku khaki --material-batch batch_20260617_001 --plan-id P11B_level1_matrix_plan_hook_preview --repair-id P11B3_visual_fidelity_fixed_hook_preview_pack
```

This command avoids scale, enhancement, sharpening, color correction, subtitles, and full rendering. It writes `visual_fidelity_audit.json` for each preview.

Audit HDR / 10-bit color metadata and build two Owner-review preview modes:

```bash
python main.py audit-color-fidelity-and-build-safe-previews --product dog_stairs_v1 --sku khaki --material-batch batch_20260617_001 --plan-id P11B_level1_matrix_plan_hook_preview --audit-id P11B4_color_fidelity_audit_safe_preview
```

This creates `source_like_preview.mp4` and `controlled_sdr_preview.mp4` for each variant, plus color metadata diffs and before/after comparison frames. Owner must choose source-like, controlled SDR, hold, or reject before P11C.

Lock the Owner-approved color pipeline after P11B4 review:

```bash
python main.py lock-owner-color-decision --product dog_stairs_v1 --sku khaki --material-batch batch_20260617_001 --audit-id P11B4_color_fidelity_audit_safe_preview --selected-pipeline controlled_sdr
```

This writes `owner_color_decision.json` and `color_pipeline_lock.json`. P11C must use `controlled_sdr` and must not fall back to `source_like`, P11B2/P11B3 previews, or raw `yuv420p` conversion.

Replan rejected or held hooks after Owner controlled-SDR review without rendering full videos:

```bash
python main.py replan-hooks-after-owner-review --product dog_stairs_v1 --sku khaki --material-batch batch_20260617_001 --plan-id P11B_level1_matrix_plan_hook_preview --color-audit-id P11B4_color_fidelity_audit_safe_preview --replan-id P11B6_hook_replacement_variant_replan
```

This keeps V02/V03 locked approved, creates replacement candidates for V01/V04/V05/V06, and exports controlled-SDR hook previews only. It does not enter P11C, render complete videos, generate TTS, or burn subtitles.

Lock final Owner replacement decisions and write the only allowed P11C controlled-SDR input manifest:

```bash
python main.py lock-owner-replacement-decisions --product dog_stairs_v1 --sku khaki --material-batch batch_20260617_001 --replan-id P11B6_hook_replacement_variant_replan --color-audit-id P11B4_color_fidelity_audit_safe_preview --decision-id P11B7_owner_replacement_decision_lock
```

This writes `p11c_render_manifest_controlled_sdr.json` with the five Owner-approved variants and stores rejected hooks in `negative_hook_examples.json`. It does not render complete videos or enter P11C.

Low-friction production rules are documented in [LOW_FRICTION_PRODUCTION_PIPELINE_POLICY.md](docs/LOW_FRICTION_PRODUCTION_PIPELINE_POLICY.md).

Render the five P11C Batch 2 visual masters with the locked controlled-SDR pipeline:

```bash
python main.py render-approved-visual-masters --product dog_stairs_v1 --sku khaki --material-batch batch_20260617_001 --decision-id P11B7_owner_replacement_decision_lock --color-audit-id P11B4_color_fidelity_audit_safe_preview --render-id P11C_visual_masters_controlled_sdr
```

This renders visual masters and Owner review packs only. It does not generate TTS, voiceover, subtitles, publish candidates, titles, captions, or enter P11D.

Produce P11D three-block voiced review videos from Owner-approved P11C visual masters:

```bash
python main.py produce-voiceover-review-pack --product dog_stairs_v1 --sku khaki --material-batch batch_20260617_001 --visual-render-id P11C_visual_masters_controlled_sdr --voiceover-id P11D_three_block_voiceover_review_pack
```

This generates sidecar scripts, edge-tts audio, and voiced review MP4s using `-c:v copy`. It does not burn subtitles, alter the controlled-SDR visual masters, generate publish candidates, or enter P11E.

Build P11E publish candidates from Owner-approved voiced review videos:

```bash
python main.py build-publish-candidates --product dog_stairs_v1 --sku khaki --material-batch batch_20260617_001 --voiceover-id P11D_three_block_voiceover_review_pack --publish-id P11E_batch2_publish_candidates
```

This copies P11D `voiced_review.mp4` files to `final_candidate.mp4` without re-rendering, re-encoding, changing audio, burning subtitles, generating new TTS, or publishing automatically. The pack is marked as `hook_ab_test` and records `high_body_overlap_after_3s` as a known Batch2 limitation.

## P12 Refactor Audit And Laptop Handoff

P12A reverse-audit and migration docs live under:

```text
docs/p12_refactor_audit/
docs/P11_FINAL_STATUS_AND_LIMITATIONS.md
docs/LAPTOP_SETUP_GUIDE.md
docs/DESKTOP_TO_LAPTOP_HANDOFF_CHECKLIST.md
```

Laptop bootstrap scripts:

```text
scripts/setup_windows_laptop.ps1
scripts/verify_laptop_env.ps1
scripts/smoke_test_laptop.ps1
```

P12A does not implement the runtime agent. It documents hard rules, general rules, redundant-rule candidates, VLM QC boundaries, `agent_state`, Owner Firewall, Git hygiene, and laptop setup.

## P12B Agent Factory Runtime Harness

P12B adds a dry-run Runtime Agent skeleton, Owner Firewall skeleton, VLM QC sidecar skeleton, Git Safety Guard, and Media Asset Guard.

Preflight:

```bash
python main.py agent-preflight --product dog_stairs_v1 --sku khaki --material-batch batch_20260617_001 --variants 12
```

Dry-run state machine:

```bash
python main.py agent-produce-review-pack-dry-run --product dog_stairs_v1 --sku khaki --material-batch batch_20260617_001 --variants 12
```

Owner Firewall dry-run:

```bash
python main.py owner-firewall --product dog_stairs_v1 --sku khaki --material-batch batch_20260617_001 --decision-file owner_firewall_decisions.template.json --dry-run
```

P12B writes reports under `../products/<product>/outputs/agent_factory/<material_batch>/`. It does not render MP4 files, call Gemini, generate TTS, delete raw videos, modify timelines, publish, or add media to Git.

## P12C Autonomous Codex Operator

The root `../AGENTS.md` is the durable project contract for Codex takeover. It defines Codex autonomous authority, mandatory Owner gates, Owner Review Packet format, GPT consultation boundaries, execution loop, session resume behavior, and single-writer data isolation.

Operator status:

```bash
python main.py project-operator-status --product dog_stairs_v1 --sku khaki --material-batch batch_20260617_001
```

Owner review packet:

```bash
python main.py owner-review-packet --product dog_stairs_v1 --sku khaki --material-batch batch_20260617_001
```

Apply an explicit Owner decision:

```bash
python main.py owner-decision-apply --product dog_stairs_v1 --sku khaki --material-batch batch_20260617_001 --decision-file owner_decision.json
```

Resume helper:

```bash
python main.py project-resume --product dog_stairs_v1 --sku khaki --material-batch batch_20260617_001
```

P12C does not enable real VLM, generate videos, run real Batch2 production, publish, or relax any media and Git guards.

## TikTok 9:16 Hard Output Guard

All TikTok outputs must pass the true 9:16 hard guard before review, release, or publish readiness. The guard checks the final container and every timeline segment; a final 1080x1920 container is not enough if a segment is horizontally inset, letterboxed, pillarboxed, stretched, or semantically unsafe.

Audit a video or JSON manifest without modifying media:

```bash
python main.py vertical-output-audit --product dog_stairs_v1 --sku khaki --material-batch batch_20260617_001 --input path/to/video_or_manifest.json
```

The report includes failed segment IDs, failed time ranges, black bar failures, stretch failures, frame fill failures, semantic crop pending, replacement requirement, and publish/release readiness.

## P12D Asset-Ready Preflight

Run the Batch2 asset-ready preflight and stop at the Owner choice menu:

```bash
python main.py p12d-preflight --product dog_stairs_v1 --sku khaki --material-batch batch_20260617_001
```

This command checks Git safety, counts raw videos, writes a read-only media inventory, runs laptop-safe resource preflight, runs a two-asset QC draft benchmark, runs the 9:16 known-failure regression, builds a deterministic candidate pool, and writes a 12-variant real batch plan. It does not render final videos, call real VLM, upload media, publish, or modify raw videos.

## P12E Three-Stage Semantic Compiler

P12E freezes the P12D free Timeline Planner for real runs and treats the three P12D validation videos as negative business-regression samples. The new path is visual-first: deterministic candidate windows, optional VLM semantic labels after Owner approval, a strict Hook/Core/Closure story compiler, and en-US Edge-TTS only.

Preflight and real VLM gate:

```bash
python main.py p12e-preflight --product dog_stairs_v1 --sku khaki --material-batch batch_20260617_001
```

This command writes only ignored reports and state under `products/<product>/outputs/agent_factory/<material_batch>/`. It does not call real VLM, upload keyframes or video proxies, generate new videos, continue the remaining P12D videos, publish, modify raw videos, or use Windows SAPI fallback.
