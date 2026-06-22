\# TASK：P12W\_OPENCV\_FFMPEG\_VLM\_ASYMMETRIC\_VISION\_COMPILER



spec\_version: P12W-v1



\## 一、任务定位



本项目继续严格执行：



`系统价值 = 成片质量 × 产出速度 ÷ 开发与调用成本`



本任务不是继续在P12U或P12V旧模块上叠加补丁。



本任务需要建立一套统一、可长期复用的：



`OpenCV + Python + GLM-4.6V + FFmpeg`



非对称视觉编译器。



核心职责必须彻底分离：



\### OpenCV



负责像素和微观时序测量：



\* 技术画质；

\* 帧序；

\* 冻结；

\* 重复帧；

\* 抖动；

\* 光流；

\* 全局运动；

\* 局部运动；

\* 运动能量；

\* 构图稳定性；

\* 候选动作窗口。



\### GLM-4.6V



负责宏观语义和商业理解：



\* 狗、产品和人手语义；

\* 痛点；

\* 功能；

\* Proof；

\* Outcome；

\* 家居氛围；

\* 产品状态；

\* 动作生命周期；

\* 视频逻辑；

\* 候选与基线的商业价值比较。



\### Python



负责确定性决策：



\* 叙事状态拓扑；

\* 硬门过滤；

\* 候选检索；

\* 节点评分；

\* 转场评分；

\* 基线严格占优；

\* Owner偏好；

\* 受控Storyboard搜索；

\* VLM调用路由。



\### FFmpeg



只负责物理执行：



\* 精确解码；

\* 帧网格切片；

\* PTS归零；

\* 单一CFR；

\* 画幅统一；

\* 音视频合流；

\* 精确重编码；

\* 最终封装。



任何一个模块不得越权承担其他模块的核心职责。



\---



\## 二、P12W取代关系



P12W为新的唯一活动任务。



如果P12V尚未执行：



\* 不再执行P12V；

\* P12V仅作为设计参考。



P12U、P12V实验代码：



\* 可读取；

\* 可复用有效算法；

\* 不允许继续堆叠条件分支；

\* 不得作为P12W主入口。



P12W必须建立新的统一包：



`03\_tk\_video\_agent/helpers/vision\_compiler/`



建议结构：



```text

helpers/vision\_compiler/

├── \_\_init\_\_.py

├── opencv\_perception.py

├── semantic\_vlm\_router.py

├── storyboard\_compiler.py

├── quality\_gate.py

└── pipeline.py

```



唯一主入口：



`helpers/vision\_compiler/pipeline.py`



P12T已验证稳定的渲染器通过适配器复用，不得重新复制第二套FFmpeg渲染实现。



\---



\## 三、历史结果与基线



\### 稳定生产基线



P12T：



\* 构图逻辑被Owner认可；

\* 管线新增冻结为0；

\* 音画误差0–1ms；

\* PTS归零；

\* 单一CFR；

\* 人手规则基本有效；

\* 动作完整性较可靠。



P12T必须作为不可退化基线。



\### 可复用正向样本



允许参考：



\* P12U V3A；

\* P12U V2A中的狗使用Proof；

\* P12U发现的14条新候选素材。



所有P12U候选必须重新通过P12W全部硬门。



\### 负向校准样本



必须读取并用于阈值校准：



\* P12S中的管线新增冻结；

\* P12U V1A人手与逻辑错误；

\* P12U V1B鬼畜画面；

\* P12U V2B人手、鬼畜和逻辑错误；

\* P12U V3B人手和逻辑错误。



不得仅依赖理论阈值。



\---



\## 四、业务目标与技术机制对齐



每一项技术都必须对应明确业务价值。



| 业务目标      | 技术机制                              | 通过标准                           |

| --------- | --------------------------------- | ------------------------------ |

| 视频无违规人手   | OpenCV自适应抽帧 + VLM视频语义审核 + 时间区间黑名单 | 普通镜头违规人手为0                     |

