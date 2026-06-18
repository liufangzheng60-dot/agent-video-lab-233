# General Rules To Optimize

一般规则不是安全底线，而是产能和质量调优策略。一般规则可以被数据、Owner 反馈、VLM 评分和后续批次表现优化。P12 需要让一般规则可配置、可降权、可替换，而不是堆更多 if/else。

| rule_id | current_location | why_not_hard_rule | optimization_direction | can_vlm_assist | owner_override_needed |
| --- | --- | --- | --- | --- | --- |
| GR_STRATEGY_SCORING | `ab_strategy_planner.py`, `batch_variant_matrix_planner.py` | 策略优先级随素材和数据变化 | 配置化权重，接入数据回填 | true | false |
| GR_HOOK_SELECTION | `hook_quality_guard.py`, matrix planner | Hook 强弱需要视觉语义判断 | VLM 一审 + negative memory 降权 | true | true for borderline |
| GR_BODY_PROOF_CTA_SELECTION | matrix/render planners | 不同批次素材结构不同 | 增加 body/proof/CTA diversity score | true | false |
| GR_BODY_OVERLAP_TOLERANCE | P11E backlog | 容忍度取决于出片量目标 | 配置 batch 级 overlap threshold | true | false |
| GR_VOICEOVER_RATE_STRATEGY | P10/P11D docs | +8/+10 是经验，不是底线 | 按画面动态强度和听感数据调整 | true | true for publish candidate |
| GR_TITLE_CAPTION | `publish_metadata_builder.py` | 标题/caption 需要迭代测试 | 按策略和表现生成多版本 | true | true before publish |
| GR_PUBLISH_PRIORITY | `publish_metadata_builder.py` | 优先级是商业假设 | 按策略学习和素材质量动态排序 | true | true |
| GR_VLM_THRESHOLD | future VLM QC | 阈值需要按误杀率调整 | 使用 approve/hold/reject 三态，不硬二分 | false | true for hold |
