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
