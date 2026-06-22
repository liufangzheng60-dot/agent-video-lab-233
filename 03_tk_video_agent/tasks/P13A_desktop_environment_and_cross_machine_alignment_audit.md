# TASK：P13A_DESKTOP_ENVIRONMENT_AND_CROSS_MACHINE_ALIGNMENT_AUDIT

spec_version: P13A-v1

## 一、任务定位

当前停止一切智谱API认证、API Key、模型权限和真实接口测试。

本任务回归项目主进度，只执行两项工作：

1. 彻底审计台式机当前运行环境是否具备继续开发和运行视频Agent的条件；
2. 审核台式机代码仓库是否与笔记本已推送到GitHub的代码状态对齐。

本任务是只读审计任务，不是环境重装任务，不是代码重构任务，也不是视频生产任务。

禁止：

* 调用智谱API；
* 发起任何真实VLM请求；
* 消耗任何模型Token；
* 上传业务素材；
* 修改原始视频；
* 修改P12系列成片；
* 执行自动发布；
* 自动安装、卸载或升级Python依赖；
* 执行`git reset --hard`；
* 执行`git clean`；
* 执行`git checkout -- .`；
* 执行`git restore .`；
* 执行自动merge、rebase或force push；
* 覆盖任何未提交代码。

允许：

* 读取系统与环境信息；
* 读取Git状态；
* 执行`git fetch origin --prune`；
* 运行不调用外部模型的本地单元测试；
* 读取和哈希代码文件；
* 生成审计报告；
* 生成后续修复建议；
* 创建本任务规定的审计输出文件。

---

## 二、项目路径与设备信息

### 台式机仓库

`E:\LFZ_CODE\agent-video-lab-233`

### 台式机Agent目录

`E:\LFZ_CODE\agent-video-lab-233\03_tk_video_agent`

### 台式机虚拟环境Python

`E:\LFZ_CODE\agent-video-lab-233\.venv\Scripts\python.exe`

### 台式机测试数据根目录

`E:\LFZ_DATA\AGENT_VIDEO_DATA_TEST`

### 笔记本历史仓库路径

`C:\Users\43871\AppData\Local\LFZ_CODE\agent-video-lab-233-laptop`

### GitHub远程仓库

`https://github.com/liufangzheng60-dot/agent-video-lab-233.git`

### GitHub共享代码真源

默认使用：

`origin/main`

但只有在笔记本已将最新修改提交并推送后，`origin/main`才能代表笔记本的最新共享代码。

不得仅凭“仓库名称相同”宣称两台机器完全对齐。

---

## 三、最高审计原则

代码对齐必须拆成四个不同层级，禁止混为一谈：

### Level 1：远程仓库对齐

检查台式机：

* remote URL是否正确；
* 当前分支；
* HEAD commit；
* `origin/main` commit；
* ahead/behind数量；
* 是否存在迁移分支；
* 是否存在未推送提交。

### Level 2：Git追踪文件对齐

检查：

* 台式机HEAD树是否与`origin/main`树一致；
* 所有追踪文件内容哈希；
* 是否有已修改但未提交文件；
* 是否有新增未追踪的代码、配置、Task或测试；
* 是否有已删除但未提交文件；
* 是否有文件只存在于台式机。

### Level 3：跨设备代码对齐

只有满足以下任一证据，才能判定笔记本与台式机代码对齐：

1. 笔记本和台式机都确认位于同一个Git commit；
2. 仓库中存在笔记本导出的机器清单，并且其commit、tree hash和追踪文件哈希与台式机一致；
3. 笔记本最新分支已推送，台式机与该远程分支commit及tree hash一致。

缺少笔记本证据时必须输出：

`LAPTOP_DESKTOP_ALIGNMENT_NOT_PROVABLE`

不得猜测为已对齐。

### Level 4：运行环境对齐

运行环境不要求字节级完全相同，但核心生产依赖必须兼容：

