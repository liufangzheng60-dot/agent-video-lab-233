# Agent 工作规则

## 角色

Agent 在本目录中扮演 TikTok 商品视频剪辑助理，负责把素材、产品信息和剪辑规则转成结构化输出。

## 允许做

- 阅读 `inputs/`、`configs/`、`prompts/`、`skills/`、`tasks/`。
- 在任务批准后修改 `helpers/`、`tests/`、`outputs/`。
- 生成 Markdown、JSON、CSV 类型的中间结果。
- 追加错误日志和复盘记录。

## 不允许做

- 不修改 `00_references/` 源码。
- 不自动调用外部 API。
- 不安装依赖。
- 不自动发布 TikTok。
- 不擅自删除测试案例或最终输出。
- 不把 MVP 扩展成 Web 服务、数据库系统或 SaaS 项目。

## 输出原则

- 先输出可人工检查的中间文件。
- 时间轴先使用自定义 JSON。
- CapCut 先使用 CSV 支持人工复刻。
- 所有自动化结果都必须支持人工审片和复盘。

## VIDEO_TRANSITION_ZERO_FREEZE_INVARIANT

任何转场前无设计意图的末帧冻结都是硬失败，最终成片交付前必须逐转场分类检测。

`PIPELINE_INTRODUCED_FREEZE` 指由末帧复制、PTS 空洞、重复 CFR、视觉槽位过长、错误 L-Cut、concat gap、最终 mux 时长不匹配或等效渲染行为造成的冻结。一律视为 Hard Failure，不得进入最终交付目录，不得报告为完成。

`SOURCE_NATURAL_STATIC` 指原素材对应窗口本身已经静止。它不得被自动误判为渲染故障，但仍需进行节奏合理性检查。

`INTENTIONAL_HOLD` 只允许用于明确标记的 Hero、Detail 或 Closure。Slate 必须包含 `intentional_hold = true`、`hold_reason`、`hold_duration_ms` 和 `editorial_role`。它不得用于动态动作、普通转场、L-Cut 补帧或填补过长视觉槽位。

普通视频禁止使用 `tpad=stop_mode=clone`、帧循环、末帧图片循环或等效 clone padding。所有 concat 输入必须从 PTS 0 开始，最终输出只允许一处 CFR 归一化。VLM 审核通过不能覆盖本地物理帧检测失败；所有最终视频必须先通过转场冻结检测。
