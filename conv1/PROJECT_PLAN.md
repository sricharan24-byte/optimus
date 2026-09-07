# Project Plan: Semantic Constraint-Based Detection of Data Integrity Attacks in Distributed IoT-Enabled Operational Systems

## 1. Project Overview & Research Identity
* **Working Title:** Semantic Constraint-Based Detection of Data Integrity Attacks in Distributed IoT-Enabled Operational Systems
* **Target Publication:** IEEE Conference Paper (Information Security Track)
* **Core Domain:** **Information Security** (Data Integrity Attack Detection)
* **Case Study Testbed:** **Post-Harvest Cold-Storage Operations** (Selected solely as an operational testbed; no logistics/routing/spoilage optimization components).
* **Guiding Development Methodology:** Reproducible, modular, evidence-based research prototype adhering to the "Lazy Senior Developer" principle: minimum necessary code, zero speculative abstractions, strict execution-grounded results, and full auditability.

---

## 2. Research Problem & Core Questions

### 2.1 The Core Problem
Modern industrial and operational systems ingest heterogeneous data streams:
1. Physical IoT telemetry (e.g., thermal, humidity, occupancy sensors).
2. Operational and business records (e.g., reported available capacity, facility status).
3. Inventory transaction ledgers (e.g., inbound batches, dispatch logs, current balance).
4. Historical operational baselines (e.g., seasonal operating ranges, historical utilization).

Traditional security mechanisms (point-in-time anomaly detection, statistical thresholding) look for outliers in single data streams. An attacker can craft **plausible-looking data integrity attacks**: values that are syntactically valid, within normal operating ranges, and plausible in isolation, but that break the **semantic, physical, operational, and historical invariants** that connect multiple sources.

Furthermore, an attacker conducting a coordinated attack may inject **multiple weak, low-severity discrepancies** across related entities and time. Individually, these do not cross single-point alarm thresholds, but collectively they undermine system state.

### 2.2 Central Research Question
> **Can semantic relationships between heterogeneous business/operational records, physical IoT telemetry, and historical operating behaviour improve the detection of plausible-looking data-integrity attacks, and can temporal and structural correlation of weak semantic violations identify coordinated attacks more reliably than individual anomaly detection?**

### 2.3 Supporting Research Questions
* **RQ1:** Can semantic constraints detect plausible operational-record manipulations that do not register as anomalies at the individual-value level?
* **RQ2:** Does semantic constraint verification reduce false negatives compared to individual sensor/record anomaly detection?
* **RQ3:** Does joint temporal and structural escalation improve the detection rate and time-to-escalation for coordinated attacks composed of weak violations?
* **RQ4:** What is the trade-off between detection sensitivity and false-positive rate across varying constraint tolerances and escalation thresholds?

---

## 3. Threat Model & Boundaries

### 3.1 Attacker Capabilities
* **Access Vector:** Attacker can compromise one or more data ingestion points (e.g., IoT edge gateway, operational database API, or inventory management system).
* **Manipulation Profile:** Attacker manipulates numerical values (e.g., reported free capacity, batch dispatch weight, or occupancy reading) while intentionally choosing values that lie within nominal operating envelopes.
* **Coordination Capacity:** Attacker may manipulate multiple related sources sequentially or concurrently with low-magnitude deviations to evade threshold alerts.

### 3.2 Attacker Objectives
* Subtly corrupt operational awareness (e.g., trigger phantom capacity allocation, conceal unauthorized inventory withdrawal, or induce inappropriate physical handling) without triggering traditional statistical alerts.

### 3.3 Trusted Computing Base (TCB)
* The Security Monitoring Engine (the verification runtime).
* The Semantic Constraint Definitions (immutable security policy).
* Reference Historical Baselines (cryptographically or administratively protected profiles).

### 3.4 Out of Scope
* Physical hardware sabotage or destruction.
* Cryptographic key extraction / TLS session hijacking.
* Denial-of-Service (DoS/DDoS) flooding against ingestion endpoints.
* Attacks that achieve simultaneous total compromise of all physical sensors, databases, and the security engine itself (collusion boundary).

