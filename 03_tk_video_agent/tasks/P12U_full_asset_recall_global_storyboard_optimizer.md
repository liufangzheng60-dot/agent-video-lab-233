\# TASK：P12U\_FULL\_ASSET\_RECALL\_GLOBAL\_STORYBOARD\_OPTIMIZER



spec\_version: P12U-v1



\## 一、最高评价体系



本项目继续严格执行：



系统价值 = 成片质量 × 产出速度 ÷ 开发与调用成本



P12T 已经完成并验证：



\* `PIPELINE\_INTRODUCED\_FREEZE` 从 2 降为 0；

\* 所有标准化切片首帧 PTS 为 0；

\* 帧数预算与实际帧数一致；

\* CFR 只保留一处；

\* 最终音画误差为 0–1ms；

\* P12S 的人手过滤、动作完整性、L-Cut、J-Cut和弹性时长均被保留；

\* 六条最终整片 VLM 审核全部通过。



因此，本任务不得再次大范围重构渲染器。



当前新的核心问题是：



1\. 如何覆盖全部 52 条母素材，避免优秀片段根本没有进入候选池；

2\. 如何通过本地搜索、全局评分和 VLM 重排，形成真正可解释、可复现的 Storyboard 择优；

3\. 如何让六条视频的 Core、景别、动作和素材来源形成真实差异；

4\. 如何让 Owner 的历次审片偏好进入下一批剪辑评分，而不是每次重新猜测。



\---



\## 二、对“扫描52条素材”的正式定义



本任务必须覆盖全部 52 条母素材。



但必须严格区分三种行为：



\### 2.1 必须执行：全量本地建图



全部 52 条素材都必须执行：



\* ffprobe；

\* 场景切分；

\* 稀疏关键帧抽取；

\* 运动峰值定位；

\* 模糊度；

\* 亮度；

\* 画幅；

\* 9:16安全裁切；

\* 重复素材指纹；

\* 视频编码与时间戳异常检测。



该层使用本地 CPU、FFmpeg和OpenCV，属于低边际货币成本操作。



\### 2.2 建议执行：全量低密度 VLM 语义覆盖



不得把52条完整原片无差别上传给VLM。



应对本地场景切分后生成的低分辨率 Contact Sheet进行一次低密度语义粗标。



目的：



\* 提高候选召回率；

\* 补足旧Asset Ledger缺失字段；

\* 找到此前未被使用的高价值镜头；

\* 发现潜在人手、动作、产品状态和脚本角色。



\### 2.3 只按需执行：高密度视频 VLM 深审



短视频代理只用于进入高价值候选池的动态窗口。



不得对所有52条原片进行完整视频级深审。



\---



\## 三、P12T 基线必须永久保留



P12U 必须继承：



\* `VIDEO\_TRANSITION\_ZERO\_FREEZE\_INVARIANT`；

\* 禁止 `tpad=stop\_mode=clone`；

\* 禁止末帧复制填充视觉槽位；

\* 所有concat输入PTS从0开始；

\* 单一CFR归一化；

\* 帧网格量化；

\* 逐转场冻结检测；

\* 管线新增冻结严格为0；

\* 人手视觉卫生规则；

\* Outcome、Proof、Transformation动作完整性；

\* L-Cut和J-Cut；

\* 弹性时长；

\* Edge-TTS字边界与呼吸组；

\* 帧级精确渲染。



P12U 不得因新的素材检索或Storyboard搜索而破坏上述能力。



\---



\## 四、任务目标



本任务必须完成：



1\. 为全部52条原片建立新一代完整素材索引；

2\. 对全部场景执行低密度视觉语义粗标；

3\. 建立角色化Top-K候选检索；

4\. 建立动作窗口自动扩张；

5\. 建立全局Storyboard序列搜索；

6\. 建立跨视频多样性约束；

7\. 建立证据化VLM重排；

8\. 建立Owner偏好学习；

9\. 使用新架构重新生成6条P12U成片；

10\. 与P12T六条视频逐条A/B。



最终必须真实输出成片。



不得只生成Ledger、索引、评分器或架构报告后停止。



\---



\## 五、项目路径



项目根目录：



`C:\\Users\\43871\\AppData\\Local\\LFZ\_CODE\\agent-video-lab-233-laptop`



工作目录：



`C:\\Users\\43871\\AppData\\Local\\LFZ\_CODE\\agent-video-lab-233-laptop\\03\_tk\_video\_agent`



产品：



`dog\_stairs\_v1`



SKU：



`khaki`



素材批次：



`batch\_20260617\_001`



原片目录：



`products/dog\_stairs\_v1/inputs/raw\_videos/batch\_20260617\_001`



P12T输入目录：



`products/dog\_stairs\_v1/outputs/renders/batch\_20260617\_001/P12T\_transition\_freeze\_zero\_tolerance\_and\_vlm\_compute\_scale`



P12U输出目录：



`products/dog\_stairs\_v1/outputs/renders/batch\_20260617\_001/P12U\_full\_asset\_recall\_global\_storyboard\_optimizer`



VLM：



\* Provider：`zhipu`

\* Model：`glm-4.6v`



TTS：



