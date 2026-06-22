\# TASK：P12X\_V2\_CINEMATIC\_GLOBAL\_SEARCH\_WITH\_GUARDRAILS



spec\_version: P12X-v2



\## 一、任务版本关系



本任务取代尚未执行的：



`P12X-v1 VLM\_VISUAL\_COVERAGE\_ORCHESTRATOR`



不得并行执行两个P12X任务。



P12X-v2不是继续在P12W上增加零散补丁，而是在已经稳定的：



\* OpenCV本地像素感知；

\* Python确定性决策；

\* GLM-4.6V商业语义理解；

\* P12T/P12W稳定FFmpeg渲染；



四层基础上，建立完整的：



`全局电影语法搜索 + 基线防退化 + VLM证据化重排`



系统。



P12W继续作为已验证生产基线，但不再限制全局搜索最多只能替换两个槽位。



P12W必须作为候选0和安全回退版本参与竞争，而不是作为不可修改的唯一时间线。



\---



\## 二、最高评价体系



继续严格执行：



`系统价值 = 成片质量 × 产出速度 ÷ 开发与调用成本`



本任务的核心目标不是：



\* 增加剪切次数；

\* 强制使用更多新素材；

\* 最大化光流匹配；

\* 把所有P12W镜头替换掉；

\* 证明Beam Search或VLM比Owner更聪明。



本任务的核心目标是：



> 在零冻结、零鬼畜、零违规人手、动作完整和叙事合法的前提下，扩大合法搜索空间，生成视觉覆盖更丰富、构图更有层次、商业因果更清晰的完整视频。



最终成片必须同时实现：



1\. 画面丰富度提升；

2\. 构图不弱于P12W；

3\. 商业叙事不弱于P12W；

4\. 动作完整；

5\. 视觉卫生通过；

6\. 无时序伪影；

7\. 无转场冻结；

8\. 没有明确提升时能够回退P12W；

9\. 至少三条视频获得Owner可感知的提升。



\---



\## 三、业务目标与技术架构颗粒度对齐



| 业务目标         | 技术机制                                     | 量化验收               |

| ------------ | ---------------------------------------- | ------------------ |

| 使用更多真正有价值的素材 | 全量候选窗口索引、角色Top-K、全局序列搜索                  | 至少三条采用新高价值视觉单元     |

| 画面更丰富但不混乱    | Visual Coverage Set、序列级Coverage评分、过度剪辑惩罚 | 每条建议7–11个视觉单元，无碎片化 |

| Hook更强       | Hook专用候选池、2–3视觉Beat、VLM商业冲突判断            | 3秒内完成认知建立          |

| Proof更有说服力   | 接触、过程、结果三段证据链                            | Claim必须有完整视觉证明     |

| 构图更高级        | 构图递进、景别功能、主体位置和视觉重心评分                    | 构图评分不低于P12W        |

| 转场更流畅        | 全局运动估计、稠密光流残差、音频切点匹配                     | 运动匹配只作低权重增益        |

| 商业逻辑正确       | Python叙事状态DAG、动作和产品状态连续                  | 非法状态转移为0           |

| 无人手和污染       | 自适应抽帧、视频代理、VLM时间段审查、区间黑名单                | 普通镜头违规人手为0         |

| 无鬼畜和冻结       | OpenCV时序检测、P12W帧网格和单一CFR                 | 鬼畜0、管线新增冻结0        |

| VLM能力充分发挥    | Top-N完整视频代理、证据化重排、顺序偏见复核                 | VLM必须引用具体时间点       |

| 不产生大面积负提升    | P12W候选0、完整视频占优门、自动回退                     | 所有最终成片不低于P12W      |

| 少返工          | 统一模块、统一配置、缓存复用、一次完成全链路                   | 不再建立平行试验流水线        |



\---



\## 四、必须吸收的技术原则



\### 4.1 电影剪辑语法代码化



以下要素必须进入本地可计算评分：



\* 叙事角色；

\* 动作阶段；

\* 产品状态；

\* 狗的位置和运动；

\* 景别；

\* 构图变化；

\* 主体入口与出口；

\* 摄影机运动；

\* 音频切点；

\* 视觉覆盖；

\* Closure；

\* 素材重复度；

\* 过度剪辑风险。



理由：



VLM可以判断语义，但最终大规模组合搜索必须依赖可缓存、可复现、可解释的本地评分。



\---



\### 4.2 在合法DAG空间内扩大全局搜索



