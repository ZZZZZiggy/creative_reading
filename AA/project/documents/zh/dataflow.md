# 数据流文档

## 0. 全局对象与命名约定

### 基本标识符

- **session_id**：一次谈判/会议的唯一 ID（UUID）
- **participant_id**：一个参与者（真人或模拟 agent）的唯一 ID（UUID）
- **speaker_id**：音频 diarization 的说话人标签（如 spk_0），后面会映射到 participant_id
- **turn_id**：一次发言的唯一 ID（UUID 或 {session_id}:{index}）
- **event_id**：一个"谈判动作事件"的唯一 ID
- **state_id**：某个时间步的状态快照 ID
- **branch_id**：某个分支路径 ID
- **step_idx**：离散推演的步数（0,1,2…），通常与事件序列对齐

---

## 1. L0 录音/信号 → Turn 时间线（转写+分说话人+特征对齐）

### Step L0.1 IngestSession（创建会话资产）

#### Input

- **AudioAsset**
- **可选**：PerceptionAsset[]（EEG/EDA/HR）

#### AudioAsset

```json
{
  "session_id": "uuid",
  "audio_uri": "s3://.../audio.wav",
  "sample_rate_hz": 16000,
  "duration_sec": 1832.4,
  "channels": 1,
  "recorded_at": "2026-01-22T18:03:11Z",
  "timezone": "America/New_York"
}
```

**字段解释**：
- `audio_uri`：音频文件位置
- `sample_rate_hz`：采样率
- `duration_sec`：总时长
- `channels`：声道数
- `recorded_at/timezone`：录制时间与时区（用于对齐外部数据）

#### PerceptionAsset（可选，例：EDA）

```json
{
  "session_id": "uuid",
  "participant_id": "uuid",
  "modality": "EDA",
  "data_uri": "s3://.../eda.csv",
  "sample_rate_hz": 32,
  "time_base": "unix_epoch_ms",
  "start_time_ms": 1737578591000
}
```

**字段解释**：
- `participant_id`：该传感器属于谁（佩戴者）
- `modality`：EEG/EDA/HR/…
- `time_base/start_time_ms`：时间基准，用于与音频对齐

#### Output

- **SessionManifest**

```json
{
  "session_id": "uuid",
  "assets": {
    "audio": {"audio_uri":"..."},
    "perception": [{"modality":"EDA","data_uri":"..."}]
  },
  "status": "INGESTED"
}
```

---

### Step L0.2 ASR + Diarization（转写+分说话人）

#### Input

- **SessionManifest**

#### Output

- **TranscriptSegment[]**

```json
{
  "session_id": "uuid",
  "segment_index": 0,
  "t0_sec": 12.30,
  "t1_sec": 18.90,
  "speaker_id": "spk_0",
  "text": "We can only do 120k.",
  "asr_confidence": 0.92,
  "words": [
    {"t0_sec":12.35,"t1_sec":12.60,"w":"We","conf":0.94},
    {"t0_sec":12.61,"t1_sec":12.90,"w":"can","conf":0.93}
  ]
}
```

**字段解释**：
- `t0_sec/t1_sec`：该片段在音频中的起止时间（秒）
- `speaker_id`：说话人标签（音频层）
- `asr_confidence`：转写置信度
- `words`：可选逐词时间戳（后续做证据 span、语速很有用）

---

### Step L0.3 TurnBuilder（合并片段→发言 turn）

#### Input

- **TranscriptSegment[]**

#### Output

- **Turn[]**（后续所有层都用 Turn）

```json
{
  "session_id": "uuid",
  "turn_id": "uuid",
  "turn_index": 12,
  "t0_sec": 120.10,
  "t1_sec": 141.85,
  "speaker_id": "spk_0",
  "participant_id": null,
  "text": "We can only do 120k and we'd need delivery by March.",
  "lang": "en",
  "source_segments": [33,34,35]
}
```

**字段解释**：
- `turn_index`：顺序编号
- `participant_id`：后面做 speaker→真实参与者映射（此时可为空）
- `source_segments`：这个 turn 由哪些 segment 合并来的（可追溯）

---

### Step L0.4 FeatureAligner（特征：音频+生理 对齐到 turn）

#### Input

- **Turn[]**
- **AudioAsset**
- **可选**：PerceptionAsset[]

#### Output

- **TurnEnriched[]**（= Turn + features）

