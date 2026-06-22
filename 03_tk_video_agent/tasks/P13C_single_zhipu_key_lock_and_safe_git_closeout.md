# TASK：P13C_SINGLE_ZHIPU_KEY_LOCK_AND_SAFE_GIT_CLOSEOUT

spec_version: P13C-v1

## 一、任务定位

P13B已经完成台式机迁移收口，并确认：

* `DESKTOP_READY_FOR_NEXT_BATCH=true`
* Python 3.12.10正常；
* OpenCV 4.13.0正常；
* FFmpeg 8.1.1正常；
* Edge-TTS 7.2.8正常；
* zai-sdk 0.2.3正常；
* pip check通过；
* 本地测试173项通过；
* Desktop HEAD与origin/main一致；
* Git Tree一致；
* 真实密钥追踪数量为0；
* 工作区处于可解释、受控状态；
* GitHub main是当前共享代码基线。

本任务只完成两个收口动作：

1. 将智谱运行时凭证策略锁定为唯一变量`ZAI_API_KEY`；
2. 审核、提交并推送P13B建议的安全代码与Task文件。

不得重新展开环境排障，不得重新安装依赖，不得重新验证智谱远程接口，不得生产视频。

---

## 二、最高安全边界

明文API Key禁止进入：

* Python源码；
* PowerShell脚本；
* Task文档；
* JSON配置；
* YAML配置；
  -测试文件；
  -日志；
  -报告；
* Git暂存区；
* Git提交；
* Git历史。

本任务不得打印：

* Key全文；
* Key前缀；
* Key后缀；
* Key的任何可识别片段。

允许记录：

* Key是否存在；
* Key长度；
* 指纹是否匹配；
* 值是否被记录：false。

本任务不得发起任何真实API请求，不得消耗Token。

---

## 三、唯一密钥源强制规则

正式运行时只允许读取：

`ZAI_API_KEY`

正式接口地址只允许读取或默认使用：

`ZAI_BASE_URL=https://open.bigmodel.cn/api/paas/v4/`

禁止正式运行时读取：

* `ZHIPUAI_API_KEY`
* `ZHIPU_API_KEY`
* `.env`中的旧Key；
* 命令行明文Key；
* JSON中的Key；
* Python硬编码Key；
* Task中的Key；
* 其他自动fallback凭证。

必须形成永久规则：

`ZHIPU_SINGLE_KEY_SOURCE_INVARIANT`

定义：

```text
provider = zhipu
model = glm-4.6v
key_source = ZAI_API_KEY only
base_url = https://open.bigmodel.cn/api/paas/v4/
credential_fallback = forbidden
model_fallback = forbidden
provider_fallback = forbidden
```

---

## 四、运行时指纹验证

当前用户环境已经设置：

* `ZAI_API_KEY`
* `ZAI_BASE_URL`
* `ZAI_KEY_FINGERPRINT_EXPECTED`

本任务只能在内存中计算`ZAI_API_KEY`的SHA-256，并与：

`ZAI_KEY_FINGERPRINT_EXPECTED`

进行比较。

禁止将明文Key写入文件。

允许本地报告记录：

```json
{
  "zai_api_key_exists": true,
  "zai_api_key_length": 49,
  "expected_fingerprint_exists": true,
  "fingerprint_matches": true,
  "secret_value_logged": false
}
```

若指纹不匹配：

* 立即停止；
* 不调用远程接口；
* 不修改代码；
* 不提交Git；
* 输出`OWNER_KEY_FINGERPRINT_MISMATCH`。

---

## 五、代码审核与最小修改范围

重点审核：

* `helpers/zhipu_vlm_adapter.py`
* `helpers/agent_factory_harness.py`
* 所有实际调用智谱适配器的活动Python入口；
* `configs/`中的Provider和模型配置；
* 与智谱环境变量相关的测试。

必须确认：

1. 生产代码只读取`ZAI_API_KEY`；
2. 不再回退到`ZHIPUAI_API_KEY`；
3. 不再回退到`ZHIPU_API_KEY`；
4. 不从`.env`自动寻找生产Key；
5. 不允许调用参数覆盖正式Key；
6. Provider锁定为`zhipu`；
7. Model锁定为`glm-4.6v`；
8. Base URL锁定为国内通用接口；
9. 没有Provider fallback；
10. 没有Model fallback；
11. 错误日志不会输出Key；
12. 调试报告不会输出Key；
13. API调用失败时必须明确失败，不得偷偷切换其他模型或Provider。

只允许围绕上述单密钥源策略做最小修改。

