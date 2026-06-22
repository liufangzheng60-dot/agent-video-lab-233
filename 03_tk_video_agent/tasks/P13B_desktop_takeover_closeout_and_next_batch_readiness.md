# TASK：P13B_DESKTOP_TAKEOVER_CLOSEOUT_AND_NEXT_BATCH_READINESS

spec_version: P13B-v1

## 一、任务定位

当前正式结束智谱API接入排障，不再继续围绕API Key、SDK、认证页面或连接测试反复调试。

Owner已确认：

* 台式机用户级环境变量已成功写入；
* `ZAI_API_KEY`已存在；
* `ZHIPUAI_API_KEY`兼容变量已存在；
* `ZAI_BASE_URL`已设置为国内智谱通用API地址；
* 本轮将API接入状态视为已完成；
* 后续真实业务调用出现问题时，再在具体业务Task中按实际错误处理；
* 本任务不得重新调用智谱接口，不得消耗Token。

本任务的唯一目标是：

> 收束台式机迁移遗留问题，确认台式机可以正式接管后续视频Agent开发与下一批真实业务任务。

本任务不是：

* API接口验证任务；
* 视频生产任务；
* P12Y重渲染任务；
* 素材迁移任务；
* 新架构重构任务；
* Git自动提交任务；
* Git自动推送任务。

---

## 二、当前已确认基线

### 2.1 台式机环境

已确认：

* Python：3.12.10
* OpenCV：4.13.0
* FFmpeg：8.1.1
* Edge-TTS：7.2.8
* zai-sdk：0.2.3
* pip check：pass
* pytest：173 passed
* `helpers`导入正常
* `.venv`可用
* FFmpeg、OpenCV和本地编译环境可用

### 2.2 Git状态

已确认：

* 仓库路径：`E:\LFZ_CODE\agent-video-lab-233`
* Agent路径：`E:\LFZ_CODE\agent-video-lab-233\03_tk_video_agent`
* 当前分支：`main`
* Desktop HEAD：`c6f3344c1a80213b7b918198889795d2ba77172a`
* Origin Main：`c6f3344c1a80213b7b918198889795d2ba77172a`
* Commit一致：true
* Tree一致：true
* 追踪媒体数量：0
* 已提交代码与GitHub完全一致

### 2.3 当前未收口问题

P13A审计报告显示：

* 工作区不干净；
* 未追踪关键文件数量：2；
* 疑似密钥追踪数量：2；
* 活动代码硬编码高风险数量：2；
* 笔记本最新本地状态尚未证明；
* `DESKTOP_READY_FOR_NEXT_BATCH=false`。

已知未追踪文件：

1. `03_tk_video_agent/tasks/P12X_v2_cinematic_global_search_with_guardrails.md`
2. `03_tk_video_agent/tasks/P13A_desktop_environment_and_cross_machine_alignment_audit.md`

上述两个文件均为Task文档，不是原素材、媒体缓存或运行输出。

---

## 三、最高执行原则

继续执行：

`系统价值 = 成片质量 × 产出速度 ÷ 开发与调用成本`

本轮必须收缩问题，只处理会阻止台式机继续工作的真实问题。

禁止重新扩大范围，包括：

* 不重新安装Python；
* 不重新安装OpenCV；
* 不重新安装FFmpeg；
* 不重新安装Edge-TTS；
* 不重新安装zai-sdk；
* 不重新创建虚拟环境；
* 不重新测试智谱API；
* 不发起任何真实模型请求；
* 不处理P12Y的12条视频；
* 不复制原始素材；
* 不迁移媒体缓存；
* 不改动TikTok前台发布内容；
* 不做新一轮视频架构研发；
* 不设计自动发布；
* 不执行破坏性Git操作。

禁止执行：

* `git reset --hard`
* `git clean`
* `git restore .`
* `git checkout -- .`
* force push
* 自动merge
* 自动rebase
* 自动commit
* 自动push
* 删除Owner未确认文件

允许：

* 只读审计；
* 修改明确的活动代码硬编码路径；
* 修正明确的`.gitignore`遗漏；
* 对疑似密钥误报进行白名单分类；
* 生成建议提交清单；
* 运行本地测试；
* 生成最终接管报告。

---

## 四、API接入状态处理规则

本任务将API接入视为Owner已确认完成。

只允许检查以下布尔状态：

