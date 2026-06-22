\# TASK：P12Y\_TIKTOK\_12\_VIDEO\_PRODUCTION\_BATCH



spec\_version: P12Y-v1



\## 一、任务定位



本任务从研发验证阶段正式进入第一轮TikTok前台生产测试。



当前目标不是继续重构算法，也不是继续证明Beam Search、OpenCV或VLM的理论能力。



当前目标是：



> 基于Owner已经看过并认可的P12W与P12X-v2版本，快速、稳定地生产12条可供TikTok前台手动发布的视频，用真实播放数据验证内容方向。



本任务必须输出12条最终MP4成片。



发布操作始终由Owner在TikTok前台手动完成。



本任务不得设计、开发或执行自动发布。



\---



\## 二、最高价值公式



继续执行：



`系统价值 = 成片质量 × 产出速度 ÷ 开发与调用成本`



本轮优先级：



1\. 12条能够真实发布；

2\. 无人手、鬼畜、冻结、逻辑错误；

3\. 每组A/B只测试一个主要变量；

4\. 充分发挥VLM的候选理解和完整视频比较能力；

5\. 不再进行大规模架构重构；

6\. 不为了使用更多Token而使用Token；

7\. 不以节省Token作为最高目标；

8\. 以单位Token带来的有效质量提升最大化为VLM底层策略。



除非Owner后续明确修改，该VLM策略持续有效。



\---



\## 三、Owner最终审片结论



\### V1A



\* P12X-v2与P12W几乎无明显变化；

\* 无人手或逻辑回归；

\* 构图无损；

\* P12W/P12X均可通过；

\* 生产控制组使用P12W。



\### V1B



\* P12X-v2与P12W视觉等价；

\* 无鬼畜或异常帧；

\* Hook与Closure保持；

\* 生产控制组使用P12W。



\### V2A



\* P12X-v2不优于P12W；

\* 未形成完整的“接触—过程—结果”Proof；

\* 存在碎片化和无意义快切；

\* 构图弱于P12W；

\* 最后一个画面出现人手，导致剪辑风格割裂；

\* 最终必须保留P12W；

\* P12X-v2 V2A最后人手画面必须作为Owner确认的负样本加入排除区间。



\### V2B



\* P12X-v2前2秒跳跃得到改善；

\* 总体效果可用；

\* 生产基线采用P12X-v2。



\### V3A



\* P12X-v2与P12W差异不大；

\* 画面丰富度可以感知；

\* 无过度剪辑；

\* 生产基线采用P12X-v2。



\### V3B



\* P12X-v2整体与P12W等价；

\* P12X-v2 Hook更好；

\* 无新增污染和逻辑回归；

\* 生产基线采用P12X-v2。



\---



\## 四、六条生产母版锁定



以下版本为本轮12条生产视频的母版：



| 视频家族                     | 生产母版    |

| ------------------------ | ------- |

| V1A Pain Solution        | P12W    |

| V1B Pain Solution        | P12W    |

| V2A Feature Proof        | P12W    |

| V2B Structure Proof      | P12X-v2 |

| V3A Lifestyle Value      | P12X-v2 |

| V3B Transformation Value | P12X-v2 |



母版目录：



\### P12W



`products/dog\_stairs\_v1/outputs/renders/batch\_20260617\_001/P12W\_opencv\_ffmpeg\_vlm\_asymmetric\_vision\_compiler`



\### P12X-v2



`products/dog\_stairs\_v1/outputs/renders/batch\_20260617\_001/P12X\_v2\_cinematic\_global\_search\_with\_guardrails`



任何生产实验版本不得低于对应母版。



\---



\## 五、12条视频的业务实验矩阵



本轮采用：



`6个内容家族 × 每个家族2个版本 = 12条视频`



每组由：



\* A：Control控制组；

\* B：Single-Variable Variant单变量实验组；



组成。



不得在同一个B版本中同时大改Hook、Core、Closure、口播和节奏。



