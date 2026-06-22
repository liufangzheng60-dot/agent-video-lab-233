\# TASK：P12M\_ZHIPU\_SECURE\_VIDEO\_PROXY\_TRANSPORT\_AND\_PASS2\_RETEST



spec\_version: P12M-v1



\## 一、Owner 决定



Owner 选择：



B. 配置安全视频代理传输后，只重测第 3 个 Pass 2 视频代理样本。



本任务只允许：



1\. 审计智谱 GLM-4.6V 当前支持的视频输入方式；

2\. 建立最小、安全、可删除的视频代理传输路径；

3\. 只重测 P12K 中被阻塞的第 3 个视频代理样本；

4\. 验证动作完整性、运动方向和产品状态变化；

5\. 生成 Owner Review Gate。



本任务不得：



\* 运行完整 Golden Pilot；

\* 重新调用已成功的两个图片样本；

\* 生成新视频成片；

\* 继续 P12D 剩余 9 条；

\* 自动发布；

\* 上传完整原片；

\* 上传原片音频；

\* 上传高分辨率母文件；

\* 使用公开网盘、公开图床或长期公开 URL；

\* 切换模型；

\* 使用模型 fallback。



\---



\## 二、项目与批次



项目根目录：



C:\\Users\\43871\\AppData\\Local\\LFZ\_CODE\\agent-video-lab-233-laptop



工作目录：



C:\\Users\\43871\\AppData\\Local\\LFZ\_CODE\\agent-video-lab-233-laptop\\03\_tk\_video\_agent



产品：



dog\_stairs\_v1



SKU：



khaki



素材批次：



batch\_20260617\_001



Provider：



zhipu



请求 Model：



glm-4.6v



API Endpoint：



https://open.bigmodel.cn/api/paas/v4/



上一个检查点：



P12K\_ZHIPU\_GLM46V\_CALIBRATION\_REVIEW\_batch\_20260617\_001



\---



\## 三、前置事实



P12K 已经完成：



\* 智谱 API 真实调用；

\* 请求模型严格为 glm-4.6v；

\* 响应模型严格为 glm-4.6v；

\* 两个低分辨率图片样本通过；

\* JSON-only 结构化输出通过；

\* Schema 通过 2 / 2；

\* 总 Token 为 1730；

\* 未发生模型 fallback；

\* 第 3 个视频代理样本因缺少安全传输通道而未调用。



本任务不得重复前两个图片调用。



如无法读取 P12K 报告，允许只读查找：



products/dog\_stairs\_v1/outputs/agent\_factory/batch\_20260617\_001/p12k\_zhipu\_glm46v\_calibration/



不得因为路径变化而重新调用图片样本。



\---



\## 四、唯一允许的模型与 Key



唯一允许：



provider = zhipu

model = glm-4.6v



每个请求前必须断言：



requested\_provider == "zhipu"

requested\_model == "glm-4.6v"



每个响应后必须断言：



response\_model == "glm-4.6v"



如响应模型：



\* 缺失；

\* 为空；

\* 不是 glm-4.6v；

\* 是 Flash、FlashX 或其他模型；



则：



pipeline\_status = BLOCKED\_BY\_MODEL\_MISMATCH



立即停止。



API Key 只能读取：



ZAI\_API\_KEY



不得：



\* 回显完整 Key；

\* 写入源码；

\* 写入 Task；

\* 写入日志；

\* 写入 JSON；

\* 写入 Git；

\* 写入远端存储元数据。



\---



\## 五、视频代理规格



只允许使用 P12K 已选定的第 3 个 Calibration 样本。



如代理尚未生成，可从对应原片时间窗口重新生成一次。



视频代理必须满足：



\* 时长：2–4 秒；

\* 分辨率：优先 360×640，最高 540×960；

\* 画幅：9:16；

\* 帧率：5–6 fps；

\* 编码：H.264；

\* 音频：无；

\* 文件大小目标：不超过 3 MB；

\* 只包含目标动作时间窗口；

\* 不得是完整原片；

\* 不得包含无关前后内容；

\* 写入 Git ignored outputs；

\* 使用确定性文件名；