\* Edge-TTS

\* `en-US-AvaNeural`



\---



\## 六、最小硬边界



仅保留：



1\. `raw\_videos`绝对只读；

2\. API Key不得进入源码、日志、报告、缓存或Git；

3\. Provider固定为`zhipu`；

4\. 请求与响应模型必须严格为`glm-4.6v`；

5\. 禁止模型fallback；

6\. 禁止破坏性Git和文件操作；

7\. 媒体与outputs保持Git ignored；

8\. Edge-TTS固定使用`en-US-AvaNeural`；

9\. 禁止Windows SAPI回退；

10\. 六条最终成片所有转场的管线新增冻结必须为0；

11\. 最终视频必须为1080×1920、SAR 1:1、9:16。



不得新增数据库、任务队列、第二套渲染器或第二套状态机。



\---



\## 七、工程实现范围



允许新增三个核心文件：



1\. `helpers/asset\_recall\_indexer.py`

2\. `helpers/storyboard\_search\_optimizer.py`

3\. `helpers/owner\_preference\_ranker.py`



允许修改：



\* `helpers/vlm\_director\_planner.py`

\* `helpers/continuity\_validator.py`

\* `helpers/transition\_freeze\_detector.py`

\* 当前Asset Ledger入口；

\* 当前Three Stage Compiler入口；

\* 当前P12T渲染入口。



允许新增配置：



\* `configs/asset\_recall\_policy\_v1.json`

\* `configs/storyboard\_search\_policy\_v1.json`

\* `configs/owner\_preference\_weights\_v1.json`

\* `configs/vlm\_compute\_policy\_v2.json`



允许新增一个主要测试文件：



`tests/test\_asset\_recall\_storyboard\_optimizer.py`



不得创建第二套平行剪辑流水线。



\---



\## 八、第一层：52条全量物理素材建图



`asset\_recall\_indexer.py`必须扫描全部52条素材。



每条原片至少记录：



\* source\_video\_id

\* source\_path

\* file\_hash

\* duration\_ms

\* width

\* height

\* avg\_frame\_rate

\* r\_frame\_rate

\* time\_base

\* codec

\* rotation

\* audio\_present

\* scene\_boundaries

\* black\_frame\_ranges

\* blur\_score

\* brightness\_score

\* crop\_safety

\* duplicate\_group

\* timestamp\_risk

\* motion\_energy\_curve

\* motion\_peaks

\* technical\_quality\_score



输出：



`physical\_asset\_index.json`



旧Asset Ledger只能作为冷启动参考。



不得把旧Ledger视为永久真相。



\---



\## 九、场景切分策略



场景检测只用于发现视觉变化边界。



不得将场景边界等同于动作边界。



每个场景必须继续检测：



\* 内部运动峰值；

\* 主体状态变化；

\* 动作启动；

\* 动作完成；

\* 人手短暂进入；

\* 产品状态变化；

\* 转场前后异常。



场景切分结果必须允许：



\* 一个长场景拆成多个动作窗口；

\* 相邻短场景合并为一个完整动作窗口；

\* 场景边界前后扩张。



\---



\## 十、全量稀疏关键帧策略



每个场景默认抽取：



1\. 首帧；

2\. 25%帧；

3\. 中间帧；

4\. 75%帧；

5\. 末帧；

6\. 最高运动能量帧；

7\. 次高运动能量帧；

8\. 场景切换前一帧；

9\. 场景切换后一帧。



静态场景可以减少重复帧。



动态场景不得只抽首中尾三帧。



所有帧必须：



\* 保持原始宽高比；

\* 禁止拉伸为512×512；

\* 推荐使用288×512或360×640；

\* Contact Sheet使用letterbox；

\* 每格烧录source\_video\_id和精确时间码；

\* 不烧录影响主体识别的大面积文字。



\---



\## 十一、自适应高密度采样



固定200ms抽帧不得作为统一规则。



根据场景风险动态采样：



\### 普通静态镜头



间隔：



`400–600ms`



\### 狗上下楼、跳跃、犹豫



间隔：



`150–250ms`



\### 产品折叠、展开、开合



间隔：



`100–200ms`



\### 人手、人脸、人体风险窗口



间隔：



`80–150ms`



\### 转场、冻结、PTS异常窗口



\* 本地逐帧检测；

\* 或50–100ms辅助采样。



Contact Sheet用于状态和构图。



短视频代理用于方向、生命周期、完整性和连续性。



\---



\## 十二、全量低密度VLM粗标



全部52条素材的场景Contact Sheet必须获得一次低密度语义覆盖。



允许将多个Contact Sheet批量组合进单次请求，但必须保持：



\* 每个场景可单独追溯；

\* source\_video\_id清晰；

\* 时间码清晰；

\* 返回结果可映射到原场景。



粗标字段：



\* dog\_present

\* product\_present

\* hand\_present

\* human\_face\_present

\* human\_body\_present

\* scene

\* shot\_scale

\* camera\_motion

\* camera\_motion\_direction

\* subject\_motion\_direction

\* likely\_action

\* product\_state

\* product\_state\_change

\* hook\_potential

\* candidate\_roles

\* showroom\_feeling

