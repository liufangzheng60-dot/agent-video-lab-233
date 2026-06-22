\# TASK：P12T\_TRANSITION\_FREEZE\_ZERO\_TOLERANCE\_AND\_VLM\_COMPUTE\_SCALE



spec\_version: P12T-v1



\## 一、最高评价体系



本项目继续严格执行：



系统价值 = 成片质量 × 产出速度 ÷ 开发与调用成本



Owner确认：



智谱GLM-4.6V算力成本足够低，可以在明确质量收益的前提下提高调用预算。



但本轮出现不可接受的物理故障：



P12S六条视频在片段切换前，前一片段末尾均出现固定画面、重复末帧或视觉冻结，造成明显拖拉、节奏停滞和转场卡顿。



该问题必须定义为：



`ZERO\_TOLERANCE\_TRANSITION\_FREEZE`



从本任务开始：



任何由渲染管线新增、无明确导演意图、发生在转场前的末帧重复或静止延长，均属于Hard Failure。



带有该问题的成片不得进入最终交付目录。



\---



\## 二、任务目标



本任务必须一次完成五件事：



1\. 精确定位P12S转场冻结的真实根因；

2\. 修复现有渲染入口中的PTS、帧率、帧数和片段拼接逻辑；

3\. 新增逐转场、本地帧级冻结检测器；

4\. 建立成熟、可提高算力但不可无限消耗的VLM质量路由；

5\. 重新渲染6条P12T成片，与P12S逐条A/B。



本任务不得通过简单删除几帧、缩短所有片段或掩盖冻结来交差。



必须从渲染管线物理层根治。



\---



\## 三、Owner确认的当前问题



P12S具备以下有效成果：



\* 视觉卫生改善；

\* 人手污染被过滤；

\* V3A动作截断被修复；

\* L-Cut和J-Cut已接入；

\* 弹性时长工作正常；

\* 6条视频均完成渲染。



但6条均出现：



\* 第一个片段结束前画面固定；

\* 进入第二片段前存在重复末帧；

\* 视觉短暂停滞；

\* 节奏被打断；

\* 多条视频在其他转场点也可能存在同类问题。



这是不可接受的成片故障。



不得因为本地审美评分高或VLM审核通过而忽略。



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



素材批次：



`batch\_20260617\_001`



P12S输入目录：



`products/dog\_stairs\_v1/outputs/renders/batch\_20260617\_001/P12S\_kinematic\_fluency\_visual\_hygiene\_elastic\_duration`



P12T输出目录：



`products/dog\_stairs\_v1/outputs/renders/batch\_20260617\_001/P12T\_transition\_freeze\_zero\_tolerance\_and\_vlm\_compute\_scale`



VLM：



\* Provider：`zhipu`

\* Model：`glm-4.6v`



TTS：



\* Edge-TTS

\* `en-US-AvaNeural`



输出帧率：



`30fps`



\---



\## 五、永久错误记录



本任务必须把以下规则追加写入现有：



`03\_tk\_video\_agent/AGENTS.md`



标题：



`VIDEO\_TRANSITION\_ZERO\_FREEZE\_INVARIANT`



内容至少包括：



1\. 任何转场前无设计意图的末帧冻结均为Hard Failure；

2\. 禁止使用末帧复制补足视觉槽位；

3\. 禁止使用`tpad=stop\_mode=clone`或等效逻辑填充普通视频；

4\. 禁止在多个阶段重复执行CFR补帧；

5\. 所有concat输入必须从PTS 0开始；

6\. 所有最终成片必须执行逐转场冻结检测；

7\. 检测不通过不得交付；

8\. VLM审核通过不能覆盖本地物理帧检测失败；

9\. 该规则适用于后续所有产品、素材批次和渲染任务。



如果该章节已存在，只更新内容，不得重复追加多个同名章节。



\---



\## 六、最小硬边界



仅保留以下规则：



1\. `raw\_videos`绝对只读；

2\. API Key不得写入源码、报告、缓存或Git；

3\. Provider固定为`zhipu`；

4\. 请求与响应模型必须严格为`glm-4.6v`；

5\. 禁止模型fallback；

6\. 禁止破坏性Git和文件操作；

7\. 媒体与outputs保持Git ignored；

8\. TTS固定使用Edge-TTS；

9\. 禁止Windows SAPI回退；

10\. 最终视频必须为1080×1920、SAR 1:1、9:16。



不得扩建数据库、任务队列、第二套Planner或大型审计系统。



\---



