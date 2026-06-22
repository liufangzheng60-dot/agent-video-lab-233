\# TASK：P12R\_V2\_SEMANTIC\_RHYTHM\_ORCHESTRA\_AB\_UPGRADE



spec\_version: P12R-v2



\## 一、最高评价体系



本项目唯一最高评价体系：



系统价值 = 成片质量 × 产出速度 ÷ 开发与调用成本



当前任务不是继续扩建审计层、状态机或报告体系，而是直接解决两个已经被Owner通过成片确认的问题：



1\. 口播时长与视频时间轴脱节，造成结尾4–6秒非设计性无声；

2\. 当前视频虽然可用，但仍缺乏专业剪辑节奏、视听因果与蒙太奇审美。



本任务允许直接调整音频编排、导演规划、连续性校验和精确渲染架构。



最终必须输出6条重剪成片，与P12Q旧版本逐条A/B。



不得只生成架构报告、JSON或导演场记板后停止。



\---



\## 二、Owner对P12Q的真实反馈



P12Q共有6条成片。



\### V1A



状态：可测试



问题：



\* Hook提升一般；

\* 后约4秒无声；

\* 节奏断裂。



\### V1B



状态：可测试



优点：



\* Hook优于上一版本。



问题：



\* 后约4秒无声；

\* Closure节奏断裂。



\### V2A



状态：可测试



优点：



\* 8–12秒连续性正确。



问题：



\* 后约4秒无声。



\### V2B



状态：可测试



优点：



\* 8–12秒连续性正确。



问题：



\* 后约4秒无声。



\### V3A



状态：小改可用



问题：



\* 中段存在动作或画面截断；

\* 后约6秒无声；

\* 无声时长不可接受。



\### V3B



状态：可测试



问题：



\* 与V3A主要只在尾部画面不同；

\* 后约6秒无声；

\* 无声时长不可接受。



总体：



\* 6条均可测试；

\* 0条完全不可用；

\* 明显高于P12D；

\* 明显高于P11平均水平；

\* 当前架构值得继续；

\* 下一阶段必须解决严格音画同步与剪辑审美。



\---



\## 三、任务目标



本任务一次完成以下四件事：



1\. 新建精确口播时码编排器；

2\. 新建VLM语义导演规划器；

3\. 新建蒙太奇连续性校验器；

4\. 重剪并输出6条P12R新版本成片。



新增核心文件严格限定为3个：



\* `helpers/audio\_rhythm\_orchestrator.py`

\* `helpers/vlm\_director\_planner.py`

\* `helpers/continuity\_validator.py`



允许对以下现有模块进行最小必要修改：



\* Three Stage Compiler入口；

\* 现有shot matcher；

\* 现有actual render或FFmpeg封装；

\* 现有Edge-TTS调用入口。



禁止新建第二套完整剪辑流水线。



\---



\## 四、项目路径



项目根目录：



`C:\\Users\\43871\\AppData\\Local\\LFZ\_CODE\\agent-video-lab-233-laptop`



工作目录：



`C:\\Users\\43871\\AppData\\Local\\LFZ\_CODE\\agent-video-lab-233-laptop\\03\_tk\_video\_agent`



产品：



`dog\_stairs\_v1`



SKU：



`khaki`



批次：



`batch\_20260617\_001`



P12Q旧视频目录：



`products/dog\_stairs\_v1/outputs/renders/batch\_20260617\_001/P12Q\_refinement\_and\_six\_video\_controlled\_batch`



P12R新视频目录：



`products/dog\_stairs\_v1/outputs/renders/batch\_20260617\_001/P12R\_v2\_semantic\_rhythm\_orchestra\_ab\_upgrade`



VLM：



\* Provider：`zhipu`

\* Model：`glm-4.6v`



TTS：



\* Engine：Edge-TTS

\* Voice：`en-US-AvaNeural`



\---



\## 五、最小硬边界



只保留以下必要规则：



1\. `raw\_videos`绝对只读；

2\. API Key不得写入源码、日志、JSON或Git；

3\. Provider固定为`zhipu`；

4\. 请求与响应模型必须严格为`glm-4.6v`；

5\. 禁止模型fallback；

6\. 禁止破坏性Git和文件操作；