允许重新搜索全片5–7个视觉槽位。



但所有候选必须位于合法叙事状态图中。



理由：



P12W最多替换两个槽位能够控制风险，但限制了全局视觉丰富度；P12U完全自由搜索又导致逻辑崩溃。



正确解法不是“完全锁死”或“完全放开”，而是：



`扩大合法空间`

而不是

`扩大无约束空间`



\---



\### 4.3 OpenCV运动描述符进入相邻边评分



必须计算候选镜头：



\* Head运动描述符；

\* Tail运动描述符；

\* 全局摄影机运动；

\* 局部主体运动；

\* 运动能量；

\* 运动置信度。



理由：



运动连续性是可感知的剪辑变量，但必须服务于构图和叙事。



\---



\### 4.4 VLM审查Top完整Storyboard



VLM不只检查单镜头，也必须比较完整Storyboard和低分辨率完整视频代理。



理由：



单镜头高质量不等于整片高质量；构图、因果、节奏和Closure必须在完整序列中判断。



\---



\### 4.5 P12W必须保留为候选0



每条视频的搜索结果必须包含：



\* P12W Baseline；

\* Coverage-Rich；

\* Cinematic-Global；

\* Narrative-First。



理由：



全局搜索必须有一个已被Owner认可的实际基线，避免评分模型再次把“数学高分”误当成“商业高质量”。



\---



\## 五、必须优化的技术原则



\### 5.1 Farneback不能使用全画面简单平均矢量



禁止直接执行：



```python

avg\_dx = np.mean(flow\[..., 0])

avg\_dy = np.mean(flow\[..., 1])

```



并将结果直接解释为摄影机Pan。



必须采用：



1\. 特征点检测；

2\. 稀疏光流追踪；

3\. RANSAC估计全局仿射变换；

4\. 提取全局平移、旋转和缩放；

5\. 使用Farneback计算局部残差；

6\. 判断运动来源：



&#x20;  \* camera；

&#x20;  \* subject；

&#x20;  \* mixed；

&#x20;  \* static；

&#x20;  \* uncertain。



理由：



狗移动、手部进入和前景视差都会污染全画面平均光流。



\---



\### 5.2 Match Cut不得无条件奖励20分



禁止只要方向余弦大于0.75就固定加20分。



运动匹配奖励必须同时满足：



\* global\_motion\_confidence ≥ 0.75；

\* direction\_similarity ≥ 0.75；

\* magnitude\_compatibility ≥ 0.60；

\* 叙事状态合法；

\* 构图不退化；

\* 主体入口和出口合理；

\* 不是主体局部运动误判。



运动匹配在最终总分中的权重：



\* 默认4%；

\* 最高6%。



理由：



P12U已经证明，运动匹配权重过高会驱动系统选择逻辑更差、构图更乱的素材。



\---



\### 5.3 相同景别不自动等于Jump Cut



只有同时满足以下条件时才重度惩罚：



\* 相同source\_video\_id；

\* 时间窗口接近、重叠或来自同一连续动作；

\* shot\_scale相同；

\* 构图相似度高；

\* 主体位置变化小；

\* 动作没有推进；

\* 没有合法的Before/After或连续动作价值。



理由：



相同景别也可能承担：



\* 连续动作；

\* 对照；

\* 结果证明；

\* 不同构图；

\* 不同信息层。



\---



\### 5.4 Beam Width扩大不等于质量提升



默认：



`beam\_width = 45`



但必须同时执行：



\* 硬门前置；

\* 每Slot Top-K限制；

\* 分数上界剪枝；

\* 重复路径去重；

\* 序列级评分；

\* 多样性重排；

\* 过度剪辑惩罚；

\* Baseline候选保留。



理由：



单独把束宽从10改成45，只会更大规模地搜索错误目标函数。



\---



\### 5.5 VLM不能只看Contact Sheet



完整Storyboard终审必须同时输入：



\* 带时间码Contact Sheet；

\* 低分辨率完整视频代理；

\* narration文本；

\* Breath Group时间线；

\* Storyboard角色JSON；

\* OpenCV技术摘要。



理由：



Contact Sheet不能可靠识别：



\* 动作方向；

\* 帧序异常；

\* 鬼畜；

\* 节奏；

\* 动作生命周期；

\* 视听因果。



\---



\## 六、必须舍弃的技术原则



\### 6.1 舍弃“完全解除全部防线”



不得恢复P12U式自由重组。



原因：



