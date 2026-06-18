# Hook Selection And Variant Replan Policy

## Hook 首帧红线

1. 不允许 Hook 首帧出现人手，除非该 variant 明确是 human_interaction_proof 且 Owner 已批准。
2. 不允许 Hook 首帧画面杂乱。
3. 不允许 Hook 首帧主体不清。
4. 不允许 Hook 首帧信息不成立。
5. 不允许为了凑策略而选择弱 Hook。
6. Hook Preview 的首 1 秒必须有明确停留理由。

## 替代帧优先规则

1. 如果某策略方向成立，但首帧失败，不应直接废弃策略。
2. 应优先在同 strategy_tag 或 secondary_strategy_tag 的素材池中重新选 Hook。
3. product_dynamic_showcase 应优先选择产品开合、折叠变化、阶梯/软墩转换、清楚展示产品运动或结构变化的镜头。
4. dog_action / real_usage_demo 应优先选择狗正在接近、踩踏、上阶梯、狗爪与踏面交互，且画面主体清楚、无杂乱干扰。
5. proof_closeup 应避免与 dog_action 的视觉意图重复。
6. 不同 clip_id 不等于不同内容，必须做 Hook visual intent 去重。

## 策略标签重构规则

1. 狭义 pain_point 不适合作为 Batch 2 的主策略标签。
2. pain_point 应改为更兼容批量化生产的广义策略：usage_friction、small_dog_access_problem、real_usage_tension、hesitation_before_climb、owner_assist_need。
3. 不要把“狗咬爬梯”当成默认痛点。
4. 批量化视频矩阵需要兼容性优先，不要把策略范围收得过窄。

## 语义去重规则

1. hook_clip_overlap_rate=0 不代表商业差异化成立。
2. 必须增加 hook_visual_intent 去重。
3. Variant_06 不得与 Variant_03 重复使用“狗刨爬梯 / 爪子刨踏面”作为核心视觉钩子。
4. 如果两个 variants 的首 1 秒视觉意图相同，应标记 semantic_duplicate=true。
5. semantic_duplicate=true 的候选不得进入 P11C candidate manifest。

## 色彩管线约束

1. P11B6 replacement preview 必须读取 `color_pipeline_lock.json`。
2. 当前 Batch 2 唯一合法预览管线是 `controlled_sdr`。
3. 禁止使用 source_like、P11B2、P11B3 或裸 yuv420p 作为 replacement preview。
4. P11C 前必须再次确认 controlled_sdr lock。

## Owner Feedback Negative Hook Memory

1. 人工 reject / hold 的原因必须沉淀为 `negative_hook_examples.json`。
2. 任何 replacement candidate 即使规则化 QA pass，也必须经过 Owner 视觉审核。
3. 人手、杂乱、语义重复、策略过窄，是 Batch2 暴露出的四类主要 Hook 风险。
4. 后续 Hook planner 必须读取 `negative_hook_examples.json` 作为降权或排除依据。
5. P11C 只能使用 Owner final approved variants，不能重新启用已记录的 negative hook。