### 3.5 Security Limitation & Inconsistency Classification
A semantic violation signifies **data inconsistency**, not an immediate mathematical proof of malicious intrusion (as sensor calibration drift or administrative delay can also cause inconsistencies). The system explicitly classifies events into graded operational states:
* `NORMAL` ($S_{\text{joint}} < \tau_{\text{low}}$)
* `LOW_LEVEL_INCONSISTENCY` ($\tau_{\text{low}} \le S_{\text{joint}} < \tau_{\text{med}}$)
* `SUSPICIOUS` ($\tau_{\text{med}} \le S_{\text{joint}} < \tau_{\text{high}}$)
* `POTENTIAL_COORDINATED_ATTACK` ($S_{\text{joint}} \ge \tau_{\text{high}}$)

---

## 4. Academic Novelty & Literature Context

### 4.1 Primary Novelty — Semantic Constraint Verification
Instead of evaluating univariate plausibility ($x_{\text{sensor}} \in [\mu - 3\sigma, \mu + 3\sigma]$), the system evaluates multi-source invariants across heterogeneous domains (physical IoT + transactional ledger + operational state):
1. **Capacity Consistency ($C_1$):**
   $$\text{Free Capacity} \approx \text{Total Physical Capacity} - \text{Occupied Inventory}$$
   $$\text{Reported Free Capacity} + \text{IoT Occupancy Telemetry} \le \text{Total Capacity} \pm \epsilon_{\text{tol}}$$
2. **Inventory Reconciliation ($C_2$):**
   $$\text{Inventory}(t) = \text{Inventory}(t-1) + \text{Inbound}(t) - \text{Outbound}(t) \pm \epsilon_{\text{mass\_loss}}$$
3. **Historical Operating Envelope ($C_3$):**
   Evaluates reported metrics against robust non-parametric envelopes (Median and Median Absolute Deviation / MAD, or 10th–90th percentile bounds) derived from historical profiles, treated as contextual weight rather than an isolated alarm.

### 4.2 Secondary Novelty — Joint Temporal and Structural Escalation
Individually weak semantic violations ($V_i \approx 0.2 - 0.4$) are correlated across:
1. **Temporal Horizon:** Rolling sliding window $W$ with exponential time-decay weighting:
   $$S_{\text{temporal}} = \sum_{k \in W} V_k \cdot e^{-\lambda(t_{\text{current}} - t_k)}$$
2. **Structural Topology:** Entity relationship graph $G = (V, E)$ where nodes represent Warehouse, StorageUnit, InventoryLedger, Sensor, and Shipment entities. Structural relatedness between violations is computed via shortest graph distance / shared parentage:
   $$R_{\text{structural}}(e_i, e_j) = \frac{1}{1 + \text{dist}_G(e_i, e_j)}$$
3. **Joint Risk Synthesis:**
   $$S_{\text{joint}} = f(S_{\text{semantic}}, S_{\text{temporal}}, S_{\text{structural}})$$
   Escalating weak, recurring, topologically clustered violations into actionable alerts.

### 4.3 Explicitly Non-Novel Elements (Supporting Baseline Architecture)
* Standard ML anomaly detection (e.g., Isolation Forest, One-Class SVM). Used strictly as a supporting comparative baseline.
* Basic cross-source redundancy checking.
* Dynamic reputation/trust weighting.

---

## 5. Cold-Storage Case Study Specification

### 5.1 Entities & Topology
* **Warehouse ($W$):** Fixed physical maximum capacity (e.g., 50.0 tonnes).
* **Storage Units ($SU_{1 \dots m}$):** Compartments within warehouse.
* **IoT Sensor Nodes ($S_{\text{temp}}, S_{\text{humidity}}, S_{\text{occupancy}}$):** Continuous environmental and occupancy telemetry.
* **Inventory Ledger ($I$):** Transaction records of incoming shipments, outgoing shipments, and current balance.
* **Operational Reporting Record ($O$):** Operational claims submitted by warehouse operators (e.g., reported available free capacity, current operational status).
* **Historical Profile ($H$):** Baseline operating distributions aggregated over prior non-compromised epochs.