* Python主次版本；
* OpenCV版本；
* NumPy版本；
* FFmpeg版本；
* FFprobe版本；
* Edge-TTS版本；
* zai-sdk版本；
* PyYAML版本；
* pytest版本；
* 项目依赖完整性；
* 环境变量命名；
* 数据根目录；
* Python导入路径；
* `.pth`路径；
* `PYTHONPATH`；
* Git配置中的换行和大小写行为。

不得把`.venv`文件夹复制一致视为环境对齐。

---

## 四、审计输出目录

所有审计文件写入：

`E:\LFZ_DATA\AGENT_VIDEO_DATA_TEST\desktop_alignment_audit`

至少生成：

* `desktop_environment_manifest.json`
* `desktop_git_manifest.json`
* `desktop_tracked_file_hashes.csv`
* `desktop_uncommitted_changes.json`
* `github_alignment_report.json`
* `cross_machine_alignment_report.md`
* `environment_compatibility_report.md`
* `hardcoded_path_audit.json`
* `gitignore_media_guard_report.json`
* `local_test_report.json`
* `laptop_manifest_export_command.ps1`
* `remediation_plan.md`
* `audit_summary.json`

审计文件不得写入API Key。

---

## 五、台式机环境彻底审计

### 5.1 操作系统与Shell

记录：

* Windows版本；
* Windows build；
* 系统架构；
* PowerShell版本；
* 当前用户名；
* 当前工作目录；
* 系统时间；
* 计算机名称。

不得记录与项目无关的私人文件。

### 5.2 Git

记录：

* Git版本；
* Git可执行文件路径；
* 仓库根目录；
* 当前分支；
* HEAD SHA；
* HEAD tree SHA；
* remote URL；
* `origin/main` SHA；
* `origin/main` tree SHA；
* ahead数量；
* behind数量；
* 工作区是否干净；
* staged修改；
* unstaged修改；
* untracked文件；
* Git submodule状态；
* Git LFS是否启用；
* `core.autocrlf`；
* `core.filemode`；
* `core.ignorecase`。

允许执行：

`git fetch origin --prune`

禁止执行：

* pull；
* merge；
* rebase；
* reset；
* clean；
* stash；
* checkout覆盖。

### 5.3 Python与虚拟环境

必须使用：

`E:\LFZ_CODE\agent-video-lab-233\.venv\Scripts\python.exe`

记录：

* 实际Python可执行文件；
* Python版本；
* `sys.prefix`；
* `sys.base_prefix`；
* 是否真实处于虚拟环境；
* site-packages路径；
* pip版本；
* `pip check`结果；
* 已安装关键包版本。

关键包：

* opencv-python-headless；
* numpy；
* edge-tts；
* zai-sdk；
* PyYAML；
* pytest。

不得自动升级任何包。

### 5.4 OpenCV

本任务不再重新安装OpenCV。

只验证：

* `import cv2`成功；
* OpenCV版本；
* Headless包存在；
* 不同时存在多个互相冲突的OpenCV wheel；
* Farneback函数存在；
* PyrLK函数存在；
* RANSAC仿射估计函数存在；
* 视频解码能力可用。

只运行小型本地合成矩阵测试，不读取业务视频。

### 5.5 FFmpeg

记录：

* `ffmpeg.exe`路径；
* `ffprobe.exe`路径；
* FFmpeg版本；
* FFprobe版本；
* 是否支持`libx264`；
* 是否支持AAC；
* 是否可生成最小本地测试文件；
* 是否可以读取生成文件的PTS和帧率。

不得使用P12业务视频。

### 5.6 Edge-TTS

只验证：

* Python包可导入；
* 版本可读取；
* CLI是否存在。

本任务默认不进行联网语音生成。

### 5.7 zai-sdk

只验证：

* 包存在；
* `from zai import ZhipuAiClient`成功；
* 版本可读取。

不得执行API请求。

### 5.8 环境变量

仅记录是否存在，不记录值：

* `AGENT_VIDEO_DATA_ROOT`
* `ZAI_API_KEY`
* `ZHIPUAI_API_KEY`
* `ZAI_BASE_URL`
* `PYTHONPATH`

对于密钥类变量，只允许记录：

* exists；
* selected variable name；
* length；
* value_logged=false。

不得打印、保存或回显Key内容。