OpenCV只能测量像素，无法独立保证商业逻辑；物理合格不等于内容正确。



\---



\### 6.2 舍弃“VLM只负责一票否决”



VLM必须参与：



\* Coverage分析；

\* 候选语义角色确认；

\* 完整Storyboard重排；

\* P12W与新版本对照判断。



但不得直接输出最终FFmpeg时码。



原因：



只把VLM放在最后否决，会浪费其最有价值的语义和商业判断能力。



\---



\### 6.3 舍弃“所有镜头必须同向”



方向反转、动静对比和空间重置可能是合法剪辑。



原因：



电影语法是条件规则，不是单一公式。



\---



\### 6.4 舍弃“同素材同景别固定扣25分”



改为多条件Jump Cut风险评分。



原因：



固定扣分会误伤连续动作和完整Proof。



\---



\### 6.5 舍弃“Top 3 Contact Sheet一次调用即可终审”



必须加入完整视频代理和必要的顺序反转复核。



原因：



P12U已经证明，粗粒度VLM判断可以漏掉短暂人手、异常帧和逻辑断裂。



\---



\### 6.6 舍弃“好莱坞级”“100%电影感”等不可验证目标



最终验收只能使用：



\* Owner A/B偏好；

\* 商业逻辑；

\* 构图；

\* Coverage；

\* 时序稳定；

\* 零污染；

\* 可感知提升数量。



\---



\## 七、项目路径



项目根目录：



`C:\\Users\\43871\\AppData\\Local\\LFZ\_CODE\\agent-video-lab-233-laptop`



工作目录：



`C:\\Users\\43871\\AppData\\Local\\LFZ\_CODE\\agent-video-lab-233-laptop\\03\_tk\_video\_agent`



原素材目录：



`products/dog\_stairs\_v1/inputs/raw\_videos/batch\_20260617\_001`



P12W基线目录：



`products/dog\_stairs\_v1/outputs/renders/batch\_20260617\_001/P12W\_opencv\_ffmpeg\_vlm\_asymmetric\_vision\_compiler`



P12X-v2输出目录：



`products/dog\_stairs\_v1/outputs/renders/batch\_20260617\_001/P12X\_v2\_cinematic\_global\_search\_with\_guardrails`



VLM：



\* provider：`zhipu`

\* model：`glm-4.6v`



TTS：



\* Edge-TTS

\* voice：`en-US-AvaNeural`



OpenCV：



\* 当前验证版本：4.13.0；

\* 正式执行必须满足`opencv\_backend\_used=true`。



\---



\## 八、统一工程结构



继续使用：



`helpers/vision\_compiler/`



新增两个核心文件：



```text

helpers/vision\_compiler/

├── cinematic\_feature\_engine.py

└── global\_storyboard\_optimizer.py

```



修改：



```text

helpers/vision\_compiler/

├── opencv\_perception.py

├── semantic\_vlm\_router.py

├── storyboard\_compiler.py

├── quality\_gate.py

└── pipeline.py

```



新增唯一主配置：



`configs/cinematic\_search\_policy\_v1.json`



不得再建立另一套平行剪辑流水线。



不得复制第二套FFmpeg渲染器。



P12T/P12W稳定渲染器必须通过适配器复用。



\---



\## 九、Cinematic Feature Engine



新增：



`helpers/vision\_compiler/cinematic\_feature\_engine.py`



职责：



\### 9.1 节点特征



每个候选镜头输出：



\* semantic\_role\_fit

\* technical\_quality

\* composition\_quality

\* crop\_safety

\* action\_completeness

\* claim\_evidence

\* visual\_hygiene

\* temporal\_stability

\* owner\_style\_match

\* novelty

\* shot\_scale

\* subject\_position

\* product\_state

\* dog\_position

\* action\_phase



\### 9.2 Head/Tail运动特征



每个候选输出：



\* head\_global\_motion

\* tail\_global\_motion

\* head\_local\_motion

\* tail\_local\_motion

\* motion\_source

\* motion\_confidence

\* motion\_energy

\* camera\_translation

\* rotation

\* scale\_change

\* subject\_entry

\* subject\_exit



\### 9.3 构图特征



允许使用OpenCV与VLM已有标签组合计算：



\* visual\_center

\* subject\_bbox\_or\_region

\* product\_region

\* negative\_space\_ratio

\* composition\_similarity

\* background\_clutter

\* showroom\_feeling

\* home\_feeling



OpenCV无法识别的商业构图语义必须使用VLM确认。



