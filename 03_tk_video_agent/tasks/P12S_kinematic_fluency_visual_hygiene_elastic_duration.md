\# TASK：P12S\_KINEMATIC\_FLUENCY\_VISUAL\_HYGIENE\_ELASTIC\_DURATION



spec\_version: P12S-v1



\## 一、最高评价体系



本项目继续严格执行：



系统价值 = 成片质量 × 产出速度 ÷ 开发与调用成本



P12R-v2已经解决：



\* 长尾无声；

\* 基础音画同步；

\* 呼吸组编排；

\* 候选Storyboard比较；

\* 帧级精确渲染。



但Owner通过最终成片确认，仍存在三个核心问题：



1\. 部分后续镜头出现人手，破坏产品内容的纯净感；

2\. V3A仍出现动作或画面截断；

3\. 系统需要在视频精简度与动作流畅度之间建立弹性时长策略。



本任务允许直接升级现有架构。



本任务不得增加新的核心工程模块，而是修改现有：



\* `helpers/audio\_rhythm\_orchestrator.py`

\* `helpers/vlm\_director\_planner.py`

\* `helpers/continuity\_validator.py`

\* 当前精确渲染入口



允许新增一个配置文件：



`configs/editorial\_constraints\_v1.json`



最终必须直接输出6条P12S成片，与P12R逐条A/B。



\---



\## 二、Owner真实反馈



\### V1A



\* P12R优于P12Q；

\* 音画逐句对应；

\* 无明显拖沓；

\* 20秒时长尚可。



\### V1B



\* P12R优于P12Q；

\* Hook优势保留；

\* 音画逐句对应；

\* 中间存在两处人手画面。



Owner要求：



人手画面必须在后续架构中写死处理。



只允许以下两种例外：



1\. 人手执行产品展开或折叠等不可替代操作；

2\. 人手作为第一帧或极短Hook的一部分。



除以上情况外，后续画面出现人手必须由VLM深度检查并淘汰。



\### V2A



\* 整体可用；

\* 8–12秒证明链保持；

\* 口播不过满。



\### V2B



\* 整体可用；

\* 景别变化存在，但不明显；

\* 展厅感有所减弱，但仍可继续优化。



\### V3A



\* 中段截断问题仍未完全消失；

\* 可能存在原素材动作不完整；

\* 必须在VLM动作审查和连续性校验中写入严格规则。



\### V3B



\* 整体提升一般；

\* 与V3A的Core差异一般；

\* 音画呼吸感一般。



总体：



\* 成片均可作为素材使用；

\* 当前架构有效；

\* 尚未出现质的剪辑审美跃迁；

\* 下一阶段先建立动作完整性、视觉卫生、弹性时长和运镜连续性系统；

\* 不得因为追求绝对精简而牺牲画面流畅度。



\---



\## 三、本任务核心目标



本任务一次完成四项升级：



\### 目标一：视觉卫生规则



严格过滤：



\* 人手；

\* 人脸；

\* 人体；

\* 与产品无关的工作人员动作；

\* 展厅干扰；

\* 无关背景行为。



\### 目标二：动作生命周期与硬阻断



所有动态候选必须具备明确动作生命周期。



Outcome、Proof、Transformation不得使用截断动作。



\### 目标三：动态视听解耦



使用：



\* L-Cut；

\* J-Cut；

\* 有界变速；

\* 弹性呼吸槽位；

\* 动作前后保护帧。



不得再强制视觉切点与语音切点完全重合。



\### 目标四：弹性时长策略



视频时长由：



\* 有效口播；

\* 完整动作；

\* 商业结构；

\* Closure；



共同决定。



不得机械固定为15秒或18秒。



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



P12R输入目录：



`products/dog\_stairs\_v1/outputs/renders/batch\_20260617\_001/P12R\_v2\_semantic\_rhythm\_orchestra\_ab\_upgrade`



P12S输出目录：



`products/dog\_stairs\_v1/outputs/renders/batch\_20260617\_001/P12S\_kinematic\_fluency\_visual\_hygiene\_elastic\_duration`



VLM：