\* home\_lifestyle\_feeling

\* visual\_quality

\* confidence

\* needs\_dense\_sampling

\* needs\_video\_proxy



粗标目的仅为召回和路由。



不得把低密度Contact Sheet粗标直接作为最终Outcome或Proof判定。



\---



\## 十三、动作窗口扩张



当粗标检测到以下动作：



\* dog\_climbing

\* dog\_descending

\* dog\_hesitating

\* dog\_paw\_contact

\* fold

\* unfold

\* open

\* close

\* stability\_test

\* product\_transformation



系统必须围绕命中时间点向前后扩张。



默认：



\* pre\_roll：300–800ms；

\* post\_roll：400–1000ms；

\* 动作完成后必须包含settle；

\* 产品形态变化必须包含初始状态和最终状态。



扩张后再执行：



\* 自适应高密度抽帧；

\* 短视频代理；

\* 动作生命周期深审。



不得直接使用单张关键帧附近的碎片。



\---



\## 十四、角色化候选检索



为每个脚本角色分别建立候选池。



建议Top-K：



\* Hook：Top 15

\* Pain：Top 12

\* Intervention：Top 12

\* Outcome：Top 15

\* Feature：Top 12

\* Demonstration：Top 15

\* Proof：Top 15

\* Situation：Top 12

\* Usage：Top 15

\* Lifestyle Payoff：Top 12

\* Closure：Top 15



检索必须同时考虑：



\* 角色语义；

\* 动作完整性；

\* 视觉质量；

\* 人手卫生；

\* 产品状态；

\* 裁切安全；

\* Owner审美偏好；

\* 与已选镜头的重复度。



不得仅使用Python `filter()`完成所谓择优。



必须先筛选，再评分，再排序。



\---



\## 十五、节点评分模型



每个候选镜头必须获得节点分数。



建议满分100：



\### 角色语义匹配：25分



\* 是否真正符合当前脚本角色；

\* 是否支持当前口播和商业Claim。



\### 动作完整性：20分



\* prepare、onset、peak、completion、settle；

\* Outcome和Proof必须完整。



\### 视觉质量：15分



\* 清晰度；

\* 曝光；

\* 构图；

\* 主体可见性。



\### 视觉卫生：15分



\* 人手；

\* 人脸；

\* 人体；

\* 展厅干扰；

\* 无关背景行为。



\### 9:16裁切安全：10分



\* 主体不被裁断；

\* 产品结构完整。



\### Claim证据：10分



\* 是否真正证明功能；

\* 是否只是相关但不充分。



\### Owner风格匹配：5分



\* 流畅；

\* 克制；

\* 高端；

\* 非廉价转场；

\* 非过度展厅感。



节点硬失败时直接淘汰，不允许通过总分补偿。



\---



\## 十六、相邻镜头边评分



每对相邻候选必须获得边分数。



建议满分100：



\### 动作与运动连续性：20分



\* 主体运动方向；

\* 相机运动方向；

\* 动作阶段；

\* 出口与入口位置。



\### 产品状态连续性：15分



\* 阶梯状态；

\* 软墩状态；

\* 折叠状态；

\* 展开状态。



\### 景别变化：15分



\* 景别是否推进信息；

\* 是否产生必要层次。



相同景别不自动判错。



\### 构图变化：15分



\* 主体位置；

\* 视觉重心；

\* 画面相似度。



\### 音频切点匹配：15分



\* breath group；

\* phrase pause；

\* strong pause；

\* L-Cut/J-Cut合法性。



\### 来源复用惩罚：10分



\* 同一原片连续使用；

\* 时间窗口重叠；

\* 同一动作重复。



\### 视觉重复惩罚：10分



\* 同构图；

\* 同动作；

\* 同景别；

\* 信息没有推进。



\---
## 补充章节：全局运动估计与光流辅助的运镜连续性择优

### 一、功能定位

本章节将运动连续性作为Storyboard相邻镜头的软评分特征接入P12U。

目标：

1. 量化前一个镜头末端与后一个镜头起始阶段的运动方向、速度与能量；
2. 奖励具有自然动量延续的镜头组合；
3. 识别无理由的空间轴反转、镜头运动冲突和视觉动量断裂；
4. 为Beam Search提供本地、确定性、可缓存的运动边特征；
5. 在不牺牲语义、动作完整性和商业叙事的前提下，提高转场流畅度。

该能力不得成为“所有镜头必须同向”的硬约束。

语义角色匹配、动作完整性和视觉卫生永远高于运动方向匹配。

---

### 二、实现范围

不得新增第四套核心架构。

在以下现有文件内完成：

1. `helpers/asset_recall_indexer.py`

   * 生成候选镜头头尾运动描述符；
   * 缓存局部和全局运动特征。

2. `helpers/storyboard_search_optimizer.py`

   * 将运动连续性加入相邻镜头Edge Score；
   * 在Beam Search中使用该评分。

3. `helpers/continuity_validator.py`

   * 只对高置信度、无空间重置且明显冲突的运动组合进行风险标记；
   * 普通方向不匹配不得直接Hard Reject。

