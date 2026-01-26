# Core Engine Black-Box Internals (Design Discussion)

This document describes the **business logic inside** the Core Engine black box and key design choices. It complements the API definition in [apps/core-egnine.md](../apps/core-egnine.md): that document specifies inputs, kernel functions, and outputs; this one explains what the engine does behind those interfaces and what design trade-offs are open for discussion. It is aimed at product, engine, and application stakeholders and **does not** cover concrete data structures or implementation detail.

---

## 1. Simulation Loop (Single-Step and Multi-Step)

### 1.1 Single-Step Flow

The engine’s core loop is **Deliberate → Transition → Attribution**:

```
State_k → F_Deliberate → Action_k → F_Transition → State_{k+1} → F_Attribution → Delta_k
```

**Variable definitions**:

| Symbol | Meaning |
|--------|---------|
| **State_k** | Current state at step k (situation snapshot), including deal terms, relationship/emotion dimensions, etc.; k = 0 is the initial state |
| **Action_k** | The action chosen at this step (e.g. ACCEPT, REJECT, EARNOUT, THREATEN), produced by F_Deliberate or **injected via external intervention** |
| **State_{k+1}** | Next state after applying Action_k, computed **deterministically** by F_Transition |
| **Delta_k** | Summary of state change at this step plus a natural-language explanation, produced by F_Attribution, describing what changed from State_k to State_{k+1} |

**Kernel functions**:

- **F_Deliberate**: Given current state and Agent persona, chooses one action from the allowed action space. Does not modify state.
- **F_Transition**: Given current state and chosen action, **deterministically** produces the next state (the system’s “physics”).
- **F_Attribution**: Compares previous and next state, identifies what changed, and produces a natural-language explanation.

A **single simulation run** repeatedly executes this step until a **termination condition** is met. **Utterance** (turning an action into natural language) is an application-layer extension; the black box works only with state and action and is not discussed further here.

### 1.2 Termination Conditions

Typical termination cases:

- **Deal**: One party takes an ACCEPT-like action; agreement is reached.
- **Breakdown**: Max rounds exceeded, REJECT triggers a threshold, or relationship/risk dimensions cross critical values.

Which actions or state combinations cause deal vs breakdown is defined by the **transition layer**’s causal rules and domain parameters. Termination logic must be explicit at design time so that Trace and Outcome stay consistent.

### 1.3 Trace and Outcome

- **Simulation Trace**: The full decision chain, i.e. the sequence `[State_0, Action_0, State_1, Action_1, ...]`. Used for replay, branch rollout (L5), evaluation (L6), etc.
- **Outcome**: Whether a deal was reached or breakdown occurred, breakdown cause (if any), and key metrics (e.g. rounds, final term dimensions). Kept conceptual; no field-level schema here.

---

## 2. Decision Layer (F_Deliberate)

### 2.1 Responsibility

Given **State**, **Profile**, and **Action Space**, select the next **Action** for the current Agent at this step. Purely decision-making; does not modify state.

### 2.2 How Inputs Affect Decisions

- **State**: The current situation (e.g. price, probability, risk, round) shapes which actions are reasonable and preferred. E.g. when price is near the other party’s limit, ACCEPT becomes more attractive.
- **Profile**: Persona parameters (e.g. aggressiveness, risk aversion, weights on relationship vs terms) influence action choice. Profiles come from **L3 fitting** or **preset templates**; L3 is not elaborated here.
- **Action Space**: The set of actions allowed at this step (e.g. `ACCEPT`, `REJECT`, `EARNOUT`, `THREATEN`). May be narrowed or expanded per round or state by the caller or transition rules.

### 2.3 LLM Role and Design Points

The decision layer **calls an LLM** to choose actions. Design questions include:

- **Prompt structure**: How to encode State, Profile, and Action Space; whether to use few-shot or rule constraints.
- **Context compression**: Whether to use **LastK**-style compression of history (e.g. recent State–Action summaries) to balance token limits and decision quality.
- **Temperature and sampling**: Deterministic runs vs moderate randomness (e.g. Monte Carlo multi-run); how to set temperature, top-p, etc.
- **Optional strategy/tone outputs**: Whether to also output `strategy_tags`, `tone_style`, etc. for L6 evaluation or teaching scenarios.

---

## 3. Transition Layer (F_Transition)

### 3.1 Responsibility