\* 记录 source\_path、start\_ms、end\_ms；

\* 记录 SHA256 或已有 content\_hash；

\* raw\_videos 始终只读。



不得为了适配上传限制而破坏动作完整性。



\---



\## 六、安全传输方式优先级



Codex 必须按以下顺序探测，不得跳级。



\### 方案 1：智谱官方文件上传或私有文件引用



优先检查当前 `zai-sdk`、智谱通用 API 和官方文件 API 是否支持：



\* 上传当前低分辨率短视频代理；

\* 返回仅限当前账号访问的 file\_id、私有 URL 或可用于 `video\_url` / `file\_url` 的引用；

\* 请求完成后删除远端文件；

\* 不产生长期公开链接。



只有官方文档、SDK签名或真实能力探测明确支持时才允许使用。



不得把 Batch、知识库或文件解析专用上传接口，未经验证直接冒充 VLM 视频输入通道。



\### 方案 2：Owner 已有私有对象存储的预签名 URL



只有本机已存在 Owner 明确拥有的对象存储配置时才允许使用。



要求：



\* 私有 Bucket；

\* HTTPS；

\* 预签名 GET URL；

\* 有效期不超过 15 分钟；

\* 对象名称不包含产品敏感信息；

\* 禁止公开读；

\* 请求结束后立即删除远端对象；

\* 日志不得保存完整带签名 URL；

\* 报告只记录 URL 已脱敏；

\* 上传凭证不得进入 Git 或日志。



\### 方案 3：无安全通道时停止



如果方案 1 不可用，且没有 Owner 已批准的私有对象存储：



不得使用：



\* 百度网盘；

\* WPS 云盘；

\* Google Drive 公开链接；

\* GitHub；

\* 图床；

\* 临时公开文件分享服务；

\* ngrok 等公开隧道；

\* 本地局域网地址；

\* 长期公开 URL。



必须触发：



GATE\_SECURE\_VIDEO\_PROXY\_TRANSPORT



并输出具体方案菜单。



\---



\## 七、官方接口能力审计



执行真实视频请求前必须确认：



\* `glm-4.6v` 支持视频输入；

\* 当前接口使用 `video\_url`、`file\_url` 或官方可接受的文件引用；

\* 当前 SDK 的参数结构；

\* 单次请求不混合图片和视频；

\* 视频代理传输方式不是公开长期 URL；

\* 上传文件可以删除；

\* 上传及删除操作可审计；

\* `usage` 可记录；

\* 响应中包含或可读取 `model`；

\* 当前调用不会自动切换模型。



能力审计不得产生超过 1 次无意义探测请求。



\---



\## 八、唯一允许的真实业务请求



本任务只允许执行：



1 次视频代理 VLM 请求。



成功业务调用硬上限：



1



总请求尝试硬上限：



2



单请求最多重试：



1



请求必须：



\* 只包含一个短视频代理；

\* 不包含图片；

\* 不包含原始音频；

\* 不包含完整原片；

\* `model = glm-4.6v`；

\* `stream = false`；

\* `do\_sample = false`；

\* 如支持，关闭 thinking；

\* 使用现有 P12E 标签 Schema；

\* 使用 JSON-only Prompt 或已验证的结构化策略。



\---



\## 九、Pass 2 语义目标



本次必须判断：



\* primary\_action

\* secondary\_action

\* action\_start

\* action\_end

\* action\_completeness

\* dog\_present

\* dog\_identity

\* dog\_motion\_direction

\* product\_present

\* product\_state

\* product\_state\_change

\* product\_visibility

\* camera\_motion

\* room\_or\_scene

\* safe\_vertical\_crop

\* demonstration\_candidate

\* outcome\_candidate

\* proof\_candidate

\* claim\_evidence\_candidates

\* quality\_risks

\* confidence

\* requires\_video\_review



必须明确区分：



\* 完整动作；

\* 动作片段；

\* 动作开始但未结束；

\* 动作结束但缺少起点；

\* 无法判断。



不得在证据不足时默认写：



action\_completeness = complete



低置信度必须真实返回，不得伪造高置信度。



\---



