# 错误日志

## 2026-05-18 工作区初始化

### 事件

创建 `agent-video-lab` 基础架构，并尝试克隆两个参考仓库。

### git clone 结果

`vibe-coding-cn` 克隆失败：

- 沙箱内执行：`Failed to connect to github.com port 443`
- 授权后执行：`could not create work tree dir '00_references\vibe-coding-cn': Permission denied`

`video-use` 克隆失败：

- 沙箱内执行：`Failed to connect to github.com port 443`
- 授权后执行：`could not create work tree dir '00_references\video-use': Permission denied`

### 后续重试命令

```powershell
git clone https://github.com/2025Emma/vibe-coding-cn 00_references\vibe-coding-cn
git clone https://github.com/browser-use/video-use 00_references\video-use
```

### 处理结果

保留 `00_references/` 目录，继续完成本地目录和文档创建。

## 2026-05-19 P0_000 工作区审计与 Git 基线

### 审计结果

- 规划目录已存在。
- 核心文档已存在。
- `.gitignore` 已补齐，用于忽略虚拟环境、缓存、大体积媒体、生成输出和 `00_references/` 下的外部参考仓库内容。
- 已为需要保留的空目录添加 `.gitkeep`。
- 已初始化 Git 仓库。
- 已创建首次基建 commit。

### git clone 重试结果

`vibe-coding-cn` 克隆失败：

- 沙箱内执行：`Failed to connect to github.com port 443`
- 授权后执行：`could not create work tree dir '00_references\vibe-coding-cn': Permission denied`

`video-use` 克隆失败：

- 沙箱内执行：`Failed to connect to github.com port 443`
- 授权后执行：`could not create work tree dir '00_references\video-use': Permission denied`

### 后续重试命令

```powershell
git clone https://github.com/2025Emma/vibe-coding-cn 00_references\vibe-coding-cn
git clone https://github.com/browser-use/video-use 00_references\video-use
```

## P12W input lessons

- P12U motion-aware scoring over-weighted motion continuity; P12W caps Motion Match at 3% default and 5% maximum.
- P12U ran without cv2; P12W requires opencv-python-headless and records opencv_backend_used=true.
- P12U V1B/V2B style temporal artifacts require OpenCV ABAB, duplicate, direction-reversal and speed-artifact checks before any replacement.
