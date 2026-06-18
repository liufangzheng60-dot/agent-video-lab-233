# Runtime Friction Report

当前系统最大问题不是视频不够精修，而是 Runtime 需要 Owner 不断粘贴 Prompt、人工判断下一步。这不是全自动 Agent。P12 必须把人工胶水收敛进 Execution Harness 和 agent_state。

| friction_point | current_cost | business_damage | p12_fix |
| --- | --- | --- | --- |
| 人工喂 Prompt | 每阶段都要 Owner 组织上下文 | 产能被人机交互吞掉 | `agent-produce-review-pack` 单命令状态机 |
| 手动跑多条 CLI | P11 被拆成几十个命令 | 容易漏步骤、跑错输入 | Execution Harness 管理 stage transition |
| 人工审 JSON / manifest | Owner 审低价值机器文本 | 增加认知负担 | Owner 只审视频 review pack |
| 人工判断下一步 | 每阶段都依赖 Owner 指令 | Runtime 不连续 | `agent_state.json` + stage policy |
| 多阶段 P11 中间锁 | B4/B6/B7 过长 | 出片速度慢 | 只保留 hard gate + final Owner Firewall |
| 视觉质检没有自动一审 | 人工先看所有问题 | Owner 时间被低质量候选占用 | VLM QC gate |
| 出错后缺少 auto-rerun | 需要人工发新任务 | 修复周期长 | `auto_replace_failed_variants` |
| 同一批视频需要人工复制审查结论 | 决策散落在 Prompt | 审计和复用困难 | Owner decision JSON + audit log |
| P11 产物无法直接进入下一批生产经验 | 学习点分散 | 负样本无法自动降权 | negative memory + rules config |
