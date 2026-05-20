# P0-001 素材盘点任务

## 目标

建立第一版商品视频素材盘点流程，帮助 Agent 判断已有素材是否足够支撑 TikTok 商品视频剪辑。

## 输入

- 商品 brief
- 产品图片
- 原始视频
- AI 生成片段
- 参考视频

## 输出

- `outputs/material_inventory/material_inventory.md`
- `outputs/material_inventory/material_inventory.json`

## 第一阶段字段建议

- 文件名
- 素材类型
- 时长
- 分辨率
- 是否有声音
- 可用片段描述
- 适合承担的视频角色
- 风险或缺口

## 当前状态

仅定义任务，不实现业务逻辑。

## 实现状态

第一版已实现本地素材盘点命令：

```bash
python main.py inventory
```

实现边界：

- 只扫描 `03_tk_video_agent/inputs/` 下的五个默认素材桶。
- 输出 JSON 和 Markdown 两份报告。
- 使用 Python 标准库。
- `ffprobe` 仅作为可选增强能力。
- 不做 AI 视觉理解、转录、剪辑或渲染。