否则前台数据无法判断究竟是哪一个变量产生效果。



\---



\## 六、12条视频文件规划



输出文件：



1\. `01\_V1A\_control\_P12Y.mp4`

2\. `02\_V1A\_hook\_variant\_P12Y.mp4`

3\. `03\_V1B\_control\_P12Y.mp4`

4\. `04\_V1B\_core\_rhythm\_variant\_P12Y.mp4`

5\. `05\_V2A\_control\_P12Y.mp4`

6\. `06\_V2A\_proof\_coverage\_variant\_P12Y.mp4`

7\. `07\_V2B\_control\_P12Y.mp4`

8\. `08\_V2B\_hook\_bridge\_variant\_P12Y.mp4`

9\. `09\_V3A\_control\_P12Y.mp4`

10\. `10\_V3A\_lifestyle\_closure\_variant\_P12Y.mp4`

11\. `11\_V3B\_control\_P12Y.mp4`

12\. `12\_V3B\_hook\_variant\_P12Y.mp4`



\---



\## 七、控制组处理原则



六条Control必须使用Owner已确认的生产母版。



如果控制组内容、音轨、尺寸和编码规格均无需改变：



\* 优先执行文件级无损复制；

\* 不得为了生成新文件名进行无意义二次编码；

\* 在输出目录生成独立文件；

\* 在报告中标记：



&#x20; \* `control\_source`

&#x20; \* `lossless\_copy=true`

&#x20; \* SHA256。



六条控制组对应：



\* 01：P12W V1A；

\* 03：P12W V1B；

\* 05：P12W V2A；

\* 07：P12X-v2 V2B；

\* 09：P12X-v2 V3A；

\* 11：P12X-v2 V3B。



\---



\## 八、六条实验组变量



\### 8.1 V1A Hook Variant



保持：



\* P12W Core；

\* P12W Closure；

\* 原商业逻辑；

\* 原口播主张。



只允许优化：



\* 0–3秒Hook；

\* Pain到Intervention的视觉建立。



目标：



\* 更快建立小型犬上下家具痛点；

\* 允许2–3个视觉Beat；

\* 不允许出现人手；

\* 不得破坏后续逻辑。



\---



\### 8.2 V1B Core Rhythm Variant



保持：



\* 原Hook；

\* 原Closure；

\* 原痛点解决逻辑。



只允许优化：



\* 3–12秒Core的景别和节奏；

\* 最多增加2个视觉单元；

\* 必须保持动作完整；

\* 不得复用P12U鬼畜素材。



目标：



\* 比控制组更有视觉层次；

\* 但不产生碎片化。



\---



\### 8.3 V2A Proof Coverage Variant



这是本轮重点实验组。



保持：



\* P12W Hook；

\* P12W整体构图风格；

\* 原功能主张。



实验目标必须形成：



`脚掌接触`

→ `身体稳定行进`

→ `成功到达或稳定结果`



禁止：



\* 使用P12X-v2 V2A最后出现人手的画面；

\* 使用任何与该Owner确认人手区间重叠超过50ms的候选；

\* 仅展示接触而没有过程；

\* 仅展示过程而没有结果；

\* 为增加镜头数量切碎完整动作。



如果无法形成完整三段Proof：



保留P12W控制组逻辑，选择其他安全单变量，例如更清楚的材质特写，不得强行拼接。



\---



\### 8.4 V2B Hook Bridge Variant



保持：



\* P12X-v2结构证明Core；

\* 后续Proof；

\* Closure；

\* 产品状态顺序。



只允许优化：



\* 前0–2.5秒；

\* 切点；

\* 桥接镜头；

\* 主体位置和构图连续性。



优先级：



1\. 调整现有切点；

2\. 增加短桥接镜头；

3\. 最后才允许替换Hook素材。



不得重新引入P12U的人手、鬼畜或逻辑倒置。



\---



\### 8.5 V3A Lifestyle Closure Variant