| 视频无鬼畜和抽搐  | OpenCV帧序、重复帧、运动能量、光流异常检测          | 时序伪影为0                         |

| 视频无转场冻结   | P12T帧网格、PTS、单一CFR + OpenCV逐转场检查   | `PIPELINE\_INTRODUCED\_FREEZE=0` |

| 叙事逻辑正确    | Python叙事状态DAG + VLM语义状态确认         | 非法状态转移为0                       |

| 构图不低于P12T | 基线锚定式槽位替换                         | 新候选构图不得低于基线                    |

| 新素材真正有价值  | 候选与P12T一对一严格占优                    | 未占优则保留P12T                     |

| 转场运动自然    | 全局运动估计 + 稠密光流残差                   | 只作为低权重Tie-breaker              |

| 片子保持流畅    | 动作生命周期、原速优先、弹性时长                  | 不截断、不强行卡15秒                    |

| 六条内容有差异   | 类型级Core隔离和跨视频重复约束                 | 差异不以降低质量为代价                    |

| VLM算力有效   | 分层路由、缓存、决策价值报告                    | 调用必须影响判断或发现问题                  |



\---



\## 五、最小硬边界



1\. `raw\_videos`绝对只读；

2\. API Key不得写入源码、配置、日志、缓存或Git；

3\. Provider固定为`zhipu`；

4\. 请求和响应模型必须严格为`glm-4.6v`；

5\. 禁止模型fallback；

6\. 禁止破坏性Git和文件操作；

7\. 媒体和outputs保持Git ignored；

8\. Edge-TTS固定使用`en-US-AvaNeural`；

9\. 禁止Windows SAPI回退；

10\. 最终视频必须为1080×1920、SAR 1:1、9:16；

11\. 管线新增冻结必须为0；

12\. 音画误差不得超过100ms；

13\. 普通镜头违规人手、人脸和明显人体必须为0；

14\. Outcome、Proof和Transformation不得使用截断动作；

15\. P12W成片不得低于对应P12T基线。



不得修改`AGENTS.md`，避免产生新的硬规则Owner Gate。



本轮失败经验写入：



`02\_learning\_notes/error\_log.md`



\---



\## 六、OpenCV环境必须真实通电



P12U已报告本机`cv2`不可用。



P12W必须先完成环境审计。



执行：



```text

python executable

python version

pip version

numpy version

skimage version

opencv package status

```



如果`cv2`不可导入：



1\. 在当前项目实际使用的Python环境安装`opencv-python-headless`；

2\. 不安装带GUI的`opencv-python`；

3\. 检查与当前NumPy兼容性；

4\. 执行`pip check`；

5\. 将实际解析出的版本写入项目依赖文件；

6\. 验证：



&#x20;  \* `import cv2`

&#x20;  \* `cv2.\_\_version\_\_`

&#x20;  \* 视频读取；

&#x20;  \* Farneback；

&#x20;  \* 特征点检测；

&#x20;  \* 仿射RANSAC；

&#x20;  \* Laplacian；

&#x20;  \* 直方图；

&#x20;  \* 帧差。



P12W验收必须证明：



`opencv\_backend\_used = true`



不得再次以skimage fallback冒充OpenCV已经接入。



允许保留skimage作为容灾回退，但正式P12W运行必须使用OpenCV主路径。



\---



\## 七、OpenCV能力边界



必须明确：



OpenCV能够测量像素，但不能独立理解以下语义：



\* 这是人手；

\* 狗在犹豫；

\* 这是痛点；

\* 这是Proof；

\* 这是高级家居氛围。



经典OpenCV不得被当作语义模型。



人手、人脸、人体和商业角色最终判断必须由：



\* 本地已有检测模型，如果存在；

\* 或GLM-4.6V；



完成。



OpenCV负责：



\* 抽取高覆盖率帧；

\* 定位风险时段；

\* 减少VLM需要查看的无关内容；

\* 提供物理证据。



\---



\## 八、全量52条素材像素建图



全部52条素材必须完整进入OpenCV本地扫描。



