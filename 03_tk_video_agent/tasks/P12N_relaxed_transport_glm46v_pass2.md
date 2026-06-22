\# TASK：P12N\_RELAXED\_TEMPORARY\_TRANSPORT\_AND\_GLM46V\_PASS2



spec\_version: P12N-v1



\## 一、Owner 决定



Owner 决定调整 P12M 的安全口径。



当前视频代理属于低敏感度产品测试素材：



\* 时长约 2–4 秒；

\* 不包含原始音频；

\* 不包含客户信息；

\* 不包含个人身份信息；

\* 不包含账号凭证；

\* 不包含完整原片；

\* 仅用于 GLM-4.6V 动作理解 Calibration。



因此，本轮不再要求：



\* 私有 Bucket；

\* 预签名对象存储；

\* 智谱私有文件引用；

\* 长期远端存储；

\* 复杂远端生命周期系统。



Owner 明确接受：



在 Calibration 期间，通过随机、短时有效的临时公网 URL 暴露一份低清无声视频代理。



该授权仅适用于本次单个 Pass 2 测试样本。



\---



\## 二、任务目标



解决：



P12M\_SECURE\_VIDEO\_PROXY\_TRANSPORT\_REQUIRED\_batch\_20260617\_001



本任务只执行：



1\. 准备一份质量足够的视频动作代理；

2\. 通过 Cloudflare Quick Tunnel 临时暴露该文件；

3\. 使用 `video\_url` 调用智谱 `glm-4.6v`；

4\. 判断动作完整性、运动方向和产品状态变化；

5\. 请求完成后立即关闭临时 HTTP 服务和 Tunnel；

6\. 生成语义人工复核包；

7\. 停止在新的 Owner Gate。



本任务不得运行完整 Golden Pilot。



本任务不得生成新的成片视频。



\---



\## 三、项目与批次



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



上一个检查点：



P12M\_SECURE\_VIDEO\_PROXY\_TRANSPORT\_REQUIRED\_batch\_20260617\_001



现有代理：



C:\\Users\\43871\\AppData\\Local\\LFZ\_CODE\\agent-video-lab-233-laptop\\products\\dog\_stairs\_v1\\outputs\\agent\_factory\\batch\_20260617\_001\\p12m\_zhipu\_video\_proxy\_retest\\generated\_proxy\\batch2\_clip\_001\_5000\_7292\_360x640\_6fps\_noaudio.mp4



\---



\## 四、风险接受边界



Owner 接受以下有限风险：



\* 临时随机 URL 在 Tunnel 运行期间可被公网访问；

\* 代理内容会经过 Cloudflare 网络并由智谱服务器读取；

\* 该 URL 不具备用户身份认证。



但仍必须保持以下最低约束：



\* 只暴露一个随机命名的代理文件；

\* 不暴露目录索引；

\* 不暴露原片目录；

\* 不暴露项目目录；

\* 不暴露其他输出文件；

\* 不暴露 API Key；

\* 不暴露本机其他端口；

\* Tunnel 只在单次 VLM 调用期间存在；

\* 调用完成或失败后立即关闭；

\* 不在报告中保存完整临时 URL；

\* 不创建长期 Cloudflare Tunnel；

\* 不注册为 Windows 服务。



这是受控临时公开暴露，不是长期存储方案。



\---



\## 五、视频代理质量优先



现有代理为：



\* 360×640；

\* 6 fps；

\* 约 2.33 秒；

\* 约 80 KB；

\* H.264；

\* 无音频。



该代理可以作为最低可用版本。



为了避免过度压缩限制 GLM-4.6V 的动作理解，在原始候选窗口允许的情况下，优先重新生成一份质量更高的 Calibration 代理：



\* 时长：2–4 秒；

\* 分辨率：540×960；

\* 帧率：8 fps；

\* 编码：H.264；

\* 像素格式：yuv420p；

\* 音频：无；

\* 文件大小：不超过 5 MB；

\* 只包含目标动作；

\* 保持真实时间顺序；

\* 不插帧；

\* 不改变播放速度；

\* 不截断关键动作；

\* 不使用完整原片。



如果原素材无法安全生成 540×960，则使用现有 360×640 代理。



必须记录最终实际规格。



\---



\## 六、临时暴露目录



创建独立临时目录。



该目录内只能有一个文件：



随机 UUID 命名的视频代理。



例如：



`<uuid>.mp4`



禁止将以下目录作为 HTTP 根目录：



\* 项目根目录；

\* raw\_videos；

\* outputs 总目录；

\* 用户目录；

\* tasks 目录。



禁止开启目录列表。



HTTP 请求只能访问精确的视频文件路径。



如使用 Python HTTP Server，必须自定义或包装 Handler：



\* 禁止 directory listing；

\* 非目标文件返回 404；

\* 只允许 GET 和 HEAD；

\* 绑定 127.0.0.1；