### 5.2 Target Attack Scenarios
* **Attack A (Plausible Operational Record Tampering):** Attacker alters operational database reported free capacity from 8.0t to 40.0t when actual inventory is 42.0t. (Plausible value in isolation; violates physical invariant $C_1$).
* **Attack B (Inventory Ledger Desynchronization):** Attacker falsifies inventory balance without corresponding inbound/outbound movements or vice versa. (Violates $C_2$).
* **Attack C (Sensor Telemetry Spoofing):** Attacker spoofs occupancy reading to indicate empty bays when physical inventory ledger shows 85% occupancy. (Violates $C_1$ cross-source telemetry check).
* **Attack D (Replay / Stale Snapshot Injection):** Attacker injects past valid operational states during a different operating context (e.g., harvest peak vs off-season). (Violates $C_3$).
* **Attack E (Coordinated Multi-Source Low-Severity Attack):** Attacker applies small, subtle drifts ($+5\%$ inventory, $-6\%$ reported free space, $+4\%$ sensor offset) across multiple storage units within the same warehouse. (Tests joint temporal-structural escalation).

---

## 6. System Architecture & Module Design

```text
                               ┌─────────────────────────────┐
                               │   Heterogeneous Sources     │
                               │  - IoT Telemetry            │
                               │  - Operational Records      │
                               │  - Inventory Ledger         │
                               │  - Historical Baselines     │
                               └──────────────┬──────────────┘
                                              │
                                              ▼
                               ┌─────────────────────────────┐
                               │ Data Ingestion & Validation │
                               │    (Time-aligned frames)    │
                               └──────────────┬──────────────┘
                                              │
                       ┌──────────────────────┴──────────────────────┐
                       ▼                                             ▼
       ┌───────────────────────────────┐             ┌───────────────────────────────┐
       │   Supporting Anomaly Model    │             │   Semantic Constraint Engine  │
       │     (Isolation Forest)        │             │  - Capacity Consistency (C1)  │
       │ (Baseline / Supporting Score) │             │  - Inventory Reconcile (C2)   │
       └───────────────┬───────────────┘             │  - Historical Envelope (C3)   │
                       │                             └───────────────┬───────────────┘
                       │                                             │
                       │     Normalized Semantic Violations [0, 1]   │
                       │                                             ▼
                       │                             ┌───────────────────────────────┐
                       │                             │     Temporal Correlator       │
                       │                             │  (Sliding Window W + Decay)   │
                       │                             └───────────────┬───────────────┘
                       │                                             │
                       │                                             ▼
                       │                             ┌───────────────────────────────┐
                       │                             │     Structural Correlator     │
                       │                             │    (Entity Graph Topology)    │
                       └──────────────────────┬──────┴───────────────┬───────────────┘
                                              │                      │
                                              ▼                      ▼
                               ┌─────────────────────────────────────────────┐
                               │           Joint Escalation Engine           │
                               │     S_joint = F(Semantic, Temporal, Graph)  │
                               └──────────────────────┬──────────────────────┘
                                                      │
                                                      ▼
                               ┌─────────────────────────────────────────────┐
                               │         Explainable Alert Generator         │
                               │     (Structured evidence reasoning logs)    │
                               └──────────────────────┬──────────────────────┘
                                                      │
                                                      ▼
                               ┌─────────────────────────────────────────────┐
                               │        Interactive Web Dashboard            │
                               │   (FastAPI + HTML5/CSS/JS + Plotly.js)      │
                               └─────────────────────────────────────────────┘
```