\## 七、核心实现范围



不得新建第二套渲染系统。



必须定位并修改现有：



\* actual render入口；

\* FFmpeg命令构建器；

\* director slate执行器；

\* continuity validator；

\* concat或最终合流流程。



允许新增一个核心文件：



`helpers/transition\_freeze\_detector.py`



允许新增两个配置文件：



\* `configs/video\_render\_invariants\_v1.json`

\* `configs/vlm\_compute\_policy\_v1.json`



允许新增或修改一个主要测试文件。



\---



\## 八、第一阶段：真实根因定位



在修改代码前，必须从P12S六条成片中提取全部剪切点并完成根因分析。



每个转场必须检查三个层级：



\### 8.1 原素材层



检查对应原片窗口：



\* 原片末尾是否本来就静止；

\* 是否存在真实的狗停稳；

\* 是否存在静态产品镜头；

\* 是否存在编码重复帧；

\* 实际可用运动帧持续到何时。



\### 8.2 标准化切片层



检查进入concat前的中间切片：



\* 首帧PTS；

\* 末帧PTS；

\* frame count；

\* avg\_frame\_rate；

\* r\_frame\_rate；

\* time\_base；

\* duration；

\* packet duration；

\* 是否存在重复末帧；

\* 是否被补足到目标槽位；

\* 是否存在`tpad`、loop、clone、apad或持续时间拉伸。



\### 8.3 最终成片层



检查最终P12S输出：



\* 实际剪切点；

\* 转场前最长重复帧序列；

\* 转场后首个有效运动帧；

\* 是否存在PTS空洞；

\* 是否由CFR补帧；

\* 是否为播放器展示上一帧；

\* 是否只发生在第一个转场；

\* 是否发生在所有转场；

\* 是否与L-Cut/J-Cut有关。



\---



\## 九、根因分类



每个冻结必须归类为以下一种或多种：



\* `SOURCE\_NATURAL\_STATIC`

\* `PLANNER\_SLOT\_LONGER\_THAN\_SOURCE\_MOTION`

\* `CLONED\_LAST\_FRAME\_PADDING`

\* `TPAD\_STOP\_MODE\_CLONE`

\* `DOUBLE\_CFR\_NORMALIZATION`

\* `OUTPUT\_R\_FRAME\_DUPLICATION`

\* `PTS\_NOT\_RESET`

\* `CONCAT\_TIMESTAMP\_GAP`

\* `AUDIO\_LONGER\_THAN\_VISUAL\_SEGMENT`

\* `L\_CUT\_WITHOUT\_REAL\_VISUAL\_FRAMES`

\* `SPEED\_REMAP\_DURATION\_MISMATCH`

\* `FINAL\_MUX\_DURATION\_MISMATCH`

\* `UNKNOWN`



不得在根因未确认前直接大范围改写渲染器。



至少输出：



`p12s\_transition\_freeze\_root\_cause\_report.json`



其中必须逐视频、逐剪切点记录证据。



\---



\## 十、禁止项扫描



必须扫描当前渲染代码和实际FFmpeg命令。



重点搜索：



\* `tpad`

\* `stop\_mode=clone`

\* `loop`

\* `-stream\_loop`

\* `apad`

\* `-r 30`

\* `fps=30`

\* `-fps\_mode cfr`

\* `-vsync`

\* `-shortest`

\* `trim`

\* `setpts`

\* `concat`

\* `xfade`

\* `-frames:v`

\* `-t`

\* `shortest=0`

\* `eof\_action`

\* `repeatlast`



输出：



`ffmpeg\_freeze\_risk\_scan.json`



同一个渲染阶段不得同时存在多个帧率强制层。



\---



\## 十一、统一帧网格



所有时间线必须在渲染前量化到统一帧网格。



输出帧率：



`FPS = 30`



定义：



`frame\_duration\_ms = 1000 / 30`



每个视觉槽位：



`target\_frames = round(target\_duration\_ms × 30 / 1000)`



量化后的真实时长：



`quantized\_duration\_ms = target\_frames × 1000 / 30`



Director Slate必须同时保存：



\* requested\_duration\_ms

\* target\_frames

\* quantized\_duration\_ms

\* duration\_quantization\_error\_ms



单段量化误差应控制在半帧以内。



不得使用无法落在帧网格上的模糊结束时间直接驱动编码器。



\---



\## 十二、每段视频的正确渲染顺序



每个视觉片段必须按以下顺序处理：



1\. 解码原素材；