保持：



\* P12X-v2现有Core；

\* 已被Owner认可的画面丰富度；

\* 原使用逻辑。



只允许优化：



\* Lifestyle Payoff；

\* 最后3–5秒Closure；

\* 产品、狗和家居之间的关系。



目标：



\* 情绪更完整；

\* 家居价值更清楚；

\* 不重新开启新动作；

\* 不得为了氛围插入无关镜头。



\---



\### 8.6 V3B Hook Variant



保持：



\* P12X-v2更好的Hook方向；

\* Transformation Core；

\* 与V3A不同的商业表达；

\* 原Closure。



只允许优化：



\* 0–3秒Hook的冲突或变化悬念；

\* 初始状态到Transformation的视觉承接。



不得：



\* 与V3A使用相同Core；

\* 重复展示同一Transformation动作；

\* 出现人手污染；

\* 破坏2-in-1变化逻辑。



\---



\## 九、画面丰富度目标



本轮不强制每条达到固定镜头数量。



\### 控制组



保持原母版视觉单元数量。



\### 实验组



目标视觉单元：



\* 最低：6个；

\* 推荐：6–9个；

\* 最高：10个。



完整动作优先于镜头数量。



Hook允许：



\* 2–3个视觉Beat；

\* 单个常规Beat不短于350ms；

\* 最多一个250–350ms冲击镜头。



Core允许：



\* 每个语义状态1–2个镜头；

\* 只有明确Coverage缺口时允许3个；

\* 不得每个词切一刀。



Closure允许：



\* 1–2个镜头；

\* 不得重新开始新的动作链。



\---



\## 十、VLM底层策略



后续VLM策略固定为：



`VLM Quality-Efficiency Maximization`



含义：



\* 不以调用最少为目标；

\* 不以Token最低为目标；

\* 不以调用越多越好为目标；

\* 以每次调用是否减少错误、改善候选排序或提升最终成片为目标；

\* VLM必须在最擅长的商业语义、动作理解、完整视频比较和画面丰富度判断中充分参与。



OpenCV、Python和FFmpeg硬门仍然保留。



VLM不得覆盖：



\* 冻结；

\* 重复帧；

\* PTS异常；

\* 鬼畜；

\* 非法叙事状态；

\* 时间区间黑名单；

\* 动作截断；

\* 画幅失败。



\---



\## 十一、每组必须完成三阶段VLM决策



六个A/B视频家族，每组至少完成以下三个决策阶段。



不得只进行一次最终Contact Sheet确认。



\### Stage 1：候选语义与风险深审



每个实验目标Slot：



\* 检索8–16个候选；

\* 本地硬门过滤后；

\* 向VLM展示3–6个最强候选。



输入必须包括：



\* 带时间码Contact Sheet；

\* 2–8秒视频代理；

\* 当前口播；

\* 当前视觉角色；

\* 前后相邻镜头；

\* OpenCV物理摘要。



输出：



\* visual\_role

\* action\_phase

\* hand\_present

\* violation\_interval

\* composition\_quality

\* claim\_evidence

\* coverage\_value

\* narrative\_fit

\* temporal\_naturalness

\* reject\_reason

\* evidence\_timestamp

\* confidence



\---



\### Stage 2：三套实验方案比较



每个B版本至少生成：



\* Option A：母版保留；

\* Option B：保守单变量增强；

\* Option C：更丰富单变量增强。



VLM必须比较三套低分辨率完整视频代理。



不得只比较Contact Sheet。



必须返回：



\* ranking

\* winner

\* visual\_richness

\* narrative\_logic

\* composition

\* action\_completeness

\* proof\_strength

\* over\_editing\_risk

\* visual\_hygiene

\* evidence\_timestamps

\* recommended\_local\_change

\* confidence



\---



\### Stage 3：Control与Variant最终A/B审查



最终必须比较：



\* A：Control；

\* B：准备交付的Variant。