\* 使用随机可用端口。



\---



\## 七、Cloudflare Quick Tunnel



优先检查：



`cloudflared`



如果未安装，允许从 Cloudflare 官方渠道安装或下载当前 Windows amd64 可执行文件。



不得：



\* 安装为 Windows 服务；

\* 创建 Cloudflare 账号配置；

\* 创建 Named Tunnel；

\* 创建永久 DNS；

\* 修改防火墙入站规则。



启动方式采用临时 Quick Tunnel，等价于：



`cloudflared tunnel --url http://127.0.0.1:<PORT>`



要求：



\* 使用随机 `trycloudflare.com` 地址；

\* Tunnel 仅在当前任务进程中运行；

\* 不在源码中写死 URL；

\* 不把完整 URL 写入 Git；

\* 报告中只记录 host hash、启动时间和关闭时间；

\* 不把 URL 输出到无关日志。



允许 Codex 在本次执行日志中临时读取完整 URL，以构建 `video\_url`。



\---



\## 八、外部可访问性验证



调用智谱前验证：



1\. HTTP 服务已启动；

2\. Tunnel 已启动；

3\. 精确视频 URL 返回 200；

4\. Content-Type 为视频类型；

5\. Content-Length 与代理大小一致；

6\. URL 无需登录即可由智谱服务器抓取；

7\. 根路径和其他随机路径不返回目录内容；

8\. 没有暴露其他文件。



只允许一次轻量 GET 或 HEAD 验证。



不得通过多个第三方扫描网站测试 URL。



\---



\## 九、唯一允许的 VLM 请求



本任务只允许：



\* 一个视频业务请求；

\* 最多一次参数兼容重试。



成功请求硬上限：



1



总尝试硬上限：



2



请求必须包含：



\* `provider = zhipu`

\* `model = glm-4.6v`

\* 一个 `video\_url`

\* 一个文本指令

\* `stream = false`

\* `do\_sample = false`

\* 如接口支持，关闭 thinking

\* 不包含图片

\* 不包含原片音频

\* 不包含完整原片



请求前必须断言：



`requested\_model == "glm-4.6v"`



响应后必须断言：



`response\_model == "glm-4.6v"`



不允许任何模型 fallback。



\---



\## 十、Pass 2 任务



GLM-4.6V 必须根据真实视频时序判断：



\* 视频中的主要主体；

\* 狗是否出现；

\* 产品是否出现；

\* 主要动作；

\* 动作开始；

\* 动作结束；

\* 动作是否完整；

\* 狗的运动方向；

\* 产品状态；

\* 产品状态是否变化；

\* 是否发生上楼；

\* 是否发生下楼；

\* 是否发生折叠；

\* 是否发生展开；

\* 是否存在稳定性证明；

\* 是否适合作为 demonstration；

\* 是否适合作为 outcome；

\* 是否适合作为 proof；

\* 可证明的 Claim；

\* 不可证明的 Claim；

\* 画面质量风险；

\* confidence；

\* 是否仍需人工复核。



必须允许模型诚实输出：



\* unknown；

\* incomplete；

\* low confidence；

\* insufficient evidence。



不得强迫模型给出不存在的动作结论。



\---



\## 十一、Prompt 策略



视频理解 Prompt 应使用清晰、直接的英文指令。



输出必须为 JSON-only。



继续复用 P12E 标签 Schema。



不得在本轮额外测试 Function Call。



不得增加第二次调用来尝试不同 Prompt，除非第一次属于明确的 API 参数或 JSON 格式错误。



不得为了得到满意答案反复调用。



\---



\## 十二、Schema 和语义校验



必须执行两层校验。



\### 第一层：结构校验



检查：



\* JSON 可解析；

\* 必填字段存在；

\* 枚举合法；

\* 时间字段合法；

\* 模型字段正确。



\### 第二层：语义人工复核准备



将以下内容放入同一审查包：



\* 本地视频代理；

\* contact sheet；

\* VLM JSON；

\* VLM 简短英文摘要；

\* VLM 中文摘要；

\* 动作完整性结论；

\* 运动方向；

\* 产品状态变化；

\* 可承担脚本角色；

\* claim\_evidence\_candidates；

\* confidence；

\* quality\_risks。



语义结果状态必须为：



`pending\_owner\_review`



不得由 Codex 自动宣告业务质量最终通过。



\---



\## 十三、调用后立即清理



无论成功或失败，都必须执行 finally 清理：



1\. 结束 Cloudflare Quick Tunnel；

2\. 结束本地 HTTP Server；

3\. 确认相关进程已经退出；

4\. 删除临时暴露目录中的代理副本；

5\. 保留项目 outputs 中的原始代理和审查包；

6\. 确认临时 URL 已不可访问。



清理失败必须在 Owner 报告中明确说明。



不得保留后台服务。



\---



\## 十四、费用和请求记录