7\. 媒体与outputs保持Git ignored；

8\. 英文口播必须为Edge-TTS；

9\. 禁止Windows SAPI回退；

10\. 最终视频必须为1080×1920、SAR 1:1、9:16。



普通工程问题由Codex自主处理。



不得因非关键报告字段缺失停止成片生成。



\---



\## 六、总体架构



新管线必须为：



Asset Ledger

→ Narration Script Beats

→ Edge-TTS Word Boundary Stream

→ Acoustic Alignment Matrix

→ Semantic Breath Groups

→ Visual Candidate Retrieval

→ Multi-Candidate Director Planning

→ Local Montage Scoring

→ GLM-4.6V Storyboard Judge

→ Continuity Validator

→ Frame-Accurate Render

→ Final Audio-Visual QA

→ 6条A/B成片



核心原则：



\* 画面先确定商业角色；

\* 口播根据真实画面生成；

\* 音频生成后获得真实时码；

\* 时间线依据音频时码和完整动作重新锁定；

\* FFmpeg只执行已经通过校验的导演场记板；

\* VLM负责理解、比较和导演判断；

\* Python负责物理规则；

\* FFmpeg负责精确执行。



\---



\## 七、资产层复用原则



优先复用已有：



\* P12Q素材池；

\* P12Q图片VLM标签；

\* P12Q镜头来源；

\* P12K/P12N既有模型接入能力；

\* 现有Asset Ledger；

\* 现有Three Stage Compiler。



不得重新无差别扫描52条素材。



只对以下情况增加VLM：



\* 动作完整性未知；

\* 上楼或下楼方向未知；

\* 折叠或展开状态未知；

\* Proof镜头因果关系未知；

\* 两个候选Storyboard难以选择。



\---



\## 八、核心文件一：audio\_rhythm\_orchestrator.py



\### 8.1 职责



该模块负责将英文口播转换为精确、可用于剪辑的音频时间结构。



必须完成：



1\. 接收分段英文口播；

2\. 使用Edge-TTS生成真实音频；

3\. 从`Communicator.stream()`或当前edge-tts可用元数据中捕获WordBoundary；

4\. 同步保存音频字节；

5\. 读取最终真实音频总时长；

6\. 结合原文标点、单词边界间隙和实际静音检测生成呼吸组；

7\. 输出`audio\_alignment.json`；

8\. 为导演规划器提供合法切点与语义时间槽。



\---



\### 8.2 禁止伪造时码



禁止：



\* 按字符数量估算时长；

\* 按单词平均分配时长；

\* 按固定WPM生成单词时码；

\* 假设标点一定产生独立事件；

\* 将整段音频均分成若干块；

\* 使用固定每3秒切换逻辑。



如果当前edge-tts版本无法稳定返回WordBoundary：



允许依次使用：



1\. Edge-TTS流式边界元数据；

2\. Edge-TTS生成的字幕边界；

3\. 音频实际静音检测与文本标点联合对齐。



不得退回字符比例估算。



\---



\### 8.3 音频时码数据结构



每条视频生成：



`audio\_alignment.json`



至少包含：



```json

{

&#x20; "audio\_duration\_ms": 14820,

&#x20; "voice": "en-US-AvaNeural",

&#x20; "rate": "+2%",

&#x20; "words": \[

&#x20;   {

&#x20;     "text": "Built",

&#x20;     "start\_ms": 180,

&#x20;     "end\_ms": 510

&#x20;   }

&#x20; ],

&#x20; "breath\_groups": \[

&#x20;   {

&#x20;     "group\_id": "bg\_001",

&#x20;     "text": "Built for a safer climb.",

&#x20;     "start\_ms": 180,

&#x20;     "end\_ms": 2240,

&#x20;     "semantic\_role": "hook",

&#x20;     "trailing\_pause\_ms": 260

&#x20;   }

&#x20; ],

&#x20; "cut\_anchors": \[

&#x20;   {

&#x20;     "time\_ms": 2240,

&#x20;     "anchor\_type": "phrase\_end",

&#x20;     "strength": 0.92

&#x20;   }

&#x20; ],

&#x20; "tail\_silence\_ms": 280

}

```



\---



\### 8.4 呼吸组生成