不得将全部完整原片直接上传给VLM。



每条素材生成：



\* source\_video\_id

\* source\_path

\* file\_hash

\* width

\* height

\* fps

\* duration\_ms

\* codec

\* frame\_count

\* rotation

\* frame\_interval\_stats

\* blur\_curve

\* exposure\_curve

\* highlight\_clip\_ratio

\* shadow\_clip\_ratio

\* motion\_energy\_curve

\* global\_motion\_curve

\* local\_motion\_curve

\* shake\_curve

\* duplicate\_frame\_ranges

\* freeze\_ranges

\* glitch\_risk\_ranges

\* motion\_peak\_ranges

\* technical\_quality\_score

\* safe\_crop\_score



输出：



`opencv\_asset\_perception\_index.json`



\---



\## 九、技术画质清洗必须使用动态校准



禁止使用未经校准的固定魔法数字，例如：



```text

Laplacian variance < 100

→ 所有素材直接淘汰

```



因为模糊阈值会受到：



\* 分辨率；

\* 压缩；

\* 纹理；

\* 光线；

\* 景深；

\* 产品材质；



影响。



正确策略：



1\. 使用P12T已认可镜头作为正向样本；

2\. 使用P12U低质镜头作为负向样本；

3\. 计算每项指标的分布；

4\. 使用分位数、稳健Z-score或校准阈值；

5\. 输出阈值来源和样本；

6\. 低于阈值先降级，不默认全部Hard Reject；

7\. 严重失焦、严重死黑、严重死白才Hard Reject。



输出：



`cv\_threshold\_calibration.json`



\---



\## 十、模糊、曝光与画面质量



\### 模糊度



使用：



\* Laplacian variance；

\* Tenengrad或等价梯度清晰度；

\* 多帧中位数；

\* 主体区域与全画面分别计算。



不得只看单帧。



\### 曝光



计算：



\* 灰度直方图；

\* 高光裁切比例；

\* 阴影裁切比例；

\* 中间调占比；

\* 帧间曝光稳定性。



\### 技术质量结果



每个候选输出：



\* blur\_score

\* exposure\_score

\* compression\_artifact\_score

\* temporal\_stability\_score

\* overall\_technical\_score

\* reject\_reason

\* confidence



\---



\## 十一、运动能量不能直接等同动作语义



帧差能定位“变化”，不能独立判断：



\* 狗开始上楼；

\* 狗完成落点；

\* 产品完成展开。



运动峰值只用于生成候选区间。



动作生命周期必须由：



1\. OpenCV运动曲线定位候选；

2\. 自适应高密度抽帧；

3\. VLM短视频代理语义确认；



共同完成。



不得把运动能量峰值直接写成：



`action\_start`或`settle`



\---



\## 十二、全局运动与稠密光流



\### 12.1 全局摄影机运动



主路径使用：



1\. 特征点检测；

2\. 稀疏光流追踪；

3\. RANSAC估计仿射变换；

4\. 提取：



&#x20;  \* dx

&#x20;  \* dy

&#x20;  \* rotation

&#x20;  \* scale

&#x20;  \* inlier\_ratio

&#x20;  \* reprojection\_error

&#x20;  \* confidence。



\### 12.2 Farneback稠密光流



使用`cv2.calcOpticalFlowFarneback`分析：



\* 局部运动能量；

\* 主体运动；

\* 全局运动残差；

\* 动作边缘；

\* 方向突然翻转；

\* 变速后运动异常。



不得将全画面光流简单平均值直接解释为摄影机Pan。



必须区分：



\* camera\_motion

\* subject\_motion

\* mixed\_motion

\* static

\* uncertain



\---



\## 十三、光流计算路由



不得对52条全部视频的每一帧运行稠密光流。



\### Level 1：全量低密度



覆盖52条全部场景：



\* 轻量帧差；

\* 低密度全局运动估计；

\* static/moving分类；

\* 风险窗口定位。



\### Level 2：角色Top-K候选



计算：



\* Head 300–500ms；

