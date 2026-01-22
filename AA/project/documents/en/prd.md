# Product Requirements Document (PRD)

---

## 1. Product One-liner

An AI platform capable of **replaying real negotiations, simulating parallel decision branches, and modeling different personality-based negotiation behaviors** for learning, training, and researching complex negotiations and decision-making.

---

## 2. Background and Problem Statement

### Real-World Problems

- Real negotiations, meetings, and discussions **disappear once they end**
- People can only rely on:
  - Subjective recall
  - Scattered summaries
  - Empiricism

But cannot answer more critical questions:

- "What would have happened if I hadn't lost my temper?"
- "Would the outcome have been better with a different negotiation strategy?"
- "What is the other party's personality and reaction patterns?"

### Limitations of Existing Solutions

- **Meeting Recording → Transcription → Summary**
  - Can only review the past, cannot simulate the future
- **Business School Case Studies**
  - Static text, non-interactive, no counterfactual simulation
- **Role-play / Chatbot**
  - Not based on real data, cannot replay specific decision points

---

## 3. Product Vision

We want to transform **negotiations and discussions** from:

> "One-time, irreversible events that can only be reflected upon afterward"

into:

> **A replayable, simulatable, trainable, and comparable decision system**

Just like:

- **Chess** has replay and branch analysis
- **Stocks** have backtesting and scenario simulation

**Negotiations should have tools of the same caliber.**

---

## 4. Target Users

### Core Users (Phase 1)

1. **Learning Users**
   - MBA / Business school students
   - Law schools, public policy, international relations
   - Negotiation training, interview preparation

2. **Professional Users**
   - Consultants
   - Sales / Business development
   - Entrepreneurs / Managers

### Secondary Users (Phase 2)

- Corporate training / Coaches
- Academic researchers (negotiation, behavioral science, human-AI collaboration)
- Military / Public sector (high-risk decision drills)

---

## 5. Core Product Features

### Feature 1: Real Negotiation Replay

#### User Input

- A recording (or text) of a negotiation / meeting / discussion
- (Optional) Participant background information
- (Optional for research scenarios) Physiological / perception data

#### System Output

1. **Structured Negotiation Timeline**
   - Who did what action at what time
   - Which are proposals, concessions, threats, clarifications

2. **Key Decision Point Identification**
   - Which points significantly changed the direction

3. **Behavior and Strategy Analysis**
   - Negotiation style
   - Emotional changes
   - Strategy patterns

**Product Value**: Not "what you said," but "what you did in the negotiation structure."

---

### Feature 2: Counterfactual Branching

At key nodes of real negotiations, the system can:

- Change a decision (e.g., no threat, no anger, early concession)
- Fix or modify emotional states
- Replace negotiation strategies

And continue **simulating the future trajectory of multi-round negotiations**.

#### Users Can See

- Original path vs. alternative paths
- Which strategy:
  - Reaches agreement faster
  - Causes less relationship damage
  - Has higher long-term utility

**Product Value**: "What would have happened if I had done that?" The first systematic answer.

---

### Feature 3: Negotiation Simulator

Users can **create a negotiation from scratch**:

- Set number of participants
- Define personality and strategy for each participant (system prompt / parameters)
- Set issues and constraints (price, deadline, responsibilities, etc.)

#### The System Will

- Drive multi-agent negotiations
- Generate dialogue in real-time
- Record every decision step

#### Suitable For

- Personal practice
- Classroom teaching
- Team drills

---

### Feature 4: Evaluation and Coaching Feedback

Every negotiation (real or simulated) is evaluated for:

- Whether agreement was reached
- Whether utility distribution is fair
- Whether emotions and relationships are out of control
- Whether strategies are consistent, clear, and effective

#### And Provides

- Highlighted key good/bad decisions
- Transferable negotiation rules
- Behavior pattern summaries

---

## 6. Core User Journey

### Flow A: Replay Real Negotiation

1. Upload recording
2. System automatically parses
3. User views negotiation timeline
4. System marks key nodes
5. User selects a node for "what if I hadn't done this"
6. Compare different future outcomes
7. View summary and recommendations

### Flow B: Simulated Negotiation Training

1. Create negotiation scenario
2. Define roles and personalities
3. Start negotiation
4. Conduct multiple rounds of interaction
5. View scores and feedback
6. Re-run or adjust strategy

---

## 7. Out of Scope for V1

Clearly define **what we are not doing now**:

- Real-time negotiation assistance (live coaching)
- Automatically "negotiate on behalf of" users
- Legal advice / decision recommendations (analysis and simulation only)
- Enforcing "best strategy" (emphasize comparison, not a single answer)

---

## 8. Success Metrics

### Product Metrics

- Percentage of users completing a full replay/simulation
- Frequency of user "branch simulation" usage
- Number of times the same negotiation is re-simulated

### Experience Metrics

- Whether users can clearly state: "What I did wrong/right at step X"
- Whether users are willing to put the negotiation into the system a second time

---

## 9. Risks and Constraints

- **Simulation ≠ Prediction of Reality** (must be clearly stated)
- **Model Bias** (personality fitting is not "fact," it's an approximation)
- **Privacy and Compliance** (recording data is sensitive)

---

## 10. MVP Positioning (No Technical Implementation)

### V1's Essential Goal:

**Prove that "negotiations can be structured, simulated, and learned"**

Not:

- How strong the model is
- How realistic the simulation is

---

## 11. Core Product Differentiators (Why This Wins)

| Dimension | Existing Tools | This Product |
|-----------|---------------|-------------|
| Review | Yes | Yes |
| Structuring | Weak | **Strong** |
| Counterfactual | No | **Yes** |
| Multi-Agent | No | **Yes** |
| Coaching Feedback | Subjective | **Systematic** |
| Repeatable Training | No | **Yes** |