必须判断：



\* Variant是否真的测试了单一变量；

\* Variant是否明显更丰富；

\* 是否破坏构图；

\* 是否破坏逻辑；

\* 是否出现人手；

\* 是否出现碎片化；

\* 是否值得进入前台测试。



如果Variant没有明确改善：



允许继续输出，但必须标记：



`experimental\_confidence=low`



并在发布清单中排到较后顺序。



如果Variant存在硬质量回归：



不得输出带病版本，必须换用第二安全候选重新渲染。



\---



\## 十二、VLM算力预算



12条视频采用：



\### Soft Budget



`800,000 Tokens`



\### Quality Escalation Budget



`1,800,000 Tokens`



\### Hard Ceiling



`3,000,000 Tokens`



达到Hard Ceiling必须停止新增调用。



不得为了省Token跳过完整视频代理比较。



不得为了消耗预算重复询问同一问题。



缓存键必须包含：



\* source hash；

\* source window；

\* candidate sequence；

\* model；

\* prompt version；

\* narration；

\* comparison order。



\---



\## 十三、VLM调用价值统计



必须输出：



\* total\_calls

\* successful\_calls

\* cached\_calls

\* candidate\_rejections

\* rankings\_confirmed

\* rankings\_changed

\* timeline\_changes\_triggered

\* human\_risks\_found

\* logic\_risks\_found

\* over\_editing\_risks\_found

\* calls\_with\_timestamp\_evidence

\* tokens\_per\_final\_adopted\_change



以下不能计为`decision\_changed`：



\* 只是确认本地原判断；

\* 只增加置信度；

\* 提出建议但未改变时间线；

\* 输出高分但没有证据。



\---



\## 十四、OpenCV与时序硬门



所有实验组必须通过：



\* blur；

\* exposure；

\* duplicate frames；

\* freeze；

\* ABAB alternating frames；

\* optical-flow discontinuity；

\* motion-energy spike；

\* non-monotonic PTS；

\* speed-remap artifact；

\* crop safety；

\* transition freeze。



已知负样本必须继续进入回归测试：



\* P12U V1A人手；

\* P12U V1B鬼畜；

\* P12U V2B人手与鬼畜；

\* P12U V3B人手；

\* P12X-v2 V2A最后人手画面；

\* P12S管线新增冻结。



必须区分：



\* 生产候选拒绝数；

\* 已知负样本检出数；

\* 误报数；

\* 漏报数。



\---



\## 十五、V2A人手区间永久写入本批次排除表



必须从P12X-v2 V2A的Director Slate、时间线或报告中，追溯Owner指出的最后人手画面：



\* source\_video\_id；

\* source\_in\_ms；

\* source\_out\_ms；

\* final\_timeline\_interval。



将该来源区间写入：



`configs/asset\_exclusion\_intervals\_v2.json`



或当前统一排除配置。



字段：



```json

{

&#x20; "reason": "owner\_confirmed\_hand\_intrusion",

&#x20; "severity": "fatal",

&#x20; "owner\_confirmed": true

}

```



不得把整条原片自动拉黑，除非整条大部分时间均不可用。



\---



\## 十六、Python决策规则



Python继续负责：



\* 候选合法性；

\* 状态拓扑；

\* Coverage；

\* 构图与动作连续；

\* 单变量实验约束；

\* VLM输出Schema验证；

\* 时间区间黑名单；

\* 最终方案编译。



实验组新方案必须满足：



\### 硬条件



\* 无人手、人脸和明显人体；

\* 无鬼畜；

\* 无冻结；

\* 无动作截断；

\* 无非法状态倒退；

\* Claim证据不弱于母版；

\* 9:16裁切安全；

\* 音画误差不超过100ms。



\### 软条件



至少一项明确提升：



\* Hook；

\* Proof；

\* 视觉层次；

\* 前后衔接；

\* Lifestyle；

\* Closure；

\* 画面丰富度。



