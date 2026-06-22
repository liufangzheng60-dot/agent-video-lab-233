\# TASK：P12K\_ZHIPU\_GLM46V\_THREE\_SAMPLE\_CALIBRATION



spec\_version: P12K-v1



\## 一、任务目标



智谱 GLM-4.6V API 与模型绑定验证已经完成。



现在正式执行最多 3 个代表性样本的真实 Calibration，用于验证：



1\. 关键帧条带视觉理解；

2\. 狗和产品动作识别；

3\. 低帧率短视频代理理解；

4\. P12E 资产标签 Schema；

5\. Function Call 或 JSON-only 结构化输出；

6\. 缓存与幂等；

7\. Token、延迟和费用记录；

8\. 是否具备进入完整 Golden Pilot 标签阶段的条件。



本任务完成后必须停在 Owner Gate。



本任务不得直接运行完整 Golden Pilot，不得生成新视频。



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



Model：



glm-4.6v



API Endpoint：



https://open.bigmodel.cn/api/paas/v4/



\---



\## 三、前置条件



执行前必须确认：



\* `ZAI\_API\_KEY` 当前进程可读取；

\* API Key 不得回显；

\* `zai-sdk` 可导入；

\* `ZhipuAiClient` 可用；

\* 请求模型为 `glm-4.6v`；

\* 响应模型为 `glm-4.6v`；

\* 不存在模型 fallback；

\* 不存在 Gemini、Flash 或 FlashX 路径；

\* 之前的模型绑定验证结果为 pass。



如果无法找到之前的绑定验证报告，允许执行一次只读状态检查，但不得重新产生公开图片验证费用。



如果请求模型或响应模型不是 `glm-4.6v`：



pipeline\_status = BLOCKED\_BY\_MODEL\_MISMATCH



立即停止。



\---



\## 四、复用现有架构



优先复用：



\* helpers/vlm\_qc\_gate.py

\* 现有 Zhipu Provider Adapter

\* 现有 Provider 抽象

\* P12E 资产候选窗口

\* P12E 关键帧条带

\* P12E 低帧率短视频代理

\* 现有标签 Schema

\* 现有缓存系统

\* 现有预算和 usage 记录

\* Owner Firewall

\* agent\_state

\* automated\_asset\_ledger 结构



禁止创建第二套：



\* Provider 框架；

\* API Key 系统；

&#x20; -缓存系统；

\* Schema；

\* Budget 系统；

\* Owner Gate；

\* 状态主权。



\---



\## 五、允许处理的三个样本



必须从现有 Golden Pilot 候选中确定性选择。



不得使用随机抽样。



\### 样本 1：静态产品关键帧条带



选择标准：



\* 产品清楚可见；

\* 产品状态明确；

\* 画面质量较好；

\* 不依赖动作连续性判断。



验证字段：



\* product\_present

\* product\_state

\* product\_visibility

\* shot\_scale

\* room\_or\_scene

\* safe\_vertical\_crop

\* segment\_role\_candidates

\* confidence



\### 样本 2：狗实际使用关键帧条带



选择标准：



\* 狗清楚可见；

\* 产品同时出现；

\* 能看到上楼、下楼或使用结果；

\* 与样本 1 不重复。



验证字段：



\* dog\_present

\* dog\_identity

\* dog\_motion\_direction

\* primary\_action

\* product\_present

\* product\_state

\* usage 或 outcome 候选资格

\* action\_completeness

\* confidence



\### 样本 3：低帧率短视频代理



选择标准：



\* 动作连续；

\* 能验证上楼、下楼、折叠、展开或稳定性；

\* 时长 2–4 秒；

\* 不包含原始音频；

\* 低分辨率；

\* 不上传完整原片。



验证字段：



\* action\_start

\* action\_end

\* action\_completeness

\* dog\_motion\_direction

\* product\_state\_change

\* demonstration 候选资格

\* outcome 候选资格

\* proof 候选资格

\* quality\_risks

\* confidence



如果当前接口无法安全传输短视频代理：



不得上传完整原片。



必须创建：



GATE\_SECURE\_VIDEO\_PROXY\_TRANSPORT



并给 Owner 提供方案。



\---



\## 六、请求分离规则



单次请求不得混合图片与视频。



\### Pass 1 图片请求



只允许包含：



\* image\_url 或平台支持的图片输入；

\* text；

\* 单个关键帧条带；

\* 对应基础元数据。



\### Pass 2 视频请求



只允许包含：



\* video\_url、官方文件上传引用或平台支持的视频输入；

\* text；

