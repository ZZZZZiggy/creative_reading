# Workflow E: Interactive Live Case (Education / HBP)

This document describes how **Education / HBP** setup, student interaction, professor intervention, and assessment feed into the [Core Engine](core-egnine.md). Step-level iteration and **external intervention** (override this step’s Action) are covered in [engine/core-engine.md](../engine/core-engine.md) §1 and §5.1. It is aimed at product and teaching stakeholders; L0–L6 data structure definitions are out of scope.

---

## 1. Scenario Definition

| Item | Description |
|------|-------------|
| **Target users** | Business schools (HBS, Wharton), corporate L&D, online platforms (EdX), etc. |
| **Core value** | Shift from “reading cases” to “playing cases”; immersive, gradable negotiation practice |
| **Keywords** | Pedagogy, Control, Grading, Gamification |

---

## 2. Data Flow and Engine Integration

### 2.1 Phase 1: Teaching Setup

**Input**: The instructor **does not** upload audio. Instead, they select a **Standard Case Template** (e.g. “Elon Musk vs Twitter Board (HBS Case #123)”) and set difficulty (e.g. Hard / Aggressive Bot).

**Process**: **Bypass L0–L3**. Load predefined **Profiles** and **Initial State** directly; no ASR, persona fitting, or event extraction.

**Purpose**: Ensure **consistency** (same AI opponent and initial situation for every student on the same case) and **low latency** for real-time classroom interaction.

### 2.2 Phase 2: Student Interaction and Intervention

**Roles**: The student plays one side (e.g. Twitter Board); the **Core Engine** plays the other (e.g. Musk). The simulation loop matches [engine](../engine/core-engine.md), but **step-level iteration** **pauses** at some steps for human input or interventions.

**Source of this step’s Action**:

| Turn | Action source | Notes |
|------|---------------|-------|
| **Student** | Student input | Natural language or discrete action choice; parsed and used as **injected Action**, overriding F_Deliberate for this step |
| **Engine (AI opponent)** | F_Deliberate | Engine decides from State, Profile, Action Space |
| **Professor** | Professor intervention | E.g. “Inject Shock”: market crash, valuation drop, etc. Override this step’s Action or force state update so the student must respond under pressure |

**Engine integration**: Student moves and professor Inject Shock both plug in via the engine’s **override this step’s Action** mechanism. The engine runs F_Transition to get `State_{k+1}` and continues step-level iteration.

### 2.3 Phase 3: Assessment and Feedback

**Process**: **L6 Rubric Scoring**. Outcomes are not only deal vs breakdown; **process quality** (e.g. empathy, logic, agility) is evaluated and compared to the Core Engine’s **optimal path**.

**Output**: **Student Report Card**. Includes overall score, dimension scores (e.g. Empathy, Logic, Agility), and **highlighted feedback** from the Trace (e.g. “At round 5, under market crash, you chose to freeze the deal—a textbook defensive move”). Field-level detail is kept conceptual.

---

## 3. Education Properties

| Property | Description |
|----------|-------------|
| **Low latency** | No L0/L1 audio processing; near real-time classroom interaction |
| **Standardization** | Same AI difficulty per case; **fair** grading |
| **Leaderboard** | Class live rankings to boost competition and engagement |
