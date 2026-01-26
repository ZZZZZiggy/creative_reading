# AgentArena Core Engine 接口规格（黑箱）

本文定义 Core Engine 对外的 **API 表面**：输入、核函数与输出的约定。黑箱**内部**的业务逻辑与设计取舍见 [engine/core-engine.md](../engine/core-engine.md)。面向产品、引擎与应用侧的设计讨论；具体序列化格式（如 JSON Schema）不在本文展开，仅给出概念级定义。

---

## 1. 引擎定义

Core Engine 是一个 **确定性的、基于状态的异步多智能体博弈机**（Deterministic State-based Async Multi-Agent Game Engine）。

**职责边界**：接收状态、执行动作、计算后果。**不**关心数据来源（录音、教授手动输入或教学配置），**不**关心输出用途（风控报告、学生打分或战略推演）。

---

## 2. 输入 (Inputs)

引擎接受单次调用所需的 **Context**，包括以下三类输入。

### 2.1 Current State（当前状态）

| 项目 | 说明 |
|------|------|
| **含义** | 第 k 步的局势快照，即单步流程中的 `State_k` |
| **典型维度** | 条款类（如 `price`、`prob`、`risk`）、过程类（如 `step`）、关系/情绪类等；与 [engine](../engine/core-engine.md) 转移层约定一致 |
| **来源** | L2 状态轨迹、教学案例初始配置，或上一轮仿真的 `State_{k+1}` |

不在此枚举完整字段；具体形状由调用方与引擎实现约定。

### 2.2 Agent Profiles（智能体参数）

| 项目 | 说明 |
|------|------|
| **含义** | 各参与方的人格与策略参数，用于 F_Deliberate 的决策 |
| **典型维度** | 如 `buyer_aggressiveness`、`board_risk_aversion` 等；可含效用权重、动作先验等 |
| **来源** | L3 拟合或预设模版 |

### 2.3 Action Space（动作空间）

| 项目 | 说明 |
|------|------|
| **含义** | 当前步允许的动作集合，约束 F_Deliberate 的输出 |
| **示例** | `ACCEPT`、`REJECT`、`EARNOUT`、`THREATEN` 等 |
| **可变性** | 可随轮次或状态由调用方或转移规则动态收缩/扩展 |

---

## 3. 核函数 (Kernel Functions)

| 函数 | 签名 | 职责 |
|------|------|------|
| **F_Deliberate** | `(State, Profile) -> Action` | 决策层。调用 LLM，基于当前状态与 Agent 人格，在 Action Space 内选出最优动作；不修改状态 |
| **F_Transition** | `(State, Action) -> Next_State` | 转移层。对 `(State, Action)` 执行**确定性**因果逻辑，得到下一状态；为系统「物理定律」，不可由 LLM 改写 |
| **F_Attribution** | `(State, Next_State) -> Delta_Explanation` | 归因层。计算两状态间的差值，并生成自然语言解释 |

单步闭环见 [engine/core-engine.md §1.1](../engine/core-engine.md)；一轮仿真为**步级迭代**，反复执行上述单步直至终止。

---

## 4. 输出 (Outputs)

| 输出 | 含义 |
|------|------|
| **Simulation Trace** | 完整决策链 `[State_0, Action_0, State_1, Action_1, ...]`，用于回放、分支推演（L5）、评估（L6）等 |
| **Outcome** | 是否成交或破裂、破裂原因（若适用），及若干关键指标（如轮次、最终条款维度等） |

---

## 5. 约束与扩展

- **无状态性**：引擎不保持跨调用状态；每次调用依赖本次传入的 Context（State、Profile、Action Space、可选历史摘要）。
- **可插拔 LLM**：F_Deliberate 与 F_Attribution 所用模型可配置（如 Llama-3 / GPT-4），以权衡延迟、成本与表现。
- **外部干预**：支持**覆盖本步 Action**（如学生出招、教授 Inject Shock、战略家设定反事实策略）；若本轮提供外部 Action，则跳过 F_Deliberate，详见 [engine §5.1](../engine/core-engine.md)。
