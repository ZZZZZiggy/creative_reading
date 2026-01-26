# AgentArena Core Engine API Specification (Black Box)

This document defines the Core Engine’s **API surface**: conventions for inputs, kernel functions, and outputs. For **internals**—business logic and design trade-offs inside the black box—see [engine/core-engine.md](../engine/core-engine.md). It is aimed at product, engine, and application stakeholders. Concrete serialization (e.g. JSON Schema) is out of scope; only conceptual definitions are given.

---

## 1. Engine Definition

The Core Engine is a **Deterministic State-based Async Multi-Agent Game Engine**.

**Scope**: Consume state, execute actions, compute consequences. It **does not** care about data provenance (recordings, instructor input, or teaching config), nor about how outputs are used (risk reports, student grading, or strategy simulation).

---

## 2. Inputs

The engine accepts the **Context** required for a single invocation, consisting of three input categories.

### 2.1 Current State

| Item | Description |
|------|-------------|
| **Meaning** | Situation snapshot at step k, i.e. `State_k` in the single-step flow |
| **Typical dimensions** | Term-like (e.g. `price`, `prob`, `risk`), process (e.g. `step`), relationship/emotion; aligned with [engine](../engine/core-engine.md) transition-layer conventions |
| **Source** | L2 state trajectory, teaching-case initial config, or `State_{k+1}` from the previous simulation step |

Full field enumeration is not given here; concrete shape is agreed between caller and engine implementation.

### 2.2 Agent Profiles

| Item | Description |
|------|-------------|
| **Meaning** | Persona and strategy parameters per participant, used by F_Deliberate for decisions |
| **Typical dimensions** | E.g. `buyer_aggressiveness`, `board_risk_aversion`; may include utility weights, action priors, etc. |
| **Source** | L3 fitting or preset templates |

### 2.3 Action Space

| Item | Description |
|------|-------------|
| **Meaning** | The set of actions allowed at the current step; constrains F_Deliberate output |
| **Examples** | `ACCEPT`, `REJECT`, `EARNOUT`, `THREATEN`, etc. |
| **Mutability** | May be narrowed or expanded per round or state by caller or transition rules |

---

## 3. Kernel Functions

| Function | Signature | Responsibility |
|----------|-----------|----------------|
| **F_Deliberate** | `(State, Profile) -> Action` | Decision layer. Calls LLM; selects best action within Action Space from current state and Agent persona. Does not modify state |
| **F_Transition** | `(State, Action) -> Next_State` | Transition layer. Applies **deterministic** causal logic to `(State, Action)` to obtain next state. System “physics”; not overridable by LLM |
| **F_Attribution** | `(State, Next_State) -> Delta_Explanation` | Attribution layer. Computes difference between the two states and produces a natural-language explanation |

See [engine/core-engine.md §1.1](../engine/core-engine.md) for the single-step loop. One simulation run is **step-level iteration**: repeatedly executing this step until termination.

---

## 4. Outputs

| Output | Meaning |
|--------|---------|
| **Simulation Trace** | Full decision chain `[State_0, Action_0, State_1, Action_1, ...]`, used for replay, branch rollout (L5), evaluation (L6), etc. |
| **Outcome** | Deal vs breakdown, breakdown cause (if any), and key metrics (e.g. rounds, final term dimensions) |

---

## 5. Constraints and Extensions

- **Statelessness**: The engine keeps no state across calls; each call depends only on Context passed in (State, Profile, Action Space, optional history summary).
- **Pluggable LLM**: Models used by F_Deliberate and F_Attribution are configurable (e.g. Llama-3 / GPT-4) to trade off latency, cost, and quality.
- **External intervention**: Supports **overriding this step’s Action** (e.g. student move, professor Inject Shock, strategist counterfactual). If an external Action is supplied for this step, F_Deliberate is skipped. See [engine §5.1](../engine/core-engine.md).