\---



\## 十、Node Score



每个候选镜头满分100。



推荐权重：



\* Narrative Role Fit：22

\* Composition：18

\* Action Completeness：16

\* Visual Hygiene：14

\* Claim Evidence：10

\* Technical Quality：8

\* Temporal Stability：6

\* Crop Safety：3

\* Owner Style Match：2

\* Novelty：1



硬门失败的候选直接淘汰，不允许用总分补偿。



以下属于硬门：



\* 违规人手；

\* 人脸或明显人体；

\* 鬼畜；

\* 冻结；

\* 动作截断；

\* 非法产品状态；

\* 非法叙事角色；

\* 无法安全裁切；

\* Proof无证据。



\---



\## 十一、Edge Score



相邻镜头边分满分100。



推荐权重：



\* Narrative State Transition：28

\* Product/Dog State Continuity：20

\* Composition Progression：16

\* Audio Cut Anchor：14

\* Shot-Scale Function：10

\* Motion Continuity：4

\* Subject Entry/Exit：4

\* Source Reuse Risk：2

\* Jump-Cut Risk：2



Motion Continuity绝对不得超过6%。



\### 11.1 Motion Match



奖励条件：



\* 高置信度；

\* 方向相近；

\* 强度相容；

\* 语义不冲突；

\* 构图不退化。



反向运动默认只软扣分。



只有同时存在：



\* 高置信度；

\* 无中性建立镜头；

\* 无状态转换；

\* 主体出口和入口冲突；

\* 空间轴明显错误；



才标记严重风险。



\### 11.2 Shot Scale



景别变化必须服务信息：



\* Wide：环境和关系；

\* Medium：动作和使用；

\* Close-up：材料、脚掌、结构；

\* Result：完成状态；

\* Lifestyle：价值收束。



不得机械追求Wide、Medium、Close交替。



\---



\## 十二、Sequence Score



完整Storyboard必须额外计算序列级分数。



推荐：



\* Story Completeness：25

\* Visual Coverage：20

\* Commercial Causality：18

\* Pacing：12

\* Composition Arc：10

\* Closure：7

\* Cross-Video Diversity：4

\* Owner Preference：4



并计算负向惩罚：



\* over\_editing\_penalty

\* repeated\_information\_penalty

\* source\_concentration\_penalty

\* state\_regression\_penalty

\* unresolved\_claim\_penalty

\* closure\_failure\_penalty



不得只累加Node和Edge分数。



\---



\## 十三、叙事DAG



\### 13.1 痛点解决型



`HOOK\_OR\_RESULT\_TEASE`

→ `PROBLEM`

→ `INTERVENTION`

→ `ACTIVE\_USE`

→ `SUCCESS\_RESULT`

→ `SETTLE`

→ `CLOSURE`



\### 13.2 功能证明型



`HOOK`

→ `FEATURE`

→ `DEMONSTRATION\_START`

→ `DEMONSTRATION\_PROGRESS`

→ `DEMONSTRATION\_COMPLETE`

→ `PROOF`

→ `CLOSURE`



\### 13.3 生活价值型



`SITUATION`

→ `PRODUCT\_CONTEXT`

→ `USAGE\_OR\_TRANSFORMATION`

→ `LIFESTYLE\_PAYOFF`

→ `CLOSURE`



允许省略非必要状态，但不得倒退。



每个镜头必须输出：



\* entry\_state

\* exit\_state

\* action\_phase

\* dog\_position\_before

\* dog\_position\_after

\* product\_state\_before

\* product\_state\_after

\* allowed\_roles



非法状态转移直接Hard Reject。



\---



\## 十四、全局搜索空间



解除P12W最多替换两个槽位的限制。



允许全片搜索：



\* 5–7个叙事槽位；

\* 每Slot最多Top 8候选；

\* Hook允许2–3个视觉Beat；

\* Core允许按视觉功能拆成1–3个镜头；

\* Closure允许1–2个镜头。



但不得强制使用最大数量。



每条建议视觉单元：



\* 最低：6；

\* 推荐：7–11；

\* 最高：12。



超过12个视觉单元：



默认触发`over\_editing\_risk`。



\---



\## 十五、Beam Search



默认参数：



```text

beam\_width = 45

per\_slot\_top\_k = 8

complete\_storyboard\_keep = 24

diversity\_rerank\_keep = 8

vlm\_finalist\_count = 3

```



搜索流程：