4. `helpers/owner_preference_ranker.py`

   * 记录Owner是否偏好运动匹配版本；
   * 后续使用真实A/B反馈校准运动评分权重。

不得修改P12T零冻结渲染底座的PTS、单一CFR、帧预算和concat原则。

---

### 三、运动分析窗口

每个候选镜头生成两个运动窗口：

#### Head Window

镜头开始后的：

`300–500ms`

#### Tail Window

镜头结束前的：

`300–500ms`

如果镜头时长不足1000ms：

* 使用镜头前35%作为Head；
* 使用镜头后35%作为Tail；
* 两个窗口不得重叠超过20%。

动作保护帧、completion和settle不得为了运动分析而被裁除。

---

### 四、全局摄影机运动估计

全局运动判断优先使用：

1. 灰度化和适度降采样；
2. 特征点检测；
3. 相邻帧稀疏光流追踪；
4. RANSAC估计全局二维仿射运动；
5. 从仿射矩阵提取：

   * translation_x；
   * translation_y；
   * rotation_deg；
   * scale_change；
   * inlier_ratio；
   * reprojection_error。

推荐将分析分辨率控制在：

* 宽度320–480像素；
* 保持原始宽高比；
* 禁止拉伸。

输出：

```json
{
  "global_motion": {
    "dx": 10.8,
    "dy": 1.3,
    "magnitude": 10.88,
    "angle_deg": 6.9,
    "rotation_deg": 0.7,
    "scale_change": 1.01,
    "inlier_ratio": 0.82,
    "confidence": 0.89
  }
}
```

如果：

* 有效特征点不足；
* RANSAC内点率过低；
* 重投影误差过高；
* 前景主体占据画面大部分区域；

必须降低置信度。

低置信度结果不得影响Storyboard排序。

---

### 五、Farneback稠密光流的正确用途

允许使用`cv2.calcOpticalFlowFarneback`，但只作为以下辅助能力：

1. 计算画面局部运动能量；
2. 判断运动主要集中在主体还是全画面；
3. 识别摄影机运动与主体运动的差异；
4. 计算转场两端的运动残差；
5. 交叉验证全局运动估计结果。

不得将所有像素光流的简单平均值直接视为摄影机运动。

必须输出：

* dense_median_dx；
* dense_median_dy；
* dense_motion_energy；
* local_motion_ratio；
* global_local_consistency；
* dominant_motion_source。

`dominant_motion_source`允许：

* camera；
* subject；
* mixed；
* static；
* uncertain。

---

### 六、运动分类

每个Head和Tail窗口至少分类为：

* static；
* pan_left；
* pan_right；
* tilt_up；
* tilt_down；
* push_in；
* pull_out；
* rotation；
* handheld_low；
* handheld_high；
* subject_motion_only；
* mixed_motion；
* uncertain。

不得将主体运动自动标记为摄影机Pan。

---

### 七、相邻镜头运动匹配分数

对于前镜头Tail与后镜头Head，计算：

1. `direction_similarity`

   * 使用归一化运动向量余弦相似度；

2. `magnitude_compatibility`

   * 判断运动能量是否处于相近范围；

3. `camera_motion_compatibility`

   * 判断Pan、Tilt、Push和Pull是否自然衔接；

4. `subject_entry_exit_compatibility`

   * 判断主体前镜头出口和后镜头入口是否产生空间冲突；

5. `semantic_transition_compatibility`

   * 判断运动匹配是否符合脚本角色变化；

6. `confidence`

   * 综合RANSAC内点率、光流稳定性和运动来源判断。

输出：

```json
{
  "motion_transition": {
    "direction_similarity": 0.86,
    "magnitude_compatibility": 0.74,
    "camera_motion_compatibility": 0.90,
    "subject_entry_exit_compatibility": 0.68,
    "semantic_transition_compatibility": 0.92,
    "confidence": 0.88,
    "motion_match_score": 8.1
  }
}
```

---

### 八、Edge Score权重

运动连续性只占相邻镜头Edge Score的：

`8%–15%`

默认建议：

`12%`

不得高于：

`15%`

因为以下因素必须始终优先：

1. 当前镜头是否符合语义角色；
2. 动作是否完整；
3. Proof是否支持Feature；
4. Outcome是否成立；
5. 是否存在人手、人脸或视觉污染；
6. 是否存在冻结、PTS或重复帧故障。

建议：

```text
EdgeScore =
动作与叙事连续性
+ 产品状态连续性
+ 景别与构图变化
+ 音频切点匹配
+ 运动连续性
- 重复与来源惩罚
```

---

### 九、奖励与惩罚

#### 高置信度同向延续

当：

* global motion confidence >= 0.75；
* direction similarity >= 0.75；
* magnitude compatibility >= 0.60；
* 语义角色不冲突；

奖励：

`+4 至 +10`

#### 高置信度方向冲突

当：

* confidence >= 0.80；
* direction similarity <= -0.60；
* 没有中性镜头重置空间轴；
* 主体出口与入口发生冲突；

惩罚：

`-4 至 -10`

但默认不Hard Reject。

#### 低置信度

当：

`confidence < 0.60`

运动连续性得分设为：

`0`

不得影响候选排序。