\* Provider：`zhipu`

\* Model：`glm-4.6v`



TTS：



\* Edge-TTS

\* `en-US-AvaNeural`



\---



\## 五、最小硬边界



仅保留以下硬规则：



1\. `raw\_videos`绝对只读；

2\. API Key不得写入源码、JSON、日志或Git；

3\. Provider固定为`zhipu`；

4\. 请求与响应模型必须严格为`glm-4.6v`；

5\. 禁止模型fallback；

6\. 禁止破坏性Git和文件操作；

7\. 媒体与outputs保持Git ignored；

8\. TTS必须使用Edge-TTS；

9\. 禁止Windows SAPI回退；

10\. 最终视频必须为1080×1920、SAR 1:1、9:16。



普通工程问题由Codex自主处理。



不得扩建数据库、状态机、任务队列或大型审计系统。



\---



\## 六、视觉卫生策略



修改或新增配置：



`configs/editorial\_constraints\_v1.json`



至少包含：



```json

{

&#x20; "human\_visibility\_policy": {

&#x20;   "default\_action": "reject",

&#x20;   "allowed\_contexts": \[

&#x20;     "opening\_hook",

&#x20;     "product\_transformation"

&#x20;   ],

&#x20;   "opening\_hook\_max\_ms": 800,

&#x20;   "transformation\_max\_ms": 1500,

&#x20;   "face\_allowed": false,

&#x20;   "body\_allowed": false,

&#x20;   "hand\_after\_hook\_allowed": false

&#x20; }

}

```



\---



\## 七、人手检测字段



所有进入最终候选池的镜头必须包含：



\* `hand\_present`

\* `human\_face\_present`

\* `human\_body\_present`

\* `hand\_start\_ms`

\* `hand\_end\_ms`

\* `hand\_duration\_ms`

\* `hand\_action`

\* `hand\_interaction\_target`

\* `allowed\_hand\_context`

\* `human\_intrusion\_score`

\* `visual\_hygiene\_result`

\* `visual\_hygiene\_reason`



\---



\## 八、人手硬规则



\### 8.1 默认规则



除明确例外外：



```text

hand\_present = true

→ hard reject

```



任何人脸或明显人体进入产品画面：



```text

human\_face\_present = true

或 human\_body\_present = true

→ hard reject

```



\---



\### 8.2 允许场景一：Opening Hook



只有当人手直接构成Hook信息时才允许。



要求：



\* 必须位于视频最开始；

\* 总出现时长不超过800ms；

\* 必须直接接触产品；

\* 不得出现人脸或明显人体；

\* 不得只是无关手部掠过；

\* 第出现时长不超过800ms；

\* 必须直接接触产品；

\* 不得出现人脸或明显一个Hook镜头结束后，后续镜头不允许再出现人手。



如果Hook后任意镜头检测到人手：



```text

HARD\_REJECT\_HAND\_AFTER\_HOOK

```



\---



\### 8.3 允许场景二：产品展开或折叠



只允许以下动作：



\* unfold；

\* fold；

\* open；

\* close；

\* lock；

\* release。



要求：



\* 人手是完成动作的必要主体；

\* 总时长不超过1500ms；

\* 不得出现人脸或完整人体；

\* 镜头必须明确展示产品状态变化；

\* 不得把普通触摸、搬动、扶持包装为Transformation；

\* 该镜头只能承担`transformation`或`demonstration`角色。



其他角色出现人手必须拒绝。



\---



\### 8.4 最终候选深度检查



只对即将进入最终Storyboard的候选执行深度审核。



每个候选：



\* 每250ms抽取一帧；

\* 生成contact sheet；

\* 使用GLM-4.6V检查人手、人脸、人体和无关工作人员；

\* 动态候选可结合短视频代理检查；

\* 如果VLM结论为uncertain，默认拒绝；

\* 不得因为本地粗标签为false而跳过最终审核。



不得对全部52条素材无差别进行深度检测。



\---



\## 九、动作生命周期数据结构



动态镜头必须包含：



\* `action\_type`

\* `action\_subject`

\* `kinematic\_prepare\_start\_ms`

