# Type and Enumeration Definitions

Below is a list of variables that can be enumerated and fixed at this stage (layered by L0–L6). Once these enumerations are fixed, your data flow, state machine, branch intervention, and evaluation systems will be much more stable.

Each enumeration is written as:
- Enumeration name
- Value list
- Meaning of each value
- Which objects/fields it appears in

---

## L0 Input and Alignment Layer (Audio / Turn)

### 1. modality (Physiological/Perception Data Type)

**Used in**: `PerceptionAsset.modality`

- **EDA**: Electrodermal Activity
- **HR**: Heart Rate
- **HRV**: Heart Rate Variability
- **EEG**: Electroencephalography
- **RESP**: Respiration
- **TEMP**: Skin/Body Temperature
- **EYE**: Eye Movement/Gaze (if integrated in the future)
- **ACC**: Acceleration (Body Movement)

---

### 2. time_base

**Used in**: `PerceptionAsset.time_base`

- **unix_epoch_ms**: Unix timestamp (milliseconds)
- **unix_epoch_sec**: Unix timestamp (seconds)
- **relative_sec**: Relative start seconds (from device recording start)

---

### 3. language_code (Turn.lang)

- **en**, **zh**, **es**... (using ISO 639-1, supporting en/zh initially is sufficient)

---

### 4. speaker_mapping_status (speaker→participant mapping status)

**Used in**: `ParticipantDirectory.mapping_status`

- **UNMAPPED**: Not mapped
- **AUTO_MAPPED**: Auto-mapped (may be inaccurate)
- **CONFIRMED**: Manually confirmed
- **CONFLICT**: Conflict requiring resolution

---

## L1 Event Extraction Layer (Negotiation Actions / Terms)

### 5. act_type (Negotiation Action Type: Most Critical)

**Used in**: `Event.act_type`, `AgentAction.action.act_type`, `Intervention.REPLACE_ACT`

Currently recommended to fix **14 types** (covers 80% of scenarios and is manageable)

#### Proposal/Terms Category

- **OFFER**: Propose explicit solution (contains terms)
- **COUNTER**: Counter-offer/counter-proposal (contains terms)
- **CONCEDE**: Concession (terms change direction favors the other party)
- **ACCEPT**: Accept the other party's proposal (explicit agreement)
- **REJECT**: Explicit rejection (does not accept current proposal)

#### Information and Clarification Category

- **ASK**: Question/clarify (does not change terms)
- **DISCLOSE**: Reveal information/preferences/constraints ("Our budget is only...")
- **SUMMARIZE**: Summarize/confirm current consensus (prevent misunderstandings)

#### Strategy and Relationship Category

- **ANCHOR**: Anchoring (high/low starting point to influence range, usually contains price)
- **JUSTIFY**: Provide reasons/arguments (support for offer/counter)
- **REFRAME**: Reframe the problem (from adversarial to cooperative, change perspective)
- **BUILD_RAPPORT**: Build relationship/empathy/ease tension
- **THREATEN**: Threat/final ultimatum/hint at exit
- **PAUSE**: Pause/postpone/need time ("We'll discuss this back at the office")

> **Note**: ANCHOR and OFFER/COUNTER sometimes overlap. For control, you can allow one turn to extract multiple Events (e.g., ANCHOR first, then OFFER).

---

### 6. act_subtype (Action Subtype, Optional but Enumerable)

**Used in**: `Event.act_subtype`

- **For THREATEN**:
  - `WALK_AWAY`: Directly state intent to exit
  - `DEADLINE`: Final deadline/cannot wait
  - `ESCALATE`: Escalate to superior/legal/public

- **For CONCEDE**:
  - `SMALL_STEP`: Small concession
  - `MAJOR_STEP`: Major concession
  - `CONDITIONAL`: Conditional concession

- **For ASK**:
  - `CLARIFY_TERM`: Clarify terms
  - `PROBE_LIMIT`: Probe bottom line
  - `PROBE_PRIORITY`: Probe priorities

- **For REFRAME**:
  - `INTEREST_BASED`: Shift from positions to interests
  - `WIN_WIN`: Emphasize win-win
  - `SCOPE_SPLIT`: Split issues

---

### 7. term_type (Term Type)

**Used in**: `Term.term_type`, `State.terms`, `UtilityWeights`

Fix **12 types** initially, sufficient to cover business/ financing/ procurement/ cooperation

