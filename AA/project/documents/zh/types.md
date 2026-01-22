# 类型与枚举定义文档

下面给你一份「现阶段可以枚举并定死」的变量清单（按 L0–L6 分层）。这些枚举一旦定下来，你的数据流、状态机、分支干预、评估体系都会稳定很多。

我把每个枚举都写成：
- 枚举名
- 取值列表
- 每个取值含义
- 出现在哪些对象/字段里

---

## L0 输入与对齐层（Audio / Turn）

### 1. modality（生理/感知数据类型）

**用于**：`PerceptionAsset.modality`

- **EDA**：皮电（Electrodermal Activity）
- **HR**：心率（Heart Rate）
- **HRV**：心率变异（Heart Rate Variability）
- **EEG**：脑电
- **RESP**：呼吸
- **TEMP**：皮温/体温
- **EYE**：眼动/注视（如果未来接入）
- **ACC**：加速度（体动）

---

### 2. time_base

**用于**：`PerceptionAsset.time_base`

- **unix_epoch_ms**：Unix 时间戳（毫秒）
- **unix_epoch_sec**：Unix 时间戳（秒）
- **relative_sec**：相对起点秒（从设备开始记录算）

---

### 3. language_code（Turn.lang）

- **en**、**zh**、**es**…（用 ISO 639-1，先支持 en/zh 就够）

---

### 4. speaker_mapping_status（speaker→participant 映射状态）

**用于**：`ParticipantDirectory.mapping_status`

- **UNMAPPED**：未映射
- **AUTO_MAPPED**：自动映射（可能不准）
- **CONFIRMED**：人工确认
- **CONFLICT**：冲突需要处理

---

## L1 事件抽取层（谈判动作 / 条款）

### 5. act_type（谈判动作类型：最关键）

**用于**：`Event.act_type`、`AgentAction.action.act_type`、`Intervention.REPLACE_ACT`

现阶段建议先定死 **14 个**（够覆盖 80% 场景，且可控）

#### 提案/条款类

- **OFFER**：提出明确方案（含 terms）
- **COUNTER**：反报价/反提案（含 terms）
- **CONCEDE**：让步（含 terms 的变更方向对对方更好）
- **ACCEPT**：接受对方提案（明确同意）
- **REJECT**：明确拒绝（不接受当前提案）

#### 信息与澄清类

- **ASK**：提问/澄清（不改 terms）
- **DISCLOSE**：透露信息/偏好/约束（"我们预算只有…"）
- **SUMMARIZE**：总结/确认当前共识（防误解）

#### 策略与关系类

- **ANCHOR**：锚定（高/低起点以影响区间，通常含 price）
- **JUSTIFY**：给理由/论证（为 offer/counter 做支撑）
- **REFRAME**：重构问题（从对抗转合作、换角度）
- **BUILD_RAPPORT**：建立关系/共情/缓和气氛
- **THREATEN**：威胁/最后通牒/暗示退出
- **PAUSE**：暂停/推迟/需要时间（"我们回去讨论"）

> **备注**：ANCHOR 和 OFFER/COUNTER 有时会重叠。为了可控，你可以允许一个 turn 抽取多个 Event（如先 ANCHOR 再 OFFER）。

---

### 6. act_subtype（动作子类型，可选但可枚举）

**用于**：`Event.act_subtype`

- **对 THREATEN**：
  - `WALK_AWAY`：直接说要退出
  - `DEADLINE`：最后期限/拖不起
  - `ESCALATE`：升级到上级/法律/公开

- **对 CONCEDE**：
  - `SMALL_STEP`：小让步
  - `MAJOR_STEP`：大让步
  - `CONDITIONAL`：有条件让步

- **对 ASK**：
  - `CLARIFY_TERM`：澄清条款
  - `PROBE_LIMIT`：探底线
  - `PROBE_PRIORITY`：探优先级

- **对 REFRAME**：
  - `INTEREST_BASED`：从立场转利益
  - `WIN_WIN`：强调共赢
  - `SCOPE_SPLIT`：拆分议题

---

### 7. term_type（条款类型）

**用于**：`Term.term_type`、`State.terms`、`UtilityWeights`

先定死 **12 个**，覆盖商谈/融资/采购/合作都够用