#### 静态结果镜头

动作镜头接：

* Proof；
* Outcome；
* Hero；
* Closure；

如果静态镜头承担明确结果展示，不得因为运动不连续而扣重分。

动静反差可能是合法的节奏收束。

---

### 十、禁止强制同向

禁止以下逻辑：

```python
if previous_direction != next_direction:
    reject()
```

方向变化只有在同时满足以下条件时才可升级为严重风险：

* 高置信度；
* 无建立镜头；
* 无语义角色转换；
* 无空间轴重置；
* 主体位置发生明显跳变；
* 相机与主体运动同时冲突。

---

### 十一、计算路由

不得对全部52条原片逐帧执行Farneback。

采用三级计算：

#### Level 1：全量低密度运动粗估

对所有场景使用低密度帧和轻量全局运动估计。

目的：

* static / moving粗分类；
* 相机运动大类；
* 是否需要精确分析。

#### Level 2：角色Top-K候选精确分析

只对进入角色Top-K的镜头计算：

* Head全局运动；
* Tail全局运动；
* Farneback局部残差；
* 运动置信度。

#### Level 3：最终Storyboard边界复核

只对Top 6完整Storyboard中的实际相邻镜头重新确认运动连续性。

结果必须缓存。

---

### 十二、Beam Search接入

Beam Search扩展新镜头时，必须读取：

* previous_clip.tail_motion_descriptor；
* candidate_clip.head_motion_descriptor。

将`motion_match_score`加入部分序列评分。

不得先选完所有镜头，再只在最后做运动评分。

否则无法在搜索过程中淘汰明显不协调的路径。

同时必须保留：

* 无运动匹配约束的baseline候选；
* motion-aware候选。

最终至少保留：

1. quality-first方案；
2. continuity-first方案；
3. motion-aware方案。

不得让运动匹配导致候选全部收敛为同一种风格。

---

### 十三、与VLM的分工

本地运动分析负责：

* 像素位移；
* 全局摄影机运动；
* 局部主体运动；
* 方向；
* 能量；
* 连续性置信度。

VLM负责：

* 判断这种运动衔接是否符合商业叙事；
* 判断是否显得刻意；
* 判断是否牺牲了语义清晰度；
* 比较motion-aware和quality-first Storyboard。

VLM不得覆盖：

* 本地实际运动矢量；
* PTS；
* 帧数；
* 冻结检测；
* 动作边界。

---

### 十四、验收标准

该功能通过必须满足：

1. 至少80%的角色Top-K候选具有Head/Tail运动描述符；
2. 低置信度结果不会改变候选排序；
3. 相同方向不会被无条件奖励；
4. 相反方向不会被无条件淘汰；
5. 主体运动与摄影机运动能够区分；
6. motion-aware Storyboard没有牺牲语义匹配和动作完整性；
7. 六条最终视频保持`PIPELINE_INTRODUCED_FREEZE = 0`；
8. 运动匹配没有引入镜头重复；
9. 至少生成一套quality-first和一套motion-aware候选用于比较；
10. 输出Owner可观看的A/B样片或明确时间点。

---

### 十五、输出记录

新增或合并输出：

* `motion_descriptor_index.json`
* `motion_transition_edge_scores.json`
* `motion_aware_storyboard_report.json`

`review_index.md`必须增加：

* 使用运动匹配的转场数量；
* 高置信度同向Match Cut数量；
* 方向冲突被降权数量；
* 低置信度未参与评分数量；
* motion-aware是否被最终选择；
* VLM是否偏好motion-aware版本；
* 建议Owner重点观看的具体转场时间点。

本功能的成功标准不是光流计算次数，而是运动连续性是否对最终成片产生可感知且不破坏语义的提升。




\## 十七、全局Storyboard评分



不得只逐镜贪心选择。



每条完整Storyboard总分必须包含：



`TotalScore = ΣNodeScore + ΣEdgeScore + StoryScore + DiversityScore + OwnerPreferenceScore - ViolationPenalty`



必须评价整条视频：



\* 三段式是否成立；

\* 能量曲线是否递进；

\* 景别曲线是否有层次；

\* Core是否真的推进；

\* Closure是否回收前文；

\* 是否过度使用同一来源；

\* 是否与同类型另一条视频重复；

\* 是否符合Owner偏好。



\---



\## 十八、Beam Search全局搜索



`storyboard\_search\_optimizer.py`必须使用Beam Search或等价全局序列搜索。



不得只执行：



`当前角色选择最高分镜头 → 下一个角色继续选择最高分镜头`



建议参数：



\* 每个角色初始候选：Top 12–15；

\* beam\_width：30；

\* 每扩展一个角色立即应用硬约束；

\* 保留Top 30部分序列；

\* 完成后保留Top 20完整Storyboard；

\* 再执行多样性重排；

\* 最终保留Top 6。



硬约束包括：



\* 人手违规；

\* 动作不完整；

\* 产品状态矛盾；

\* 管线冻结风险；

\* source window重叠；

\* Proof无证据；

\* Outcome无settle；

\* 口播与视觉冲突。



\---



\## 十九、多样性重排



单纯选择最高分会造成：