1\. 按叙事DAG确定合法下一状态；

2\. 获取当前Slot Top-K候选；

3\. 先执行硬门；

4\. 计算Node Score；

5\. 计算Edge Score；

6\. 计算部分序列的Coverage与状态完整度；

7\. 使用分数上界剪枝；

8\. 去除重复窗口和近重复路径；

9\. 每层保留Top 45；

10\. 完整后保留Top 24；

11\. 执行多样性重排保留Top 8；

12\. 选择三套完整候选进入VLM。



不得只按照累计局部分数剪枝。



必须防止早期高分但最终无法闭环的路径占满Beam。



\---



\## 十六、候选家族



每条视频必须生成至少四类完整候选：



\### Candidate 0：P12W Baseline



保持P12W。



\### Candidate 1：Narrative-First



叙事和Proof优先。



\### Candidate 2：Coverage-Rich



视觉功能覆盖优先，但不得过度剪辑。



\### Candidate 3：Cinematic-Global



构图弧线、景别功能和合法运动匹配优先。



如果某类候选无法通过硬门：



必须明确记录，不得伪造。



最终Top 3应尽量来自不同候选家族。



\---



\## 十七、Visual Coverage



每个Claim必须建立Coverage Set。



例如Proof：



```text

contact

→ stable\_progress

→ successful\_result

```



Transformation：



```text

initial\_state

→ transformation\_progress

→ final\_state

```



Lifestyle：



```text

home\_context

→ dog\_product\_relationship

→ lifestyle\_payoff

```



Coverage评分必须判断：



\* 必要角色是否齐全；

\* 是否存在重复信息；

\* 是否缺少结果；

\* 是否缺少settle；

\* 是否插入无关镜头；

\* 是否增加理解成本。



不得用更多镜头数量替代完整证据。



\---



\## 十八、视觉节奏约束



\### Hook 0–3秒



允许：



\* 2–3个视觉Beat；

\* 常规镜头不短于350ms；

\* 最多一个250–350ms冲击镜头；

\* 必须在3秒内建立问题、差异或结果悬念。



\### Core



\* 完整动作优先；

\* 单一状态默认1–2个镜头；

\* 明确Coverage缺口时允许3个；

\* 不得切碎狗完整上楼、下楼或Transformation动作。



\### Closure



\* 1–2个镜头；

\* 不得重新启动新动作；

\* 必须回收商业Claim或情绪结果。



\---



\## 十九、OpenCV运动分析



\### 19.1 全局运动主路径



使用：



\* `goodFeaturesToTrack`或ORB；

\* `calcOpticalFlowPyrLK`；

\* RANSAC仿射估计；

\* 提取dx、dy、rotation和scale；

\* 输出inlier\_ratio和reprojection\_error。



\### 19.2 Farneback辅助路径



使用：



`cv2.calcOpticalFlowFarneback`



但只分析：



\* 局部运动能量；

\* 主体运动；

\* 全局运动残差；

\* 高频方向翻转；

\* 变速后异常。



\### 19.3 置信度



当以下情况存在时降低置信度：



\* 特征点不足；

\* RANSAC内点率低；

\* 主体占据画面绝大部分；

\* 大面积遮挡；

\* 快速模糊；

\* 强手持抖动。



`motion\_confidence < 0.60`



则Motion Score归零。



\---



\## 二十、视觉卫生与时序硬门



所有进入完整Storyboard的候选必须通过：



\### OpenCV



\* 重复帧；

\* 冻结；

\* ABAB交替帧；

\* PTS异常；

\* 运动能量异常；

\* 高频方向反转；

\* 变速伪影；

\* 模糊和曝光；

\* 裁切安全。



\### VLM



\* 人手；

\* 人脸；

\* 明显人体；

\* 产品状态；

\* 动作生命周期；

\* 商业角色；

\* 狗的位置和方向；

\* 展厅污染；

\* 家居关系。



不得只依赖Contact Sheet。



动态候选必须同时提供视频代理。



\---



\## 二十一、VLM非对称审查



\### Level 1：候选语义深审



对Top动态候选执行：



\* 动作生命周期；

\* 人手时间段；

\* 产品状态；

\* Claim资格；

\* 角色资格；

\* 构图和家居感。



\### Level 2：完整Storyboard重排



输入：



\* P12W Baseline；

\* 三套完整候选；

\* 每套完整低分辨率视频代理；

\* Contact Sheet；

\* narration；

\* 时间线JSON；

\* OpenCV摘要。