\* Tail 300–500ms；

\* 全局运动；

\* Farneback残差；

\* 运动来源；

\* 置信度。



\### Level 3：最终转场



对真实进入P12W时间线的每个相邻镜头执行：



\* 精确Head/Tail运动分析；

\* 转场动量评分；

\* 鬼畜与时序异常检查。



所有结果必须缓存。



\---



\## 十四、运动匹配不能成为主导目标



P12U已经证明：



VLM偏向motion-aware方案，但Owner多数认为P12T更好。



因此P12W中：



\* Motion Match权重默认3%；

\* 最高不得超过5%；

\* 只作为构图、叙事、卫生和动作完整性全部通过后的Tie-breaker；

\* 高置信同向可以小幅加分；

\* 反向默认只扣分；

\* 不得为了同向运动替换更好的构图；

\* 不得为了Match Cut选择低质素材。



不得宣称光流自动产生“好莱坞级”或“网红级”审美。



\---



\## 十五、时序伪影与鬼畜检测



OpenCV必须对源候选和渲染候选同时分析。



检测：



\* exact\_duplicate\_run；

\* near\_duplicate\_run；

\* ABAB alternating frame pattern；

\* non-monotonic motion；

\* abrupt motion energy spike；

\* high-frequency direction reversal；

\* frame interval instability；

\* repeated frame clusters；

\* speed remap artifact；

\* source-render motion mismatch；

\* shake intensity；

\* optical-flow discontinuity。



必须区分：



\* 正常快速运动；

\* 设计性手持；

\* 源素材原生抖动；

\* FFmpeg引入异常；

\* 变速引入异常；

\* 真正鬼畜帧。



已被Owner确认的P12U V1B和V2B异常区间必须作为负向测试样本。



\---



\## 十六、冻结检测



不得只比较最后3帧。



必须结合：



\* 精确帧hash；

\* 像素差；

\* SSIM或近似相似度；

\* 运动能量；

\* 原素材对照；

\* Director Slate的`intentional\_hold`。



动态镜头中：



`PIPELINE\_INTRODUCED\_FREEZE > 100ms`



必须Hard Reject。



P12T零冻结机制必须完整复用。



\---



\## 十七、人手和人体审核



OpenCV主要负责：



\* 自适应抽帧；

\* 风险区间定位；

\* 边缘帧覆盖；

\* 视频代理生成。



不得声称经典OpenCV能够100%识别人手。



每个替换候选必须生成：



\### Contact Sheet



\* 普通场景：125–200ms抽帧；

\* 人手风险：80–125ms；

\* 转场边界：50–100ms；

\* 保持原始比例；

\* 烧录source ID和时间码。



\### 视频代理



动态候选：



\* 2–6秒；

\* 8–12fps；

\* 保持完整动作；

\* 不变速；

\* 无音频；

\* H.264；

\* 保持9:16比例。



\### VLM语义审核



必须输出：



\* hand\_present

\* face\_present

\* body\_present

\* violation\_intervals\_ms

\* hand\_action

\* allowed\_context

\* action\_start\_ms

\* completion\_ms

\* settle\_ms

\* logical\_role\_eligibility

\* confidence

\* reject\_reason



`uncertain`默认不替换P12T。



\---



\## 十八、资产时间区间黑名单



使用：



`configs/asset\_exclusion\_intervals\_v2.json`



禁止因为一个短暂人手片段默认淘汰整条原片。



记录：



\* source\_video\_id

\* start\_ms

\* end\_ms

\* violation\_type

\* severity

\* evidence\_source

\* confidence

\* owner\_confirmed



候选只要与fatal区间重叠超过50ms：



直接拒绝。



支持：



\* hand\_intrusion

\* human\_face

\* human\_body

\* temporal\_glitch

\* ghost\_frame

\* freeze

\* source\_corruption

\* incomplete\_action

\* severe\_showroom\_pollution



\---



\## 十九、P12T基线锚定



六条视频必须以P12T对应时间线作为：



`incumbent\_timeline`