\* 单个低帧率短视频代理。



禁止：



\* 同一请求同时包含 image\_url 和 video\_url；

\* 上传完整原片；

\* 上传原片音频；

\* 上传高分辨率母文件；

\* 上传 Golden Pilot 之外素材。



\---



\## 七、调用与重试限制



硬限制：



\* max\_successful\_business\_calls = 3

\* max\_total\_request\_attempts = 6

\* max\_retry\_per\_request = 1

\* request\_timeout\_sec = 180

\* upload\_audio = false

\* stream = false

\* cache\_enabled = true



错误规则：



\### 401 / 403



\* 不重试；

\* 标记 Key、权限或模型访问问题；

\* 立即停止。



\### 400



\* 普通参数兼容问题允许修复一次；

\* 不得更换模型；

\* 不得扩大上传范围。



\### 429 / 5xx



\* 最多退避重试一次；

\* 不得无限重试。



每个真实请求前必须再次断言：



requested\_provider == "zhipu"

requested\_model == "glm-4.6v"



每个响应后必须断言：



response\_model == "glm-4.6v"



\---



\## 八、结构化输出策略



优先级：



1\. 多模态 Function Call；

2\. Function Call 不可用时使用 JSON-only Prompt；

3\. 使用现有 Pydantic 或 Schema Validator 本地验证。



Schema 失败：



\* 允许一次结构修复请求；

\* 第二次仍失败则该样本失败。



禁止：



\* 正则静默补字段；

\* 自动填默认值后标记 pass；

\* Mock 结果冒充真实标签；

\* 非法 JSON 写入正式账本；

\* VLM 直接生成 Timeline；

\* VLM 修改三段式商业脚本；

\* VLM 决定发布。



必须保留字段：



\* clip\_id

\* start\_ms

\* end\_ms

\* primary\_action

\* secondary\_action

\* dog\_present

\* dog\_identity

\* dog\_motion\_direction

\* product\_present

\* product\_state

\* product\_visibility

\* shot\_scale

\* camera\_motion

\* room\_or\_scene

\* action\_completeness

\* safe\_vertical\_crop

\* hook\_strength

\* emotional\_tone

\* segment\_role\_candidates

\* claim\_evidence\_candidates

\* continuity\_keys

\* quality\_risks

\* requires\_video\_review

\* confidence

\* provider

\* model

\* schema\_version



segment\_role\_candidates 只能使用 P12E 已定义角色。



\---



\## 九、缓存和幂等



缓存键必须包含：



\* asset\_hash

\* window\_start\_ms

\* window\_end\_ms

\* prompt\_schema\_version

\* provider

\* model

\* media\_resolution

\* proxy\_version



同一成功缓存键：



\* 不得再次上传；

\* 不得再次调用；

\* 不得再次扣费；

\* 不得因为重新执行 Task 而重复请求。



缓存必须原子写入：



1\. 写临时文件；

2\. flush；

3\. fsync；

4\. os.replace。



缓存验证必须通过本地查找完成。



不得为了测试缓存再次发送收费请求。



\---



\## 十、质量判断



\### 样本 1 通过标准



\* 产品存在判断正确；

\* 产品状态合理；

\* 景别合理；

\* 场景合理；

\* 脚本角色候选合法；

\* Schema 通过。



\### 样本 2 通过标准



\* 狗存在判断正确；

\* 产品同时识别；

\* 动作方向合理；

\* 使用角色合理；

\* action\_completeness 不得伪造高置信度；

\* Schema 通过。



\### 样本 3 通过标准



\* 视频输入成功；

\* 动作起止判断合理；

\* 动作完整性判断合理；

\* 产品状态变化判断合理；

\* Outcome、Demonstration 或 Proof 分类具有依据；

\* Schema 通过。



整体通过要求：



\* 三个样本中至少两个成功；

\* 两个图片样本必须成功；

\* 视频样本成功，或明确触发安全传输 Gate；

\* response\_model 全部严格为 glm-4.6v；

\* 未上传未授权素材；

\* 未产生未授权模型调用；

\* 未调用 fallback；

\* usage 可以记录；

\* 缓存正常；

\* 无 Schema 静默修复。



\---



\## 十一、费用与资源记录



每个请求记录：



\* request\_id

\* requested\_provider

\* requested\_model

\* response\_model

\* request\_type

\* input\_tokens

\* output\_tokens

\* total\_tokens

\* image\_tokens

\* video\_tokens

\* cached\_tokens

\* latency\_ms

\* retry\_count

\* resource\_pack\_before

\* resource\_pack\_after