VLM必须输出：



\* ranking

\* winner

\* composition\_score

\* narrative\_score

\* coverage\_score

\* proof\_score

\* rhythm\_score

\* temporal\_stability\_score

\* visual\_hygiene\_score

\* over\_editing\_risk

\* evidence\_timestamps

\* rejected\_sequences

\* recommended\_local\_changes

\* confidence



不得只输出`pass`或统一高分。



\### Level 3：顺序偏见复核



当以下任一成立时执行一次候选顺序反转：



\* Top 2差距小；

\* winner confidence < 0.80；

\* VLM选择与本地第一名不同；

\* VLM偏好Cinematic-Global但构图或叙事分低；

\* Owner高优先级视频。



两次结论不一致：



优先选择P12W或Narrative-First。



不得无限重试。



\---



\## 二十二、VLM不得直接做的事情



VLM不得：



\* 直接生成FFmpeg命令；

\* 直接确定最终毫秒切点；

\* 覆盖OpenCV时序失败；

\* 覆盖DAG非法状态；

\* 使用候选池之外的clip\_id；

\* 为了画面丰富而创造不存在的素材；

\* 自动突破Token Hard Ceiling。



VLM可以提出局部改进建议。



具体切点必须由Python和FFmpeg计算。



\---



\## 二十三、P12W基线防退化



全局搜索可以替换多个槽位，但最终完整视频必须与P12W比较。



硬条件：



\* 无新增人手；

\* 无鬼畜；

\* 无冻结；

\* 无动作截断；

\* 无逻辑倒退；

\* 构图不得明显下降；

\* Claim证据不得下降；

\* Closure不得下降；

\* 音画误差≤100ms。



完整视频占优边际：



`video\_dominance\_margin >= 6`



且以下至少三项提升：



\* Hook；

\* Coverage；

\* Proof；

\* 构图层次；

\* 商业因果；

\* Closure；

\* 情绪表达；

\* Owner风格匹配。



不满足：



`fallback\_to\_p12w = true`



\---



\## 二十四、多样性约束



六条视频不得因为全局搜索再次趋同。



同类型A/B必须满足：



\* Core镜头重合率目标≤25%；

\* 全片镜头重合率目标≤40%；

\* 不得使用相同连续镜头组合；

\* V1A/V1B Hook机制不同；

\* V2A/V2B Proof类型不同；

\* V3A/V3B Core价值不同。



但多样性不得覆盖质量。



如果只有一个高质量方案：



允许两条在部分镜头上相似，并明确报告素材不足。



\---



\## 二十五、V2B专项要求



Owner确认P12W V2B前2秒略有跳跃。



P12X-v2必须为V2B生成：



1\. P12W原版；

2\. 仅调整切点版本；

3\. 增加合法桥接镜头版本；

4\. 全局Cinematic候选。



优先级：



`切点调整`

→ `桥接镜头`

→ `整体替换`



不得为了修复2秒跳跃破坏后续结构Proof。



\---



\## 二十六、变速原则



\### 狗动作



默认：



`1.00x`



最高：



`1.05x`



且必须通过：



\* OpenCV时序检测；

\* VLM自然度审核；

\* 动作完整；

\* 完整视频占优。



\### 产品开合



允许：



`1.00x–1.15x`



必须完整覆盖：



\* 初始状态；

\* 变化过程；

\* 最终状态。



\### 高运动能量镜头



强制：



`1.00x`



不得为适配时长制造鬼畜或跳帧。



\---



\## 二十七、FFmpeg执行契约



完整复用P12W稳定渲染底座。



每个片段：



1\. 精确trim；

2\. `setpts=PTS-STARTPTS`；

3\. 合法变速；

4\. scale/crop；

5\. 唯一一次`fps=30`；

6\. 精确目标帧数；

7\. PTS验证；

8\. concat；

9\. 完整Edge-TTS音轨一次合流。



禁止：



\* `tpad=stop\_mode=clone`；

\* 末帧复制；

\* 双重CFR；

\* 依赖`-shortest`规划时长；

\* 循环帧填充；

\* 用播放器保持末帧；

\* 无效视觉槽位。



\---



\## 二十八、算力预算



Owner允许在明确质量收益下提高GLM-4.6V算力。



\### Soft Budget



`750,000 Tokens / 6条`



\### Quality Escalation



`1,500,000 Tokens / 6条`



\### Hard Ceiling



`2,500,000 Tokens / 6条`