视觉编排单位必须是：



`breath\_group`



不是单个单词。



一个breath group通常对应：



\* 一个短句；

\* 一个语义从句；

\* 一个强调词组；

\* 一个完整商业信息；

\* 一个自然呼吸段。



推荐时长：



\* Hook短句：600–1600ms；

\* Core短句：1200–2800ms；

\* Closure短句：1000–2500ms。



不得因为存在WordBoundary就逐词换镜头。



\---



\### 8.5 停顿识别



停顿必须综合判断：



\* 原文逗号、句号、破折号和问号；

\* 前一个单词结束时码；

\* 后一个单词开始时码；

\* 实际音频静音区间；

\* 当前语义是否完成。



停顿分为：



\* micro\_pause：80–180ms；

\* phrase\_pause：180–450ms；

\* strong\_pause：450–750ms；

\* abnormal\_silence：超过750ms且未被设计。



只有phrase\_pause和strong\_pause可以成为主要视觉切点。



不得把每个micro\_pause都用于切镜头。



\---



\### 8.6 严格口播节奏标准



每条视频必须满足：



\* 第一段语音在150–450ms内开始；

\* 非设计性内部连续静音不超过700ms；

\* 尾部静音不超过400ms；

\* 最后一句在视频结束前150–600ms结束；

\* Closure必须有对应口播；

\* 音频不得被截断；

\* 视频不得在完整单词中间结束；

\* TTS速率限制为`-8%`到`+8%`；

\* 语速自然优先于机械填满。



不得通过无意义文案填满视频。



\---



\## 九、核心文件二：vlm\_director\_planner.py



\### 9.1 职责



该模块不是普通标签器。



它负责：



1\. 读取现有Asset Ledger；

2\. 读取`audio\_alignment.json`；

3\. 读取三段式商业骨架；

4\. 读取已通过视频的风格参数；

5\. 检索与每个breath group语义匹配的视觉候选；

6\. 生成多套导演场记板；

7\. 为每个镜头提供可解释选片原因；

8\. 调用GLM-4.6V比较最优候选Storyboard；

9\. 输出最终`director\_slate.json`。



\---



\### 9.2 绝对规则



音频时码是最终时间轴的主坐标系。



视觉镜头必须映射到：



\* breath group；

\* 语义角色；

\* 动作边界；

\* 合法cut anchor。



但不得为了完全贴合短句而截断完整动作。



优先级：



完整动作



> 视听语义同步

> 呼吸点切换

> 精确时长

> 固定视频总时长



必要时允许视频总时长在12–18秒内动态变化。



\---



\### 9.3 导演场记板结构



每条视频输出：



`director\_slate.json`



至少包含：



```json

{

&#x20; "variant\_id": "V2A\_feature\_proof\_v2",

&#x20; "audio\_duration\_ms": 14720,

&#x20; "video\_duration\_ms": 15020,

&#x20; "timeline": \[

&#x20;   {

&#x20;     "sequence": 1,

&#x20;     "semantic\_role": "hook",

&#x20;     "audio\_group\_id": "bg\_001",

&#x20;     "audio\_start\_ms": 180,

&#x20;     "audio\_end\_ms": 1620,

&#x20;     "assigned\_clip\_id": "clip\_014",

&#x20;     "source\_path": "source.mp4",

&#x20;     "source\_in\_ms": 2100,

&#x20;     "source\_out\_ms": 3650,

&#x20;     "timeline\_in\_ms": 0,

&#x20;     "timeline\_out\_ms": 1550,

&#x20;     "shot\_scale": "close\_up",

&#x20;     "primary\_action": "paw\_contact",

&#x20;     "action\_completeness": "complete",

&#x20;     "motion\_direction": "forward",

&#x20;     "reasoning": "The paw contact visually proves the opening claim and creates an immediate tactile hook."

&#x20;   }

&#x20; ]

}

```



\---



\### 9.4 候选计划生成



每条视频必须生成4套候选：



1\. `grammar\_baseline`



&#x20;  \* 使用确定性剪辑文法生成；



2\. `rhythm\_first`



&#x20;  \* 优先呼吸组与重音切点；



3\. `continuity\_first`



&#x20;  \* 优先完整动作、方向和状态连续；