本轮是前台实验，不要求每条Variant全面击败Control。



但不得存在明确回归。



\---



\## 十七、FFmpeg执行契约



继续复用P12W稳定渲染底座。



禁止：



\* `tpad=stop\_mode=clone`；

\* 末帧复制；

\* 双重CFR；

\* PTS未归零；

\* 用`-shortest`承担时长规划；

\* 循环帧填充；

\* 切碎完整动作；

\* 无必要二次编码控制组。



所有实验组执行：



1\. 精确trim；

2\. PTS归零；

3\. 合法变速；

4\. scale/crop；

5\. 唯一一次30fps；

6\. 精确帧预算；

7\. concat；

8\. Edge-TTS音轨合流；

9\. OpenCV最终扫描。



\---



\## 十八、变速规则



\### 狗动作



默认：



`1.00x`



最高：



`1.05x`



\### 高运动能量动作



强制：



`1.00x`



\### 产品开合



允许：



`1.00x–1.15x`



但必须完整展示：



\* 初始状态；

\* 变化过程；

\* 最终状态。



任何变速都必须通过OpenCV时序伪影检测。



\---



\## 十九、12条输出目录



输出到：



`products/dog\_stairs\_v1/outputs/renders/batch\_20260617\_001/P12Y\_tiktok\_12\_video\_production\_batch`



至少包含：



\* 12条MP4；

\* `production\_source\_map.json`

\* `ab\_experiment\_matrix.json`

\* `owner\_confirmed\_exclusions.json`

\* `vlm\_candidate\_audit\_report.json`

\* `vlm\_option\_comparison\_report.json`

\* `final\_control\_variant\_ab\_report.json`

\* `opencv\_final\_validation.json`

\* `negative\_sample\_regression\_report.json`

\* `transition\_freeze\_detection\_report.json`

\* `vlm\_compute\_value\_report.json`

\* `tk\_manual\_publish\_manifest.csv`

\* `manual\_publish\_checklist.md`

\* `review\_index.md`



\---



\## 二十、TikTok手动发布清单



生成：



`tk\_manual\_publish\_manifest.csv`



字段：



\* publish\_order

\* filename

\* pair\_id

\* family

\* control\_or\_variant

\* tested\_variable

\* source\_master

\* duration

\* visual\_unit\_count

\* hook\_type

\* core\_type

\* closure\_type

\* owner\_review\_priority

\* experimental\_confidence

\* quality\_status

\* notes



不得调用TikTok发布接口。



不得自动上传。



不得自动安排发布时间。



\---



\## 二十一、建议前台发布顺序



第一批优先验证已经表现更稳定的家族：



1\. `07\_V2B\_control\_P12Y.mp4`

2\. `08\_V2B\_hook\_bridge\_variant\_P12Y.mp4`

3\. `09\_V3A\_control\_P12Y.mp4`

4\. `10\_V3A\_lifestyle\_closure\_variant\_P12Y.mp4`

5\. `11\_V3B\_control\_P12Y.mp4`

6\. `12\_V3B\_hook\_variant\_P12Y.mp4`



第二批：



7\. `01\_V1A\_control\_P12Y.mp4`

8\. `02\_V1A\_hook\_variant\_P12Y.mp4`

9\. `03\_V1B\_control\_P12Y.mp4`

10\. `04\_V1B\_core\_rhythm\_variant\_P12Y.mp4`

11\. `05\_V2A\_control\_P12Y.mp4`

12\. `06\_V2A\_proof\_coverage\_variant\_P12Y.mp4`



实际发布始终由Owner手动完成。



\---



\## 二十二、验收标准



\### 12条交付



\* 必须存在12条独立MP4；

\* 6条Control；

\* 6条Variant；

\* 每组A/B测试变量清楚；

\* Control来源正确；

\* Variant没有多变量混杂。



\### 物理质量



12条全部满足：



\* `PIPELINE\_INTRODUCED\_FREEZE=0`；

