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

```bash
python main.py inventory --product pet_nail_trimmer
python main.py material-pack --product pet_nail_trimmer
python main.py edit-strategy --product pet_nail_trimmer
python main.py timeline --product pet_nail_trimmer
python main.py render --product pet_nail_trimmer
python main.py subtitles --product pet_nail_trimmer
python main.py batch-variants --product pet_nail_trimmer
```

Current commands remain compatible without `--product`. No existing files were moved.

Future matrix direction: multiple source materials -> keyframe extraction -> clip library -> multiple Hook timelines -> batch rendering -> performance feedback selects winner. The goal is compliant, differentiated, non-duplicate TikTok Shop product video variants, not algorithm evasion.