\* `kinematic\_start\_ms`

\* `kinematic\_peak\_ms`

\* `kinematic\_completion\_ms`

\* `kinematic\_settle\_end\_ms`

\* `min\_viable\_source\_duration\_ms`

\* `action\_completeness`

\* `can\_be\_speed\_adjusted`

\* `max\_natural\_playback\_speed`

\* `requires\_preroll\_ms`

\* `requires\_postroll\_ms`



动作阶段：



```text

prepare

→ onset

→ peak

→ completion

→ settle

```



\---



\## 十、角色与动作完整性



\### Outcome



必须包含：



\* action onset；

\* action completion；

\* result state；

\* settle。



不得使用：



\* incomplete；

\* onset\_only；

\* completion\_missing；

\* result\_not\_visible。



\### Proof



必须包含：



\* 被证明的Feature；

\* 真实Demonstration；

\* 明确结果。



例如：



```text

non-slip

→ paw contact

→ stable passage

```



不得只有脚掌特写，没有稳定通过结果。



\### Transformation



必须包含：



\* 原始状态；

\* 状态变化过程；

\* 最终状态。



折叠一半或展开一半不得作为完整Transformation。



\### Hook



允许使用部分动作制造悬念，但必须标记：



`intentional\_partial\_hook = true`



该镜头不得同时承担Outcome或Proof。



\---



\## 十一、动作保护帧



完整动作窗口除生命周期本体外，必须保留：



\* 动作前保护：150–350ms；

\* 动作后保护：250–500ms。



动作前保护用于：



\* 建立主体；

\* 避免动作突然开始。



动作后保护用于：



\* 展示落点；

\* 展示产品最终状态；

\* 防止动作刚完成便被切走。



不得用保护帧制造无意义拖沓。



\---



\## 十二、L-Cut与J-Cut



\### L-Cut



当下一段口播已经开始，但当前视觉动作尚未完成：



允许视觉跨越声音边界继续播放。



默认范围：



\* 150–450ms；

\* 宏观产品动作最高600ms；

\* 狗运动建议不超过400ms。



要求：



\* 下一段口播语义不得与当前画面冲突；

\* 当前画面必须处于completion或settle阶段；

\* 不得跨越一个完整的新语义段。



\### J-Cut



当下一段声音可以提前建立预期时：



允许新声音先进入，随后画面切换。



默认范围：



\* 120–350ms。



适用：



\* 从Pain进入Solution；

\* 从Feature进入Demonstration；

\* 从Situation进入Usage。



不得在核心Claim尚未有视觉证据时提前过久播放。



\---



\## 十三、有界变速策略



变速不是默认行为。



优先级：



1\. L-Cut或J-Cut；

2\. 调整口播文案；

3\. 调整非关键镜头；

4\. 轻量变速；

5\. 动态延长视频时长。



\---



\### 13.1 正确公式



定义：



```text

source\_duration = 原始动作时长

target\_duration = 目标时间槽长度

playback\_speed = source\_duration / target\_duration

```



FFmpeg：



```text

setpts=PTS/playback\_speed

```



例如：



```text

source\_duration = 2500ms

target\_duration = 2000ms

playback\_speed = 1.25

setpts=PTS/1.25

```



\---



\### 13.2 狗动作速度限制



狗的：



\* climbing；

\* descending；

\* jumping；

\* paw placement；

\* hesitation；



自然播放速度范围：



```text

1.00x–1.08x

```



只有动作仍然自然时才允许。



超过1.08x：



```text

HARD\_REJECT\_UNNATURAL\_ANIMAL\_SPEED

```



不得使用明显加速的狗动作换取精简度。



\---



\### 13.3 产品动作速度限制



产品：



\* fold；

\* unfold；

\* open；

\* close；

\* transform；



播放速度范围：



```text

1.00x–1.25x

```



前提：



\* 状态变化仍然清楚；

\* 手部动作不显得抽搐；

\* 产品结构细节仍可辨认；

\* 不跳过中间关键状态。



\---



\### 13.4 不允许变速的镜头



以下镜头不得依靠加速解决时长：