4\. `vlm\_directed`



&#x20;  \* 由GLM-4.6V基于语义与参考风格生成。



不得直接接受唯一VLM时间线。



\---



\### 9.5 VLM输入



VLM Director输入必须限制为：



\* 当前视频三段式结构；

\* breath groups；

\* cut anchors；

\* 高置信度Asset Ledger候选；

\* 镜头contact sheets；

\* 必要的视频动作摘要；

\* 参考风格参数；

\* 当前商业卖点。



不得上传全部52条原片。



不得让VLM直接生成FFmpeg命令。



\---



\### 9.6 Storyboard Judge



4套候选先经过本地评分。



只将本地评分前2名发送给GLM-4.6V进行一次Storyboard比较。



每条最多：



\* 1次Storyboard Judge。



Judge必须评价：



\* Hook是否在3秒内成立；

\* 口播和画面是否逐段对应；

\* 动作是否完整；

\* Proof是否真的证明Feature；

\* 景别是否有变化；

\* 镜头是否重复；

\* 节奏是否拖沓；

\* Closure是否完整；

\* 是否符合高端宠物家具与TikTok节奏。



输出：



\* winner；

\* score\_A；

\* score\_B；

\* audiovisual\_cohesion\_score；

\* rhythm\_score；

\* continuity\_score；

\* aesthetic\_score；

\* risks；

\* recommended\_adjustment。



\---



\## 十、核心文件三：continuity\_validator.py



\### 10.1 职责



该模块是FFmpeg渲染前的白盒校验器。



必须区分：



\* hard violations；

\* soft penalties。



不得把所有审美偏好都写成硬阻断。



\---



\### 10.2 硬阻断规则



以下情况必须阻断：



1\. 同一原片的相邻窗口存在明显重叠或重复帧；

2\. 标记为完整动作的镜头实际截断起点或结果；

3\. Outcome使用`incomplete`动作；

4\. 口播说`fold`，视觉资产不存在折叠或形态变化证据；

5\. 口播说`non-slip`，视觉不存在踏面、脚掌接触或稳定通过证据；

6\. Proof与Feature不存在可解释因果关系；

7\. 相邻镜头产品状态互相矛盾；

8\. 相邻动作方向发生无法解释的反转；

9\. timeline总时长与音频实际时长偏差超过600ms；

10\. 非设计性尾部静音超过400ms；

11\. 音频在单词中间被截断；

12\. source\_in\_ms或source\_out\_ms越界；

13\. 视频镜头不足以覆盖对应breath group。



硬阻断状态：



`BLOCKED\_BY\_MONTAGE\_VIOLATION`



阻断后只允许：



\* 替换违规镜头；

\* 调整入点或出点；

\* 选择下一候选计划；

\* 重新生成该条导演场记板。



不得停止整个6条批次。



\---



\### 10.3 软扣分规则



以下只扣分，不直接阻断：



\* 相邻镜头景别相同；

\* 连续两个Wide Shot；

\* 连续构图相似；

\* 单个静态镜头略长；

\* 镜头变化不足；

\* Hook张力普通；

\* Closure视觉偏弱；

\* 同一主体连续出现时间过长；

\* 产品镜头偏展厅感；

\* 节奏变化不足。



只有综合评分低于阈值时才选择其他候选。



\---



\### 10.4 镜头时长动态范围



不得使用统一500–4000ms硬区间。



按角色设置：



\#### Hook



\* 快速信息镜头：550–1400ms；

\* 高冲突完整动作允许延长至2200ms。



\#### Core



\* 静态说明：900–2200ms；

\* Demonstration：1200–3500ms；

\* 完整上楼、下楼、折叠或展开：允许最长5000ms。



\#### Closure



\* 1200–3000ms；

\* 必须有Closure Voice；

\* 不得留下长时间空白Hero。



任何镜头都不得为了满足时长而截断关键动作。



\---



\### 10.5 本地候选评分



总分100。



\#### 视听因果一致性：30分



\* 每个breath group是否有对应视觉；

\* Claim是否有证据；

\* 音画是否同步。



\#### 动作与叙事连续性：25分



\* 动作完整；

\* 方向连续；

\* 产品状态连续；

\* Outcome成立。