不得从空白重新生成完整视频。



每个P12T槽位默认保留。



允许替换：



\* Hook；

\* Pain；

\* Demonstration；

\* Proof；

\* Outcome；

\* Transformation；

\* Closure。



每条第一轮最多替换：



\* 2个核心槽位；

\* 或1个Hook加1个Core。



没有明确提升时：



保留P12T原镜头。



\---



\## 二十、叙事状态拓扑



\### 痛点型



`PROBLEM`

→ `INTERVENTION`

→ `ACTIVE\_USE`

→ `SUCCESS\_RESULT`

→ `SETTLE`

→ `CLOSURE`



\### 功能证明型



`FEATURE`

→ `DEMONSTRATION\_START`

→ `DEMONSTRATION\_COMPLETE`

→ `PROOF`

→ `CLOSURE`



\### 生活价值型



`SITUATION`

→ `USAGE\_OR\_TRANSFORMATION`

→ `LIFESTYLE\_PAYOFF`

→ `CLOSURE`



每个候选镜头必须包含：



\* entry\_state

\* exit\_state

\* dog\_position\_before

\* dog\_position\_after

\* product\_state\_before

\* product\_state\_after

\* action\_phase

\* allowed\_roles



非法状态转移直接拒绝。



不得使用软评分覆盖非法状态。



\---



\## 二十一、构图与商业逻辑优先级



本地软评分建议：



\* Narrative Causality：25%

\* Composition：20%

\* Visual Hygiene：15%

\* Action Completeness：15%

\* Temporal Stability：10%

\* Audio-Visual Cohesion：10%

\* Motion Match：3%

\* Novelty：2%



构图评分必须评价：



\* 主体清晰度；

\* 产品完整度；

\* 狗与产品关系；

\* 视觉重心；

\* 9:16裁切；

\* 背景干净度；

\* 展厅感；

\* 前后镜头构图推进；

\* 是否存在突兀空白。



新奇性与运动匹配合计不得超过5%。



\---



\## 二十二、受控Storyboard搜索



不得恢复P12U的120套全片自由重组。



采用基线锚定式搜索：



1\. P12T作为候选0；

2\. 每个可替换槽位检索Top 5；

3\. 每次只替换1–2个槽位；

4\. 每个候选先通过全部硬门；

5\. beam\_width = 10；

6\. 保留P12T原方案；

7\. 输出Top 3局部改进方案；

8\. 不生成完全脱离P12T结构的时间线。



Beam Search只用于在合法DAG状态内组合少量替换。



\---



\## 二十三、严格占优门



新候选必须与P12T原槽位进行一对一比较。



硬条件全部通过：



\* 无违规人手；

\* 无鬼畜；

\* 无冻结；

\* 动作完整；

\* 叙事状态合法；

\* 构图不低于P12T；

\* Claim证据不低于P12T；

\* 9:16裁切不低于P12T；

\* 时序稳定性不低于P12T。



软条件至少两项明确提升：



\* Hook；

\* 构图；

\* Proof；

\* 情绪表达；

\* 景别层次；

\* 家居融合；

\* Closure；

\* Owner风格匹配。



综合占优边际：



`dominance\_margin >= 6`



否则保留P12T。



\---



\## 二十四、VLM非对称调用机制



\### Level 1：全量低密度语义覆盖



输入：



\* OpenCV生成的场景Contact Sheet。



输出：



\* dog\_present

\* product\_present

\* scene

\* likely\_action

\* product\_state

\* candidate\_roles

\* hand\_risk

\* showroom\_feeling

\* home\_feeling

\* confidence

\* needs\_video\_proxy



\### Level 2：Top候选动态深审



输入：



\* OpenCV定位的候选视频代理；

\* 运动曲线；

\* 候选角色。



输出：



\* 动作生命周期；

\* 人手区间；

\* 产品状态；

\* 狗位置；

\* Outcome或Proof资格；

\* 语义风险。



\### Level 3：Candidate与P12T基线对照



必须同时呈现：