\* cash\_charge

\* error\_code



如果无法确认现金费用：



cash\_charge\_status = unknown



不得伪造为 0。



如果发现明显套餐外扣费风险：



pipeline\_status = BLOCKED\_BY\_BUDGET\_SAFETY



停止后续调用。



\---



\## 十二、输出产物



全部写入 Git ignored 的：



products/dog\_stairs\_v1/outputs/agent\_factory/batch\_20260617\_001/p12k\_zhipu\_glm46v\_calibration/



至少生成：



\* selected\_calibration\_samples.json

\* zhipu\_calibration\_requests.json

\* zhipu\_calibration\_results.json

\* zhipu\_model\_binding\_report.json

\* zhipu\_schema\_validation\_report.json

\* zhipu\_cache\_report.json

\* zhipu\_token\_usage\_report.json

\* zhipu\_calibration\_review.md



报告不得包含完整 API Key。



报告必须包含每个样本的：



\* source 文件；

\* 时间范围；

\* 代理文件；

\* 请求类型；

\* requested\_model；

\* response\_model；

\* 标签结果；

\* Schema 结果；

\* confidence；

\* Token；

\* 延迟；

\* 费用状态；

\* 是否通过。



\---



\## 十三、测试与 Git



如修改源码，依次运行：



1\. P12K focused tests；

2\. P12E/P12H/P12J VLM 回归；

3\. Three Stage Compiler 回归；

4\. Owner Firewall 回归；

5\. Git Safety；

6\. 全量 unittest。



禁止：



\* git add .

\* force push

\* reset --hard

\* 提交 API Key

\* 提交媒体

\* 提交 VLM 代理

\* 提交真实 VLM 响应原文

\* 提交 outputs



只允许选择性提交安全源码、测试和必要配置模板。



\---



\## 十四、完成后的 Owner Gate



创建：



checkpoint\_id = P12K\_ZHIPU\_GLM46V\_CALIBRATION\_REVIEW\_batch\_20260617\_001



checkpoint\_type = GATE\_ZHIPU\_GLM46V\_CALIBRATION\_REVIEW



设置：



awaiting\_owner\_review = true

pipeline\_status = BLOCKED\_BY\_OWNER\_GATE



Codex 必须在界面用简体中文输出：



OWNER\_REVIEW\_REQUIRED



检查点编号：

Provider：

请求Model：

响应Model：

模型绑定结果：

SDK版本：

API Key鉴权结果：

Calibration样本数量：

图片调用成功/失败：

视频调用成功/失败：

Function Call可用性：

最终结构化输出方式：

Schema成功率：

产品状态识别结果：

狗使用动作识别结果：

动作完整性判断结果：

脚本角色判断结果：

低置信度样本：

缓存结果：

实际请求次数：

输入Token：

输出Token：

总Token：

图片Token：

视频Token：

资源包扣减：

现金费用状态：

平均请求延迟：

失败与重试：

报告路径：

主要风险：



请选择：



A. Calibration通过，批准使用glm-4.6v运行完整Golden Pilot标签

B. 只批准运行Pass 1关键帧标签

C. 指定错误标签并修订Prompt后重新Calibration

D. 配置或修复视频代理传输后重新测试Pass 2

E. 停止智谱VLM方向



Codex必须给出推荐方案和理由。



Owner未明确选择前不得：



\* 运行完整Golden Pilot；

\* 生成three\_stage\_plan；

\* 生成新视频；

\* 调用额外VLM；

\* 继续剩余9条；

\* 自动发布。



\---



\## 十五、执行顺序



现在执行：



1\. 完整读取本 Task；

2\. 确认 spec\_version = P12K-v1；

3\. 检查 P12J 模型绑定结果；

4\. 检查 ZAI\_API\_KEY；

5\. 检查 zai-sdk；

6\. 检查 glm-4.6v Provider 配置；

7\. 确认无模型 fallback；

8\. 确定性选择三个 Calibration 样本；

9\. 生成必要关键帧条带和一个低帧率视频代理；

10\. 分别执行图片和视频请求；

11\. 校验 response\_model；

12\. 校验 Schema；

13\. 验证缓存与幂等；

14\. 记录 Token、延迟和费用；

15\. 生成 Calibration 报告；

16\. 运行测试和 Git Safety；

17\. 如有安全源码修改，选择性 commit 并 push；

18\. 创建 P12K Owner Gate；

19\. 输出中文方案菜单；

20\. 停止等待 Owner。



本任务不得运行完整 Golden Pilot。



本任务不得生成新视频。