**Deterministically** map `(State, Action)` to `Next_State`. This is the system’s “physics”: same inputs always yield same output, **cannot** be overridden by the LLM, ensuring reproducible and explainable runs.

### 3.2 Causal Rules (Concept and Examples)

Transition rules define “how each state dimension changes after action A.” Examples (illustrative, not exhaustive):

- **EARNOUT**: Price decreases, deal probability increases; may have step size, bounds, etc.
- **THREATEN**: Relationship tension rises, counterparty risk perception increases; may raise breakdown probability.
- **ACCEPT**: Enters deal terminal state; **REJECT** may cause immediate breakdown or raise tension, depending on rules.

Design must specify which dimensions each action type affects, direction and magnitude, and any coupling (e.g. higher tension making the other side less willing to concede).

### 3.3 State Dimensions and Termination

State includes at least **term-like** dimensions (e.g. price, probability, risk, step) and **relationship/emotion** dimensions (e.g. tension, trust), aligned with [apps](../apps/core-egnine.md) `price`, `prob`, `risk`, `step`, etc. No field-level enumeration here.

**Termination** is part of the transition rules: certain Actions (e.g. ACCEPT) or State combinations (e.g. max rounds, tension above threshold) trigger **deal** or **breakdown**. This must be agreed at design time so Trace and Outcome align.

### 3.4 Domain Parameters

Different domains (M&A, labor disputes, teaching cases, etc.) may use different **CausalTransition** parameter sets: the same action can have different magnitude or thresholds per domain. The engine supports **configurable** rule sets; concrete table layouts are out of scope.

---

## 4. Attribution Layer (F_Attribution)

### 4.1 Responsibility

Compare **State** and **Next_State**, produce “what changed” and a **natural-language explanation**. Serves explainability, debrief reports, and teaching feedback.

### 4.2 Delta and Explanation

- **Delta**: Which dimensions changed, direction and approximate magnitude (conceptually analogous to pipeline StateDelta). No patch-level detail; kept conceptual.
- **Explanation generation**: **Rule templates** (e.g. “price −5%, tension +0.1”) or **LLM-generated** text (more natural, different controllability and cost). Design should trade off readability, stability, cost, and i18n.

---

## 5. Extensions and Design Discussion

### 5.1 External Intervention

Instructors, strategists, etc. may **inject actions** (e.g. “hold at 50,” “Inject Shock”) that override F_Deliberate’s output for a step. The engine must support **“override this step’s Action”**:

- **Interface**: Whether this step accepts an externally supplied Action; if provided, skip F_Deliberate.
- **Timing**: When in the step the override is applied; whether it affects subsequent Action Space or transition rules.

Concrete protocols can be refined at the API and orchestration layer.

### 5.2 Multi-Run and Monte Carlo

Use cases like “run 100 times” require **Monte Carlo**-style multi-run. Open questions:

- **Engine-built** multi-run (e.g. `run_n_simulations(n, ...)`) vs **orchestrator** calling the engine once per run.
- If built-in: how to inject initial state / randomness (e.g. Profile sampling, action tie-break); how to aggregate Trace and Outcome (e.g. breakdown rate, expected utility).

### 5.3 Stateless and Pluggable LLM

- **Stateless**: The engine holds no state across calls; each call depends only on Context passed in (State, Profile, Action Space, optional history summary).
- **Pluggable LLM**: Both decision and attribution can use configurable models (e.g. Llama-3 vs GPT-4). Design should consider impact on **latency**, **cost**, and **quality**, and whether to fix the model for certain scenarios.

---

## 6. Upstream and Downstream (Conceptual)

### 6.1 Upstream

**State**, **Profile**, and **Action Space** come from:

- **L0–L3 pipeline**: Audio → transcription → events → state trajectory → persona fitting; the engine consumes its outputs and does not care about L0–L1 audio/transcript detail.
- **Teaching / strategy config**: Preset case templates, initial state, and Profiles, loaded and passed into the engine.

Only conceptual linkage; pipeline layers are not elaborated.

### 6.2 Downstream

**Trace** and **Outcome** are consumed by:

- **L5 branch rollout**: Inject interventions at some state, continue simulation to obtain branch paths; engine provides single- or multi-run simulation.
- **L6 evaluation and reporting**: Metrics, rubric scoring, debrief generation, etc., all use Trace and Outcome.

Again conceptual; no L5/L6 data structure definitions here.
