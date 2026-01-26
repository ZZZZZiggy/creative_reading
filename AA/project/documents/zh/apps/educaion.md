# Workflow E：互动式现场案例（教育 / HBP）

本文描述 **教育 / HBP** 场景下，教学配置、学生互动、教授干预与评估反馈如何与 [Core Engine](core-egnine.md) 衔接。引擎内部步级迭代与**外部干预**（覆盖本步 Action）机制见 [engine/core-engine.md](../engine/core-engine.md) §1、§5.1。面向产品与教学侧设计讨论；不展开 L0–L6 的数据结构定义。

---

## 1. 场景定义

| 项目 | 说明 |
|------|------|
| **目标客户** | 商学院（HBS、Wharton）、企业内训（L&D）、在线教育平台（EdX）等 |
| **核心价值** | 从「读案例」变为「演案例」；沉浸式、可评分的谈判练习 |
| **关键词** | Pedagogy, Control, Grading, Gamification |

---

## 2. 数据流与引擎衔接

### 2.1 Phase 1：教学配置（Setup）

**输入**：教授**不**上传录音，而是选择 **标准案例模版**（Standard Case Template），如「Elon Musk vs Twitter Board (HBS Case #123)」，并设定难度（如 Hard / Aggressive Bot）。

**过程**：**绕过 L0–L3**。直接加载预设的 **Profiles** 与 **Initial State**，不做 ASR、人格拟合或事件抽取。

**目的**：保证教学**一致性**（同一案例下每位学生面对相同 AI 对手与初始局势），并**降低延迟**，满足课堂实时互动。

### 2.2 Phase 2：学生互动与干预（Interaction & Intervention）

**角色分工**：学生扮演一方（如 Twitter Board），**Core Engine** 扮演另一方（如 Musk）。仿真循环与 [engine](../engine/core-engine.md) 相同，但**步级迭代**在部分步骤**暂停**，等待人力输入或接受干预。

**本步 Action 的来源**：

| 轮到方 | Action 来源 | 说明 |
|--------|-------------|------|
| **学生** | 学生输入 | 自然语言或离散动作选择；经解析后作为 **外部注入的 Action**，覆盖本步 F_Deliberate |
| **引擎（AI 对手）** | F_Deliberate | 由引擎按 State、Profile、Action Space 决策 |
| **教授** | 教授干预 | 如「Inject Shock」：注入市场崩盘、估值骤降等；通过 **覆盖本步 Action** 或强制更新状态，迫使学生在压力下反应 |

**与引擎的衔接**：学生动作、教授 Inject Shock 均通过引擎的 **覆盖本步 Action** 机制接入；引擎据此执行 F_Transition，得到 `State_{k+1}`，再继续步级迭代。

### 2.3 Phase 3：评估与反馈（Assessment）

**过程**：采用 **L6 Rubric Scoring（量表评分）**。不只按成交/破裂论输赢，而是评估**过程质量**（如共情、逻辑、应变），并与 Core Engine 的**最优解路径**对比。

**输出**：**Student Report Card**。包括综合分数、各维度得分（如 Empathy、Logic、Agility），以及基于 Trace 的**高亮点评**（如「第 5 轮面对市场崩盘时选择冻结交易，为教科书式防御」）。具体字段保持概念级，不在此展开。

---

## 3. 教育特性

| 特性 | 说明 |
|------|------|
| **低延迟** | 省略 L0/L1 音频处理，课堂互动近实时 |
| **标准化** | 同一案例下 AI 难度一致，确保评分**公平** |
| **Leaderboard** | 班级实时排名，增强竞争与参与感 |
