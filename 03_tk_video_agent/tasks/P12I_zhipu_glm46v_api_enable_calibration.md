# TASK：P12I_ZHIPU_GLM46V_API_ENABLE_AND_CALIBRATION

spec_version: P12I-v1

## 一、任务目标

正式启用智谱开放平台 GLM-4.6V API，并执行最多 3 个代表性样本的真实 Calibration。

本任务承接：

- P12E 三段式语义视频编译器；
- P12H 智谱 Provider 适配；
- P12H_ZHIPU_GLM46V_CALIBRATION_REVIEW_batch_20260617_001。

本任务仅允许：

1. 验证 API Key；
2. 验证 glm-4.6v 调用权限；
3. 验证图片输入；
4. 验证低帧率视频代理输入；
5. 验证 Function Call 或 JSON-only 结构化输出；
6. 执行最多 3 个真实 Calibration 样本；
7. 验证 Token、费用、缓存和幂等；
8. 生成 Calibration Owner Gate。

本任务不得运行完整 Golden Pilot，不得生成视频。

---

## 二、Owner 正式授权

Owner 已批准：

- Provider：zhipu；
- Model：glm-4.6v；
- 国内通用 API；
- 最多 3 个真实 Calibration 样本；
- 最多 6 次总请求尝试；
- 单请求最多重试 1 次；
- 允许上传低分辨率关键帧条带；
- 允许上传最多 1 个低帧率短视频代理；
- 不上传原片音频；
- 不上传完整原片；
- 不运行完整 Golden Pilot；
- 不生成新视频；
- 不自动发布。

禁止自动替换为 Flash、FlashX、其他 GLM 或其他 Provider。

---

## 三、项目与批次

项目根目录：

C:\Users\43871\AppData\Local\LFZ_CODE\agent-video-lab-233-laptop

工作目录：

C:\Users\43871\AppData\Local\LFZ_CODE\agent-video-lab-233-laptop\03_tk_video_agent

产品：

dog_stairs_v1

SKU：

khaki

素材批次：

batch_20260617_001

模型：

glm-4.6v

API Base URL：

https://open.bigmodel.cn/api/paas/v4/

---

## 四、API Key 安全

只允许读取：

ZAI_API_KEY

兼容只读检查：

ZHIPUAI_API_KEY

优先级：

1. ZAI_API_KEY
2. ZHIPUAI_API_KEY

禁止：

- 在界面输出完整 Key；
- 写入源码；
- 写入 Task；
- 写入日志；
- 写入 JSON；
- 写入 .env；
- 写入 Git；
- 把 Key 传给 Comet；
- 把 Key 发给其他 Provider。

允许输出：

- 是否存在；
- 字符长度；
- 脱敏状态。

如果 Key 不存在：

pipeline_status = BLOCKED_BY_API_KEY

停止真实调用，并在 Codex 界面输出安全设置步骤。

---

## 五、SDK 和 Provider 路径

优先复用现有：

- helpers/vlm_qc_gate.py
- 现有 Provider 抽象
- P12H 智谱 Adapter
- 现有 Schema
- 现有缓存
- 现有预算系统
- Owner Firewall
- agent_state

官方 SDK：

zai-sdk

客户端：

from zai import ZhipuAiClient

只允许一条实际智谱 Provider 调用路径。

不得同时启用 zai-sdk 和旧 zhipuai SDK 两条生产路径。

---

## 六、模型能力和输入边界

必须验证：

- glm-4.6v 当前账号可调用；
- 图片输入可用；
- 视频输入可用；
- usage 字段可读取；
- 输入 Token 可记录；
- 输出 Token 可记录；
- 视觉或视频 Token 可记录；
- thinking 参数实际支持情况；
- do_sample 参数实际支持情况；
- Function Call 对视觉请求是否可用；
- JSON-only 输出是否可解析。

重要硬规则：

单次请求不得同时混合：

- image_url
- video_url
- file_url

因此：