\#### 节奏：20分



\* Cut是否落在合法锚点；

\* 镜头时长是否自然；

\* 无拖沓和碎切。



\#### Hook：10分



\* 1秒内出现主体；

\* 3秒内完成认知。



\#### 视觉变化：10分



\* 景别、构图、主体和信息变化。



\#### Closure：5分



\* 音画共同收束。



本地得分低于75不得渲染。



\---



\## 十一、风格参考与剪辑审美



使用以下通过Owner验证的视频抽取风格参数：



\* P12P V3；

\* P12Q V1B；

\* P12Q V2A；

\* P12Q V3B。



只抽取参数，不复制原时间线。



风格参数至少包括：



\* 平均镜头时长；

\* Hook镜头数量；

\* Core镜头数量；

\* Closure镜头数量；

\* 景别变化序列；

\* 动作镜头平均时长；

\* 静态镜头平均时长；

\* 前3秒信息密度；

\* Core证明链结构；

\* Closure稳定时长；

\* 口播开始时间；

\* 口播结束时间；

\* 设计停顿范围。



保存到现有配置目录：



`configs/editorial\_style\_profile\_v2.json`



该配置不是新的核心工程模块。



\---



\## 十二、剪辑文法



\### 12.1 Hook：0–3秒



必须：



\* 第一帧出现狗、产品、动作或结果；

\* 1秒内建立主体关系；

\* 3秒内表达痛点、卖点或结果；

\* 口播在150–450ms内开始；

\* 使用1–3个镜头；

\* 不允许空镜建立。



切点优先：



\* 强重音后；

\* 短句结束；

\* 动作开始；

\* 结果揭示；

\* 景别变化点。



\---



\### 12.2 Core



Core必须形成一条明确因果链：



\* pain → intervention → outcome；

\* feature → demonstration → proof；

\* situation → usage → lifestyle payoff。



禁止：



\* 只有功能介绍，没有证明；

\* 只有狗动作，没有产品关系；

\* 只有产品Hero，没有剧情推进；

\* 同一动作重复两次；

\* 口播说A，画面显示B。



\---



\### 12.3 Closure



Closure必须同时包含：



\* 视觉结果；

\* 最后一个价值句；

\* 明确音频收束。



Closure Voice结束后只允许150–400ms视觉余韵。



不得再出现4–6秒无声尾巴。



\---



\### 12.4 Cut Anchor



允许切镜的优先级：



1\. 完整动作边界；

2\. strong pause；

3\. phrase pause；

4\. 语义角色转换；

5\. 画面运动自然遮挡点；

6\. 景别变化点。



禁止仅因为固定时长到达而切镜。



\---



\## 十三、精确渲染架构



为了保证严格毫秒同步，允许修改现有FFmpeg封装。



\### 13.1 禁止



不得对任意毫秒入点、出点直接依赖纯`-c copy`拼接。



不得假设Stream Copy可以稳定实现帧级精确切片。



\---



\### 13.2 正确流程



剪辑片段必须：



1\. 使用精确`source\_in\_ms`和`source\_out\_ms`；

2\. 解码到帧域；

3\. 使用`trim`、`setpts`或等价精确方案；

4\. 统一输出：



&#x20;  \* 1080×1920；

&#x20;  \* 固定帧率；

&#x20;  \* SAR 1:1；

&#x20;  \* H.264；

&#x20;  \* yuv420p；

5\. 片段时间戳从0开始；

6\. 按director slate顺序拼接；

7\. 音频使用实际Edge-TTS时间轴；

8\. 最终音视频长度偏差控制在100ms以内。



只有在最终视频流与音频流时间戳已经验证一致时，最终封装阶段才允许Stream Copy。



\---



\### 13.3 音画同步标准



每个breath group必须记录：



\* audio\_start\_ms；

\* audio\_end\_ms；

\* visual\_start\_ms；

\* visual\_end\_ms；

\* sync\_error\_ms。



要求：



\* 语义段开始偏差不超过150ms；

\* 强调词对应视觉揭示偏差不超过250ms；

\* Closure尾部偏差不超过200ms；

\* 总音视频时长偏差不超过100ms。



\---



\## 十四、VLM算力注入范围



