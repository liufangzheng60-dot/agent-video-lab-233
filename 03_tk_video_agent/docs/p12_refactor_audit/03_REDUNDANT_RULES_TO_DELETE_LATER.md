# Redundant Rules To Delete Later

冗余规则不是立刻删除的规则。它们让链路变长、Prompt 胶水变多、Owner 心智摩擦变高，但没有明显提升出片吞吐量。本任务只标记，不直接删除。删除必须进入后续 P12B / P12C，由 Owner 审核后执行。

| rule_id | current_location | why_redundant | safe_delete_condition | replacement_path | risk_if_deleted_now |
| --- | --- | --- | --- | --- | --- |
| RR_OWNER_TEXT_PLAN_REVIEW | P10/P11 owner review docs | Owner 审文本 plan 低价值且慢 | P12 review pack 可直接生成 | Owner 只审视频 review pack | 可能失去人工策略纠偏 |
| RR_MULTI_INTERMEDIATE_LOCKS | P11B4/B6/B7 flow | 中间 lock 过多，日常生产摩擦高 | Harness 能自动 preflight 和记录 agent_state | Owner Firewall 最终裁决 | 可能放过未记录决策 |
| RR_REPAIR_STEPS_AS_DAILY_FLOW | P11B2/P11B3/P11B4 | 事故修复步骤不应暴露为日常流程 | controlled_sdr hard rule 稳定 | color_fidelity_guard + one review pack | 可能丢失诊断入口 |
| RR_CODE_ONLY_TIKTOK_FEEL | quality heuristics | 纯代码难判断网感 | VLM + Owner + publish data | VLM QC gate | 可能降低自动初筛 |
| RR_PIXEL_MICROTUNING | visual fidelity repair docs | 过细像素规则拖慢产出 | controlled color pipeline 稳定 | Color metadata hard gate | 可能复发色彩事故 |
| RR_HOOK_ONLY_MATRIX | P11E limitation | 只看前 3 秒造成伪矩阵 | body/proof/CTA diversity metrics 上线 | timeline_structural_diversity_score | 继续输出高度相似视频 |
| RR_DUPLICATE_MANIFEST_REVIEW | many P11 reports | 机器清单不应成为 Owner 审核点 | preflight tests 稳定 | Harness preflight + owner review pack | 可能漏掉 manifest 错误 |