2\. 根据source\_in与source\_out执行trim；

3\. 立即执行`setpts=PTS-STARTPTS`；

4\. 执行允许的播放速度映射；

5\. 执行scale、crop和SAR处理；

6\. 在唯一一处执行30fps归一化；

7\. 按目标帧数执行frame-domain trim；

8\. 再次生成从0开始的连续PTS；

9\. 输出标准化视频切片；

10\. 用ffprobe验证首帧、末帧、帧数和时长。



不得通过复制末帧将实际较短的视频补到目标槽位。



\---



\## 十三、单一CFR原则



整个系统只允许一个CFR归一化节点。



推荐策略：



\* 在标准化切片filtergraph中统一为30fps；

\* 最终合流阶段使用已经连续的30fps时间戳；

\* 最终输出不得再次使用第二套自动补帧机制。



禁止同时出现：



\* `fps=30`

\* 输出`-r 30`

\* `-fps\_mode cfr`



三者中的多个主动补帧层。



系统必须明确选择一个主控机制。



其余阶段只能做验证，不得再次复制或删除帧。



\---



\## 十四、`-frames:v`的正确定位



允许使用：



`-frames:v N`



但只作为：



\* 编码上限；

\* 防止意外溢出；

\* 与target\_frames一致性的最后保险。



禁止把`-frames:v`作为唯一冻结修复手段。



如果上游只产生了少于N个有效帧：



\* 不得复制最后一帧补到N；

\* 必须返回Planner；

\* 延长真实source\_out；

\* 调整视觉槽位；

\* 使用另一个完整素材；

\* 或合理修改L-Cut/J-Cut。



\---



\## 十五、禁止末帧填充



普通动态片段禁止：



\* `tpad=stop\_mode=clone`

\* 末帧循环；

\* 最后图片循环；

\* 自动重复帧填满slot；

\* 用freeze frame承担L-Cut；

\* 通过延长容器时长伪造视觉时长。



只有明确的静态设计镜头才允许停留。



静态设计镜头必须标记：



\* `intentional\_hold = true`

\* `hold\_reason`

\* `hold\_duration\_ms`

\* `editorial\_role`



并满足：



\* 只能用于Hero、产品特写或Closure；

\* 不得连续出现在多个转场前；

\* 不得造成拖拉；

\* 不得与动态动作角色混用。



\---



\## 十六、视频与音频合流原则



禁止在每个视觉片段内附带独立音频后再逐段concat。



推荐流程：



1\. 先生成完整纯视频时间线；

2\. 验证所有视觉剪切点；

3\. 生成完整全局Edge-TTS音轨；

4\. 在最终阶段一次性合流；

5\. 最终音视频长度误差控制在100ms以内；

6\. `-shortest`只能作为最终保险，不能代替时长规划。



如果音轨比视频长：



不得让播放器展示最后一帧等待音频结束。



必须：



\* 扩展真实视觉素材；

\* 修改口播；

\* 调整合法动作窗口；

\* 或重新规划时间线。



\---



\## 十七、Transition Freeze Detector



新增：



`helpers/transition\_freeze\_detector.py`



该模块必须接收：



\* 最终视频；

\* director slate；

\* 每个剪切点；

\* 原素材窗口；

\* 输出fps。



针对每一个剪切点分析：



\* 剪切前500ms；

\* 剪切后200ms；

\* 对应原素材末端500ms；

\* 对应标准化切片末端500ms。



\---



\## 十八、冻结检测必须采用多指标



禁止仅检查最后3帧。



必须同时使用：



\### 18.1 精确重复帧



计算连续帧的：



\* frame checksum；

\* framemd5；

\* 或等价精确hash。



记录：



\* exact\_duplicate\_run\_frames

\* exact\_duplicate\_run\_ms



\### 18.2 近似静止



使用：



\* 像素绝对差；

\* 灰度MAD；

\* SSIM或等价相似度；

\* motion energy。



记录：



\* mean\_abs\_diff

\* similarity\_score

\* motion\_energy

\* near\_static\_run\_ms



\### 18.3 与原素材对比



如果原素材该时段仍然有运动，但渲染输出变为重复帧：



标记：



`PIPELINE\_INTRODUCED\_FREEZE`



这是最高优先级Hard Failure。



如果原素材本来静止：



进入设计性静止判断，不得直接认定渲染故障。



\---



\## 十九、冻结硬阈值



对动态镜头：



\* 允许最多2个连续相同帧；

\* 超过2帧必须进入风险判断；