* `ZAI_API_KEY`是否存在；
* `ZHIPUAI_API_KEY`是否存在；
* `ZAI_BASE_URL`是否存在；
* `ZAI_BASE_URL`是否等于：
  `https://open.bigmodel.cn/api/paas/v4/`

禁止：

* 输出完整Key；
* 输出Key前缀；
* 输出Key后缀；
* 输出Key哈希；
* 输出Key内容；
* 发起API请求；
* 检查余额；
* 检查模型权限；
* 打开智谱网页；
* 创建或覆盖Key；
* 写入`.env`；
* 将密钥写入代码或报告。

报告只允许记录：

```json
{
  "zai_api_key_exists": true,
  "zhipuai_api_key_exists": true,
  "zai_base_url_valid": true,
  "api_remote_call_performed": false,
  "secret_value_logged": false
}
```

API状态字段定义为：

`API_ENVIRONMENT_CONFIGURED=true`

不得输出`API_MODEL_VERIFIED=true`，因为本轮不进行远程验证。

---

## 五、处理两个未追踪Task文件

必须检查：

1. `P12X_v2_cinematic_global_search_with_guardrails.md`
2. `P13A_desktop_environment_and_cross_machine_alignment_audit.md`

分别确认：

* 文件存在；
* 文件非空；
* 标题完整；
* spec_version存在；
* 不包含真实API Key；
* 不包含原始素材；
* 不包含二进制内容；
* 属于应被Git追踪的项目Task文档；
* 没有被`.gitignore`错误忽略。

不得自动执行`git add`、commit或push。

必须生成：

`proposed_git_commit_manifest.md`

其中列出：

* 建议加入Git的文件；
* 建议提交理由；
* 是否包含设备绝对路径；
* 是否包含密钥；
* 是否需要Owner确认；
* 建议commit message。

若两个文件均安全，标记：

`UNTRACKED_TASK_FILES_SAFE_TO_COMMIT=true`

若发现真实密钥或敏感值：

* 立即标记P0；
* 不修改文件；
* 不打印密钥；
* 停止提交建议；
* 输出Owner Gate。

---

## 六、疑似密钥命中复核

必须读取：

`E:\LFZ_DATA\AGENT_VIDEO_DATA_TEST\desktop_alignment_audit\gitignore_media_guard_report.json`

定位两个疑似密钥追踪命中的：

* 文件路径；
* 行号；
* 命中规则；
* 内容类型。

不得在控制台或报告中输出命中的完整字符串。

按以下规则分类：

### 6.1 误报

以下属于误报：

* `ZAI_API_KEY`
* `ZHIPUAI_API_KEY`
* `YOUR_API_KEY`
* `***REDACTED***`
* 环境变量名；
* 测试占位符；
* 密钥格式正则表达式；
* 文档中的安全示例；
* 仅说明“不得输出Key”的文字。

标记：

`secret_risk=false_positive`

### 6.2 真实风险

以下属于真实风险：

* 可直接使用的完整Key；
* 固定写入Python、JSON、PowerShell或Markdown的真实凭证；
* `.env`被Git追踪；
* 密钥已存在于Git历史中。

标记：

`secret_risk=confirmed`

如果确认真实风险：

* 不显示密钥；
* 不自动删除；
* 不自动改Git历史；
* 标记P0；
* 输出准确文件路径与处理建议；
* 等待Owner。

必须生成：

`secret_risk_resolution.json`

字段：

* total_hits；
* false_positive_hits；
* confirmed_secret_hits；
* affected_files；
* owner_gate_required；
* conclusion。

只有：

`confirmed_secret_hits=0`

才允许继续判定台式机可投产。

---

## 七、活动代码硬编码路径复核

必须读取：

`E:\LFZ_DATA\AGENT_VIDEO_DATA_TEST\desktop_alignment_audit\hardcoded_path_audit.json`

复核两个高风险命中。

按以下规则分类：

### 7.1 可接受命中

* 历史Task中的旧路径；
* 迁移说明；
* 审计脚本自身的设备路径；
* 示例命令；
* 不参与生产运行的文档。

标记：

`runtime_risk=false`

### 7.2 真实运行风险

* 活动Python代码写死笔记本路径；
* 活动配置写死笔记本用户目录；
* 主执行脚本依赖固定用户名；
* 生产入口写死旧仓库名；
* 数据目录未通过`AGENT_VIDEO_DATA_ROOT`解析；
* 当前台式机无法访问的绝对路径。