预算建议：



\* 20%：候选动态视频深审；

\* 25%：Coverage和角色审核；

\* 35%：完整Storyboard视频代理重排；

\* 15%：顺序偏见复核；

\* 5%：失败重试。



停止条件：



1\. 相同缓存键已有结果；

2\. 连续两次没有改变完整候选排序；

3\. VLM没有提供时间码证据；

4\. 本地硬门已经失败；

5\. P12W明显更优；

6\. 顺序反转结论冲突；

7\. 达到Hard Ceiling；

8\. 当前视频已有明确占优方案。



\---



\## 二十九、缓存与速度



必须复用P12W已有：



\* 52条OpenCV索引；

\* 技术质量特征；

\* 动作窗口；

\* Motion Descriptor；

\* VLM粗标签；

\* 时间区间黑名单；

\* 正负样本校准。



缓存键必须包括：



\* source file hash；

\* source window；

\* OpenCV version；

\* feature version；

\* analysis parameters；

\* VLM model；

\* Prompt version。



未变化时不得重新扫描全部52条。



目标增量运行时间：



\* 不含首次依赖安装；

\* 6条完整搜索、审核和渲染尽量控制在12–20分钟。



\---



\## 三十、六条输出



输出：



\* `V1A\_pain\_solution\_P12Xv2.mp4`

\* `V1B\_pain\_solution\_P12Xv2.mp4`

\* `V2A\_feature\_proof\_P12Xv2.mp4`

\* `V2B\_feature\_proof\_P12Xv2.mp4`

\* `V3A\_lifestyle\_value\_P12Xv2.mp4`

\* `V3B\_lifestyle\_value\_P12Xv2.mp4`



要求：



\### V1A



在保持P12W构图和逻辑的基础上，增强Hook或Pain到Intervention的视觉层次。



\### V1B



保持无鬼畜、Hook和Closure，增加Core视觉功能覆盖。



\### V2A



保持P12W的连贯性，增强完整Proof：



`contact → stable progress → result`



\### V2B



优先修复前2秒跳跃，并保持结构证明链。



\### V3A



保持P12W已验证优势，增强家居价值或Closure，不得破坏现有Core。



\### V3B



保持与V3A不同Core，增强Transformation过程覆盖。



\---



\## 三十一、测试



新增：



`tests/test\_p12x\_v2\_cinematic\_global\_search.py`



至少覆盖：



1\. P12W候选0始终存在；

2\. DAG非法路径被拒绝；

3\. beam\_width为45；

4\. 每Slot Top-K限制；

5\. 分数上界剪枝；

6\. Node Score；

7\. Edge Score；

8\. Sequence Score；

9\. Motion权重≤6%；

10\. 低置信运动归零；

11\. Farneback不直接等于camera motion；

12\. 相同景别不自动重罚；

13\. Jump Cut多条件判断；

14\. Coverage完整性；

15\. Over-editing惩罚；

16\. Top 3候选家族差异；

17\. VLM只能引用合法clip\_id；

18\. 完整视频代理审查；

19\. 顺序反转冲突回退；

20\. P12W安全回退；

21\. 时间区间黑名单；

22\. 鬼畜检测；

23\. 冻结检测；

24\. PTS归零；

25\. 单一CFR；

26\. 音画误差；

27\. 六条最终物理检查。



\---



\## 三十二、输出目录与报告



输出到：



`products/dog\_stairs\_v1/outputs/renders/batch\_20260617\_001/P12X\_v2\_cinematic\_global\_search\_with\_guardrails`



至少包含：



\* 六条P12X-v2成片；

\* `cinematic\_feature\_index.json`

\* `node\_score\_report.json`

\* `edge\_score\_report.json`

\* `sequence\_score\_report.json`

\* `beam\_search\_report.json`

\* `candidate\_family\_report.json`

\* `coverage\_report.json`

\* `jump\_cut\_risk\_report.json`

\* `motion\_match\_report.json`

\* `vlm\_storyboard\_rerank\_report.json`

\* `final\_ab\_dominance\_report.json`

\* `transition\_freeze\_detection\_report.json`

\* `temporal\_artifact\_report.json`

\* `vlm\_compute\_value\_report.json`

\* `review\_index.md`



不得生成名称包含`mcp`的报告。



本任务没有使用外部MCP服务。



\---



\## 三十三、review\_index.md



每条必须记录：



\* P12W路径；

\* P12X-v2路径；

\* P12W视觉单元数；