- Pass 1 只发送 image_url + text；
- Pass 2 只发送 video_url + text；
- 不得在同一请求同时发送关键帧图片和短视频。

---

## 七、媒体传输方式

### 图片

优先使用：

- Base64 image_url；
- 或项目已有安全 URL。

禁止上传高分辨率原图。

### 视频

优先探测平台支持的：

- video_url；
- 官方文件上传能力；
- 私有、短期、受控 URL。

如果视频接口只接受公网 URL，而当前项目没有安全私有上传通道：

不得：

- 上传到公开网盘；
- 上传到公开图床；
- 上传完整原片；
- 临时使用个人公开分享链接。

必须触发：

GATE_SECURE_VIDEO_PROXY_TRANSPORT

并提供：

A. 配置短期私有对象存储 URL  
B. 暂停 Pass 2，只执行图片 Calibration  
C. 使用官方文件上传能力  
D. 停止

---

## 八、资源包和现金扣费门禁

真实调用前必须确认或要求 Owner 确认：

- 资源包名称；
- 有效期；
- glm-4.6v 是否包含；
- 通用 API 是否包含；
- 图片 Token 是否抵扣；
- 视频 Token 是否抵扣；
- 输入 Token 是否抵扣；
- 输出 Token 是否抵扣；
- 套餐超额后的行为；
- 是否可能现金扣费；
- 是否可关闭自动超额扣费。

无法确认时：

checkpoint_type = GATE_ZHIPU_PACKAGE_CONFIRMATION
pipeline_status = BLOCKED_BY_OWNER_GATE

不得真实调用。

不得根据历史截图自动推断。

---

## 九、Calibration 样本

最多三个业务样本。

### 样本 1：静态产品关键帧条带

验证：

- product_present
- product_state
- product_visibility
- shot_scale
- room_or_scene
- segment_role_candidates

### 样本 2：狗实际使用关键帧条带

验证：

- dog_present
- dog_identity
- dog_motion_direction
- primary_action
- product_present
- usage 或 outcome 资格
- confidence

### 样本 3：低帧率动作短视频代理

验证：

- action_start
- action_end
- action_completeness
- dog_motion_direction
- product_state_change
- demonstration、outcome 或 proof 资格

不得为了凑满 3 个样本调用无意义素材。

---

## 十、调用限制

硬限制：

- max_successful_calls = 3
- max_total_attempts = 6
- max_retry_per_request = 1
- request_timeout_sec = 180
- upload_audio = false
- cache_enabled = true
- stream = false

能力探测调用计入总请求限制。

遇到 401：

- 不重试；
- 标记 API Key 或权限错误。

遇到 400：

- 普通参数错误允许修正后重试一次；
- 不得换模型。

遇到 429 或 5xx：

- 最多重试一次；
- 使用退避；
- 不得无限重试。

---

## 十一、结构化输出

优先：

1. 多模态 Function Call；
2. Function Call 不可用时使用 JSON-only Prompt；
3. 本地 Pydantic 或现有 Schema Validator 校验。

Schema 失败：

- 最多一次修复请求；
- 第二次失败后该样本 fail。

禁止：

- 正则静默补字段；
- 自动填默认值后标记 pass；
- Mock 冒充真实结果；
- 非法 JSON 写入正式 ledger；
- VLM 直接生成 Timeline。

必须保留 P12E 标签字段。

---

## 十二、缓存和幂等

缓存键至少包括：

- asset_hash
- window_start_ms
- window_end_ms
- prompt_schema_version
- provider
- model
- media_resolution
- proxy_version

同一成功缓存键不得再次请求。

缓存原子写入：

1. 临时文件；
2. flush；
3. fsync；
4. os.replace。

缓存测试优先通过本地查找验证，不得为了测试缓存再次产生收费请求。

---

## 十三、费用记录

必须记录：

- request_count
- successful_calls
- failed_calls
- retry_count
- input_tokens
- output_tokens
- image_tokens
- video_tokens
- cached_tokens
- resource_pack_before
- resource_pack_after
- cash_charge
- average_latency_ms