标记：

`runtime_risk=true`

若属于真实运行风险，允许执行一次最小化修复：

* 仓库路径使用Git根目录自动解析；
* Agent路径使用当前文件相对路径；
* 数据目录使用`AGENT_VIDEO_DATA_ROOT`；
* 禁止大规模重构；
* 禁止修改历史Task；
* 禁止修改业务逻辑；
* 禁止修改剪辑算法；
* 禁止修改模型策略。

每次修改后必须：

* 输出diff；
* 运行相关专项测试；
* 运行全部173项测试；
* 不自动提交。

必须生成：

`hardcoded_path_resolution.json`

字段：

* total_hits；
* documentation_only_hits；
* runtime_risk_hits；
* files_modified；
* tests_after_fix；
* owner_review_required；
* conclusion。

只有：

`runtime_risk_hits=0`

或所有真实风险已被最小修复且测试通过，才允许台式机继续下一批任务。

---

## 八、Git工作区收口

执行只读状态检查：

* `git status --short`
* `git diff --name-status`
* `git diff --cached --name-status`
* `git ls-files --others --exclude-standard`
* `git ls-files`
* `git check-ignore`

不得自动提交。

工作区状态按以下方式判定：

### 8.1 可接受的未提交状态

仅包含：

* 本轮P13B Task；
* 已确认安全的P12X-v2 Task；
* 已确认安全的P13A Task；
* 本轮生成的最小路径修复；
* 明确等待Owner提交的文档。

标记：

`WORKTREE_CONTROLLED=true`

### 8.2 不可接受状态

包含：

* 不明Python修改；
* 不明配置修改；
* 真实密钥；
* 媒体；
* outputs；
* 原素材；
* 缓存；
* 大文件；
* 无法解释的删除；
* 冲突文件。

标记：

`WORKTREE_CONTROLLED=false`

必须生成：

`desktop_worktree_closeout.json`

字段：

* staged；
* unstaged；
* untracked；
* known_safe_files；
* unknown_files；
* media_files；
* secret_files；
* controlled；
* suggested_next_action。

---

## 九、本地环境最终确认

不得重新安装依赖。

只执行：

1. Python版本检查；
2. OpenCV导入与版本检查；
3. FFmpeg版本检查；
4. Edge-TTS版本检查；
5. zai-sdk导入检查；
6. `pip check`；
7. `helpers`导入检查；
8. `helpers.vlm_qc_gate`导入检查；
9. `helpers.zhipu_vlm_adapter`导入检查；
10. 全部本地测试。

必须从：

`E:\LFZ_CODE\agent-video-lab-233\03_tk_video_agent`

运行：

`E:\LFZ_CODE\agent-video-lab-233\.venv\Scripts\python.exe -m pytest -q tests`

预期：

`173 passed`

不得运行任何联网测试。

不得调用：

* `glm-4.6`
* `glm-4.6v`
* `glm-4-flash`
* 任何远程模型。

---

## 十、台式机与GitHub对齐复核

必须再次确认：

* origin URL正确；
* 当前分支为main；
* Desktop HEAD；
* origin/main；
* Commit一致；
* Tree一致；
* ahead/behind数量。

允许：

`git fetch origin --prune`

禁止：

`git pull`

当满足：

* Desktop HEAD等于origin/main；
* Tree一致；
* 无未提交关键代码；
* 未追踪文件全部已分类；
* 未发现真实密钥；
* 无运行时硬编码高风险；

标记：

`DESKTOP_GITHUB_BASELINE_VALID=true`

---

## 十一、笔记本对齐边界

本轮不再要求立即操作笔记本。

由于笔记本最新本地状态尚未导出，必须继续保留：

`LAPTOP_UNPUSHED_CHANGES_RISK=unknown`

但该状态不得继续阻止台式机开展下一批工作，前提是：

* GitHub main被定义为当前共享代码基线；
* 台式机与GitHub main一致；
* Owner确认以后双机切换必须先commit并push；
* 周末第一次回到笔记本时再做`git fetch`和状态比对。

状态定义：

`LAPTOP_DESKTOP_ALIGNMENT_DEFERRED=true`

不得虚构：

`LAPTOP_DESKTOP_ALIGNMENT_EXACT=true`