更多VLM调用只有在直接提升成片时才允许。



本轮新增上限：



\### 视频动作验证



最多6次。



仅用于：



\* 完整上楼；

\* 完整下楼；

\* 折叠；

\* 展开；

\* 稳定性证明；

\* 动作方向歧义。



\### Storyboard Judge



每条最多1次。



6条最多6次。



\### 图片补标



最多4次。



仅用于缺少高置信度景别、场景或静态Proof的候选。



\### 总量



新增成功请求不超过16次。



总尝试不超过22次。



不得重复调用已经有高置信度结果的素材。



\---



\## 十五、六条重剪视频



必须生成：



\* `V1A\_pain\_solution\_v2.mp4`

\* `V1B\_pain\_solution\_v2.mp4`

\* `V2A\_feature\_proof\_v2.mp4`

\* `V2B\_feature\_proof\_v2.mp4`

\* `V3A\_lifestyle\_value\_v2.mp4`

\* `V3B\_lifestyle\_value\_v2.mp4`



对应旧版：



\* P12Q V1A；

\* P12Q V1B；

\* P12Q V2A；

\* P12Q V2B；

\* P12Q V3A；

\* P12Q V3B。



不得只在旧视频尾部补充口播。



每条必须重新执行：



\* 口播分段；

\* TTS生成；

\* WordBoundary捕获；

\* breath group生成；

\* 候选计划；

\* Storyboard比较；

\* 连续性校验；

\* 精确渲染。



\---



\## 十六、单条改进目标



\### V1A



\* 提高Hook张力；

\* 修复4秒无声；

\* 确保痛点与Outcome因果成立。



\### V1B



\* 保留已有Hook优势；

\* 修复4秒无声；

\* Closure Voice必须完整。



\### V2A



\* 保留8–12秒连续证明链；

\* 修复4秒无声；

\* Proof与防滑或稳定卖点严格匹配。



\### V2B



\* 保留产品结构证明；

\* 增加合理景别变化；

\* 减弱纯展厅感；

\* 修复4秒无声。



\### V3A



\* 修复中段动作截断；

\* 修复6秒无声；

\* 保持整体流畅。



\### V3B



\* Core必须与V3A真正不同；

\* 强化2-in-1或家居价值；

\* 修复6秒无声。



\---



\## 十七、最小测试



只新增一个主要测试文件：



`tests/test\_semantic\_rhythm\_orchestra.py`



必须覆盖：



1\. WordBoundary解析；

2\. breath group生成；

3\. pause分类；

4\. tail silence检查；

5\. 音频时长与时间线误差；

6\. director slate字段；

7\. Outcome不得使用incomplete动作；

8\. Claim与视觉证据匹配；

9\. 重叠窗口阻断；

10\. 同景别只软扣分；

11\. 动作完整性优先；

12\. 精确渲染时长；

13\. 最终音画偏差不超过100ms。



只运行：



\* 本任务focused tests；

\* 现有TTS smoke test；

\* 现有GLM模型绑定检查；

\* 现有9:16检查；

\* Git媒体安全检查。



不得为了追求全量测试数字延迟成片交付。



\---



\## 十八、输出目录



输出到：



`products/dog\_stairs\_v1/outputs/renders/batch\_20260617\_001/P12R\_v2\_semantic\_rhythm\_orchestra\_ab\_upgrade`



至少包含：



\* 6条P12R新视频；

\* 6份`audio\_alignment.json`；

\* 6份`director\_slate.json`；

\* 6份`montage\_validation.json`；

\* 6份分段英文口播；

\* 每条4套候选计划；

\* 每条本地候选评分；

\* 每条Storyboard Judge结果；

\* 每条镜头来源；

\* VLM调用统计；

\* 总渲染时间；

\* `review\_index.md`。



\---



\## 十九、review\_index.md



第一页必须直接展示A/B信息。



每条包含：



\* P12Q旧视频路径；

\* P12R新视频路径；

\* 旧视频时长；

\* 新视频时长；

\* 旧版尾部无声时长；

\* 新版尾部无声时长；

\* 新版内部最大非设计性静音；

\* 新版音画总时长误差；

\* 新版本地审美评分；

\* Storyboard Judge选择结果；

\* 主要改动；