### 5.9 路径可写性

验证以下目录是否存在和可写：

* 仓库根目录；
* Agent目录；
* Task目录；
* 台式机测试数据根目录；
* 审计输出目录；
* 临时目录。

测试可写性时只能创建并立即删除审计专用小文件。

---

## 六、代码仓库对齐审计

### 6.1 远程仓库身份

必须确认：

`git remote get-url origin`

等于：

`https://github.com/liufangzheng60-dot/agent-video-lab-233.git`

允许末尾`.git`形式差异。

远程仓库不一致时：

* 只报告；
* 不自动修改remote；
* 输出建议命令。

### 6.2 Commit对齐

执行只读比较：

* desktop HEAD vs origin/main；
* desktop HEAD vs所有可见的远程迁移分支；
* desktop tree hash vs origin/main tree hash。

输出：

* exact commit match；
* same tree different commit；
* desktop ahead；
* desktop behind；
* diverged；
* remote unavailable。

### 6.3 追踪文件哈希

对Git追踪文件计算SHA256，但排除：

* `.git`；
* `.venv`；
* outputs；
* caches；
  -原始视频；
* 渲染视频；
  -临时文件。

必须输出：

* relative_path；
* size_bytes；
* sha256；
* git_blob_sha；
* file_category。

文件类别至少包括：

* source；
* config；
* task；
* test；
* documentation；
* script；
* other。

### 6.4 未提交差异

必须明确列出：

* staged；
* unstaged；
* untracked；
* deleted；
* renamed；
* conflicted。

对于每个差异，标记：

* code_relevant；
* environment_only；
* generated_output；
* media；
* secret_risk；
* needs_owner_review。

不得自动提交。

### 6.5 必须共享的小型状态文件

审核以下项目是否已进入Git追踪：

* `configs/`
* `tasks/`
* `tests/`
* Owner偏好权重或pairwise数据；
* 资产排除时间区间；
* 叙事DAG；
* cinematic/search策略；
* Prompt版本；
  -错误日志；
  -迁移脚本；
  -依赖文件；
  -环境说明文档。

如果关键状态仅存在于被忽略的outputs目录：

标记为：

`PORTABILITY_STATE_AT_RISK`

并列出应该迁移到Git追踪目录的文件，但本任务不得自动移动。

### 6.6 Git忽略防线

确认以下内容不会进入Git：

* `.env`
* `.venv`
* API Key；
* MP4；
* MOV；
* WAV；
* MP3；
  -原始素材；
* outputs；
* caches；
  -临时帧；
* Python缓存；
* pytest缓存。

检查：

* `.gitignore`规则；
* 当前是否已有媒体被追踪；
* 当前是否有超过50MB的追踪文件；
* 当前是否有疑似密钥字符串被追踪。

密钥检测只报告文件路径和规则命中类型，不得输出疑似密钥原文。

---

## 七、硬编码路径审计

扫描活动代码和配置：

* `.py`
* `.ps1`
* `.json`
* `.yaml`
* `.yml`
* `.toml`
* `.ini`

排除：

* `.git`
* `.venv`
* outputs
* caches
  -历史渲染报告。

重点搜索：

* `C:\Users\43871`
* `agent-video-lab-233-laptop`
* `E:\LFZ_CODE\agent-video-lab-233`
* `C:\AGENT_VIDEO_DATA`
* `E:\LFZ_DATA`
* 固定盘符；
* 固定用户名；
* 旧P12输出目录；
* 直接写死的API地址；
* 已废弃环境变量名。

分类：

### 合法

-历史Task中的说明文字；
-审计脚本中的显式设备路径；
-文档示例。

### 风险

-活动Python执行逻辑；
-活动配置；
-生产PowerShell入口；
-测试依赖本机绝对路径；
-代码直接假设笔记本目录存在。

输出每个命中：

* file；
* line；
* category；
* severity；
* remediation。

不得自动大规模替换路径。

---

## 八、本地测试要求

### 8.1 禁止联网模型测试

不得运行：

-真实智谱请求；
-任何VLM连接测试；
-任何视频上传测试；
-任何Token计费测试。