\* P12T原镜头；

\* 新候选；

\* 前后相邻镜头；

\* 口播；

\* 角色。



VLM不得孤立评价新素材。



\### Level 4：最终整片A/B审查



P12W草稿与P12T完整视频对比。



必须输出：



\* winner

\* composition\_comparison

\* narrative\_comparison

\* temporal\_stability

\* visual\_hygiene

\* action\_completeness

\* audiovisual\_cohesion

\* evidence\_timestamps

\* timeline\_change\_required

\* expected\_quality\_gain

\* confidence



仅返回`pass`或统一高分不算有效审查。



\---



\## 二十五、VLM算力预算



Owner允许在明确质量收益下拉高算力。



每6条：



\### Soft Budget



`500,000 Tokens`



\### Quality Escalation



`1,500,000 Tokens`



\### Hard Ceiling



`3,000,000 Tokens`



达到Hard Ceiling必须停止。



预算建议：



\* 20%：全量场景语义粗标；

\* 30%：Top动态候选深审；

\* 30%：Candidate与P12T对照；

\* 15%：最终整片A/B；

\* 5%：失败重试。



停止条件：



1\. 同一缓存键已有成功结果；

2\. 连续两次没有改变候选判断；

3\. VLM建议没有具体时间码证据；

4\. 本地硬门已拒绝；

5\. 顺序反转结论冲突；

6\. 已达到Hard Ceiling；

7\. P12T明显更优；

8\. 当前视频已通过验收。



\---



\## 二十六、FFmpeg执行契约



必须复用P12T稳定渲染底座。



每个切片：



1\. 精确trim；

2\. `setpts=PTS-STARTPTS`；

3\. 必要时执行合法变速；

4\. scale/crop；

5\. 唯一一处`fps=30`；

6\. 目标帧数；

7\. PTS连续验证；

8\. concat；

9\. 全局Edge-TTS音轨一次性合流。



禁止：



\* `tpad=stop\_mode=clone`；

\* 末帧复制补槽；

\* 双重CFR；

\* 用`-shortest`承担时长规划；

\* 通过循环帧填充声音；

\* 依赖播放器保持最后一帧。



\---



\## 二十七、变速原则



\### 狗和动物动作



默认：



`1.00x`



最高：



`1.05x`



且必须：



\* 运动能量低至中等；

\* OpenCV时序伪影检测通过；

\* VLM判断自然；

\* 明确优于P12T。



\### 产品折叠或展开



允许：



`1.00x–1.15x`



必须通过OpenCV时序伪影检测。



\### 高运动镜头



强制：



`1.00x`



如果无法适配：



\* 调整口播；

\* 调整L-Cut/J-Cut；

\* 使用更长真实窗口；

\* 或保留P12T。



\---



\## 二十八、六条P12W目标



输出：



\* `V1A\_pain\_solution\_P12W.mp4`

\* `V1B\_pain\_solution\_P12W.mp4`

\* `V2A\_feature\_proof\_P12W.mp4`

\* `V2B\_feature\_proof\_P12W.mp4`

\* `V3A\_lifestyle\_value\_P12W.mp4`

\* `V3B\_lifestyle\_value\_P12W.mp4`



\### V1A



以P12T为基线。



不得继承P12U人手或逻辑错误。



\### V1B



以P12T为基线。



不得继承P12U鬼畜镜头。



\### V2A



允许尝试采用P12U中证明力更强的狗使用Proof。



必须整条不弱于P12T。



\### V2B



以P12T结构证明链为基线。



不得继承P12U人手、鬼畜或状态倒置。



\### V3A



允许采用P12U已被Owner认可的正向方案。



仍需通过P12W全部硬门。



\### V3B



以P12T为基线。



Core必须与V3A不同，但差异不得以质量下降为代价。



\---



\## 二十九、最终质量门



每条P12W必须通过：



\### OpenCV物理检查



\* 模糊；

\* 曝光；

\* 重复帧；

\* 冻结；

\* ABAB交替帧；