必须记录：



\* request\_id

\* provider

\* requested\_model

\* response\_model

\* proxy\_duration\_ms

\* proxy\_width

\* proxy\_height

\* proxy\_fps

\* proxy\_size\_bytes

\* transport\_type

\* tunnel\_started\_at

\* tunnel\_stopped\_at

\* exposure\_duration\_seconds

\* input\_tokens

\* output\_tokens

\* total\_tokens

\* video\_tokens

\* latency\_ms

\* retry\_count

\* error\_code

\* cash\_charge\_status

\* resource\_pack\_deduction\_status



如果现金费用无法从响应确认：



`cash\_charge\_status = unknown`



不得伪造为 0。



\---



\## 十五、输出目录



输出到：



products/dog\_stairs\_v1/outputs/agent\_factory/batch\_20260617\_001/p12n\_glm46v\_pass2/



至少生成：



\* selected\_video\_proxy.json

\* temporary\_transport\_report.json

\* zhipu\_video\_request\_redacted.json

\* zhipu\_video\_result.json

\* zhipu\_video\_schema\_validation.json

\* zhipu\_video\_token\_usage.json

\* zhipu\_video\_semantic\_review.md

\* video\_proxy\_contact\_sheet.png



所有文件保持 Git ignored。



不得保存：



\* 完整临时 URL；

\* API Key；

\* Cloudflare 凭证；

\* 完整原片；

\* 原始音频。



\---



\## 十六、测试与 Git



如修改源码，运行：



1\. P12N focused tests；

2\. P12K VLM 回归；

3\. P12E Three Stage Compiler 回归；

4\. Owner Firewall 回归；

5\. Git Safety；

6\. 全量 unittest。



禁止：



\* `git add .`

\* force push

\* `git reset --hard`

\* 提交视频代理；

\* 提交 VLM 真实响应；

\* 提交临时 URL；

\* 提交 API Key；

\* 提交 outputs。



只允许选择性提交安全源码和测试。



\---



\## 十七、完成后的 Owner Gate



成功后创建：



`checkpoint\_id = P12N\_GLM46V\_PASS2\_REVIEW\_batch\_20260617\_001`



`checkpoint\_type = GATE\_GLM46V\_PASS2\_SEMANTIC\_REVIEW`



设置：



`awaiting\_owner\_review = true`



`pipeline\_status = BLOCKED\_BY\_OWNER\_GATE`



Codex 界面输出：



OWNER\_REVIEW\_REQUIRED



检查点编号：

Provider：

请求Model：

响应Model：

视频代理路径：

视频代理规格：

临时传输方式：

公网暴露持续时间：

Tunnel关闭结果：

HTTP服务关闭结果：

临时URL失效结果：

视频调用结果：

Schema结果：

识别的主要动作：

动作起止：

动作完整性：

狗运动方向：

产品状态：

产品状态变化：

Demonstration候选：

Outcome候选：

Proof候选：

可证明Claim：

不可证明Claim：

Confidence：

Quality Risks：

输入Token：

输出Token：

总Token：

现金费用状态：

人工复核包路径：

主要风险：



请选择：



A. Pass 2 语义准确，批准运行 Golden Pilot 全量标签，但暂不生成剪辑计划

B. Pass 2 基本准确，修订 Prompt 后只再测试一个视频样本

C. Pass 2 明显错误，暂停扩大调用并分析原因

D. 暂停视频标签，只运行 Pass 1 图片标签

E. 停止智谱 VLM 方向



Codex 必须给出推荐方案和理由。



Owner 未明确选择前不得：



\* 运行完整 Golden Pilot；

\* 生成 three\_stage\_plan；

\* 生成新成片；

\* 调用额外 VLM。



\---



\## 十八、执行顺序



1\. 验证本 Task；

2\. 确认 `spec\_version = P12N-v1`；

3\. 读取 P12K 和 P12M 结果；

4\. 检查 `ZAI\_API\_KEY`；

5\. 检查 `glm-4.6v` 严格绑定；

6\. 生成或选择质量足够的视频代理；

7\. 创建单文件临时暴露目录；

8\. 启动受限本地 HTTP Server；

9\. 启动 Cloudflare Quick Tunnel；

10\. 验证精确视频 URL；

11\. 执行一个 GLM-4.6V 视频请求；

12\. 校验响应模型和 JSON；

13\. 生成语义人工复核包；

14\. 立即关闭 Tunnel 和 HTTP Server；

15\. 删除临时暴露副本；

16\. 验证 URL 失效；

17\. 记录 Token、费用和暴露时间；

18\. 运行测试与 Git Safety；

19\. 如有安全源码修改，选择性 commit 和 push；

20\. 创建 P12N Owner Gate；

21\. 输出中文方案菜单；

22\. 停止等待 Owner。



本任务不得运行完整 Golden Pilot。



本任务不得生成新的成片视频。