\* 产品Hero；

\* 情绪停顿；

\* 狗最终落点；

\* Stability Proof；

\* Closure；

\* 需要用户观察细节的特写。



\---



\## 十四、设计停顿



不得再使用400–800ms无声作为默认垫片。



设计停顿范围：



\### Micro Pause



80–180ms



用于自然语言停顿，不作为主要剪辑槽。



\### Phrase Pause



180–350ms



可作为正常切镜锚点。



\### Strong Reveal Pause



350–500ms



只用于：



\* 产品最终展开；

\* 狗成功到达；

\* 关键Proof揭示；

\* 形态转换结果。



超过500ms必须具有明确的视觉高潮或环境音支撑。



不得通过纯无声填充时长。



\---



\## 十五、弹性时长策略



最终视频时长是编译结果，不是预先固定值。



定义：



```text

T\_audio = 有效口播总时长

T\_action\_floor = 所有关键完整动作所需的最小时长

T\_story\_floor = 三段式角色成立所需的最小时长

T\_closure = Closure所需时长

```



最终目标：



```text

T\_target = max(

&#x20;   T\_audio + 尾部余韵,

&#x20;   T\_action\_floor,

&#x20;   T\_story\_floor

)

```



\---



\### 15.1 时长分级



\#### 快节奏型



```text

13–16秒

```



适合：



\* 静态功能；

\* 单一Proof；

\* 不包含宏观完整动作。



\#### 标准叙事型



```text

16–21秒

```



适合：



\* 1–2个完整动作；

\* Pain → Solution → Outcome；

\* Feature → Demonstration → Proof。



\#### 动作展示型



```text

21–24秒

```



适合：



\* 完整上楼或下楼；

\* 产品折叠或展开；

\* 双形态展示；

\* 多阶段证明。



\---



\### 15.2 超时处理



如果自然编译时长超过24秒，依次执行：



1\. 删除重复语义句；

2\. 删除重复视觉证明；

3\. 合并相邻breath groups；

4\. 替换冗余镜头；

5\. 对产品动作进行有界变速；

6\. 重新选择更紧凑的完整动作素材。



禁止：



\* 截断关键动作；

\* 将动物运动加速到不自然；

\* 删除Closure；

\* 强行卡入15秒；

\* 用短画面反复循环填补声音。



\---



\## 十六、时长裁决优先级



当精简度与流畅度冲突时，优先级为：



1\. 动作完整性；

2\. 视听因果；

3\. 自然运动速度；

4\. 叙事闭环；

5\. 口播节奏；

6\. 视频精简度；

7\. 固定目标时长。



因此：



```text

20秒流畅完整视频

优于

15秒动作截断视频

```



\---



\## 十七、剪辑审美体系



剪辑审美不得只由镜头时长决定。



必须同时评价：



\* 景别序列；

\* 构图变化；

\* 主体运动；

\* 相机运动；

\* 动作方向；

\* 视觉能量曲线；

\* 音画揭示点；

\* 商业Claim；

\* Closure余韵。



\---



\## 十八、运镜和运动连续性



Asset Ledger及最终候选增加：



\* `camera\_motion`

\* `camera\_motion\_direction`

\* `subject\_motion\_direction`

\* `motion\_energy`

\* `composition\_center`

\* `visual\_entry\_direction`

\* `visual\_exit\_direction`



相机运动类型：



\* static；

\* pan\_left；

\* pan\_right；

\* tilt\_up；

\* tilt\_down；

\* push\_in；

\* pull\_out；

\* handheld；

\* follow。



\---



\### 18.1 运动匹配



优先：



\* 同方向动作连续；

\* 主体从左出，下一个镜头从左或中央进入；

\* Push-in后接Close-up；

\* 动作镜头后接稳定结果镜头；

\* 快运动后接稳定Proof或Closure。



避免：



\* 左向运动突然接右向运动；

\* Push-in突然接无关Wide；

\* 连续三个静态远景；

\* 连续多个同构图产品Hero；

\* 狗位置无理由跳变。



\---



\### 18.2 数字运镜限制