### 8.2 运行测试

从以下目录运行：

`E:\LFZ_CODE\agent-video-lab-233\03_tk_video_agent`

使用：

`E:\LFZ_CODE\agent-video-lab-233\.venv\Scripts\python.exe`

运行：

`python -m pytest -q tests`

记录：

* collected；
* passed；
* failed；
* skipped；
* duration；
  -失败测试；
  -失败原因类别。

预期当前基线：

`173 passed`

如果数量变化：

必须解释是仓库版本不同、测试新增、测试缺失还是环境问题。

不得为了通过测试修改代码。

### 8.3 导入测试

至少验证：

* `helpers`
* `helpers.vlm_qc_gate`
* `helpers.zhipu_vlm_adapter`
* OpenCV
* Edge-TTS包
* zai-sdk

---

## 九、笔记本与台式机对齐判定

### 9.1 优先查找笔记本清单

在仓库和远程分支中查找：

* `machine_manifests/laptop*.json`
* `migration_manifests/laptop*.json`
* `environment_snapshot.txt`
* 其他明确标记为笔记本导出的commit/tree/file hash清单。

### 9.2 有清单时

比较：

* remote URL；
* branch；
* commit SHA；
* tree SHA；
  -追踪文件SHA256；
  -关键配置；
  -Task文件；
  -测试文件；
  -依赖文件；
  -核心包版本。

输出：

* exact；
* code_exact_environment_compatible；
* code_diverged；
* environment_diverged；
* incomplete_evidence。

### 9.3 无清单时

生成：

`laptop_manifest_export_command.ps1`

该命令未来在笔记本运行后，应输出：

* laptop_environment_manifest.json；
* laptop_git_manifest.json；
* laptop_tracked_file_hashes.csv。

命令必须：

* 只读；
* 不复制视频；
* 不上传媒体；
* 不打印API Key；
* 不修改Git；
* 将清单写入笔记本本地桌面或指定审计目录。

在无笔记本清单的情况下，本轮只能确认：

* 台式机与GitHub是否对齐；
* GitHub能否作为共享代码真源；
* 不能确认笔记本尚未推送的本地修改。

最终必须明确输出：

`LAPTOP_DESKTOP_ALIGNMENT_NOT_PROVABLE`

而不是假设已对齐。

---

## 十、对齐状态定义

### DESKTOP_ENVIRONMENT_PASS

以下全部满足：

* Python虚拟环境有效；
  -核心依赖可导入；
* OpenCV功能存在；
* FFmpeg/FFprobe存在；
* pip check通过；
* tests通过；
  -关键目录可写；
  -无环境级阻塞。

### DESKTOP_GITHUB_ALIGNMENT_EXACT

以下全部满足：

* remote正确；
* HEAD commit等于origin/main；
* tree hash相同；
  -工作区干净；
  -无未追踪的关键代码或配置。

### DESKTOP_GITHUB_ALIGNMENT_WITH_LOCAL_CHANGES

满足：

* committed tree与origin/main一致；
  -但存在本地未提交代码、配置、Task或测试。

### DESKTOP_GITHUB_DIVERGED

满足任一：

* HEAD和origin/main各自有独立提交；
* tree hash不同；
* remote错误；
  -关键追踪文件不同。

### LAPTOP_DESKTOP_ALIGNMENT_EXACT

只有笔记本证据充分且：

* commit相同；
* tree hash相同；
  -追踪文件哈希相同。

### LAPTOP_DESKTOP_ALIGNMENT_NOT_PROVABLE

无笔记本最新清单，或无法确认笔记本已推送全部修改。

---

## 十一、修复建议规则

本任务只生成修复建议，不直接执行。

`remediation_plan.md`必须按优先级分组：

### P0：阻止生产

例如：

-代码仓库diverged；
-核心依赖缺失；
-tests失败；
-remote错误；
-关键状态未追踪且可能丢失；
-媒体或Key被Git追踪。

### P1：迁移前必须处理

例如：

-活动代码含笔记本硬编码路径；
-依赖版本严重不一致；
-数据根目录不可写；
-台式机存在未提交关键代码。