\* 鬼畜为0；

\* 违规人手为0；

\* 人脸和明显人体为0；

\* 动作截断为0；

\* 非法状态倒退为0；

\* PTS连续；

\* 单一CFR；

\* 1080×1920；

\* SAR 1:1；

\* 音画误差不超过100ms。



\### 业务质量



\* V2A实验版形成更完整Proof，或安全采用替代实验；

\* V2B实验版进一步优化前2秒承接；

\* V3A实验版增强Lifestyle或Closure；

\* V3B实验版保持更强Hook；

\* 至少4条Variant获得中高实验置信度；

\* 所有12条均可供Owner在TikTok前台手动发布测试。



\---



\## 二十三、review\_index.md



每条列出：



\* 文件路径；

\* Control或Variant；

\* 来源母版；

\* 测试变量；

\* 视觉单元数量；

\* 新素材数量；

\* 人手审核；

\* 时序伪影；

\* 动作完整；

\* 叙事状态；

\* VLM Stage 1结果；

\* VLM Stage 2结果；

\* VLM Stage 3结果；

\* 是否改变本地决策；

\* 零冻结；

\* 音画误差；

\* Owner重点观看时间点。



汇总：



\* Control无损复制数量；

\* Variant重新渲染数量；

\* VLM总调用；

\* VLM总Token；

\* VLM改变候选排序次数；

\* VLM改变时间线次数；

\* VLM发现人手数量；

\* 生产候选拒绝数；

\* 已知负样本检出率；

\* 12条零冻结结果；

\* 12条音画误差；

\* 总执行时间。



\---



\## 二十四、最终输出格式



完成后只输出：



TK\_12\_VIDEO\_PRODUCTION\_BATCH\_READY



视频目录：

01视频：

02视频：

03视频：

04视频：

05视频：

06视频：

07视频：

08视频：

09视频：

10视频：

11视频：

12视频：

Control无损复制数量：

Variant重新渲染数量：

V2A人手负样本追溯结果：

生产候选人手拒绝数：

已知负样本人手检出率：

已知鬼畜负样本检出率：

VLM Stage 1调用数：

VLM Stage 2调用数：

VLM Stage 3调用数：

VLM总Token：

VLM改变候选排序次数：

VLM改变最终时间线次数：

12条零冻结结果：

12条音画误差：

中高置信度Variant数量：

总执行时间：

主要已知问题：

TikTok手动发布清单：

建议发布顺序：



然后停止等待Owner观看和前台数据。



\---



\## 二十五、执行顺序



1\. 验证本Task；

2\. 确认`spec\_version=P12Y-v1`；

3\. 读取P12W、P12X-v2和Owner反馈；

4\. 锁定六条生产母版；

5\. 追溯P12X-v2 V2A最后人手来源区间；

6\. 更新批次时间区间排除表；

7\. 创建12条A/B实验矩阵；

8\. 无损复制六条Control；

9\. 为六条Variant分别建立单变量目标；

10\. 每个目标检索8–16个候选；

11\. OpenCV执行前置硬门；

12\. VLM Stage 1候选深审；

13\. 生成A/B/C三套实验方案；

14\. VLM Stage 2完整代理比较；

15\. Python验证单变量、DAG、Coverage和硬门；

16\. 选择最终Variant时间线；

17\. 使用P12W渲染底座输出六条Variant；

18\. OpenCV执行最终物理检查；

19\. VLM Stage 3 Control/Variant最终A/B；

20\. 存在硬回归则更换第二安全候选并局部重渲染；

21\. 生成12条最终MP4；

22\. 生成手动发布清单；

23\. 生成review\_index；

24\. 输出最终结果；

25\. 停止等待Owner发布和数据反馈。



本任务的成功由12条真实可发布成片、单变量实验可解释性、VLM质量效率最大化、OpenCV与FFmpeg物理稳定性以及TikTok前台真实数据共同决定。