允许对高分辨率静态镜头使用轻微数字运镜：



\* 缩放幅度：最多2%–4%；

\* 只用于静态Hero或细节；

\* 必须平滑；

\* 不得降低主体清晰度。



禁止：



\* 大幅数字推拉；

\* 廉价Ken Burns；

\* 无意义左右平移；

\* 快速缩放；

\* 与高端家居定位冲突的转场。



\---



\## 十九、VLM算力路由



更多VLM算力必须用在高价值位置。



\### 19.1 最终候选视觉卫生审核



每条成片的最终候选镜头必须进行审核。



重点检测：



\* 人手；

\* 人脸；

\* 人体；

\* 无关工作人员；

\* 展厅干扰；

\* 截断动作；

\* 产品状态异常；

\* 口播与画面不符。



允许结合：



\* contact sheet；

\* 短视频代理；

\* Asset Ledger。



\---



\### 19.2 视频动作VLM



最多新增8次。



只用于：



\* Outcome；

\* Proof；

\* Transformation；

\* 完整上楼；

\* 完整下楼；

\* 折叠；

\* 展开；

\* 人手出现时段确认。



同一次请求应同时判断：



\* 动作生命周期；

\* 人手；

\* 运动方向；

\* 产品状态；

\* 角色适用性。



不得拆成多个重复请求。



\---



\### 19.3 Storyboard Judge



不再每条固定调用。



只有当本地前两套候选：



```text

score\_gap < 5

```



时才调用GLM-4.6V Judge。



最多3次。



如果本地第一名比第二名高5分或以上：



直接选择本地第一名。



避免为无争议决策浪费VLM调用。



\---



\### 19.4 图片补标



最多4次。



只用于：



\* 人手不确定；

\* 景别不确定；

\* 产品状态不确定；

\* Closure候选不确定。



不得重新扫描已有高置信度素材。



\---



\## 二十、连续性硬阻断



修改`continuity\_validator.py`。



以下情况必须Hard Reject：



1\. Outcome或Proof使用不完整动作；

2\. 动作缺少completion或settle；

3\. 产品折叠或展开停在中间状态；

4\. 狗动作被截断在悬空、转身或踏步中间；

5\. 后续普通画面出现人手；

6\. 人脸或人体出现；

7\. 人手出现但不属于明确开合操作；

8\. Hook后再次出现人手；

9\. 产品状态前后矛盾；

10\. 动作方向无理由反转；

11\. 口播Claim无视觉证据；

12\. 变速超过主体允许范围；

13\. L-Cut或J-Cut造成语义冲突；

14\. 结尾无Closure；

15\. 非设计性长静音重新出现。



不得因为一条违规停止整个批次。



应：



\* 更换镜头；

\* 调整入点和出点；

\* 选择下一候选；

\* 局部重排该条视频。



\---



\## 二十一、本地审美评分



总分100。



\### 视听因果：25分



\* 每句口播有对应视觉；

\* Claim有证据；

\* 揭示点准确。



\### 动作完整性：20分



\* 生命周期完整；

\* 无动作截断；

\* Outcome和Proof成立。



\### 视觉卫生：15分



\* 无违规人手；

\* 无人脸人体；

\* 无展厅干扰。



\### 节奏与弹性：15分



\* 无拖沓；

\* 无机械等分；

\* L/J Cut合理；

\* 无强制15秒痕迹。



\### 运动与景别：15分



\* 景别变化；

\* 运镜方向；

\* 主体运动连续；

\* 构图变化。



\### Hook：5分



\* 3秒内完成认知。



\### Closure：5分



\* 音画共同收束。



本地得分低于80不得渲染。



\---



\## 二十二、Owner审美偏好配置



`editorial\_constraints\_v1.json`必须记录：



```json

{

&#x20; "owner\_preferences": {

&#x20;   "prioritize\_flow\_over\_forced\_brevity": true,

&#x20;   "reject\_hands\_by\_default": true,

&#x20;   "allow\_hand\_only\_for\_hook\_or\_transformation": true,

&#x20;   "reject\_truncated\_actions": true,

&#x20;   "prefer\_complete\_motion": true,

&#x20;   "avoid\_showroom\_feel": true,

&#x20;   "prefer\_restrained\_high\_end\_style": true,

&#x20;   "avoid\_gimmicky\_transitions": true,

&#x20;   "allow\_duration\_up\_to\_24s\_when\_justified": true

&#x20; }

}

```