- **PRICE**：价格/金额
- **CURRENCY**：币种（通常是 term 的属性，也可单独）
- **QUANTITY**：数量
- **SCOPE**：范围/交付内容（可结构化为文本+标签）
- **TIMELINE**：时间线/里程碑（大框架）
- **DEADLINE**：截止日期（单点日期）
- **PAYMENT_TERMS**：付款条件（预付/账期/分期）
- **DELIVERABLES**：交付物清单（可结构化列表）
- **QUALITY_SLA**：质量/服务等级（SLA）
- **LIABILITY**：责任/赔偿/上限
- **EXCLUSIVITY**：独家/竞业限制
- **TERMINATION**：解约/退出条款

---

### 8. term_value_type（条款值的类型）

**用于**：`Term.value_type`（帮助标准化）

- **NUMBER**：数值（如 120000）
- **MONEY**：货币（value + currency）
- **PERCENT**：百分比（如 2.5%）
- **DATE**：日期（ISO）
- **DURATION**：时长（如 P30D）
- **TEXT**：文本（如 scope 描述）
- **ENUM**：枚举（如付款方式）
- **LIST**：列表（deliverables）

---

### 9. stance（态度/开放程度）

**用于**：`Event.stance`

- **FIRM**：强硬/不松口
- **OPEN**：开放/可讨论
- **CONDITIONAL**：有条件
- **HESITANT**：犹豫/不确定
- **NONCOMMITTAL**：模糊/不表态

---

### 10. intent（意图：高层可枚举）

**用于**：`Event.intent`、`AgentAction.strategy_tags`

先定死 **10 个**够用

- **SET_BASELINE**：设定基准（锚定）
- **SEEK_CONCESSION**：争取对方让步
- **TEST_LIMITS**：测试底线
- **SHARE_CONSTRAINT**：说明约束/限制
- **BUILD_TRUST**：建立信任/关系
- **REDUCE_TENSION**：降温
- **GAIN_TIME**：争取时间
- **CLOSE_DEAL**：推进成交
- **SHIFT_TOPIC**：转移议题
- **ESCALATE_PRESSURE**：施压升级

---

### 11. tone_style（语言风格/语气）

**用于**：`AgentAction.tone_style`、`Event.tone_style`

- **CALM**：冷静
- **ASSERTIVE**：坚定
- **FRIENDLY**：友好
- **APOLOGETIC**：歉意/柔和
- **AGGRESSIVE**：攻击/强压
- **SARCASTIC**：讽刺（可选，很多场景不用）
- **FORMAL**：正式
- **CASUAL**：随意
- **UNCERTAIN**：不确定/试探

---

## L2 状态机层（数值状态的维度枚举）

### 12. emotion_dim（情绪维度：建议定死 4 维）

**用于**：`State.emotion[participant_id]`

- **anger**：愤怒/敌意
- **stress**：压力/紧张
- **confidence**：自信/掌控感
- **warmth**：友好/亲和

取值范围建议固定：**0.0 – 1.0**

---

### 13. relationship_dim（关系维度：建议定死 3 维）

**用于**：`State.relationship`

- **trust**：信任度（0–1）
- **tension**：对抗/紧张（0–1）
- **alignment**：目标一致性/合作倾向（0–1）

---

### 14. belief_type（信念/估计的类型）

**用于**：`State.beliefs[belief_key].type`

- **RANGE**：区间（min/max）
- **GAUSSIAN**：正态（mu/sigma）
- **CATEGORICAL**：类别分布（概率表）

---

### 15. belief_key（你可以先定死一组常用信念键）

**用于**：`State.beliefs`

- `opponent_min_price`：对方最低可接受价格（买方视角是最高可接受价格）
- `opponent_max_price`
- `opponent_urgency`：对方紧迫度
- `opponent_risk_aversion`：对方风险厌恶
- `opponent_priority_PRICE`
- `opponent_priority_TIME`
- `opponent_priority_RELATIONSHIP`

---

## L3 Persona/Profile 层（可枚举的参数键）

### 16. trait_key（人格/行为特质键）

**用于**：`AgentProfile.traits`

- **dominance**：支配性/强势
- **agreeableness**：宜人性/合作
- **risk_aversion**：风险厌恶
- **patience**：耐心/愿意拖
- **emotional_reactivity**：情绪反应强度（容易上头）

---

### 17. trigger_condition_type（触发条件类型）

**用于**：`TriggerRule.condition.type`