```json
{
  "session_id": "uuid",
  "turn_id": "uuid",
  "t0_sec": 120.10,
  "t1_sec": 141.85,
  "speaker_id": "spk_0",
  "text": "...",
  "audio_features": {
    "speech_rate_wps": 2.9,
    "mean_pitch_hz": 185.2,
    "pitch_std_hz": 22.4,
    "energy_rms": 0.031,
    "pause_total_ms": 420
  },
  "physio_features": {
    "EDA": {
      "window": {"t0_sec":118.10,"t1_sec":143.85},
      "eda_mean": 0.12,
      "eda_slope": 0.008
    }
  }
}
```

**字段解释**：
- `speech_rate_wps`：语速（words per second）
- `pause_total_ms`：turn 内停顿总时长
- `physio_features.EDA.window`：用于提取生理特征的时间窗（通常比 turn 稍微扩大）
- `eda_slope`：该窗口内 EDA 趋势（紧张/唤醒变化信号之一）

> **说明**：到这里，L0 完成：你有一个统一时间轴、可回放、有多模态特征的 Turn 序列。

---

## 2. L1 Turn → Event（谈判动作/条款抽取）

### Step L1.1 EventExtractor（每个 turn 抽取一个或多个事件）

#### Input

- **TurnEnriched[]**
- **可选**：ParticipantDirectory（把 spk_0 映射为 A/B）

#### ParticipantDirectory（可选）

```json
{
  "session_id":"uuid",
  "speaker_to_participant": {
    "spk_0": "uuid-A",
    "spk_1": "uuid-B"
  },
  "participants": [
    {"participant_id":"uuid-A","display_name":"Person A","role":"Seller"},
    {"participant_id":"uuid-B","display_name":"Person B","role":"Buyer"}
  ]
}
```

#### Output

- **Event[]**

```json
{
  "session_id": "uuid",
  "event_id": "uuid",
  "turn_id": "uuid",
  "actor_participant_id": "uuid-A",
  "act_type": "ANCHOR",
  "act_subtype": null,
  "targets": ["uuid-B"],
  "terms": [
    {
      "term_type": "PRICE",
      "value": 120000,
      "currency": "USD",
      "confidence": 0.86,
      "evidence": {"text_span":"120k","char_start":17,"char_end":21}
    }
  ],
  "stance": "FIRM",
  "intent": "SET_BASELINE",
  "tone": {
    "valence": -0.1,
    "arousal": 0.4,
    "confidence": 0.7
  }
}
```

**字段解释**：
- `act_type`：动作类型（建议固定枚举）
- `targets`：这句话主要针对谁（可为空/多人）
- `terms[]`：条款抽取列表
- `term_type`：PRICE / DEADLINE / SCOPE / EQUITY / …
- `value`：标准化数值（比如 120k→120000）
- `evidence`：在原 turn 文本里的位置，用于可解释性/高亮
- `stance`：态度（FIRM/OPEN/CONDITIONAL/…）
- `intent`：意图（SET_BASELINE / SEEK_CONCESSION / BUILD_RAPPORT 等）
- `tone`：情绪/语气的结构化表示（可由音频+文本融合推断）

---

## 3. L2 Event → State（状态机轨迹）

### Step L2.1 StateInit（初始化谈判世界）

#### Input

- **SessionConfig**（议题、默认条款、参与者角色）

```json
{
  "session_id":"uuid",
  "issues":[
    {"term_type":"PRICE","unit":"USD"},
    {"term_type":"DEADLINE","unit":"ISO_DATE"}
  ],
  "initial_terms": {},
  "participants":[
    {"participant_id":"uuid-A","role":"Seller"},
    {"participant_id":"uuid-B","role":"Buyer"}
  ]
}
```

#### Output

- **StateSnapshot**（step_idx=0）

```json
{
  "session_id":"uuid",
  "state_id":"uuid",
  "step_idx": 0,
  "last_event_id": null,
  "terms": {},
  "beliefs": {},
  "relationship": {"trust": 0.5, "tension": 0.0},
  "emotion": {"uuid-A":{"anger":0.0,"stress":0.2},"uuid-B":{"anger":0.0,"stress":0.2}},
  "meta": {"round":1}
}
```

**字段解释**：
- `terms`：当前条款（结构化）
- `beliefs`：对对方底线/偏好估计（概率分布/区间）
- `relationship`：关系状态
- `emotion`：每个参与者的情绪状态（建议固定 2–4 维）
- `meta.round`：谈判轮次（可自定义轮次逻辑）