后续批次默认继承。



\---



\## 二十三、六条P12S成片



输出：



\* `V1A\_pain\_solution\_P12S.mp4`

\* `V1B\_pain\_solution\_P12S.mp4`

\* `V2A\_feature\_proof\_P12S.mp4`

\* `V2B\_feature\_proof\_P12S.mp4`

\* `V3A\_lifestyle\_value\_P12S.mp4`

\* `V3B\_lifestyle\_value\_P12S.mp4`



不得只修改个别指标。



每条必须重新执行：



1\. 最终候选视觉卫生检查；

2\. 动作生命周期检查；

3\. 弹性时长计算；

4\. L-Cut/J-Cut规划；

5\. 有界变速决策；

6\. 连续性校验；

7\. 精确渲染。



\---



\## 二十四、单条目标



\### V1A



\* 保留音画逐句对应；

\* 不强制缩短20秒；

\* 提升Hook；

\* 后续不得出现人手。



\### V1B



\* 保留Hook优势；

\* 删除中间两处人手画面；

\* Hook之后不允许任何人手；

\* 保持音画同步。



\### V2A



\* 保留8–12秒证明链；

\* Outcome必须完整；

\* 不因精简破坏狗动作。



\### V2B



\* 保留产品结构证明；

\* 使用合理景别变化和运镜连续性；

\* 降低展厅感；

\* 开合操作允许人手，其余人手拒绝。



\### V3A



\* 截断动作必须修复；

\* 如原素材本身不完整，必须换镜头；

\* 不得通过加速伪造完整动作；

\* 保持流畅。



\### V3B



\* Core必须与V3A真正不同；

\* 强化2-in-1或家居价值；

\* 增加运镜和景别层次；

\* 避免只更换尾部画面。



\---



\## 二十五、渲染规格



每条：



\* 1080×1920；

\* SAR 1:1；

\* 9:16；

\* H.264；

\* yuv420p；

\* Edge-TTS；

\* `en-US-AvaNeural`；

\* 帧级精确切片；

\* 串行渲染；

\* FFmpeg并发1。



音视频总时长误差：



```text

<= 100ms

```



尾部余韵：



```text

150–400ms

```



内部非设计性静音：



```text

<= 700ms

```



\---



\## 二十六、最小测试



修改现有P12R测试或增加同一测试文件中的P12S用例。



必须测试：



1\. 人手默认拒绝；

2\. Opening Hook人手800ms限制；

3\. Hook后人手拒绝；

4\. Transformation人手1500ms限制；

5\. 人脸和人体拒绝；

6\. Outcome动作完整性；

7\. Proof动作完整性；

8\. Transformation首尾状态；

9\. 动作保护帧；

10\. L-Cut范围；

11\. J-Cut范围；

12\. 狗动作最大1.08x；

13\. 产品动作最大1.25x；

14\. 正确setpts公式；

15\. 弹性时长计算；

16\. 超过24秒优先压缩语义；

17\. 同景别为软扣分；

18\. 动作截断为硬阻断；

19\. 运镜方向连续；

20\. 最终音画误差不超过100ms。



只运行：



\* P12S focused tests；

\* GLM模型绑定检查；

\* Edge-TTS smoke test；

\* 9:16检查；

\* Git媒体检查。



\---



\## 二十七、输出目录



输出到：



`products/dog\_stairs\_v1/outputs/renders/batch\_20260617\_001/P12S\_kinematic\_fluency\_visual\_hygiene\_elastic\_duration`



至少包含：



\* 6条P12S成片；

\* 每条最终director slate；

\* 每条动作生命周期报告；

\* 每条视觉卫生报告；

\* 每条L-Cut/J-Cut使用记录；

\* 每条播放速度记录；

\* 每条弹性时长计算；