禁止修改：

* 视频剪辑算法；
* OpenCV评分逻辑；
* FFmpeg渲染逻辑；
* Beam Search；
  -叙事DAG；
* P12Y视频；
* TikTok发布内容；
* 原始素材；
  -缓存。

---

## 六、必须新增的本地测试

新增：

`tests/test_single_zhipu_key_source.py`

测试不得联网。

至少覆盖：

### 6.1 正常唯一密钥

仅设置`ZAI_API_KEY`时：

* 正确读取；
  -选中变量名为`ZAI_API_KEY`；
  -不输出值。

### 6.2 旧变量不允许生效

仅设置以下任一变量时：

* `ZHIPUAI_API_KEY`
* `ZHIPU_API_KEY`

必须返回明确缺少正式Key，不得使用旧变量。

### 6.3 多变量冲突

同时设置：

* `ZAI_API_KEY`
* `ZHIPUAI_API_KEY`
* `ZHIPU_API_KEY`

必须只选择`ZAI_API_KEY`。

### 6.4 无Key

所有变量为空时：

* 明确失败；
  -不调用Provider；
  -不产生fallback。

### 6.5 日志脱敏

异常和状态输出中不得包含测试Key原文。

### 6.6 固定Provider与模型

断言：

* Provider为`zhipu`；
* Model为`glm-4.6v`；
* Base URL为国内通用地址；
* Provider fallback为false；
* Model fallback为false。

### 6.7 指纹校验

使用测试假Key验证：

-相同指纹通过；
-不同指纹失败；
-报告不包含原文。

---

## 七、Task文件安全审核

审核以下未追踪Task：

1. `tasks/P12X_v2_cinematic_global_search_with_guardrails.md`
2. `tasks/P13A_desktop_environment_and_cross_machine_alignment_audit.md`
3. `tasks/P13B_desktop_takeover_closeout_and_next_batch_readiness.md`
4. `tasks/P13C_single_zhipu_key_lock_and_safe_git_closeout.md`

必须确认：

-文件非空；
-标题完整；

* spec_version存在；
  -不含真实API Key；
  -不含媒体；
  -不含二进制；
  -可安全进入Git。

历史设备绝对路径允许保留在Task文档中，因为它们是执行记录，不是生产运行依赖。

---

## 八、agent_factory_harness审核

审核：

`helpers/agent_factory_harness.py`

必须确认：

-文件属于真实项目代码；
-不是临时测试残留；
-不含真实Key；
-不含业务媒体；
-不含本机临时目录依赖；
-不破坏现有Agent工厂；
-与当前测试和项目架构一致；
-应该进入Git。

若发现其为无用临时文件：

-不得提交；
-不得删除；
-报告中解释原因；
-等待Owner处理。

---

## 九、Git提交前安全门

提交前必须执行：

1. `git fetch origin --prune`
   2.确认当前分支是`main`
   3.确认Desktop HEAD等于origin/main
   4.确认Tree一致
   5.检查`git status --short`
   6.检查待提交文件
   7.扫描待提交文件中的疑似真实Key
   8.确认无媒体
   9.确认无outputs
   10.确认无cache
   11.确认无`.env`
   12.确认无`.venv`
   13.确认无超过50MB的文件
   14.运行`pip check`
   15.运行全部本地测试。

禁止：

* `git add -A`
* `git add .`
* `git commit -a`
  -自动加入未知文件。

必须使用显式文件路径执行`git add`。

---

## 十、允许提交的候选文件

经安全审核后，允许显式加入：

* `03_tk_video_agent/tasks/P12X_v2_cinematic_global_search_with_guardrails.md`
* `03_tk_video_agent/tasks/P13A_desktop_environment_and_cross_machine_alignment_audit.md`
* `03_tk_video_agent/tasks/P13B_desktop_takeover_closeout_and_next_batch_readiness.md`
* `03_tk_video_agent/tasks/P13C_single_zhipu_key_lock_and_safe_git_closeout.md`
* `03_tk_video_agent/helpers/agent_factory_harness.py`
* `03_tk_video_agent/helpers/zhipu_vlm_adapter.py`，仅在本轮确实发生安全修改时；
* `03_tk_video_agent/tests/test_single_zhipu_key_source.py`
* 与单密钥策略直接相关、且经审核安全的现有测试修改。

不得加入任何其他未知文件。

---

## 十一、测试要求

从：

`E:\LFZ_CODE\agent-video-lab-233\03_tk_video_agent`

使用：

`E:\LFZ_CODE\agent-video-lab-233\.venv\Scripts\python.exe`