\* 建议Owner重点观看时间点。



汇总：



\* 6条消除长尾无声数量；

\* 6条动作完整数量；

\* 6条视听因果通过数量；

\* 6条审美评分；

\* V3A截断修复状态；

\* V3A/V3B差异状态；

\* 新增视频VLM次数；

\* Storyboard Judge次数；

\* 新增Token；

\* 总开发与渲染时间。



\---



\## 二十、最终通过标准



\### 严格音画同步



6条必须全部满足：



\* 尾部非设计性静音不超过400ms；

\* 内部非设计性静音不超过700ms；

\* Closure Voice存在；

\* 音频未截断；

\* 音视频总时长偏差不超过100ms；

\* 强调词和视觉揭示偏差不超过250ms；

\* 不再出现固定时长空等音频。



\### 剪辑连续性



至少5条满足：



\* 不截断关键动作；

\* 无重复帧跳切；

\* 无无法解释的运动方向反转；

\* 无产品状态矛盾；

\* Proof与Feature匹配；

\* Outcome完整。



\### 审美提升



至少4条满足：



\* 明显优于P12Q对应旧版本；

\* 节奏有层次；

\* 景别变化合理；

\* 音画关系紧密；

\* 不像机械等分剪辑；

\* 不需要Owner逐镜重剪。



\### 单项要求



\* V3A中段截断必须修复；

\* V3A与V3B必须拥有不同Core；

\* V2A/V2B必须保持8–12秒连续性；

\* V1B不得丢失Hook优势。



\---



\## 二十一、VLM价值归因



生成：



`vlm\_value\_attribution.json`



只记录：



\* VLM验证了哪些动作；

\* VLM排除了哪些错误镜头；

\* VLM选择了哪些Storyboard；

\* VLM候选是否最终获胜；

\* VLM调用是否改变最终成片；

\* 新增Token；

\* 对应成片质量变化。



不得以调用次数本身证明模型有价值。



VLM价值必须体现在：



\* 动作更完整；

\* 镜头方向更正确；

\* Storyboard更优；

\* Proof更准确；

\* 最终成片更好。



\---



\## 二十二、最终输出格式



完成后只输出：



SEMANTIC\_RHYTHM\_ORCHESTRA\_AB\_READY



视频目录：

V1A新版本：

V1B新版本：

V2A新版本：

V2B新版本：

V3A新版本：

V3B新版本：

6条视频时长：

6条尾部静音：

6条最大内部非设计性静音：

6条音画总时长误差：

6条本地审美评分：

视频VLM调用数：

Storyboard Judge调用数：

图片补标调用数：

新增VLM总Token：

总开发与渲染时间：

V3A截断修复结果：

V3A/V3B差异结果：

VLM价值归因摘要：

主要已知问题：

建议A/B观看顺序：



然后停止等待Owner观看。



\---



\## 二十三、执行顺序



1\. 验证本Task；

2\. 确认`spec\_version = P12R-v2`；

3\. 读取P12Q六条视频、脚本、计划和素材池；

4\. 新建`audio\_rhythm\_orchestrator.py`；

5\. 新建`vlm\_director\_planner.py`；

6\. 新建`continuity\_validator.py`；

7\. 对现有渲染模块做精确切片的最小调整；

8\. 从已通过视频提取`editorial\_style\_profile\_v2.json`；

9\. 复用已有Asset Ledger；

10\. 只对动作歧义候选增加视频VLM；

11\. 为每条生成分段英文口播；

12\. 生成Edge-TTS并捕获真实边界；

13\. 生成word alignment、breath groups和cut anchors；

14\. 每条生成4套候选director slate；

15\. 本地评分并保留前2套；

16\. 每条执行一次Storyboard Judge；

17\. continuity validator校验；

18\. 对违规计划局部修复或选用下一候选；

19\. 使用帧级精确方案渲染6条P12R视频；

20\. 检查尾部静音、内部静音和音画误差；

21\. 检查动作完整性和蒙太奇连续性；

22\. 生成A/B review\_index；

23\. 生成VLM价值归因；

24\. 输出6条视频路径和核心指标；

25\. 停止等待Owner观看。



本任务的成功由严格音画同步与最终成片审美共同决定。



