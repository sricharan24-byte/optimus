# Semantic Constraint-Based Detection of Data Integrity Attacks in Distributed IoT-Enabled Operational Systems

An IEEE-oriented research prototype and experimental testbed for detecting plausible-looking data-integrity attacks across heterogeneous operational databases, physical IoT telemetry, and historical baselines.

---

## 1. Research Overview & Problem Statement

Modern operational environments rely on heterogeneous data sources:
* **IoT Sensor Telemetry:** Ambient temperature, humidity, and storage unit occupancy.
* **Operational & Business Ledgers:** Reported available capacity, operational status claims.
* **Inventory Transactions:** Batch receipts, dispatches, and ledger balances.
* **Historical Operational Envelopes:** Normal operating ranges and seasonal baselines.

### The Stealth Threat
Traditional anomaly detection (univariate thresholds or standard unsupervised ML) evaluates data streams in isolation. An attacker can inject **plausible-looking, in-range values** (e.g., claiming 38 tonnes of free capacity in a 50-tonne warehouse that actually holds 42 tonnes of inventory). The value itself is numerically plausible, but it violates the **semantic, physical invariants** connecting disparate operational streams.

Furthermore, attackers can orchestrate **coordinated attacks** composed of individually weak discrepancies distributed across time and related entities.

### Core Contributions
1. **Primary Contribution — Semantic Constraint Verification:** Mathematical invariant checks cross-verifying physical capacity ($C_1$), inventory movement reconciliation ($C_2$), and robust historical operating envelopes ($C_3$).
2. **Secondary Contribution — Joint Temporal & Structural Escalation:** An explicit algorithmic formulation correlating weak violations over an exponential decay sliding window ($W$) and an entity relationship graph ($G$), escalating coordinated attacks without false alarms on normal operating variations.

---

## 2. Project Architecture

```text
├── config/
│   └── default_config.yaml         # System parameters, sensor noise, and threshold calibration
├── src/
│   ├── data_generation/            # Synthetic generator & Attacks A–E + collusion injector
│   ├── anomaly_detection/          # Isolation Forest ML baseline (Pathak et al., ICC 2021)
│   ├── semantic_constraints/       # Invariant rules C1, C2, C3 and normalized scoring
│   ├── temporal_analysis/          # Sliding window decay accumulator (frequency & persistence)
│   ├── structural_analysis/        # NetworkX entity relationship graph & topological relatedness
│   ├── escalation/                 # Joint evidence synthesis & 4-tier alert classification
│   ├── alerting/                   # Explainable diagnostic report generator
│   ├── evaluation/                 # Metrics, benchmark comparisons, and ablation harness
│   └── pipeline.py                 # Unified end-to-end detection pipeline
├── dashboard/
│   ├── app.py                      # FastAPI backend with scenario simulation APIs
│   └── templates/index.html        # Interactive HTML5/Plotly monitoring dashboard
├── experiments/
│   └── run_all_experiments.py      # Master harness executing Experiments 1 to 9
├── results/
│   ├── tables/                     # Empirical raw CSV result tables
│   └── figures/                    # 300-DPI publication figures (IEEE format)
├── tests/                          # Assert-based unit and integration test suite
├── scripts/
│   └── generate_guide_pdf.py       # ReportLab PDF documentation builder
├── PROJECT_PLAN.md                 # Formal project plan per Section 41 specifications
├── User_and_Technical_Guide.pdf    # Complete user and technical guide (generated)
└── requirements.txt
```

---

## 3. Quick Start & Execution

### 3.1 Install Dependencies
```bash
pip install -r requirements.txt
```

### 3.2 Run the Test Suite
```bash
pytest -v tests/
```
*All 7 unit and integration tests execute in < 3 seconds.*

### 3.3 Run All Research Experiments
```bash
python experiments/run_all_experiments.py
```
This single command executes Experiments 1 to 9:
* **Exp 1:** Normal baseline false-alarm calibration (2016 timestamps).
* **Exp 2:** Plausible capacity manipulation (Attack A).
* **Exp 3:** Sensor telemetry spoofing (Attack C).
* **Exp 4:** Stale / replay state injection (Attack D).
* **Exp 5:** Coordinated multi-source weak violation escalation (Attack E) & Ablation study.
* **Exp 6:** Attack severity sensitivity sweep ($2\text{t}$ to $35\text{t}$).
* **Exp 7:** Attack duration sweep ($15\text{m}$ to $4\text{h}$).
* **Exp 9:** Robustness & multi-source collusion boundary analysis.

Outputs are stored in `results/tables/*.csv` and `results/figures/*.png`.

### 3.4 Launch the Interactive Web Dashboard
```bash
uvicorn dashboard.app:app --host 127.0.0.1 --port 8000 --reload
```
Open **`http://127.0.0.1:8000`** in your browser to inspect live telemetry, switch between attack scenarios in real time, view evidence decomposition curves, and inspect explainable security audit dossiers.

---

## 4. Key Experimental Results

| Evaluation Metric | Baseline 1 (Threshold) | Baseline 2 (Isolation Forest) | Baseline 3 (Semantic Only) | Proposed Method (Joint Escalation) |
| :--- | :--- | :--- | :--- | :--- |
| **Normal False Positive Rate** | 0.0% | 52.8% (High false alarms) | 0.0% | **0.0% (Zero false alarms)** |
| **Attack A (Plausible Capacity)** | Recall: 0.0% | Recall: 0.0% | Recall: 100% | **Recall: 100% (Delay: 0m)** |
| **Attack E (Coordinated Multi-Source)** | Recall: 0.0% | Precision: 3.8% | Recall: 0.0% (Missed) | **Recall: 93.3%, Precision: 100%** |
| **Ablation Arm C (Sem + Temp)** | — | — | — | **Recall: 93.3%** |
| **Multi-Source Collusion Boundary** | Recall: 0.0% | Recall: 52.8% | Recall: 2.8% | **Recall: 0.0% (Documented ceiling)** |

---

## 5. Comprehensive Documentation
A publication-ready user and technical guide is available as a PDF in the project root:
* [User_and_Technical_Guide.pdf](file:///e:/ssss/IS%20conference%20paper/User_and_Technical_Guide.pdf)
