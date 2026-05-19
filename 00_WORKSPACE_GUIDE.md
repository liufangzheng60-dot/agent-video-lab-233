# agent-video-lab 工作区指南

## 工作区目标

本工作区用于学习 Agent、Skills、Vibe Coding，并围绕 TikTok 商品视频 AI 自动化剪辑 MVP 建立可执行的工程闭环：

1. AI 生成视频素材
2. Agent 盘点素材
3. 输出剪辑策略
4. 生成自定义 JSON 时间轴
5. 输出 CapCut 人工复刻用 CSV
6. 自动合成 final.mp4
7. 人工审片
8. TikTok 发布与数据反馈复盘

当前阶段只建立基础架构，不实现具体业务功能。

## 目录用途与 Agent 权限

### 00_references/

用途：存放外部参考仓库和学习材料。

允许放：克隆的参考项目、只读资料、架构参考。

不允许放：本项目业务代码、输出视频、临时生成文件。

Agent 权限：只读参考区，不允许 Agent 修改其中源码。若需要更新参考仓库，必须先获得明确批准。

计划参考仓库：

- `https://github.com/2025Emma/vibe-coding-cn`
- `https://github.com/browser-use/video-use`

本次 clone 结果：

- `vibe-coding-cn`：失败。沙箱内连接 GitHub 失败；授权后 `git` 返回 `could not create work tree dir '00_references\vibe-coding-cn': Permission denied`。
- `video-use`：失败。沙箱内连接 GitHub 失败；授权后 `git` 返回 `could not create work tree dir '00_references\video-use': Permission denied`。

后续重试命令：

```powershell
git clone https://github.com/2025Emma/vibe-coding-cn 00_references\vibe-coding-cn
git clone https://github.com/browser-use/video-use 00_references\video-use
```

### 01_project_brief/

用途：存放项目目标、MVP 范围、非目标、技术栈和周计划。

允许放：稳定的项目说明、阶段边界、路线图。

不允许放：临时笔记、素材文件、脚本输出。

Agent 权限：需要批准后才可修改。

### 02_learning_notes/

用途：记录 Agent、Skills、Vibe Coding、video-use 架构学习笔记，以及错误复盘。

允许放：学习记录、实验观察、失败原因、解决方案。

不允许放：大体积视频素材、最终产物。

Agent 权限：允许追加记录，避免无批准重写历史内容。

### 03_tk_video_agent/

用途：TikTok 商品视频剪辑 Agent 主开发区。

允许放：Python 代码、配置、Prompt、Skill、测试、任务文档、输入输出中间产物。

不允许放：与 MVP 无关的前端 UI、Web 服务、数据库项目、自动发布 TikTok 代码。

Agent 权限：允许在任务批准后修改。

### 04_test_cases/

用途：产品测试案例区，用于保存商品素材、产品 brief、预期输出和人工审片结果。

允许放：每个商品的测试素材、`product_brief.md`、`expected_output.md`、`result_review.md`。

不允许放：未归类的大量散乱素材、最终发布资产。

Agent 权限：允许在任务批准后新增，不允许随意删除。

### 05_final_outputs/

用途：最终视频、CapCut 时间轴、发布记录和数据反馈。

允许放：`final.mp4`、最终时间轴、发布记录、效果复盘。

不允许放：开发中间文件、参考源码、未审核素材。

Agent 权限：仅在渲染或复盘任务中写入。

## 当前 MVP 开发规则

第一阶段只做最小闭环，不做复杂平台化。

默认技术栈：

- Python 3.10+
- ffmpeg / ffprobe
- Markdown
- YAML
- JSON
- CSV
- pytest
- VS Code
- Codex
- Git

暂时不引入：

- 前端 UI
- Web 服务
- 数据库
- TikTok 自动发布
- 复杂 SaaS 架构

时间轴第一阶段采用自定义中间格式：

- `03_tk_video_agent/outputs/timelines/timeline.json`：程序内部使用的剪辑时间轴。
- `03_tk_video_agent/outputs/timelines/capcut_timeline.csv`：人工在 CapCut 中复刻剪辑的表格。

## 禁止事项

- 不擅自修改 `00_references/` 中克隆下来的源码。
- 不调用外部 API，除非任务明确批准。
- 不安装依赖，除非任务明确批准。
- 不运行视频处理，除非任务明确批准。
- 不生成 `final.mp4`，除非进入明确的渲染任务。
- 不创建 UI。
- 不自动发布 TikTok。
- 不擅自扩大项目范围。

## 建议工作流

1. 先在 `04_test_cases/` 选择一个商品案例。
2. 把素材放入该案例的 `source_materials/`。
3. 把商品信息写入 `product_brief.md`。
4. 在 `03_tk_video_agent/tasks/` 新建或更新任务。
5. Agent 在批准后生成素材盘点、剪辑策略和时间轴。
6. 人工审片后记录到 `result_review.md`。
7. 最终结果进入 `05_final_outputs/`。

## 2026-05-19 审计记录

`P0_000_workspace_audit_and_git_baseline` 已完成：目录结构、核心文档和 `.gitignore` 已审计，Git 仓库已初始化，并已创建首次基建 commit。

本次再次重试两个参考仓库 clone，结果仍失败：

- `vibe-coding-cn`：沙箱内无法连接 GitHub；授权后无法创建目标 work tree，返回 `Permission denied`。
- `video-use`：沙箱内无法连接 GitHub；授权后无法创建目标 work tree，返回 `Permission denied`。

后续可在本机终端重试：

```powershell
git clone https://github.com/2025Emma/vibe-coding-cn 00_references\vibe-coding-cn
git clone https://github.com/browser-use/video-use 00_references\video-use
```