---

### Step L2.2 StateReducer（逐事件更新状态）

#### Input

- **StateSnapshot**(step_idx=k)
- **Event**(event_idx=k+1)（按时间顺序）
- **可选**：Profiles（若已拟合可用于更合理更新）

#### Output

- **StateSnapshot**(step_idx=k+1) + **StateDelta**

#### StateDelta（解释"改变了什么"）

```json
{
  "session_id":"uuid",
  "from_state_id":"uuid_prev",
  "to_state_id":"uuid_next",
  "event_id":"uuid_evt",
  "deltas": {
    "terms": [{"op":"SET","path":"$.PRICE","value":120000}],
    "relationship": [{"op":"ADD","path":"$.tension","value":0.10}],
    "emotion": [{"op":"ADD","path":"$.uuid-B.stress","value":0.15}]
  },
  "rationale": "Anchor increased tension slightly; buyer stress rose due to high initial price."
}
```

**字段解释**：
- `deltas`：像 JSON patch 的形式描述变化（利于回放/分支）
- `rationale`：解释（可选）

---

## 4. L3 Persona Fitting（从轨迹拟合 Profile）

### Step L3.1 FitProfile（给每个参与者拟合参数）

#### Input

- **TurnEnriched[]**
- **Event[]**
- **StateSnapshots[]**（可选但很有帮助）

#### Output

- **AgentProfile[]** + **FitMetrics**

#### AgentProfile

```json
{
  "session_id":"uuid",
  "participant_id":"uuid-A",
  "profile_version":"v1",
  "traits": {
    "dominance": 0.78,
    "agreeableness": 0.22,
    "risk_aversion": 0.55
  },
  "tactic_priors": {
    "ANCHOR": 0.60,
    "CONCEDE": 0.20,
    "THREATEN": 0.05,
    "ASK": 0.15
  },
  "trigger_rules": [
    {
      "trigger_id":"t1",
      "condition": {"type":"INTERRUPT_COUNT_GTE","value":2},
      "effect": {"emotion_delta":{"anger":0.25}}
    }
  ],
  "utility_weights": {
    "PRICE": 0.60,
    "TIME": 0.15,
    "RELATIONSHIP": 0.25
  }
}
```

**字段解释**：
- `traits`：稳定特质（0–1 归一化）
- `tactic_priors`：动作先验概率（归一化总和≈1）
- `trigger_rules`：触发器（条件→情绪/策略变化）
- `utility_weights`：效用权重（用于 L4/L6）

#### FitMetrics

```json
{
  "session_id":"uuid",
  "participant_id":"uuid-A",
  "next_act_prediction_f1": 0.61,
  "confidence": 0.72,
  "notes": "Profile explains most concessions but underpredicts threats."
}
```

---

## 5. L4 State + Profile → Action → Utterance（仿真用）

### Step L4.1 DecideAction（决策动作）

#### Input

- **StateSnapshot**(step_idx=k)
- **AgentProfile**(participant_id=X)
- **LastKContext**（最近 K 个事件/turn 摘要，避免 token 爆炸）

#### Output

- **AgentAction**

```json
{
  "session_id":"uuid",
  "step_idx": 35,
  "actor_participant_id":"uuid-B",
  "action": {
    "act_type":"COUNTER",
    "terms":[{"term_type":"PRICE","value":95000,"currency":"USD"}],
    "tone_style":"CALM",
    "strategy_tags":["SIGNAL_LIMIT","KEEP_RELATIONSHIP"],
    "rationale":"Counter to move anchor down while maintaining rapport."
  }
}
```

**字段解释**：
- `tone_style`：用于语言实现（CALM/ASSERTIVE/APOLOGETIC/…）
- `strategy_tags`：策略标签（可用于评估与教学）

---

### Step L4.2 RealizeUtterance（把动作说成人话）

#### Input

- **AgentAction**
- **StateSnapshot**（用于引用上下文但不得改 terms）

#### Output

- **Utterance**

```json
{
  "session_id":"uuid",
  "step_idx":35,
  "actor_participant_id":"uuid-B",
  "text":"I hear you. Given our constraints, we could move forward at $95k if we can lock the March delivery date.",
  "constraints_check": {
    "terms_consistent": true,
    "no_new_terms_introduced": true
  }
}
```

**字段解释**：
- `constraints_check`：自动校验语言是否"偷改条款"

---

## 6. L5 分支引擎（反事实干预 → rollout）