### P2：可以后续优化

例如：

-文档路径陈旧；
-历史Task包含旧绝对路径；
-非关键版本差异；
-审计工具未标准化。

每项建议必须给出：

-问题；
-影响；
-证据文件；
-建议命令；
-是否需要Owner确认；
-是否具有破坏性。

---

## 十二、最终报告要求

`cross_machine_alignment_report.md`必须包含：

1. 执行时间；
2. 台式机环境总状态；
3. 台式机Git总状态；
4. GitHub对齐状态；
5. 笔记本对齐证据状态；
6. commit和tree对比；
   7.未提交差异；
   8.关键依赖版本；
   9.测试结果；
   10.硬编码路径；
7. Git忽略防线；
   12.可移植性风险；
   13.是否允许台式机继续开发；
   14.是否允许台式机处理真实新素材；
   15.是否需要先回笔记本导出清单；
   16.下一步唯一建议。

---

## 十三、允许继续生产的条件

只有同时满足以下条件，报告才可输出：

`DESKTOP_READY_FOR_NEXT_BATCH=true`

条件：

* `DESKTOP_ENVIRONMENT_PASS`
* Git远程正确；
  -台式机代码至少与origin/main完全一致；
  -tests全部通过；
  -工作区无不明关键修改；
  -不存在被Git追踪的API Key或业务媒体；
  -不存在活动代码依赖笔记本绝对路径；
  -数据根目录可写。

笔记本最新本地状态无法证明时，仍可允许台式机继续开发，但必须附加：

`LAPTOP_UNPUSHED_CHANGES_RISK=unknown`

不得宣称双机完全对齐。

---

## 十四、最终控制台输出格式

完成后只输出：

DESKTOP_ENVIRONMENT_AND_CODE_ALIGNMENT_AUDIT_READY

审计目录：
台式机环境状态：
Python版本：
OpenCV版本：
FFmpeg版本：
Edge-TTS版本：
zai-sdk版本：
pip check：
pytest结果：
Git远程地址：
台式机当前分支：
Desktop HEAD：
Origin Main：
Commit是否一致：
Tree是否一致：
工作区是否干净：
未提交关键文件数量：
未追踪关键文件数量：
追踪媒体数量：
疑似密钥追踪数量：
活动代码硬编码高风险数量：
台式机与GitHub状态：
笔记本证据是否存在：
笔记本与台式机状态：
DESKTOP_READY_FOR_NEXT_BATCH：
LAPTOP_UNPUSHED_CHANGES_RISK：
P0问题数量：
P1问题数量：
下一步唯一建议：
完整报告：

然后停止，等待Owner审阅。

---

## 十五、执行顺序

1. 验证Task；
2. 确认`spec_version=P13A-v1`；
3. 确认停止所有API认证和真实模型测试；
4. 创建审计输出目录；
5. 记录操作系统、PowerShell和设备信息；
6. 审计Git版本和配置；
7. 只读fetch远程引用；
8. 检查remote URL；
9. 比较Desktop HEAD与origin/main；
10. 比较commit与tree hash；
11. 审计工作区差异；
12. 生成追踪文件哈希清单；
13. 审计Git忽略和媒体防线；
14. 审计疑似密钥追踪风险；
15. 审计Python和虚拟环境；
16. 执行pip check；
17. 审计OpenCV、FFmpeg、Edge-TTS和zai-sdk；
18. 审计环境变量存在状态，不记录值；
19. 审计目录可写性；
20. 审计活动代码硬编码路径；
21. 从Agent目录运行全部本地测试；
22. 查找笔记本机器清单；
23. 有清单则执行跨设备哈希比较；
24. 无清单则生成笔记本清单导出命令；
25. 生成环境兼容性报告；
26. 生成跨设备对齐报告；
27. 生成分级修复计划；
28. 生成audit_summary.json；
29. 输出完成信号；
30. 停止等待Owner。

本任务的成功标准是形成可验证、不可伪造的台式机环境结论和跨设备代码对齐结论，而不是通过修改环境或代码强行制造“全部通过”。