- **PRICE**: Price/amount
- **CURRENCY**: Currency (usually an attribute of term, can also be separate)
- **QUANTITY**: Quantity
- **SCOPE**: Scope/deliverable content (can be structured as text + tags)
- **TIMELINE**: Timeline/milestones (high-level framework)
- **DEADLINE**: Deadline (single date point)
- **PAYMENT_TERMS**: Payment terms (prepayment/credit period/installments)
- **DELIVERABLES**: Deliverable list (structured list)
- **QUALITY_SLA**: Quality/service level (SLA)
- **LIABILITY**: Liability/compensation/cap
- **EXCLUSIVITY**: Exclusivity/non-compete restrictions
- **TERMINATION**: Termination/exit clauses

---

### 8. term_value_type (Term Value Type)

**Used in**: `Term.value_type` (helps standardization)

- **NUMBER**: Numeric value (e.g., 120000)
- **MONEY**: Currency (value + currency)
- **PERCENT**: Percentage (e.g., 2.5%)
- **DATE**: Date (ISO)
- **DURATION**: Duration (e.g., P30D)
- **TEXT**: Text (e.g., scope description)
- **ENUM**: Enumeration (e.g., payment method)
- **LIST**: List (deliverables)

---

### 9. stance (Attitude/Openness Level)

**Used in**: `Event.stance`

- **FIRM**: Firm/unyielding
- **OPEN**: Open/discussable
- **CONDITIONAL**: Conditional
- **HESITANT**: Hesitant/uncertain
- **NONCOMMITTAL**: Vague/non-committal

---

### 10. intent (Intent: High-Level Enumerable)

**Used in**: `Event.intent`, `AgentAction.strategy_tags`

Fix **10 types** initially, sufficient

- **SET_BASELINE**: Set baseline (anchoring)
- **SEEK_CONCESSION**: Seek concession from the other party
- **TEST_LIMITS**: Test bottom line
- **SHARE_CONSTRAINT**: Explain constraints/limitations
- **BUILD_TRUST**: Build trust/relationship
- **REDUCE_TENSION**: De-escalate
- **GAIN_TIME**: Buy time
- **CLOSE_DEAL**: Push for closure
- **SHIFT_TOPIC**: Shift topic
- **ESCALATE_PRESSURE**: Escalate pressure

---

### 11. tone_style (Language Style/Tone)

**Used in**: `AgentAction.tone_style`, `Event.tone_style`

- **CALM**: Calm
- **ASSERTIVE**: Assertive
- **FRIENDLY**: Friendly
- **APOLOGETIC**: Apologetic/soft
- **AGGRESSIVE**: Aggressive/pressuring
- **SARCASTIC**: Sarcastic (optional, not used in many scenarios)
- **FORMAL**: Formal
- **CASUAL**: Casual
- **UNCERTAIN**: Uncertain/probing

---

## L2 State Machine Layer (Numerical State Dimension Enumerations)

### 12. emotion_dim (Emotion Dimensions: Recommended to Fix 4 Dimensions)

**Used in**: `State.emotion[participant_id]`

- **anger**: Anger/hostility
- **stress**: Pressure/tension
- **confidence**: Confidence/sense of control
- **warmth**: Friendliness/affinity

Recommended value range: **0.0 – 1.0**

---

### 13. relationship_dim (Relationship Dimensions: Recommended to Fix 3 Dimensions)

**Used in**: `State.relationship`

- **trust**: Trust level (0–1)
- **tension**: Adversarial/tension (0–1)
- **alignment**: Goal consistency/cooperation tendency (0–1)

---

### 14. belief_type (Belief/Estimate Type)

**Used in**: `State.beliefs[belief_key].type`

- **RANGE**: Range (min/max)
- **GAUSSIAN**: Normal distribution (mu/sigma)
- **CATEGORICAL**: Categorical distribution (probability table)

---

### 15. belief_key (You can fix a set of common belief keys initially)

**Used in**: `State.beliefs`

- `opponent_min_price`: Opponent's minimum acceptable price (from buyer's perspective, this is maximum acceptable price)
- `opponent_max_price`
- `opponent_urgency`: Opponent's urgency
- `opponent_risk_aversion`: Opponent's risk aversion
- `opponent_priority_PRICE`
- `opponent_priority_TIME`
- `opponent_priority_RELATIONSHIP`

---

## L3 Persona/Profile Layer (Enumerable Parameter Keys)

### 16. trait_key (Personality/Behavior Trait Keys)

**Used in**: `AgentProfile.traits`

- **dominance**: Dominance/assertiveness
- **agreeableness**: Agreeableness/cooperation
- **risk_aversion**: Risk aversion
- **patience**: Patience/willingness to delay
- **emotional_reactivity**: Emotional reactivity intensity (tendency to escalate)

