# Data Flow Documentation

## 0. Global Objects and Naming Conventions

### Basic Identifiers

- **session_id**: Unique ID for a negotiation/meeting (UUID)
- **participant_id**: Unique ID for a participant (real person or simulated agent) (UUID)
- **speaker_id**: Speaker label from audio diarization (e.g., spk_0), later mapped to participant_id
- **turn_id**: Unique ID for a turn (UUID or {session_id}:{index})
- **event_id**: Unique ID for a "negotiation action event"
- **state_id**: State snapshot ID at a time step
- **branch_id**: Branch path ID
- **step_idx**: Discrete simulation step number (0,1,2…), usually aligned with event sequence

---

## 1. L0 Recording/Signal → Turn Timeline (Transcription + Speaker Separation + Feature Alignment)

### Step L0.1 IngestSession (Create Session Assets)

#### Input

- **AudioAsset**
- **Optional**: PerceptionAsset[] (EEG/EDA/HR)

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

**Field Explanation**:
- `audio_uri`: Audio file location
- `sample_rate_hz`: Sample rate
- `duration_sec`: Total duration
- `channels`: Number of channels
- `recorded_at/timezone`: Recording time and timezone (for aligning external data)

#### PerceptionAsset (Optional, Example: EDA)

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

**Field Explanation**:
- `participant_id`: Who the sensor belongs to (wearer)
- `modality`: EEG/EDA/HR/…
- `time_base/start_time_ms`: Time base for alignment with audio

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

### Step L0.2 ASR + Diarization (Transcription + Speaker Separation)

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

**Field Explanation**:
- `t0_sec/t1_sec`: Start and end time of this segment in audio (seconds)
- `speaker_id`: Speaker label (audio layer)
- `asr_confidence`: Transcription confidence
- `words`: Optional word-level timestamps (useful for evidence spans and speech rate)

---

### Step L0.3 TurnBuilder (Merge Segments → Turn)

#### Input

- **TranscriptSegment[]**

#### Output

- **Turn[]** (all subsequent layers use Turn)

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

**Field Explanation**:
- `turn_index`: Sequential number
- `participant_id`: Later mapped from speaker→real participant (can be null at this stage)
- `source_segments`: Which segments this turn was merged from (traceable)

---

### Step L0.4 FeatureAligner (Features: Audio + Physiological Aligned to Turn)

#### Input

- **Turn[]**
- **AudioAsset**
- **Optional**: PerceptionAsset[]

#### Output

- **TurnEnriched[]** (= Turn + features)

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

**Field Explanation**:
- `speech_rate_wps`: Speech rate (words per second)
- `pause_total_ms`: Total pause duration within turn
- `physio_features.EDA.window`: Time window for extracting physiological features (usually slightly expanded from turn)
- `eda_slope`: EDA trend within this window (one signal of tension/arousal change)

> **Note**: At this point, L0 is complete: you have a unified timeline, replayable Turn sequence with multimodal features.

---

## 2. L1 Turn → Event (Negotiation Action/Term Extraction)

### Step L1.1 EventExtractor (Extract One or More Events from Each Turn)

#### Input

- **TurnEnriched[]**
- **Optional**: ParticipantDirectory (map spk_0 to A/B)

#### ParticipantDirectory (Optional)

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

**Field Explanation**:
- `act_type`: Action type (recommended to fix enumeration)
- `targets`: Who this statement primarily targets (can be empty/multiple people)
- `terms[]`: Term extraction list
- `term_type`: PRICE / DEADLINE / SCOPE / EQUITY / …
- `value`: Normalized value (e.g., 120k→120000)
- `evidence`: Position in original turn text, for explainability/highlighting
- `stance`: Attitude (FIRM/OPEN/CONDITIONAL/…)
- `intent`: Intent (SET_BASELINE / SEEK_CONCESSION / BUILD_RAPPORT, etc.)
- `tone`: Structured representation of emotion/tone (can be inferred from audio + text fusion)