发现可能发生套餐外现金扣费时立即停止。

不得扩大 Owner 授权。

---

## 十四、Calibration 通过标准

必须满足：

1. glm-4.6v 可调用；
2. 两个图片样本可调用；
3. 图片结果通过 Schema；
4. 视频代理调用成功，或明确触发安全传输 Gate；
5. 产品状态识别合理；
6. 狗和使用动作识别合理；
7. 动作完整性能够判断或明确低置信度；
8. 脚本角色合法；
9. usage 和 Token 可记录；
10. 缓存不重复调用；
11. 未上传未授权媒体；
12. 未产生未授权费用。

---

## 十五、输出

写入 Git ignored outputs：

- zhipu_api_key_status.json
- zhipu_provider_capability_report.json
- zhipu_package_confirmation_report.json
- zhipu_calibration_requests.json
- zhipu_calibration_results.json
- zhipu_schema_validation_report.json
- zhipu_token_cost_report.json
- zhipu_cache_report.json
- zhipu_calibration_review.md

报告不得包含完整 API Key。

---

## 十六、完成后 Owner Gate

创建：

checkpoint_id = P12I_ZHIPU_GLM46V_CALIBRATION_REVIEW_batch_20260617_001

checkpoint_type = GATE_ZHIPU_GLM46V_CALIBRATION_REVIEW

设置：

awaiting_owner_review = true
pipeline_status = BLOCKED_BY_OWNER_GATE

在 Codex 界面输出：

OWNER_REVIEW_REQUIRED

检查点编号：
实际Provider：
实际Model：
SDK版本：
API Key状态：
资源包确认结果：
图片调用成功/失败：
视频调用成功/失败：
视频代理传输方式：
Function Call可用性：
最终结构化输出策略：
Schema成功率：
产品状态识别结果：
狗动作识别结果：
动作完整性判断结果：
脚本角色判断结果：
缓存结果：
输入Token：
输出Token：
图片Token：
视频Token：
资源包扣减：
现金费用：
平均延迟：
失败与重试：
报告路径：
主要风险：

请选择：

A. Calibration通过，批准运行完整Golden Pilot标签  
B. 只批准运行Pass 1关键帧标签  
C. 修订Prompt或Schema后重新Calibration  
D. 配置安全视频代理传输后重新测试Pass 2  
E. 停止智谱VLM方向

Codex必须给出推荐方案及理由。

Owner未明确选择前不得：

- 运行完整Golden Pilot；
- 生成three_stage_plan；
- 生成新视频；
- 调用额外VLM；
- 自动发布。

---

## 十七、安全与Git

继续遵守：

- raw_videos immutable；
- 媒体和报告 Git ignored；
- API Key 不进入 Git；
- 禁止 git add .；
- 禁止 force push；
- 禁止 reset --hard；
- 禁止删除负面样本；
- 禁止旧自由 Planner；
- 禁止自动发布。

如有源码修改：

1. 运行 P12I focused tests；
2. 运行 P12E/P12H VLM 回归；
3. 运行 Owner Firewall 和 Git Safety；
4. 运行全量 unittest；
5. 选择性 commit；
6. 安全 push。

---

## 十八、执行顺序

现在执行：

1. 验证本 Task 完整性；
2. 确认 spec_version = P12I-v1；
3. 检查 ZAI_API_KEY；
4. 检查 zai-sdk；
5. 检查 glm-4.6v 权限；
6. 检查资源包门禁；
7. 检查现有候选样本；
8. 运行最多 3 个 Calibration；
9. 验证 Schema、缓存和费用；
10. 生成报告；
11. 运行测试与 Git Safety；
12. 如有源码修改，选择性 commit 和 push；
13. 创建 P12I Owner Gate；
14. 输出中文方案菜单；
15. 停止。

本任务不得运行完整 Golden Pilot。