### 6.1 Project Directory Structure
```text
project/
├── PROJECT_PLAN.md
├── requirements.txt
├── config/
│   └── default_config.yaml
├── data/
│   ├── generated/
│   └── reference/
├── src/
│   ├── __init__.py
│   ├── data_generation/
│   │   ├── __init__.py
│   │   ├── generator.py
│   │   └── attack_injector.py
│   ├── semantic_constraints/
│   │   ├── __init__.py
│   │   ├── engine.py
│   │   └── rules.py
│   ├── anomaly_detection/
│   │   ├── __init__.py
│   │   └── baseline_isolation_forest.py
│   ├── temporal_analysis/
│   │   ├── __init__.py
│   │   └── temporal_aggregator.py
│   ├── structural_analysis/
│   │   ├── __init__.py
│   │   └── graph_model.py
│   ├── escalation/
│   │   ├── __init__.py
│   │   └── joint_escalator.py
│   ├── alerting/
│   │   ├── __init__.py
│   │   └── explainability.py
│   └── evaluation/
│       ├── __init__.py
│       ├── metrics.py
│       ├── benchmark.py
│       └── ablation.py
├── dashboard/
│   ├── app.py
│   ├── templates/
│   │   └── index.html
│   └── static/
│       ├── css/style.css
│       └── js/main.js
├── experiments/
│   ├── run_all_experiments.py
│   ├── exp1_normal_baseline.py
│   ├── exp2_capacity_manipulation.py
│   ├── exp3_sensor_tampering.py
│   ├── exp4_replay_attack.py
│   ├── exp5_coordinated_escalation.py
│   ├── exp6_severity_sweep.py
│   ├── exp7_duration_sweep.py
│   ├── exp8_compromised_sources_sweep.py
│   └── exp9_robustness_collusion.py
├── results/
│   ├── tables/
│   └── figures/
├── tests/
│   ├── test_generator.py
│   ├── test_constraints.py
│   ├── test_temporal.py
│   ├── test_structural.py
│   ├── test_escalation.py
│   └── test_pipeline_integration.py
└── docs/
    ├── threat_model.md
    ├── mathematical_formulation.md
    └── experiment_reproducibility.md
```

---

## 7. Comparative Baselines & Ablation Framework

### 7.1 Baselines
1. **Baseline 1 — Rule / Static Thresholding:** Simple checks for value out of range (e.g., $free\_capacity > 50$ or $< 0$).
2. **Baseline 2 — ML Anomaly Detection:** Standard unsupervised Isolation Forest model trained on historical sensor and telemetry records.
3. **Baseline 3 — Semantic Constraints Only:** Evaluates $C_1, C_2, C_3$ violations independently per timestamp without memory or topology.
4. **Proposed Method:** Full pipeline combining Semantic Constraints + Temporal Window Decay + Structural Graph Topology + Joint Escalation.

### 7.2 Ablation Study Arms
* **Arm A:** ML Anomaly Detection only.
* **Arm B:** Semantic Constraints only.
* **Arm C:** Semantic + Temporal Correlation.
* **Arm D:** Semantic + Structural Correlation.
* **Arm E:** Semantic + Temporal + Structural Correlation (Proposed Full Model).

### 7.3 Evaluation Metrics
* **Point Detection Performance:** Precision, Recall, $F_1$-score, False Positive Rate (FPR), False Negative Rate (FNR).
* **Temporal Efficiency:** Detection Delay ($\Delta t$ between attack injection and alert trigger).
* **Coordinated Attack Metrics:** Coordinated Attack Detection Rate (CADR), Time-to-Escalation (TTE), Minimum Violations to Escalation (MVE).

---

## 8. Controlled Experiments Execution Matrix