---

## 3. L2 Event → State (State Machine Trajectory)

### Step L2.1 StateInit (Initialize Negotiation World)

#### Input

- **SessionConfig** (issues, default terms, participant roles)

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

- **StateSnapshot** (step_idx=0)

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

**Field Explanation**:
- `terms`: Current terms (structured)
- `beliefs`: Estimates of opponent's bottom line/preferences (probability distributions/ranges)
- `relationship`: Relationship state
- `emotion`: Emotional state of each participant (recommended to fix 2–4 dimensions)
- `meta.round`: Negotiation round (can customize round logic)

---

### Step L2.2 StateReducer (Update State Event by Event)

#### Input

- **StateSnapshot**(step_idx=k)
- **Event**(event_idx=k+1) (in chronological order)
- **Optional**: Profiles (if fitted, can be used for more reasonable updates)

#### Output

- **StateSnapshot**(step_idx=k+1) + **StateDelta**

#### StateDelta (Explains "What Changed")

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

**Field Explanation**:
- `deltas`: JSON patch-like form describing changes (beneficial for replay/branching)
- `rationale`: Explanation (optional)

---

## 4. L3 Persona Fitting (Fit Profile from Trajectory)

### Step L3.1 FitProfile (Fit Parameters for Each Participant)

#### Input

- **TurnEnriched[]**
- **Event[]**
- **StateSnapshots[]** (optional but very helpful)

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

**Field Explanation**:
- `traits`: Stable traits (0–1 normalized)
- `tactic_priors`: Action prior probabilities (normalized sum≈1)
- `trigger_rules`: Triggers (condition→emotion/strategy change)
- `utility_weights`: Utility weights (for L4/L6)

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

## 5. L4 State + Profile → Action → Utterance (For Simulation)

### Step L4.1 DecideAction (Decision Action)

#### Input

- **StateSnapshot**(step_idx=k)
- **AgentProfile**(participant_id=X)
- **LastKContext** (summary of last K events/turns, to avoid token explosion)

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

**Field Explanation**:
- `tone_style`: For language realization (CALM/ASSERTIVE/APOLOGETIC/…)
- `strategy_tags`: Strategy tags (can be used for evaluation and teaching)

---

### Step L4.2 RealizeUtterance (Convert Action to Natural Language)

#### Input

- **AgentAction**
- **StateSnapshot** (for referencing context but must not change terms)

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

**Field Explanation**:
- `constraints_check`: Automatic validation of whether language "secretly changed terms"

---

## 6. L5 Branch Engine (Counterfactual Intervention → Rollout)

### Step L5.1 IdentifyBranchPoints (Find Branch Points)

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

### Step L5.2 ApplyIntervention + Rollout (Apply Intervention and Simulate)

#### Input

- **BaseStateSnapshot**(step_idx=bp)
- **Intervention**
- **Profiles[]**
- **RolloutConfig** (number of rounds, beam width, etc.)

#### Output

- **BranchTrace** (one path)
- Multiple paths form **BranchTree**

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

#### BranchTrace (Path)

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

## 7. L6 Evaluation and Reporting (Metrics + Coaching Feedback)

### Step L6.1 ComputeMetrics (Rule-Based Metrics)

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

**Field Explanation**:
- `utility`: Normalized utility (based on utility_weights or preset curves)
- `relationship_damage`: Relationship damage relative to baseline
- `volatility`: Emotional/conflict fluctuation level
- `efficiency_rounds`: Number of rounds to reach agreement

---

### Step L6.2 JudgeRubric (Soft Evaluation: Language/Strategy)

#### Input

- **BranchTrace** (actions + utterances)
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

### Step L6.3 ReportBuilder (Generate Replay/Comparison Report)

#### Input

- **BaseTrace** (original trajectory)
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

## Complete "Sequential Flow" Simplified

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