\* V1A和V1B只换Hook；

\* V3A和V3B只换尾部；

\* 六条视频使用相同Core；

\* 高分素材被反复使用。



必须使用多样性重排。



允许使用MMR或等价逻辑：



`MMR = λ × QualityScore - (1 - λ) × SimilarityToSelected`



推荐：



`λ = 0.72–0.80`



同类型两条视频必须满足：



\* 全片镜头重合率不高于40%；

\* Core镜头重合率不高于25%；

\* 相同连续镜头组合不得超过1组；

\* 主卖点不得完全相同；

\* Storyboard角色序列允许相同，但视觉实现必须不同。



若素材不足以达到差异要求：



必须明确报告，不得伪造差异。



\---



\## 二十、Owner偏好学习



新建：



`helpers/owner\_preference\_ranker.py`



必须将已有Owner反馈转换为pairwise preference数据。



至少吸收：



\* P12P优于P12D；

\* P12Q整体优于P12P；

\* P12R音画同步优于P12Q；

\* P12S视觉卫生和动作完整性规则；

\* P12T零冻结要求；

\* 人手默认拒绝；

\* 流畅度优先于强制精简；

\* 允许合理的16–21秒；

\* 动作完整优先；

\* 反对长尾无声；

\* 反对冻结；

\* 反对截断；

\* 反对展厅感；

\* V1B Hook被偏好；

\* V3A/V3B必须拥有不同Core；

\* 偏好高端、克制、真实。



输出：



`owner\_preference\_pairs.jsonl`



示例：



```json

{

&#x20; "preferred": "P12T\_V1B",

&#x20; "rejected": "P12R\_V1B",

&#x20; "reasons": \[

&#x20;   "zero\_transition\_freeze",

&#x20;   "no\_hand\_intrusion",

&#x20;   "better\_action\_completion"

&#x20; ]

}

```



\---



\## 二十一、偏好权重更新策略



不得建设复杂强化学习系统。



采用轻量方案：



1\. 初始化人工规则权重；

2\. 保存每次Owner A/B选择；

3\. 将视频特征转成向量；

4\. 使用简单pairwise logistic ranking或Bradley–Terry式更新；

5\. 每累计5–10个有效新比较再更新权重；

6\. 保留默认规则作为下限；

7\. 输出新旧权重变化；

8\. 权重变化不得自动覆盖硬约束。



硬约束永远优先于学习权重。



Owner偏好学习只影响软评分。



\---



\## 二十二、VLM动态候选深审



只对Top动态候选进行视频VLM。



重点：



\* 上楼；

\* 下楼；

\* 犹豫；

\* 脚掌接触；

\* 折叠；

\* 展开；

\* 稳定性；

\* 人手短暂进入；

\* completion；

\* settle。



同一次请求应同时判断：



\* 动作生命周期；

\* 人手；

\* 人脸；

\* 产品状态；

\* 运动方向；

\* Proof资格；

\* Outcome资格；

\* 视觉风险。



不得拆成多个重复请求。



\---



\## 二十三、VLM Storyboard重排



经过Beam Search和多样性重排后，选出Top 3候选。



VLM不得只返回无证据的`winner=A`。



必须返回：



\* winner

\* score\_A

\* score\_B

\* score\_C

\* audiovisual\_cohesion\_score

\* rhythm\_score

\* action\_completeness\_score

\* aesthetic\_variety\_score

\* owner\_style\_match\_score

\* rejected\_clip\_ids

\* evidence

\* recommended\_adjustments

\* confidence



`evidence`必须引用具体：



\* clip\_id；

\* sequence；

\* problem；

\* reason。



没有具体证据时，不接受VLM裁决。



\---



\## 二十四、顺序偏见控制



当以下任一成立时，执行一次候选顺序反转复核：



\* winner confidence低；

\* Top 2分差小于5；

\* VLM结论与本地第一名相反；

\* 关键Owner高优先级视频；

\* VLM没有提供充分证据。



第一次：



`A / B / C`



第二次：



调整候选顺序。



两次结论一致：



视为强裁决。



结论不一致：



\* 回退本地综合高分方案；

\* 或选择证据最充分方案；

\* 不允许无限重试。



\---



\## 二十五、整片VLM审核策略



P12T六次整片VLM审核全部通过，但改变时间线次数为0。



说明原有整片审核在该批次的边际价值有限。



P12U中，最终整片审核必须升级为：



\* 必须指出具体时间段；

\* 必须引用具体问题；

\* 必须说明是否需要修改时间线；

\* 必须输出`timeline\_change\_required`；

\* 必须输出`changed\_sequence\_ids`；

\* 必须输出`expected\_quality\_gain`。



仅返回统一高分和`pass`不能触发重复调用。



本轮由于Storyboard架构发生重大变化，允许六条各执行一次整片审查。



若整片审查发现明确问题：



每条最多再执行一次缺陷复核。



若仍无时间线改动价值：



后续批次将整片审查降级为抽样。



\---



\## 二十六、VLM算力预算



Owner允许在明确质量收益的前提下拉高GLM-4.6V算力。



每6条视频采用：



\### Soft Budget



`500,000 Tokens`