- **INTERRUPT_COUNT_GTE**：被打断次数 ≥ N
- **NEGATIVE_TONE_GTE**：对方负向语气 ≥ 阈值
- **TENSION_GTE**：关系紧张度 ≥ 阈值
- **CONCESSION_FROM_OPPONENT**：对方让步发生
- **TIME_PRESSURE_GTE**：时间压力 ≥ 阈值
- **TERM_MOVED_AGAINST_ME**：条款朝不利方向移动

---

### 18. trigger_effect_type

**用于**：`TriggerRule.effect`

- **EMOTION_DELTA**：情绪增量（改 anger/stress…）
- **TACTIC_PRIOR_SHIFT**：策略先验偏移（更可能 threaten/更可能 concede）
- **TONE_STYLE_OVERRIDE**：强制语气（比如变 aggressive）

---

## L4 Agent 决策层（可枚举的策略标签）

### 19. strategy_tag（决策解释/教学标签）

**用于**：`AgentAction.strategy_tags`

- **SIGNAL_LIMIT**：表明底线
- **PROBE_LIMIT**：探底线
- **TRADE_OFF**：交换条件（你给我X我给你Y）
- **SPLIT_THE_DIFFERENCE**：折中
- **PACKAGE_DEAL**：打包议题
- **SLOW_CONCEDE**：慢让步节奏
- **FAST_CLOSE**：快速成交
- **APPEAL_AUTHORITY**：诉诸权威/规则/政策
- **USE_DEADLINE**：用期限施压
- **DE_ESCALATE**：降温

---

## L5 分支干预层（Intervention 类型）

### 20. intervention_type

**用于**：`Intervention.type`

- **REPLACE_ACT**：替换某个动作（THREATEN→REFRAME）
- **EDIT_TERMS**：修改条款（把 price 改为某值）
- **CLAMP_EMOTION**：夹紧情绪（anger=0）
- **ADD_TRIGGER**：添加触发器（模拟某刺激）
- **REMOVE_EVENT**：移除某事件（假设没说那句话）
- **INFO_HIDE**：信息遮蔽（某 participant 看不到某信念/事实）
- **POLICY_SHIFT**：临时改变 profile 参数（dominance↓）

---

## L6 评估层（指标枚举 + rubric 维度）

### 21. metric_key（规则指标键）

**用于**：`OutcomeMetrics`

- **agreement_reached**：是否达成
- **utility_self**：自己效用
- **utility_other**：对方效用
- **utility_avg**：平均效用
- **fairness_gap**：效用差距（越小越公平）
- **relationship_damage**：关系损伤
- **volatility**：波动/冲突强度
- **efficiency_rounds**：轮次数
- **time_to_agreement_sec**：达成耗时
- **concession_count**：让步次数

---

### 22. rubric_dim（LLM 软评分维度）

**用于**：`RubricScores.scores`

- **clarity**：清晰度
- **empathy**：共情
- **leverage**：筹码/策略性
- **coherence**：一致性/不自相矛盾
- **professionalism**：职业度
- **creativity**：创造性解决方案（可选）

---

### 23. highlight_type

**用于**：`RubricScores.highlights[].type`

- **GOOD_MOVE**：好招
- **MISSED_OPPORTUNITY**：错失机会
- **RISK**：风险点
- **ESCALATION**：升级点
- **DE_ESCALATION**：降温点

---

## 额外：全局通用枚举（强烈建议定死）

### 24. confidence_level

**用于**：各种置信度分桶（UI/过滤用）

- **LOW**：<0.4
- **MEDIUM**：0.4–0.7
- **HIGH**：>0.7

---

### 25. status（pipeline 任务状态）

**用于**：所有步骤的 job state

- **PENDING**
- **RUNNING**
- **SUCCEEDED**
- **FAILED**
- **NEEDS_REVIEW**（需要人工修正，比如 diarization）

---

## 最小集合建议

你现在可以立刻"定死并写进 schema"的最小集合（强烈建议）

如果你只想先定最关键的 **6 个枚举**来锁住系统：

1. **act_type**
2. **term_type**
3. **tone_style**
4. **emotion_dim**
5. **intervention_type**
6. **rubric_dim**

---

> **提示**：如果你点头，我下一条可以把这些枚举变成一份可直接粘贴进项目的 schema 定义（TS type + as const，或者 JSON Schema），并同时给出每个字段应该挂在哪些对象上（避免你团队实现时乱放）。
