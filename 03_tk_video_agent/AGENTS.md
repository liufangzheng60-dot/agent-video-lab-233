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