正常高质量生产预算。



\### Quality Escalation Budget



`1,000,000 Tokens`



只有以下情况允许进入：



\* 全量粗标召回明显不足；

\* 多个高价值动作需要视频深审；

\* Top 3 Storyboard分数接近；

\* Owner优先级视频需要顺序反转复核；

\* 最终整片发现明确可修复问题。



\### Hard Ceiling



`1,500,000 Tokens`



达到后必须停止新增调用，使用已有结果完成当前批次。



不得自动突破。



Hard Ceiling不是目标消耗量。



\---



\## 二十七、算力分配建议



每6条视频：



\### 全量场景粗标：20%



覆盖全部52条场景Contact Sheet。



\### 动态候选深审：25%



动作生命周期、人手、方向和状态变化。



\### Storyboard重排：25%



Top 3候选、证据化比较和必要顺序反转。



\### 最终整片审查：20%



节奏、叙事、展厅感、视觉重复和整体可用性。



\### 重试与争议储备：10%



只用于：



\* API失败；

\* 非法JSON；

\* 顺序反转；

\* 明确争议候选。



不得用于反复请求直到得到满意答案。



\---



\## 二十八、VLM停止规则



以下任一成立时停止同类新增调用：



1\. 已达到Hard Ceiling；

2\. 同一输入、Prompt版本和模型已有成功缓存；

3\. 连续两次调用没有改变候选排序；

4\. VLM建议没有改变最终时间线；

5\. 本地物理故障尚未解决；

6\. 同一请求失败两次；

7\. 模型低置信度且没有新增证据；

8\. 成片已达到通过标准。



不得使用VLM替代：



\* 冻结检测；

\* PTS检查；

\* 帧数预算；

\* 音画时长检查；

\* 黑帧检测；

\* 重复帧检测。



\---



\## 二十九、六条P12U视频



必须生成：



\* `V1A\_pain\_solution\_P12U.mp4`

\* `V1B\_pain\_solution\_P12U.mp4`

\* `V2A\_feature\_proof\_P12U.mp4`

\* `V2B\_feature\_proof\_P12U.mp4`

\* `V3A\_lifestyle\_value\_P12U.mp4`

\* `V3B\_lifestyle\_value\_P12U.mp4`



要求：



\### V1A与V1B



\* 使用不同Hook逻辑；

\* Core镜头重合率不超过25%；

\* 至少一条使用此前未进入P12T的新素材。



\### V2A与V2B



\* 证明不同核心卖点；

\* 一个偏狗使用Proof；

\* 一个偏产品结构或形态Proof；

\* 不得使用相同证明链。



\### V3A与V3B



\* Core必须真正不同；

\* 一个偏家居融合；

\* 一个偏2-in-1双形态；

\* 不得只在后段替换素材。



\---



\## 三十、P12U质量要求



六条必须全部满足：



\### 物理质量



\* `PIPELINE\_INTRODUCED\_FREEZE = 0`；

\* 所有PTS连续；

\* 所有切片PTS从0开始；

\* 单一CFR；

\* 音画误差不超过100ms；

\* 无长尾无声；

\* 无黑屏；

\* 无拉伸。



\### 视觉卫生



\* 普通镜头无违规人手；

\* 无人脸或明显人体；

\* 开合人手仅用于允许角色；

\* 不得回退P12S视觉卫生能力。



\### 动作完整性



\* Outcome完整；

\* Proof完整；

\* Transformation有首尾状态；

\* 动作包含completion和settle；

\* 不因缩短时长截断动作。



\### Storyboard质量



\* Hook在3秒内成立；

\* Core具有因果递进；

\* Proof支持Feature；

\* Closure完成认知闭环；

\* 景别和构图有层次；

\* 运动方向自然；

\* 六条视频具有真实差异。



\---



\## 三十一、本地物理终检



每条最终视频必须继续经过：



\* transition freeze detector；

\* framemd5或精确帧重复检测；

\* PTS检查；

\* 帧数预算；

\* 音画误差；

\* 黑帧检查；

\* 9:16检查；

\* 人手规则检查；

\* 动作完整性检查。



VLM通过不能覆盖本地物理检查失败。



\---



\## 三十二、输出目录



输出到：



`products/dog\_stairs\_v1/outputs/renders/batch\_20260617\_001/P12U\_full\_asset\_recall\_global\_storyboard\_optimizer`



至少包含：



\* 六条P12U成片；

\* `physical\_asset\_index.json`

\* `scene\_contact\_sheet\_index.json`

\* `coarse\_vlm\_scene\_labels.json`

\* `dense\_candidate\_windows.json`

\* `role\_candidate\_rankings.json`

\* `beam\_search\_storyboards.json`

\* `diversity\_rerank\_report.json`

\* `owner\_preference\_pairs.jsonl`

\* `owner\_preference\_weight\_report.json`

\* `vlm\_storyboard\_judge\_report.json`

\* `final\_video\_review\_report.json`

\* `transition\_freeze\_detection\_report.json`

\* `vlm\_compute\_value\_report.json`

\* `review\_index.md`



报告不得替代最终成片。



\---



\## 三十三、review\_index.md



第一部分必须直接列出：