\* P12X-v2视觉单元数；

\* 替换槽位数；

\* 新素材数；

\* 候选家族；

\* Node Score；

\* Edge Score；

\* Sequence Score；

\* Coverage；

\* 构图；

\* Proof；

\* Closure；

\* Motion Match贡献；

\* Jump Cut风险；

\* Over-editing风险；

\* VLM完整Storyboard排序；

\* 是否执行顺序反转；

\* 是否fallback；

\* 零冻结；

\* 音画误差；

\* Owner建议观看时间点。



汇总：



\* 完整Storyboard搜索数量；

\* Beam剪枝数量；

\* 多样性去重数量；

\* 使用新素材数量；

\* 人手拒绝数；

\* 鬼畜拒绝数；

\* 非法DAG路径拒绝数；

\* P12W回退数量；

\* VLM总调用；

\* VLM总Token；

\* VLM改变最终候选次数；

\* 缓存命中率；

\* 总开发和渲染时间。



\---



\## 三十四、验收标准



\### 物理与卫生



六条全部满足：



\* `PIPELINE\_INTRODUCED\_FREEZE=0`；

\* 鬼畜和异常帧为0；

\* 违规人手为0；

\* 人脸和明显人体为0；

\* 动作截断为0；

\* PTS连续；

\* 单一CFR；

\* 音画误差≤100ms；

\* 1080×1920；

\* SAR 1:1；

\* 9:16。



\### 商业与审美



\* 至少三条明显优于P12W；

\* 至少三条拥有更完整视觉Coverage；

\* V2A Proof更完整；

\* V2B前2秒跳跃改善；

\* V3A/V3B保持不同Core；

\* 画面丰富度提升但没有碎片化；

\* 构图和逻辑不得弱于P12W。



\### 安全回退



不满足完整视频占优门时：



`fallback\_to\_p12w=true`



不得为了证明全局搜索有效而强制使用新版本。



\---



\## 三十五、最终输出格式



完成后只输出：



CINEMATIC\_GLOBAL\_SEARCH\_READY



视频目录：

V1A新版本：

V1B新版本：

V2A新版本：

V2B新版本：

V3A新版本：

V3B新版本：

P12W候选0读取结果：

完整Storyboard搜索数量：

Beam剪枝数量：

最终候选家族：

平均视觉单元数量：

新增高价值镜头数量：

人手拒绝数：

鬼畜拒绝数：

非法DAG路径拒绝数：

Jump Cut风险拒绝数：

fallback到P12W数量：

VLM调用数：

VLM总Token：

VLM改变最终候选次数：

缓存命中率：

六条零冻结结果：

六条音画误差：

明确优于P12W数量：

总开发与渲染时间：

主要已知问题：

建议A/B观看顺序：



然后停止等待Owner观看。



\---



\## 三十六、执行顺序



1\. 验证本Task；

2\. 确认`spec\_version=P12X-v2`；

3\. 确认旧P12X-v1不再执行；

4\. 读取P12W视频、时间线、索引和Owner反馈；

5\. 复用全部有效缓存；

6\. 新建`cinematic\_feature\_engine.py`；

7\. 新建`global\_storyboard\_optimizer.py`；

8\. 新建统一主配置；

9\. 生成候选Node特征；

10\. 生成Head/Tail全局运动和Farneback残差；

11\. 建立Node、Edge和Sequence评分；

12\. 建立三类叙事DAG；

13\. 构建每Slot Top 8候选；

14\. 执行硬门前置过滤；

15\. 使用beam\_width 45执行全局搜索；

16\. 保留Top 24完整Storyboard；

17\. 执行重复路径和多样性重排；

18\. 生成不同候选家族；

19\. 选择三套完整候选；

20\. 生成完整低分辨率视频代理和Contact Sheet；

21\. 调用VLM执行完整Storyboard重排；

22\. 必要时执行一次顺序反转；

23\. 保留P12W候选0参与最终竞争；

24\. 通过完整视频占优门后确定最终时间线；

25\. 使用P12W稳定FFmpeg底座渲染；

26\. 执行OpenCV时序、鬼畜和冻结终检；

27\. 不占优时自动回退P12W；

28\. 输出六条P12X-v2成片；

29\. 生成全部报告；

30\. 输出完成信号；

31\. 停止等待Owner审片。



本任务的成功由合法搜索空间扩大、电影语法可计算化、VLM完整序列判断、P12W无回归以及最终Owner可感知提升共同决定。