| Experiment ID | Title | Description & Objective | Expected Security Finding |
| :--- | :--- | :--- | :--- |
| **Exp 1** | Normal Baseline Calibration | Evaluate purely normal operating data containing realistic sensor noise and operational shifts. | Validates low false positive rate ($FPR \le 2\%$). |
| **Exp 2** | Plausible Capacity Tampering | Injects plausible free-capacity records while inventory remains high (Attack A). | Baselines 1 & 2 miss; Semantic Engine flags invariant violation ($C_1$). |
| **Exp 3** | Sensor Telemetry Tampering | Injects spoofed occupancy/thermal signals (Attack C). | Evaluates sensor anomaly detector vs cross-source semantic verification. |
| **Exp 4** | Stale / Replay State Injection | Injects valid past state snapshots into divergent operational context (Attack D). | Historical envelopes ($C_3$) flag temporal context violation. |
| **Exp 5** | Coordinated Low-Severity Attack | Injects subtle, multi-source distributed violations across related units (Attack E). | Arm B (semantic only) misses; Arm E (joint escalation) successfully triggers high-confidence alert. |
| **Exp 6** | Attack Severity Sensitivity Sweep | Stepwise variation of injected deviation magnitude (Low: $5-15\%$, Med: $20-40\%$, High: $>50\%$). | Evaluates detection boundary and ROC characteristics. |
| **Exp 7** | Attack Duration Sweep | Evaluates short transient burst vs chronic persistent attack. | Characterizes temporal accumulator and decay responsiveness. |
| **Exp 8** | Source Compromise Sweep | Scales number of simultaneously compromised entities ($K = 1, 2, 3, 4$). | Evaluates degradation curve and identification of multi-source attacks. |
| **Exp 9** | Robustness & Collusion Boundary | Tests adversarial case where attacker compromises and mutually synchronizes operational record, inventory ledger, and sensor. | Empirically documents the fundamental collusion boundary of cross-source validation. |

---

## 9. Technology Stack & Verification Tools
* **Language:** Python 3.12+
* **Data Processing & ML:** `numpy`, `pandas`, `scipy`, `scikit-learn`
* **Graph Topology:** `networkx`
* **Web Service & Dashboard:** `fastapi`, `uvicorn`, `jinja2`, `plotly.js`
* **Quality Assurance & Verification:** `pytest` (assert-based unit and integration test suite, runnable via single command).

---

## 10. Phased Implementation Roadmap (15 Phases)

1. **Phase 1: Environment & Config Setup:** Requirements, configuration structures, directory layout.
2. **Phase 2: Data Model & Synthetic Normal Generator:** Realistic cold-storage telemetry with stochastic noise, thermal diurnal cycle, and inventory replenishment.
3. **Phase 3: Attack Injection Engine:** Reproducible attack generators for Attacks A, B, C, D, and E with configurable seeds.
4. **Phase 4: Supporting Anomaly Baseline:** Implementation and calibration of Isolation Forest baseline.
5. **Phase 5: Semantic Constraint Engine:** Core mathematical formulation of $C_1, C_2, C_3$ with normalized violation scoring $[0, 1]$.
6. **Phase 6: Temporal Aggregation Module:** Sliding window state tracking with exponential decay weighting.
7. **Phase 7: Structural Graph Model:** NetworkX topological modeling of warehouse physical and transactional entities.
8. **Phase 8: Joint Escalation Engine:** Mathematical synthesis of semantic, temporal, and structural evidence into alert levels.
9. **Phase 9: Explainable Alerting Generator:** Diagnostic structured report generator detailing specific evidence contributing to alerts.
10. **Phase 10: Interactive Security Dashboard:** FastAPI app rendering status, timeline, warehouse telemetry, constraint violations, and real-time graph.
11. **Phase 11: Automated Benchmark & Ablation Harness:** Automated pipelines for running all comparison baselines and ablation arms.
12. **Phase 12: Controlled Experiments Execution (Exp 1–5):** Running core detection benchmarks and logging raw empirical outputs.
13. **Phase 13: Sensitivity & Sweep Experiments (Exp 6–8):** Severity, duration, and compromised source scaling sweeps.
14. **Phase 14: Robustness Collusion Testing (Exp 9):** Formal empirical evaluation of the multi-source collusion threat ceiling.
15. **Phase 15: IEEE Conference Paper Artifacts & Documentation:** Auto-generated LaTeX publication tables, publication-quality vector plots, and final documentation.