\* P12T旧视频路径；

\* P12U新视频路径；

\* 每条时长；

\* 使用的新素材数量；

\* 镜头与P12T重合率；

\* Core重合率；

\* Beam Search候选数量；

\* 本地第一名；

\* VLM最终选择；

\* VLM是否改变本地排序；

\* 整片审查是否改变时间线；

\* Owner偏好分；

\* 零冻结结果；

\* 建议重点观看时间点。



汇总：



\* 52条母素材覆盖率；

\* 场景总数；

\* 粗标场景数；

\* 动态深审窗口数；

\* 新发现高价值镜头数；

\* 六条视频使用的新素材数；

\* Storyboard候选总数；

\* 多样性淘汰数；

\* VLM改变排序次数；

\* VLM改变时间线次数；

\* 总Token；

\* 总开发和渲染时间。



\---



\## 三十四、验收标准



\### 素材召回



\* 52条母素材本地覆盖率100%；

\* 所有场景具有稀疏帧索引；

\* 所有场景具有粗语义标签或明确失败记录；

\* 至少发现此前未进入P12T候选池的新镜头。



\### 择优可解释性



每条最终Storyboard必须能够回答：



\* 为什么选这个镜头；

\* 淘汰了哪些镜头；

\* 节点得分；

\* 边得分；

\* 全局得分；

\* Owner偏好得分；

\* VLM证据；

\* 多样性惩罚；

\* 是否改变本地排序。



\### 成片差异



\* 六条中至少四条使用此前未进入P12T的新高价值镜头；

\* 同类型视频Core重合率不超过25%；

\* V3A和V3B必须具有明显不同Core；

\* V1A和V1B Hook机制不同；

\* V2A和V2B证明链不同。



\### 最终质量



\* 六条全部可作为内容素材使用；

\* 至少四条在镜头丰富度、Core差异或剪辑审美上明显优于P12T；

\* 不得出现冻结、长尾无声、人手污染或动作截断回归；

\* 不需要Owner普遍逐镜重剪。



\---



\## 三十五、VLM价值归因



必须记录：



\* 粗标发现了哪些新素材；

\* 视频VLM确认了哪些动作；

\* VLM淘汰了哪些错误候选；

\* VLM改变了哪些Storyboard排序；

\* VLM发现了哪些整片问题；

\* 哪些调用没有改变任何决策；

\* 每100k Tokens带来的有效决策数；

\* 每条最终视频Token成本；

\* 每条被Owner接受视频Token成本。



不得用高Token消耗本身证明质量提升。



\---



\## 三十六、最终输出格式



完成后只输出：



FULL\_ASSET\_RECALL\_GLOBAL\_STORYBOARD\_READY



视频目录：

V1A新版本：

V1B新版本：

V2A新版本：

V2B新版本：

V3A新版本：

V3B新版本：

52条母素材覆盖率：

场景总数：

粗标场景数：

动态深审窗口数：

发现的新高价值镜头数：

六条使用新素材数量：

Beam Search完整Storyboard数量：

多样性淘汰数量：

VLM改变候选排序次数：

VLM改变最终时间线次数：

VLM总调用数：

VLM总Token：

六条镜头重合率：

六条Core重合率：

六条零冻结结果：

六条音画误差：

Owner偏好权重更新：

总开发与渲染时间：

主要已知问题：

建议A/B观看顺序：



然后停止等待Owner观看。



\---



\## 三十七、执行顺序



1\. 验证本Task；

2\. 确认`spec\_version = P12U-v1`；

3\. 读取P12T六条视频、Director Slate、冻结检测结果和VLM价值报告；

4\. 新建`asset\_recall\_indexer.py`；

5\. 新建`storyboard\_search\_optimizer.py`；

6\. 新建`owner\_preference\_ranker.py`；

7\. 全量扫描52条母素材；

8\. 建立物理素材索引；

9\. 执行场景切分与运动峰值分析；

10\. 生成全量稀疏Contact Sheet；

11\. 对全部场景执行低密度VLM粗标；

12\. 建立角色化Top-K候选池；

13\. 对动态候选执行窗口扩张；

14\. 对高价值动态窗口执行视频VLM深审；

15\. 生成节点得分和相邻边得分；

16\. 使用Beam Search生成Top 20完整Storyboard；

17\. 使用多样性重排保留Top 6；

18\. 结合Owner偏好进行软评分；

19\. 将Top 3交给VLM证据化重排；

20\. 必要时执行顺序反转复核；

21\. 生成六条不同的最终Director Slate；

22\. 使用P12T零冻结渲染底座生成六条P12U视频；

23\. 逐片段检查PTS、帧数与CFR；

24\. 逐转场执行冻结检测；

25\. 对六条执行一次升级后的整片VLM审查；

26\. 只对明确缺陷执行条件式复核；

27\. 生成Owner偏好权重报告；

28\. 生成VLM价值归因；

29\. 生成A/B review\_index；

30\. 输出六条P12U成片和核心指标；

31\. 停止等待Owner观看。



本任务的成功由52条素材的完整召回、可解释的全局择优、六条真实差异化成片以及最终Owner审片共同决定。