\## 十、结构化输出与 Schema



继续使用 P12E 已有 Schema。



优先使用 P12K 已验证的 JSON-only 策略。



本任务不得为了测试 Function Call 再增加额外请求。



Schema 失败时：



\* 允许在同一重试预算内进行一次结构修复请求；

\* 第二次仍失败则本样本失败。



禁止：



\* 正则静默补齐字段；

\* 自动填默认值后标记 Pass；

\* Mock 冒充真实输出；

\* 非法 JSON 进入正式 Asset Ledger；

\* 仅因 JSON 合法就判断语义正确。



\---



\## 十一、语义人工复核包



VLM 返回后必须生成一个人工复核包，至少包含：



\* 代理视频本地路径；

\* 代理视频 contact sheet；

\* 原片 source\_path；

\* start\_ms；

\* end\_ms；

\* VLM 原始语义摘要；

\* 结构化 JSON；

\* action\_completeness；

\* dog\_motion\_direction；

\* product\_state\_change；

\* demonstration / outcome / proof 判断；

\* confidence；

\* quality\_risks；

\* requested\_model；

\* response\_model；

\* request\_id；

\* Token；

\* 延迟。



语义结果必须标记：



semantic\_validation\_status = pending\_owner\_review



Codex 不得仅凭自身判断将语义质量标记为最终通过。



\---



\## 十二、远端文件生命周期



如使用远端文件或对象存储：



1\. 上传代理；

2\. 获取短时效引用；

3\. 调用 GLM-4.6V；

4\. 保存脱敏请求记录；

5\. 删除远端对象；

6\. 验证删除成功；

7\. 不保留长期可访问 URL。



如删除失败：



remote\_cleanup\_status = fail



必须输出风险并停止。



日志不得保存完整预签名 URL。



\---



\## 十三、调用与费用记录



必须记录：



\* requested\_provider

\* requested\_model

\* response\_model

\* request\_id

\* transport\_type

\* remote\_object\_created

\* remote\_object\_deleted

\* proxy\_size\_bytes

\* proxy\_duration\_ms

\* input\_tokens

\* output\_tokens

\* total\_tokens

\* video\_tokens

\* latency\_ms

\* retry\_count

\* error\_code

\* cash\_charge\_status

\* resource\_pack\_deduction\_status



如无法读取现金费用：



cash\_charge\_status = unknown



不得伪造为 0。



本任务不得因费用未知而自动扩大调用。



\---



\## 十四、错误处理



\### 401 / 403



\* 不重试；

\* 停止；

\* 输出鉴权或模型权限问题。



\### 400



\* 仅允许修正一次普通参数或输入格式问题；

\* 不得切换模型；

\* 不得改用完整原片；

\* 不得扩大上传范围。



\### 429 / 5xx



\* 最多退避重试一次；

\* 不得无限重试。



\### 视频传输失败



不得自动改为公开链接。



必须触发 Owner Gate。



\---



\## 十五、输出目录



输出到：



products/dog\_stairs\_v1/outputs/agent\_factory/batch\_20260617\_001/p12m\_zhipu\_video\_proxy\_retest/



至少生成：



\* secure\_transport\_capability\_report.json

\* selected\_video\_proxy.json

\* remote\_transport\_ledger.json

\* zhipu\_video\_request.json

\* zhipu\_video\_result.json

\* zhipu\_video\_schema\_validation.json

\* zhipu\_video\_token\_usage.json

\* zhipu\_video\_semantic\_review.md

\* video\_proxy\_contact\_sheet.png



全部保持 Git ignored。



报告不得包含：



\* API Key；

\* 完整预签名 URL；

\* 远端存储密钥；

\* 完整原片；

\* 原始音频。



\---



\## 十六、测试与 Git



如修改源码，必须依次运行：



1\. P12M focused tests；

2\. P12K VLM 回归；

3\. P12E Three Stage Compiler 回归；

4\. Owner Firewall 回归；

5\. Git Safety；

6\. 全量 unittest。



禁止：



\* `git add .`

\* force push

\* `git reset --hard`

\* 提交媒体；

\* 提交代理视频；