必须生成：

`laptop_next_session_checklist.md`

内容只需包括：

1. 打开笔记本仓库；
2. `git status`；
3. `git fetch origin --prune`；
4. 比较Laptop HEAD与origin/main；
5. 如有未推送修改，先审阅再提交；
6. 禁止直接覆盖；
7. 对齐后再切换工作设备。

---

## 十二、P12Y与前台测试边界

本轮不得处理：

* P12Y的12条视频；
* TikTok前台已发布视频；
* Control和Variant；
* 发布清单；
* 视频数据表现；
* 原始素材；
  -历史输出目录。

P12Y当前状态视为：

`FRONTEND_TEST_IN_PROGRESS=true`

台式机迁移只处理代码与环境，不处理该批视频文件。

---

## 十三、最终输出目录

所有收口结果写入：

`E:\LFZ_DATA\AGENT_VIDEO_DATA_TEST\desktop_takeover_closeout`

至少包含：

* `desktop_takeover_summary.json`
* `api_environment_status.json`
* `secret_risk_resolution.json`
* `hardcoded_path_resolution.json`
* `desktop_worktree_closeout.json`
* `desktop_environment_final_check.json`
* `desktop_github_final_check.json`
* `proposed_git_commit_manifest.md`
* `laptop_next_session_checklist.md`
* `next_batch_readiness_report.md`
* `review_index.md`

禁止在任何报告中写入API Key。

---

## 十四、正式接管判定

只有以下全部满足，才能输出：

`DESKTOP_READY_FOR_NEXT_BATCH=true`

条件：

1. Python环境通过；
2. OpenCV通过；
3. FFmpeg通过；
4. Edge-TTS通过；
5. zai-sdk导入通过；
6. pip check通过；
7. pytest为173 passed；
8. Desktop HEAD与origin/main一致；
9. Tree一致；
10. 追踪媒体为0；
11. 确认真实密钥命中为0；
12. 活动代码运行时硬编码高风险为0；
13. 未追踪文件全部可解释；
14. 工作区受控；
15. API环境变量存在；
16. 本轮没有发起远程API请求；
17. P12Y视频未被改动。

笔记本证据缺失只保留风险提示，不再作为台式机启动下一批工作的绝对阻塞项。

---

## 十五、最终控制台输出格式

完成后只输出：

DESKTOP_TAKEOVER_CLOSEOUT_READY

输出目录：
台式机环境状态：
Python版本：
OpenCV版本：
FFmpeg版本：
Edge-TTS版本：
zai-sdk版本：
pip check：
pytest结果：
API_ENVIRONMENT_CONFIGURED：
API_REMOTE_CALL_PERFORMED：
Desktop HEAD：
Origin Main：
Commit一致：
Tree一致：
真实密钥命中数量：
密钥误报数量：
运行时硬编码高风险数量：
文档型硬编码数量：
未追踪Task数量：
未追踪Task是否安全：
工作区是否受控：
DESKTOP_GITHUB_BASELINE_VALID：
LAPTOP_DESKTOP_ALIGNMENT_DEFERRED：
LAPTOP_UNPUSHED_CHANGES_RISK：
FRONTEND_TEST_IN_PROGRESS：
DESKTOP_READY_FOR_NEXT_BATCH：
建议纳入Git的文件：
建议commit message：
下一步唯一动作：
完整报告：

然后停止等待Owner确认是否提交本轮安全文件。

---

## 十六、执行顺序

1. 验证Task；
2. 确认`spec_version=P13B-v1`；
3. 确认禁止远程API调用；
4. 读取P13A审计输出；
5. 检查三个API环境变量是否存在，不读取值；
6. 复核两个疑似密钥命中；
7. 复核两个硬编码路径命中；
8. 检查两个未追踪Task；
9. 分类全部工作区差异；
10. 如存在真实活动路径风险，进行最小修复；
11. 输出diff；
12. 运行专项测试；
13. 运行全部173项测试；
14. 复核Git远程与Commit；
15. 生成建议提交清单；
16. 生成笔记本下次会话检查清单；
17. 生成台式机接管报告；
18. 输出完成信号；
19. 停止等待Owner。

本任务的成功标准是结束无效排障、收口台式机迁移、保留Git安全边界，并让台式机具备明确、可验证的下一批业务接管资格。
