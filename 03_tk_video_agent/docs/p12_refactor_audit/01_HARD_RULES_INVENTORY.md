# Hard Rules Inventory

硬规则是任何模型、任何 Runtime Agent、任何自动化脚本都不能绕过的底线。硬规则失败时，Pipeline 必须中断或进入 Owner hold。硬规则不能被 VLM 或 LLM 覆盖，也不能为了出片速度临时关闭。

| rule_id | current_location | why_keep | failure_if_removed | test_coverage | recommended_owner_level |
| --- | --- | --- | --- | --- | --- |
| HR_COLOR_CONTROLLED_SDR | `color_fidelity_guard.py`, P11B4/P11B4D docs | 防止 HDR/10-bit 转码失真再次回流 | 画面曝光/色彩异常，Owner 无法审核 | `test_color_fidelity_guard`, `test_color_pipeline_lock` | Owner hold on fail |
| HR_GLOBAL_CONFLICT_REGISTRY | `global_conflict_registry.py` | 防止 hook/window 重复导致伪矩阵 | 多条视频只换标题或轻微扰动 | `test_global_conflict_registry` | Owner hold on conflict |
| HR_NEGATIVE_MEMORY | `negative_hook_memory.py`, P11B7 negative examples | 沉淀人手、杂乱、语义重复等失败样本 | 系统反复选择已 reject 的坏 hook | `test_negative_hook_memory` | Owner can override with log |
| HR_FFPROBE_DURATION | media probe helpers | 确认真实视频/音频时长 | 音画错位、截断或无效文件进入下游 | existing ffprobe tests | Pipeline fail |
| HR_AUDIO_FIT | `audio_fit_guard.py`, P11D | 防止口播超长或尾部异常 | 发布候选声音不可用 | `test_audio_fit_guard` | Pipeline fail or Owner hold |
| HR_VIDEO_STREAM_COPY | `visual_stream_copy_guard.py` | 配音合成后不改 controlled-SDR 画面 | P11D 改色视频或重编码视觉母版 | `test_visual_stream_copy_guard` | Pipeline fail |
| HR_NO_VISUAL_REENCODE_AFTER_MASTER | P11D policy, stream copy guard | 保护视觉母版一致性 | 二次转码引入色彩/锐化问题 | `test_visual_stream_copy_guard` | Pipeline fail |
| HR_NO_AUTO_PUBLISH | README/docs | Owner 必须手动发布 | 系统越权发布商业内容 | docs/tests only | Owner only |
| HR_NO_GIT_ADD_DOT | P12A git hygiene | 防止媒体、secrets、outputs 被误提交 | 仓库污染或泄露 | `test_gitignore_hygiene` | Pipeline fail |
| HR_RAW_VIDEOS_IMMUTABLE | `.gitignore`, docs | 原始素材不可移动/删除/误提交 | 素材丢失、Git 大文件污染 | `test_gitignore_hygiene` | Owner approval required |
| HR_OWNER_FIREWALL | P12 specs | Owner 是最高裁决层 | VLM/LLM 越权进入发布或删除 | docs/tests only | Owner final |
| HR_NO_SECRETS_IN_REPO | `.gitignore`, `.env.example` | 防止 API key 泄露 | GitHub 泄露凭证 | `test_gitignore_hygiene` | Pipeline fail |