\* 提交真实 VLM 响应原文；

\* 提交远端 URL；

\* 提交 API Key；

\* 提交 outputs。



只允许选择性提交安全源码、测试和配置模板。



\---



\## 十七、完成后的 Owner Gate



如视频请求成功，创建：



checkpoint\_id = P12M\_ZHIPU\_PASS2\_VIDEO\_REVIEW\_batch\_20260617\_001



checkpoint\_type = GATE\_ZHIPU\_PASS2\_VIDEO\_REVIEW



设置：



awaiting\_owner\_review = true

pipeline\_status = BLOCKED\_BY\_OWNER\_GATE



Codex 必须使用简体中文输出：



OWNER\_REVIEW\_REQUIRED



检查点编号：

Provider：

请求Model：

响应Model：

视频代理路径：

视频代理时长：

视频代理分辨率：

视频代理大小：

安全传输方式：

远端对象删除结果：

视频调用成功/失败：

Schema结果：

识别的主要动作：

动作起止：

动作完整性：

狗运动方向：

产品状态变化：

Demonstration候选：

Outcome候选：

Proof候选：

Confidence：

Quality Risks：

实际请求次数：

输入Token：

输出Token：

总Token：

视频Token：

现金费用状态：

人工复核包路径：

主要风险：



请选择：



A. Pass 2 语义正确，批准运行 Golden Pilot 全量标签，但暂不生成剪辑计划

B. Pass 2 基本正确，先修订视频 Prompt / Schema 后再测一次

C. Pass 2 语义错误，停止扩大 VLM 调用并分析原因

D. 视频传输不稳定，改为只运行 Pass 1 图片标签

E. 停止智谱 VLM 方向



Codex 必须给出推荐方案和理由。



Owner 未明确选择前，不得：



\* 运行完整 Golden Pilot；

\* 生成 three\_stage\_plan；

\* 生成新视频；

\* 调用额外 VLM；

\* 自动发布。



\---



\## 十八、无安全传输通道时的 Gate



如果不能建立安全视频传输，创建：



checkpoint\_id = P12M\_SECURE\_VIDEO\_PROXY\_TRANSPORT\_REQUIRED\_batch\_20260617\_001



checkpoint\_type = GATE\_SECURE\_VIDEO\_PROXY\_TRANSPORT



输出：



OWNER\_ACTION\_REQUIRED



已验证的官方输入方式：

官方文件上传是否可用于VLM：

是否存在Owner私有对象存储：

阻塞原因：

已生成代理文件：

代理大小和时长：

未上传的数据：

当前费用：



请选择：



A. 配置Owner私有对象存储和15分钟预签名URL

B. 使用智谱官方支持的私有文件上传引用

C. 暂停Pass 2，仅运行Pass 1图片标签

D. 停止VLM方向



未收到 Owner 选择前不得上传代理。



\---



\## 十九、执行顺序



现在执行：



1\. 验证本 Task 完整；

2\. 确认 `spec\_version = P12M-v1`；

3\. 读取 P12K 结果；

4\. 确认两个图片样本不重复调用；

5\. 检查 `ZAI\_API\_KEY`；

6\. 检查 `glm-4.6v` 严格绑定；

7\. 确定第 3 个视频样本；

8\. 生成或验证 2–4 秒低清无声视频代理；

9\. 审计智谱官方安全视频输入能力；

10\. 优先验证官方私有文件引用；

11\. 如已有 Owner 私有对象存储，则使用短时效预签名 URL；

12\. 如无安全通道，创建 Transport Owner Gate 并停止；

13\. 如安全通道成立，执行最多 1 次视频业务请求；

14\. 校验响应模型；

15\. 校验 Schema；

16\. 生成语义人工复核包；

17\. 删除远端代理对象；

18\. 记录 Token、费用和传输生命周期；

19\. 运行测试与 Git Safety；

20\. 如有安全源码修改，选择性 commit 和 push；

21\. 创建 P12M Owner Gate；

22\. 输出中文方案菜单；

23\. 停止等待 Owner。



本任务不得运行完整 Golden Pilot。



本任务不得生成新视频成片。