### Step L5.1 IdentifyBranchPoints（找分叉点）

#### Input

- **StateSnapshots[]**
- **Events[]**

#### Output

- **BranchPoint[]**

```json
{
  "session_id":"uuid",
  "branch_point_id":"uuid",
  "step_idx": 28,
  "reason": "High tension jump after THREATEN",
  "candidate_interventions": [
    {"type":"REPLACE_ACT","from":"THREATEN","to":"REFRAME"},
    {"type":"CLAMP_EMOTION","participant_id":"uuid-A","field":"anger","value":0.0}
  ]
}
```

---

### Step L5.2 ApplyIntervention + Rollout（应用干预并推演）

#### Input

- **BaseStateSnapshot**(step_idx=bp)
- **Intervention**
- **Profiles[]**
- **RolloutConfig**（轮数、beam 宽度等）

#### Output

- **BranchTrace**（一条路径）
- 多条路径组成 **BranchTree**

#### Intervention

```json
{
  "type":"CLAMP_EMOTION",
  "participant_id":"uuid-A",
  "field":"anger",
  "value":0.0,
  "duration_steps": 3
}
```

#### BranchTrace（路径）

```json
{
  "session_id":"uuid",
  "branch_id":"b1",
  "parent_branch_id": null,
  "start_step_idx": 28,
  "steps":[
    {"step_idx":29,"state_id":"...","action_id":"...","utterance_id":"..."},
    {"step_idx":30,"state_id":"...","action_id":"...","utterance_id":"..."}
  ]
}
```

---

## 7. L6 评估与报告（指标 + 教练反馈）

### Step L6.1 ComputeMetrics（规则指标）

#### Input

- **BranchTrace** + associated **StateSnapshots**

#### Output

- **OutcomeMetrics**

```json
{
  "session_id":"uuid",
  "branch_id":"b1",
  "agreement_reached": true,
  "final_terms": {"PRICE": 102000, "DEADLINE":"2026-03-01"},
  "utility": {"uuid-A": 0.62, "uuid-B": 0.58},
  "relationship_damage": 0.18,
  "volatility": 0.22,
  "efficiency_rounds": 6
}
```

**字段解释**：
- `utility`：归一化效用（基于 utility_weights 或预设曲线）
- `relationship_damage`：相对基线的关系损伤
- `volatility`：情绪/冲突波动程度
- `efficiency_rounds`：达成所用轮次

---

### Step L6.2 JudgeRubric（软性评估：话术/策略）

#### Input

- **BranchTrace**（actions + utterances）
- **RubricDefinition**

#### Output

- **RubricScores**

```json
{
  "session_id":"uuid",
  "branch_id":"b1",
  "scores": {
    "clarity": 8.2,
    "empathy": 7.6,
    "leverage": 6.9,
    "coherence": 8.8
  },
  "highlights": [
    {"step_idx":35,"type":"GOOD_MOVE","note":"Reframed without conceding too early."}
  ],
  "risks":[
    {"step_idx":37,"type":"RISK","note":"Introduced deadline condition could trigger resistance."}
  ]
}
```

---

### Step L6.3 ReportBuilder（生成复盘/对比报告）

#### Input

- **BaseTrace**（原始轨迹）
- **BranchTraces[]**
- **OutcomeMetrics[]**
- **RubricScores[]**

#### Output

- **ReviewReport**

```json
{
  "session_id":"uuid",
  "summary": "...",
  "key_moments":[{"step_idx":28,"why":"tension spike","what_to_try":["reframe","pause"]}],
  "branch_comparison":[
    {"branch_id":"base","agreement":false,"utility_avg":0.41},
    {"branch_id":"b1","agreement":true,"utility_avg":0.60}
  ],
  "recommendations":[
    {"for_participant":"uuid-A","rule":"When tension>0.7, avoid THREATEN; use REFRAME + ask constraint."}
  ]
}
```

---

## 完整"时序流"的简化版

1. **AudioAsset**(+PerceptionAsset)
2. → **TranscriptSegment[]**
3. → **Turn[]**
4. → **TurnEnriched[]**
5. → **Event[]**
6. → **StateSnapshot[]** + **StateDelta[]**
7. → **AgentProfile[]** + **FitMetrics[]**
8. → **(Sim) AgentAction[]** → **Utterance[]**
9. → **BranchPoint[]** → **BranchTrace/BranchTree**
10. → **OutcomeMetrics** + **RubricScores**
11. → **ReviewReport**