\* 抖动；

\* 光流突变；

\* 帧间隔；

\* PTS；

\* CFR；

\* 帧预算；

\* 黑帧；

\* 裁切安全。



\### Python逻辑检查



\* 状态拓扑；

\* 动作完整；

\* Claim证据；

\* 基线占优；

\* Core差异；

\* Owner偏好；

\* 时间区间黑名单。



\### VLM语义检查



\* 人手；

\* 人脸；

\* 人体；

\* 商业逻辑；

\* 产品状态；

\* 狗位置；

\* Outcome；

\* Proof；

\* 家居价值；

\* Candidate/P12T对比。



任意本地硬门失败：



VLM不得覆盖。



\---



\## 三十、校准而非魔法阈值



所有OpenCV关键阈值必须通过以下样本校准：



\### 正向样本



\* P12T六条；

\* P12U V3A；

\* P12U V2A有效Proof区间。



\### 负向样本



\* P12S冻结区间；

\* P12U V1A人手区间；

\* P12U V1B鬼畜区间；

\* P12U V2B人手和鬼畜区间；

\* P12U V3B人手区间。



必须输出：



\* sample\_id

\* feature\_values

\* threshold

\* threshold\_method

\* false\_positive\_risk

\* false\_negative\_risk

\* calibration\_result



不得声称检测率100%。



\---



\## 三十一、统一配置



新增一个主配置：



`configs/vision\_compiler\_policy\_v1.json`



该文件统一管理：



\* OpenCV采样；

\* 阈值；

\* VLM预算；

\* 叙事DAG；

\* 基线占优；

\* 运动权重；

\* 变速限制；

\* 黑名单路径；

\* FFmpeg契约；

\* Owner偏好。



不得再把同一规则散落在多个实验配置中。



旧配置可以读取迁移，但P12W运行时以该主配置为唯一入口。



\---



\## 三十二、测试



新增：



`tests/test\_p12w\_vision\_compiler.py`



必须覆盖：



1\. cv2真实导入；

2\. OpenCV视频解码；

3\. 模糊度；

4\. 曝光；

5\. 重复帧；

6\. 冻结；

7\. ABAB帧模式；

8\. 运动能量；

9\. 全局运动；

10\. Farneback局部残差；

11\. 摄影机与主体运动区分；

12\. P12U鬼畜负样本被检出；

13\. P12S冻结负样本被检出；

14\. 时间区间黑名单；

15\. 状态拓扑；

16\. 基线严格占优；

17\. motion权重不超过5%；

18\. P12T安全回退；

19\. PTS归零；

20\. 单一CFR；

21\. 零冻结；

22\. 音画误差；

23\. VLM缓存；

24\. VLM预算上限；

25\. 六条最终视频物理检查。



不得追求与成片无关的测试数量。



\---



\## 三十三、输出目录



输出到：



`products/dog\_stairs\_v1/outputs/renders/batch\_20260617\_001/P12W\_opencv\_ffmpeg\_vlm\_asymmetric\_vision\_compiler`



至少包含：



\* 六条P12W视频；

\* `opencv\_asset\_perception\_index.json`

\* `cv\_threshold\_calibration.json`

\* `motion\_descriptor\_index.json`

\* `temporal\_artifact\_report.json`

\* `asset\_exclusion\_intervals\_v2.json`

\* `candidate\_windows.json`

\* `narrative\_topology\_report.json`

\* `baseline\_dominance\_report.json`

\* `vlm\_semantic\_audit\_report.json`

\* `final\_ab\_review\_report.json`

\* `transition\_freeze\_detection\_report.json`

\* `vlm\_compute\_value\_report.json`

\* `review\_index.md`



报告不得替代成片。



\---



\## 三十四、review\_index.md



每条列出：



\* P12T路径；

\* P12U路径；

\* P12W路径；

\* 保留P12T槽位；

\* 替换槽位；

\* OpenCV技术质量结果；

\* 人手审核；

\* 时序伪影审核；

\* 动作完整性；