执行：

-单密钥专项测试；
-智谱适配器现有本地测试；
-全部`tests`。

现有173项测试必须继续通过。

新增测试后，总通过数应大于173。

不得通过跳过、删除或放宽旧测试制造通过。

不得联网。

---

## 十二、Commit与Push规则

只有以下全部通过才允许提交：

-指纹匹配；
-真实密钥扫描命中为0；
-追踪媒体为0；
-所有候选文件均安全；
-单密钥策略测试通过；
-现有173项测试保持通过；
-新增测试通过；

* pip check通过；
* HEAD与origin/main提交前一致；
  -工作区没有无法解释的差异。

建议Commit Message：

`chore: lock single zhipu key source and close desktop takeover`

使用显式路径暂存。

提交成功后：

1.执行`git push origin main`
2.执行`git fetch origin --prune`
3.确认Desktop HEAD等于origin/main
4.确认Tree一致
5.确认没有未提交的关键代码。

不得force push。

---

## 十三、输出目录

输出至：

`E:\LFZ_DATA\AGENT_VIDEO_DATA_TEST\single_key_git_closeout`

至少生成：

* `single_key_runtime_policy.json`
* `key_fingerprint_check.json`
* `legacy_key_source_scan.json`
* `secret_scan_report.json`
* `candidate_file_review.json`
* `test_report.json`
* `git_commit_manifest.json`
* `git_push_verification.json`
* `p13c_closeout_report.md`
* `review_index.md`

所有报告禁止包含明文Key或Key片段。

---

## 十四、完成标准

必须满足：

* `ZHIPU_SINGLE_KEY_SOURCE_INVARIANT=true`
* `ZAI_API_KEY_ONLY=true`
* `KEY_FINGERPRINT_MATCH=true`
* `LEGACY_KEY_FALLBACK_COUNT=0`
* `PROVIDER_FALLBACK_COUNT=0`
* `MODEL_FALLBACK_COUNT=0`
* `REMOTE_API_CALL_PERFORMED=false`
* `SECRET_VALUE_LOGGED=false`
* `CONFIRMED_SECRET_HITS=0`
* `TRACKED_MEDIA_COUNT=0`
* `EXISTING_173_TESTS_PRESERVED=true`
* `ALL_TESTS_PASS=true`
* `COMMIT_CREATED=true`
* `PUSH_SUCCEEDED=true`
* `DESKTOP_HEAD_EQUALS_ORIGIN_MAIN=true`
* `DESKTOP_READY_FOR_NEXT_BATCH=true`

---

## 十五、最终控制台输出

完成后只输出：

P13C_SINGLE_KEY_AND_GIT_CLOSEOUT_READY

输出目录：
唯一Key变量：
Key长度：
Key指纹匹配：
旧Key变量读取数量：
旧Key fallback数量：
Provider：
Model：
Base URL：
Provider fallback数量：
Model fallback数量：
远程API调用：
明文Key记录：
真实密钥命中：
追踪媒体数量：
候选文件审核数量：
实际提交文件：
专项测试结果：
全部测试结果：
Commit SHA：
Commit Message：
Push结果：
Desktop HEAD：
Origin Main：
Commit一致：
Tree一致：
工作区状态：
DESKTOP_READY_FOR_NEXT_BATCH：
下一步唯一动作：
完整报告：

然后停止，等待Owner进入下一批业务。

---

## 十六、执行顺序

1.读取并验证P13C Task；
2.确认`spec_version=P13C-v1`；
3.确认禁止远程API调用；
4.检查`ZAI_API_KEY`存在；
5.检查期望指纹变量存在；
6.在内存中计算并核对指纹；
7.扫描生产代码中的所有Key来源；
8.清除生产代码中的旧变量fallback；
9.锁定Provider、Model和Base URL；
10.新增单密钥策略测试；
11.审核四个Task文件；
12.审核`agent_factory_harness.py`；
13.运行secret扫描；
14.运行媒体和大文件扫描；
15.运行专项测试；
16.运行全部本地测试；
17.执行pip check；
18.执行Git远程基线复核；
19.仅显式暂存安全文件；
20.生成提交前manifest；
21.创建Commit；
22.推送main；
23.重新fetch；
24.验证Desktop HEAD与origin/main；
25.生成最终报告；
26.输出完成信号；
27.停止。

本任务的成功标准是把唯一智谱凭证源、固定Provider与固定模型固化为可测试的运行时规则，同时安全提交台式机迁移产物并恢复干净、可追溯的Git共享基线。
