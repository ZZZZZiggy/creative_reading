# Workflow B: Digital Twin and Strategic War-Gaming (Business / Consulting)

This document describes how **Business / Consulting** digitization, counterfactual simulation, and decision intelligence integrate with the [Core Engine](core-egnine.md). **Step-level** and **run-level** iteration (Monte Carlo) and **external intervention** are covered in [engine/core-engine.md](../engine/core-engine.md) §1, §5.1, and §5.2. It is aimed at product and business stakeholders; L0–L6 data structures and concrete Schema are out of scope.

---

## 1. Scenario Definition

| Item | Description |
|------|-------------|
| **Target users** | Investment banks, law firms, corporate strategy, behavioral-research orgs, etc. |
| **Core value** | “Replay and rehearse”: turn past negotiations into data, future decisions into repeatable experiments |
| **Keywords** | High Fidelity, Cloning, Counterfactuals, Deep Sensing |

---

## 2. Data Flow and Engine Integration

### 2.1 Phase 1: Digitization

**Standard input**: Real negotiation **audio** or **transcripts**.

**Process (L0–L1)**: ASR, speaker diarization; extract **key facts** (e.g. initial offer, main concerns) from text or event stream for state init and persona fitting.

#### Branch: Deep-Sensing (Research / Pro)

| Item | Description |
|------|-------------|
| **Role** | **Research approximation tool** for high-end consulting / psychology |
| **Input** | Physiological signals (EEG / EDA / HRV) or facial micro-expressions via Riff / cameras / wearables |
| **Process** | **Signal alignment**: align physiological peaks (e.g. stress) with negotiation timeline (ms). **Hidden-state extraction**: find “say–do mismatch” moments (e.g. verbal agreement but HRV shows resistance) to supply **subconscious parameters** for persona fitting |

#### L3 Persona Fitting

**Input**: Historical data—**text only** (transcript + events) or **text + sensing**.

**Process**: Infer counterparty **persona and strategy parameters** (e.g. impulsiveness, stress threshold, deception tendency). Text-only yields behavioral params; adding sensing allows richer psychological estimates.

**Output**: **AI Clone** (Profile + optional subconscious params) that closely approximates the real counterparty, used as Core Engine Agent Profile for high-fidelity counterfactual runs.

### 2.2 Phase 2: Core Engine Invocation

**User setup**: Counterfactual strategy or intervention, e.g. “What if we had held at 50 instead of accepting 54.20?”

**Engine call**: Pass **Profiles** (e.g. Fitted_Musk_Clone_Advanced), **Initial State** (Real_World_State_T0), **User Intervention** (e.g. Offer_50); optionally **Simulation Mode** (e.g. DEEP_PSYCH for psych-dynamics rules or params).

**Execution**: Engine performs **run-level iteration** (e.g. 100-run Monte Carlo). Each run starts from initial state + user intervention, completes full step-level iteration until termination; Trace and Outcome are aggregated across runs to produce breakdown probability, counterparty irrational breakdown points, etc. Multi-run may be engine-built-in or orchestrator calling the engine repeatedly. See [engine §5.2](../engine/core-engine.md).

### 2.3 Phase 3: Decision Intelligence

**Output (L6)**: **Risk & Opportunity Report**.

| Type | Description |
|------|-------------|
| **Standard** | Aggregate over runs, e.g. “In 100 runs, holding at 50 led to breakdown in 65% of cases.” |
| **Sensing-enhanced** (Research branch) | Use physiological / micro-expression signals to identify cognitive load, weak moments on specific issues, and suggest tactics (e.g. introduce complex terms at that moment) |

---

## 3. Business Properties

| Property | Description |
|----------|-------------|
| **Tiered service** | **Standard**: Audio only, for most deal debriefs. **Research / Pro**: With sensing, “lie-detector–grade” psychological game analysis |
| **Data privacy** | On-prem deployment; biometric and physiological data encrypted, never leave site |
| **Domain templates** | **CausalTransition** parameter sets customized for M&A, labor disputes, etc., aligned with [engine](../engine/core-engine.md) transition-layer domain params |