\* 每条本地审美评分；

\* VLM调用统计；

\* `review\_index.md`。



\---



\## 二十八、review\_index.md



每条必须直接对比：



\* P12R路径；

\* P12S路径；

\* P12R时长；

\* P12S时长；

\* P12S时长等级；

\* 是否出现人手；

\* 人手是否属于允许场景；

\* 动作完整性；

\* 是否使用L-Cut；

\* 是否使用J-Cut；

\* 是否使用变速；

\* 实际playback\_speed；

\* 是否存在动作截断；

\* 本地审美评分；

\* 建议Owner重点观看时间点。



汇总：



\* 违规人手淘汰数量；

\* 允许开合人手数量；

\* 截断动作修复数量；

\* 替换素材数量；

\* L-Cut使用次数；

\* J-Cut使用次数；

\* 变速使用次数；

\* 视频VLM调用数；

\* Storyboard Judge调用数；

\* 新增Token；

\* 6条最终时长；

\* 总开发与渲染时间。



\---



\## 二十九、最终通过标准



\### 视觉卫生



6条全部满足：



\* 普通镜头无违规人手；

\* 无人脸；

\* 无明显人体；

\* Hook后无普通人手镜头；

\* 开合人手只出现在Transformation角色。



\### 动作完整性



6条全部满足：



\* Outcome不截断；

\* Proof不截断；

\* Transformation有明确首尾状态；

\* V3A截断问题被修复或替换。



\### 弹性时长



\* 不强制卡15秒；

\* 最终时长位于13–24秒；

\* 超过21秒必须有完整动作或明确商业理由；

\* 无拖沓；

\* 无长无声；

\* 无不自然加速。



\### 审美



至少4条：



\* 明显优于P12R；

\* 运动方向更自然；

\* 景别层次更清楚；

\* 展厅感降低；

\* V3A与V3B形成明显不同Core；

\* 不需要Owner逐镜重剪。



\---



\## 三十、最终输出格式



完成后只输出：



KINEMATIC\_FLUENCY\_VISUAL\_HYGIENE\_READY



视频目录：

V1A新版本：

V1B新版本：

V2A新版本：

V2B新版本：

V3A新版本：

V3B新版本：

6条最终时长：

6条时长等级：

违规人手淘汰数：

允许人手镜头数：

动作截断修复结果：

L-Cut使用数：

J-Cut使用数：

变速使用数：

实际播放速度范围：

视频VLM调用数：

Storyboard Judge调用数：

图片补标调用数：

新增VLM总Token：

6条本地审美评分：

总开发与渲染时间：

主要已知问题：

建议A/B观看顺序：



然后停止等待Owner观看。



\---



\## 三十一、执行顺序



1\. 验证本Task；

2\. 确认`spec\_version = P12S-v1`；

3\. 读取P12R六条视频和产物；

4\. 生成`editorial\_constraints\_v1.json`；

5\. 升级`audio\_rhythm\_orchestrator.py`；

6\. 升级`vlm\_director\_planner.py`；

7\. 升级`continuity\_validator.py`；

8\. 升级精确渲染入口的L/J Cut和有界变速支持；

9\. 对最终候选执行人手和视觉卫生深度审核；

10\. 对关键动态候选执行动作生命周期VLM审核；

11\. 淘汰违规人手镜头；

12\. 淘汰不完整Outcome、Proof和Transformation；

13\. 计算每条弹性目标时长；

14\. 生成多套候选director slate；

15\. 本地评分；

16\. 仅在本地分差小于5时调用Storyboard Judge；

17\. 使用L-Cut/J-Cut保护动作完整性；

18\. 必要时使用有界变速；

19\. continuity validator硬校验；

20\. 帧级精确渲染6条P12S视频；

21\. 检查视觉卫生；

22\. 检查动作完整性；

23\. 检查时长合理性；

24\. 检查音画同步；

25\. 生成A/B review\_index；

26\. 输出6条视频和核心指标；

27\. 停止等待Owner观看。



本任务的成功由视觉卫生、动作完整性、时长弹性与最终成片共同决定。