\* 渲染器新增的连续重复帧超过100ms，直接Hard Reject；

\* 转场前运动能量相较原素材下降90%以上，且持续超过100ms，直接Hard Reject；

\* 每个视频任何一个转场Hard Reject，则整条不得交付。



对明确静态镜头：



\* 必须标记`intentional\_hold=true`；

\* 必须符合Hero、Detail或Closure角色；

\* 必须经过节奏检查；

\* 不得作为默认转场填充。



阈值应由已知失败P12S片段校准，不能仅写死后不验证。



\---



\## 二十、冻结修复优先级



检测到冻结时，按以下顺序修复：



1\. 删除末帧复制或`tpad clone`；

2\. 修正PTS清零；

3\. 删除重复CFR层；

4\. 修正concat时间戳；

5\. 缩短错误的视觉槽位；

6\. 延长真实可用源素材窗口；

7\. 重新选择完整动作素材；

8\. 调整L-Cut或J-Cut范围；

9\. 修改口播或breath group；

10\. 重新规划该段Storyboard。



禁止：



\* 直接删除所有尾帧；

\* 统一缩短所有镜头；

\* 牺牲动作completion和settle；

\* 使用新的冻结帧覆盖旧冻结帧；

\* 隐藏检测报告。



\---



\## 二十一、VLM算力策略



按Owner当前额度成本，允许显著提高GLM-4.6V调用，但必须建立成熟预算。



新增：



`configs/vlm\_compute\_policy\_v1.json`



采用三级预算。



\### 21.1 Soft Budget



每6条视频：



`250,000 Tokens`



用于正常高质量生产。



\### 21.2 Quality Escalation Budget



当视频存在以下情况时，允许提升至：



`500,000 Tokens`



触发条件：



\* 动作完整性不确定；

\* 人手或人体风险不确定；

\* 本地Top-2 Storyboard分差小；

\* 最终整片审美评分不足；

\* VLM指出明确叙事或连续性缺陷；

\* Owner要求质量优先。



\### 21.3 Hard Ceiling



每6条视频最高：



`800,000 Tokens`



达到后必须停止新增调用并使用已有结果完成当前批次。



禁止自动突破。



硬上限不是目标消耗量。



\---



\## 二十二、VLM算力分配



每6条视频建议分配：



\### 资产语义与视觉卫生



预算占比：



`20%`



用途：



\* 人手；

\* 人脸；

\* 产品状态；

\* 景别；

\* 画面污染；

\* Hero与Closure资格。



\### 动作视频理解



预算占比：



`25%`



用途：



\* 动作生命周期；

\* 上下楼方向；

\* unfold/fold；

\* completion；

\* settle；

\* Proof资格。



\### Storyboard深度比较



预算占比：



`25%`



用途：



\* 比较Top-2或Top-3候选；

\* 视听因果；

\* 视觉疲劳；

\* 景别变化；

\* 叙事递进；

\* 展厅感。



\### 最终整片审片



预算占比：



`25%`



用途：



\* 低分辨率完整视频代理；

\* 全片节奏；

\* 情绪曲线；

\* 音画一致性；

\* 动作截断；

\* 人手遗漏；

\* 视觉重复；

\* Closure。



\### 重试储备



预算占比：



`5%`



只用于：



\* API失败；

\* 非法JSON；

\* 明确参数问题。



不得用于反复请求直到得到满意答案。



\---



\## 二十三、VLM调用层级



\### Level 1：本地确定性检查



不消耗Token。



必须覆盖：



\* 重复帧；

\* 冻结；

\* PTS；

\* 帧数；

\* 音画时长；

\* 画幅；

\* 黑帧；

\* 重复素材窗口。



物理问题必须在本地解决。



\### Level 2：候选素材深审



对进入Top候选池的动态素材调用。



重点：



\* 动作完整性；

\* 人手；

\* 产品状态；

\* 运动方向；

\* Proof和Outcome资格。



\### Level 3：Storyboard Judge



每条允许比较Top-3候选。



本地第一名优势明显时只需一次综合审查。



存在争议时可执行第二次不同角度审查。



每条最多2次。



\### Level 4：最终整片审查



六条最终草稿必须各执行一次GLM-4.6V整片审查。



输入使用：



\* 低分辨率完整视频代理；

\* director slate摘要；

\* 口播文本；

\* 商业目标。



必须评价：



\* Hook；

\* Rhythm；

\* Continuity；

\* Visual-Acoustic Cohesion；

\* Aesthetic Variety；