\* 状态拓扑；

\* 构图比较；

\* dominance margin；

\* VLM A/B结论；

\* 是否顺序反转；

\* 是否fallback到P12T；

\* 零冻结；

\* 音画误差；

\* 建议Owner观看时间点。



汇总：



\* 52条OpenCV覆盖率；

\* cv2主路径是否真实启用；

\* 被技术质量降级数量；

\* 时序伪影拒绝数量；

\* 人手拒绝数量；

\* 状态拓扑拒绝数量；

\* 候选替换数量；

\* fallback到P12T数量；

\* VLM总调用；

\* VLM总Token；

\* VLM改变决策次数；

\* 六条最终时长；

\* 总开发与渲染时间。



\---



\## 三十五、验收标准



\### 基础技术



\* `opencv\_backend\_used=true`；

\* 52条本地像素扫描覆盖率100%；

\* 管线新增冻结为0；

\* 鬼畜和时序伪影为0；

\* PTS连续；

\* 单一CFR；

\* 音画误差不超过100ms；

\* 1080×1920、9:16。



\### 商业质量



\* 违规人手为0；

\* 动作截断为0；

\* 逻辑状态倒退为0；

\* 构图不低于P12T；

\* 六条均可作为内容素材使用。



\### 有效提升



\* 至少2条明确优于P12T；

\* V3A保留已确认的正向价值；

\* V2A尝试保留更强Proof；

\* 其余没有明确提升时安全回退P12T。



不要求六条全部更换素材。



\---



\## 三十六、最终输出格式



完成后只输出：



OPENCV\_FFMPEG\_VLM\_ASYMMETRIC\_COMPILER\_READY



视频目录：

V1A新版本：

V1B新版本：

V2A新版本：

V2B新版本：

V3A新版本：

V3B新版本：

opencv\_backend\_used：

OpenCV版本：

52条像素扫描覆盖率：

技术质量降级数：

人手拒绝数：

时序伪影拒绝数：

状态拓扑拒绝数：

保留P12T槽位数：

替换槽位数：

fallback到P12T数量：

VLM调用数：

VLM总Token：

VLM改变决策次数：

六条零冻结结果：

六条音画误差：

明确优于P12T数量：

总开发与渲染时间：

主要已知问题：

建议A/B观看顺序：



然后停止等待Owner观看。



\---



\## 三十七、执行顺序



1\. 验证本Task；

2\. 确认`spec\_version=P12W-v1`；

3\. 不执行旧P12V任务；

4\. 读取P12T、P12U及Owner反馈；

5\. 将失败记录写入`error\_log.md`；

6\. 审计当前Python环境；

7\. 安装并验证`opencv-python-headless`；

8\. 新建`helpers/vision\_compiler/`统一包；

9\. 迁移必要的P12T渲染适配；

10\. 建立统一主配置；

11\. 用正负样本校准CV阈值；

12\. OpenCV全量扫描52条素材；

13\. 生成技术质量、运动与伪影索引；

14\. 生成Contact Sheet和候选视频代理；

15\. 执行VLM低密度语义覆盖；

16\. 建立时间区间级黑名单；

17\. 加载P12T incumbent timeline；

18\. 为每个可替换槽位检索Top候选；

19\. 执行OpenCV物理硬门；

20\. 执行VLM语义深审；

21\. 执行状态拓扑检查；

22\. 执行候选与P12T严格占优；

23\. 在合法候选中执行受控搜索；

24\. 生成P12W草稿；

25\. 执行P12T与P12W完整视频VLM A/B；

26\. 不占优则局部或整条回退；

27\. 使用P12T稳定FFmpeg底座渲染；

28\. 执行全部OpenCV和FFmpeg物理终检；

29\. 生成六条P12W视频；

30\. 生成review\_index；

31\. 输出最终结果；

32\. 停止等待Owner观看。



本任务的成功由OpenCV真实像素感知、P12T无回归、VLM高价值语义判断、FFmpeg物理稳定性以及最终Owner审片共同决定。



