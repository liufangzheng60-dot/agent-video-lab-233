# Low Friction Production Pipeline Policy

## Owner 不再审核低价值文本计划

- Owner 不审 `variant_matrix_plan.json`。
- Owner 不审 render manifest 的细节行。
- Owner 不审机械 preflight 报告。
- Owner 只审视频 review pack、完整视觉母版、最终发布候选。
- 文本 manifest 是机器读的，不是 Owner 的主要审核对象。

## 机器盲跑，红线失败才中断

- 系统自动执行 manifest preflight。
- 系统自动验证 `color_pipeline_lock`。
- 系统自动验证 Global Conflict Registry。
- 系统自动验证 `negative_hook_examples`。
- 系统自动渲染 approved variants。
- 只有红线失败才中断，不要因为普通 warning 阻塞出片。

## 首尾刚性死锁，中间流程脱水

必须死守：

- `controlled_sdr` 色彩管线。
- 禁止 `source_like`。
- 禁止 P11B2 / P11B3 失真 preview。
- 禁止裸 `yuv420p` 转换。
- Global Conflict Registry 跨视频镜头熔断。
- `negative_hook_examples` 负样本排除。
- 不接 VLM。
- 不提前生成 TTS。
- 不提前烧字幕。
- 不提交 outputs/raw_videos 到 Git。

可以脱水：

- 不再人工审文本 plan。
- 不再让 Owner 判断 manifest 是否合理。
- 不再把每个中间 json 暴露成独立审核点。
- 机器直接生成完整视觉母版 review pack。

## 当前阶段的正确流水线

当前 Batch2 目标：

1. P11B7 锁定 approved variants。
2. P11C 自动渲染完整视觉母版。
3. P11C2 Owner 审完整视频。
4. P11D 只给通过的视频做 three-block voiceover。
5. P11E 生成发布候选包。

## 禁止过早扩系统

当前不做：

- Harness daemon。
- VLM / Video VLM。
- TTS cache provider。
- 自动发布。
- 多维 folder-as-tag 大重构。

这些进入后续 backlog，不阻塞今天出片。

## P11D Low-Friction Voiceover Rule

1. Owner 已经 approve 的视觉母版，不再进行脚本文本逐条人工审核。
2. P11D 直接生成 three-block voiceover、TTS 音频和带声音 review pack。
3. Owner 只审最终带声音 mp4。
4. P11D 不得改变视觉画面，不得重渲染色彩，不得重新裁切视频。
5. 合成音频时优先 copy video stream，保持 controlled_sdr 视觉母版不被二次处理。
6. TTS 脚本文本作为 sidecar 记录，不作为前置人工审核点。
7. 硬规则失败才中断：源视频不存在、duration 异常、audio 超长无法贴合、ffmpeg 合成失败。
8. 普通 warning 不阻断跑量，只写入 risk_flags。

## P11E Low-Friction Publish Candidate Rule

P11E 可直接从 Owner approved voiced videos 复制生成发布候选，不得重新渲染或重新编码；Owner 最后只审发布候选路径、标题、caption 与发布优先级。