\* Human Intrusion；

\* Action Completeness；

\* Closure；

\* Showroom Feeling；

\* Overall Publishability。



此处的`Publishability`仅代表内容可用性评分，不涉及任何发布动作。



\### Level 5：条件式缺陷复核



只有最终整片审查发现明确问题时再调用。



每条最多1次。



不得对已通过视频重复审查。



\---



\## 二十四、VLM停止规则



以下任一成立时停止继续调用：



1\. 达到Hard Ceiling；

2\. 同一输入、同一Prompt、同一模型已有成功缓存；

3\. 同一缺陷连续两次建议相同；

4\. VLM建议没有改变最终时间线；

5\. 本地物理错误尚未修复；

6\. 请求失败超过两次；

7\. 模型输出低置信度且没有新增证据；

8\. 成片已达到通过标准。



不得使用VLM处理本地可确定解决的重复帧故障。



\---



\## 二十五、VLM价值指标



必须生成：



`vlm\_compute\_value\_report.json`



记录：



\* total\_tokens

\* tokens\_per\_video

\* tokens\_per\_accepted\_video

\* calls\_by\_stage

\* calls\_that\_changed\_timeline

\* calls\_that\_rejected\_bad\_clip

\* calls\_that\_changed\_storyboard

\* calls\_that\_found\_final\_cut\_defect

\* duplicate\_cache\_hits

\* failed\_requests

\* retry\_requests

\* defects\_found\_per\_100k\_tokens

\* final\_owner\_acceptance



算力价值不由调用数量判断。



必须由以下结果判断：



\* 是否淘汰错误素材；

\* 是否改变最终时间线；

\* 是否发现Owner可感知问题；

\* 是否提高最终成片通过率。



\---



\## 二十六、P12T重渲染原则



必须保留P12S已经验证有效的：



\* 人手过滤；

\* 动作完整性；

\* V3A完整dog path与settle；

\* L-Cut；

\* J-Cut；

\* 弹性时长；

\* 音画同步；

\* Edge-TTS；

\* 视觉卫生。



本轮不得重新推翻P12S内容架构。



优先复用现有Director Slate，只修复：



\* 冻结；

\* PTS；

\* 帧数；

\* CFR；

\* concat；

\* 片段时长匹配。



只有冻结修复无法在原计划完成时，才允许局部重新规划对应片段。



\---



\## 二十七、六条P12T成片



输出：



\* `V1A\_pain\_solution\_P12T.mp4`

\* `V1B\_pain\_solution\_P12T.mp4`

\* `V2A\_feature\_proof\_P12T.mp4`

\* `V2B\_feature\_proof\_P12T.mp4`

\* `V3A\_lifestyle\_value\_P12T.mp4`

\* `V3B\_lifestyle\_value\_P12T.mp4`



输出目录：



`products/dog\_stairs\_v1/outputs/renders/batch\_20260617\_001/P12T\_transition\_freeze\_zero\_tolerance\_and\_vlm\_compute\_scale`



\---



\## 二十八、逐片段验收



每个标准化片段必须验证：



\* first\_pts = 0；

\* PTS单调递增；

\* target\_frames与actual\_frames一致；

\* 没有被系统新增的重复末帧；

\* 没有`tpad clone`；

\* 没有时长超出；

\* 没有PTS gap；

\* 没有负时间戳；

\* 帧率控制只发生一次；

\* source duration足够覆盖visual slot。



单个片段不通过，不得进入concat。



\---



\## 二十九、逐转场验收



六条视频的每一个转场必须输出：



\* cut\_time\_ms

\* previous\_clip\_id

\* next\_clip\_id

\* exact\_duplicate\_run\_frames

\* exact\_duplicate\_run\_ms

\* near\_static\_run\_ms

\* source\_motion\_energy

\* output\_motion\_energy

\* pipeline\_introduced\_freeze

\* intentional\_hold

\* transition\_result

\* repair\_action



必须达到：



`pipeline\_introduced\_freeze = false`



所有转场：



`transition\_result = pass`



\---



\## 三十、最终成片验收



六条必须全部满足：



1\. 所有转场新增冻结为0；

2\. 所有PTS连续；

3\. 所有标准化切片从0开始；

4\. 只有一处CFR归一化；

5\. 没有末帧clone填充；

6\. 没有视觉槽位长于真实帧内容；

7\. 音视频总时长误差不超过100ms；

8\. 尾部非设计性静音不超过400ms；

9\. 人手视觉卫生保持通过；

