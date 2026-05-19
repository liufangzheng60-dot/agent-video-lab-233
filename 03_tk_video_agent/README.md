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