---

### 17. trigger_condition_type (Trigger Condition Type)

**Used in**: `TriggerRule.condition.type`

- **INTERRUPT_COUNT_GTE**: Interruption count ≥ N
- **NEGATIVE_TONE_GTE**: Opponent's negative tone ≥ threshold
- **TENSION_GTE**: Relationship tension ≥ threshold
- **CONCESSION_FROM_OPPONENT**: Opponent concession occurs
- **TIME_PRESSURE_GTE**: Time pressure ≥ threshold
- **TERM_MOVED_AGAINST_ME**: Terms moved in unfavorable direction

---

### 18. trigger_effect_type

**Used in**: `TriggerRule.effect`

- **EMOTION_DELTA**: Emotion delta (change anger/stress...)
- **TACTIC_PRIOR_SHIFT**: Tactic prior shift (more likely to threaten/more likely to concede)
- **TONE_STYLE_OVERRIDE**: Force tone (e.g., become aggressive)

---

## L4 Agent Decision Layer (Enumerable Strategy Tags)

### 19. strategy_tag (Decision Explanation/Teaching Tags)

**Used in**: `AgentAction.strategy_tags`

- **SIGNAL_LIMIT**: Signal bottom line
- **PROBE_LIMIT**: Probe bottom line
- **TRADE_OFF**: Trade-off (you give me X, I give you Y)
- **SPLIT_THE_DIFFERENCE**: Split the difference
- **PACKAGE_DEAL**: Package issues
- **SLOW_CONCEDE**: Slow concession pace
- **FAST_CLOSE**: Fast closure
- **APPEAL_AUTHORITY**: Appeal to authority/rules/policy
- **USE_DEADLINE**: Use deadline pressure
- **DE_ESCALATE**: De-escalate

---

## L5 Branch Intervention Layer (Intervention Types)

### 20. intervention_type

**Used in**: `Intervention.type`

- **REPLACE_ACT**: Replace an action (THREATEN→REFRAME)
- **EDIT_TERMS**: Modify terms (change price to a value)
- **CLAMP_EMOTION**: Clamp emotion (anger=0)
- **ADD_TRIGGER**: Add trigger (simulate a stimulus)
- **REMOVE_EVENT**: Remove an event (assume that statement wasn't made)
- **INFO_HIDE**: Information hiding (a participant cannot see a belief/fact)
- **POLICY_SHIFT**: Temporarily change profile parameters (dominance↓)

---

## L6 Evaluation Layer (Metric Enumerations + Rubric Dimensions)

### 21. metric_key (Rule Metric Keys)

**Used in**: `OutcomeMetrics`

- **agreement_reached**: Whether agreement was reached
- **utility_self**: Self utility
- **utility_other**: Other party utility
- **utility_avg**: Average utility
- **fairness_gap**: Utility gap (smaller is fairer)
- **relationship_damage**: Relationship damage
- **volatility**: Volatility/conflict intensity
- **efficiency_rounds**: Number of rounds
- **time_to_agreement_sec**: Time to reach agreement
- **concession_count**: Number of concessions

---

### 22. rubric_dim (LLM Soft Scoring Dimensions)

**Used in**: `RubricScores.scores`

- **clarity**: Clarity
- **empathy**: Empathy
- **leverage**: Leverage/strategic value
- **coherence**: Consistency/no self-contradiction
- **professionalism**: Professionalism
- **creativity**: Creative solutions (optional)

---

### 23. highlight_type

**Used in**: `RubricScores.highlights[].type`

- **GOOD_MOVE**: Good move
- **MISSED_OPPORTUNITY**: Missed opportunity
- **RISK**: Risk point
- **ESCALATION**: Escalation point
- **DE_ESCALATION**: De-escalation point

---

## Additional: Global Common Enumerations (Strongly Recommended to Fix)

### 24. confidence_level

**Used in**: Various confidence buckets (for UI/filtering)

- **LOW**: <0.4
- **MEDIUM**: 0.4–0.7
- **HIGH**: >0.7

---

### 25. status (Pipeline Task Status)

**Used in**: Job state for all steps

- **PENDING**
- **RUNNING**
- **SUCCEEDED**
- **FAILED**
- **NEEDS_REVIEW** (requires manual correction, e.g., diarization)

---

## Minimum Set Recommendation

The minimum set you can immediately "fix and write into schema" (strongly recommended)

If you only want to fix the most critical **6 enumerations** to lock the system:

1. **act_type**
2. **term_type**
3. **tone_style**
4. **emotion_dim**
5. **intervention_type**
6. **rubric_dim**

---