10\. 动作完整性保持通过；

11\. V3A截断修复不得回退；

12\. 1080×1920、SAR 1:1、9:16通过。



任意一条含有系统新增冻结，不得输出完成信号。



\---



\## 三十一、回归测试



必须增加或修改主要测试文件，覆盖：



1\. PTS未归零时失败；

2\. concat输入首帧PTS必须为0；

3\. 双重CFR配置失败；

4\. `tpad=stop\_mode=clone`在动态镜头中失败；

5\. source frame不足时不得clone补足；

6\. `-frames:v`不能代替有效帧检查；

7\. 精确重复帧序列检测；

8\. 近似静止检测；

9\. 原素材静止与管线新增冻结区分；

10\. 动态镜头转场前冻结超过阈值失败；

11\. intentional\_hold合法；

12\. 每个转场都必须被扫描；

13\. 音轨较长时不得保持最后视频帧等待；

14\. L-Cut必须有真实后续视觉帧；

15\. 30fps帧网格量化；

16\. 音视频误差不超过100ms；

17\. 已知失败P12S视频必须被检测器检出；

18\. 修复后P12T六条必须通过。



\---



\## 三十二、输出报告



至少生成：



\* `p12s\_transition\_freeze\_root\_cause\_report.json`

\* `ffmpeg\_freeze\_risk\_scan.json`

\* `segment\_frame\_budget\_report.json`

\* `transition\_freeze\_detection\_report.json`

\* `transition\_repair\_report.json`

\* `vlm\_compute\_value\_report.json`

\* `review\_index.md`

\* 六条P12T成片。



不得用报告替代成片。



\---



\## 三十三、review\_index.md



第一部分直接列出：



\* P12S旧视频路径；

\* P12T新视频路径；

\* 每条时长；

\* P12S冻结转场数量；

\* P12T冻结转场数量；

\* 最长冻结时长变化；

\* 修复根因；

\* 是否改动Storyboard；

\* VLM整片审查结果；

\* 建议Owner重点观看时间点。



汇总：



\* P12S检测到的冻结总数；

\* P12T冻结总数；

\* 删除的clone逻辑；

\* 修复的PTS gap数量；

\* 修复的双重CFR数量；

\* 调整的视觉槽位数量；

\* VLM总Token；

\* VLM改变时间线次数；

\* 总开发与渲染时间。



\---



\## 三十四、最终输出格式



完成后只输出：



TRANSITION\_FREEZE\_ZERO\_TOLERANCE\_READY



视频目录：

V1A新版本：

V1B新版本：

V2A新版本：

V2B新版本：

V3A新版本：

V3B新版本：

P12S冻结转场总数：

P12T冻结转场总数：

最长冻结时长修复前：

最长冻结时长修复后：

根因分类：

删除或修改的高风险FFmpeg参数：

单一CFR策略：

PTS归零结果：

六条音画误差：

VLM总调用数：

VLM总Token：

VLM改变时间线次数：

六条最终整片VLM结果：

总开发与渲染时间：

主要已知问题：

建议A/B观看顺序：



然后停止等待Owner观看。



\---



\## 三十五、执行顺序



1\. 验证本Task；

2\. 确认`spec\_version = P12T-v1`；

3\. 将零冻结规则写入现有`AGENTS.md`；

4\. 读取P12S六条视频、Director Slate和实际FFmpeg命令；

5\. 提取所有剪切点；

6\. 对原素材、中间切片和最终成片进行三级冻结诊断；

7\. 生成根因报告；

8\. 扫描高风险FFmpeg参数；

9\. 确定唯一CFR控制节点；

10\. 修复trim、setpts、frame grid、concat和最终mux逻辑；

11\. 新增`transition\_freeze\_detector.py`；

12\. 对已知失败P12S运行检测器；

13\. 确认检测器能够检出Owner看到的冻结；

14\. 重渲染六条P12T视频；

15\. 对所有标准化切片执行帧预算验证；

16\. 对所有转场执行冻结检测；

17\. 任意冻结失败时局部修复并重新渲染对应视频；

18\. 对六条最终草稿执行GLM-4.6V整片审核；

19\. 仅对有明确问题的成片执行条件式第二次审核；

20\. 生成VLM算力价值报告；

21\. 生成A/B review\_index；

22\. 输出六条P12T视频和核心指标；

23\. 停止等待Owner观看。



本任务的成功由转场冻结数量严格为零、成片节奏恢复和最终视频质量共同决定。



