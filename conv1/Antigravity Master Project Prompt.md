# MASTER PROMPT — INFORMATION SECURITY RESEARCH PROJECT

You are building a complete research-oriented Information Security project from scratch.

The project must be implemented as a working, reproducible prototype and must be designed so that it can later support an IEEE conference paper.

## 1. PROJECT TITLE

Use the working title:

**Semantic Constraint-Based Detection of Data Integrity Attacks in Distributed IoT-Enabled Operational Systems**

The application/case-study environment will be **post-harvest cold-storage operations**, but this is ONLY the application environment.

The research contribution is in **Information Security**, specifically data-integrity attack detection.

Do NOT turn this into a logistics optimization, farmer marketplace, route optimization, spoilage prediction, or warehouse optimization project.

---

# 2. CORE RESEARCH PROBLEM

Modern operational environments combine heterogeneous information sources:

- IoT sensors
- operational/business databases
- inventory records
- physical-state measurements
- historical operational data

An attacker may compromise one or more sources and manipulate information.

The difficult attack is not necessarily an obviously impossible value.

Instead, an attacker may inject a value that is:

- syntactically valid;
- numerically plausible;
- within a reasonable range;
- not obviously anomalous when viewed individually;

but is inconsistent with the **semantic, physical, operational, or historical relationships** that should govern that value.

Example:

A cold-storage warehouse has:

- physical capacity = 50 tonnes;
- inventory = approximately 42 tonnes;
- IoT occupancy = near full;
- historical free capacity = normally 5–10 tonnes.

An attacker modifies an operational record:

**reported free capacity = 40 tonnes**

The number 40 is syntactically valid.

A simple anomaly detector may not necessarily identify it as malicious.

However, the claim conflicts with:

- inventory state;
- physical occupancy;
- historical operating behaviour.

Therefore, the research problem is:

> **How can a security system detect plausible-looking manipulation of operational/business records by verifying whether those records satisfy semantic constraints derived from heterogeneous physical, operational, and historical evidence?**

A second problem is that individual semantic violations may be weak.

Several small violations occurring:

- repeatedly over time;
- across related entities;
- across structurally connected operational records;

may collectively indicate a coordinated integrity attack.

Therefore, the second research problem is:

> **How can individually low-severity semantic constraint violations be jointly correlated across time and structural relationships to identify potential coordinated data-integrity attacks?**

---

# 3. RESEARCH OBJECTIVES

Build a system that can:

1. Ingest heterogeneous operational and IoT data.
2. Detect ordinary anomalies using supporting anomaly-detection methods.
3. Represent semantic/physical/operational relationships as explicit constraints.
4. Evaluate operational claims against those constraints.
5. Calculate a semantic constraint violation score.
6. Track violations over time.
7. Identify relationships between affected entities/sources.
8. Combine temporal and structural evidence.
9. Escalate multiple weak violations when their joint pattern indicates a potential coordinated integrity attack.
10. Produce explainable security alerts showing WHY an event was considered suspicious.

---

# 4. PRIMARY NOVELTY

The primary novelty MUST be:

## Semantic Constraint Verification

The system should not only ask:

> "Is this sensor value abnormal?"

It should ask:

> "Does this operational/business claim satisfy the physical, operational, and historical constraints that should logically govern it?"

The system must therefore represent relationships between heterogeneous information sources.

Examples:

### Capacity constraint

Reported free capacity should be consistent with:

- total physical capacity;
- current inventory;
- occupancy telemetry.

Conceptually:

**Free Capacity ≈ Total Capacity − Occupied Capacity**

and:

**Free Capacity + Occupied Inventory ≤ Total Capacity**

### Inventory reconciliation constraint

Current inventory should be reasonably explainable by:

**Previous Inventory + Incoming Quantity − Outgoing Quantity**

within an explicitly defined tolerance.

### Historical operating constraint

A reported value should be compared against an appropriate historical operating envelope.

For example:

- historical median;
- historical percentile range;
- seasonal operating range.

A historical deviation should NOT automatically mean an attack.

It should become security evidence only when combined with semantic inconsistency or other evidence.

---

# 5. SECONDARY NOVELTY

The second research contribution is:

## Joint Temporal and Structural Escalation

Do NOT simply claim:

"we detect coordinated attacks."

That is too generic.

Implement a specific mechanism that combines:

### Temporal evidence

Examples:

- repeated violations;
- increasing violation frequency;
- multiple violations within a time window;
- persistence of inconsistency.

### Structural evidence

Examples:

- same warehouse;
- same inventory chain;
- related operational records;
- connected data sources;
- entities participating in the same operational workflow.

A single weak violation should not automatically produce a high-confidence attack.

Instead:

```text
Weak semantic violation
        +
Weak semantic violation
        +
Weak semantic violation
        ↓
Temporal correlation
        +
Structural correlation
        ↓
Joint escalation
        ↓
Potential coordinated integrity attack
```

Implement this as an explicit algorithm rather than merely describing it in documentation.

---

# 6. WHAT IS NOT NOVEL

This is extremely important.

DO NOT claim any of the following as the primary research novelty:

- machine-learning anomaly detection;
- Isolation Forest;
- generic anomaly detection;
- cross-source verification by itself;
- dynamic trust/reputation by itself;
- collaborative detection by itself;
- consensus by itself;
- coordinated attack detection by itself;
- IoT security in general.

These are supporting/existing concepts.

If ML is used, clearly describe it as a **supporting baseline/evidence source**.

If trust scoring is used, clearly describe it as a **supporting mechanism**, not the research novelty.

The research novelty must remain centered on:

1. semantic constraint verification; and
2. joint temporal/structural escalation of semantic violations.

---

# 7. CASE STUDY

Use a **cold-storage/post-harvest warehouse** as the primary case study.

Do NOT build a full agricultural marketplace or logistics-management platform.

The case study should contain:

### Entities

- Warehouse
- Storage unit
- Inventory
- Sensor
- Operational record
- Shipment/incoming movement
- Shipment/outgoing movement

### Data sources

1. IoT telemetry
2. Inventory database
3. Warehouse operational records
4. Historical operating data

---

# 8. DATA MODEL

Design a clear synthetic/reproducible dataset.

Each record should have appropriate timestamps and identifiers.

Example IoT data:

```text
timestamp
warehouse_id
storage_unit_id
temperature
humidity
occupancy
sensor_id
```

Example inventory data:

```text
timestamp
warehouse_id
inventory_quantity
incoming_quantity
outgoing_quantity
```

Example operational/business records:

```text
timestamp
warehouse_id
reported_free_capacity
reported_inventory
operational_status
```

Example historical data:

```text
timestamp
warehouse_id
historical_capacity
historical_inventory
historical_occupancy
```

Do not hard-code only one example.

Generate enough data to perform meaningful experiments.

---

# 9. NORMAL DATA

Create realistic normal operating data.

Normal data should contain:

- ordinary sensor noise;
- small measurement variation;
- normal inventory changes;
- normal capacity fluctuations;
- realistic temporal behaviour.

Do NOT make normal data perfectly clean.

Otherwise the experiment becomes unrealistic.

---

# 10. ATTACK DATA

Implement several attack scenarios.

At minimum include:

### Attack A — Operational record manipulation

Example:

Actual free capacity:

8 tonnes

Attacker changes operational record to:

40 tonnes

The manipulated value must remain numerically plausible.

---

### Attack B — Inventory manipulation

Attacker modifies inventory records so that the reported inventory differs from the physical state.

---

### Attack C — Sensor manipulation

Attacker modifies occupancy or other telemetry.

---

### Attack D — Replay/stale information

Use an old but valid-looking value at a later time.

---

### Attack E — Coordinated manipulation

Manipulate multiple related records/sources in a way that creates several weak semantic violations.

The purpose is to test the temporal/structural escalation mechanism.

---

# 11. IMPORTANT ATTACK DESIGN

Do NOT make attacks unrealistically obvious.

Avoid examples such as:

```text
capacity = -500 tonnes
temperature = 9999°C
inventory = impossible negative number
```

Such attacks are trivial.

The research problem is **plausible-looking integrity manipulation**.

Attack values should remain within reasonable numerical ranges whenever possible.

---

# 12. SEMANTIC CONSTRAINT ENGINE

Implement an explicit constraint engine.

Do NOT hide the logic inside arbitrary code.

Create a clear representation such as:

```text
Constraint:
C1 = Capacity Consistency

Inputs:
total_capacity
inventory
occupancy
reported_free_capacity

Expected relationship:
reported_free_capacity
≈
total_capacity - occupancy/inventory
```

Each constraint should produce:

- constraint ID;
- entities involved;
- expected relationship;
- observed values;
- deviation;
- normalized violation score;
- timestamp.

Example:

```text
Constraint C1
Warehouse W01

Reported free capacity = 40
Expected free capacity ≈ 8

Violation score = 0.82
```

---

# 13. VIOLATION SCORING

Define mathematically clear violation scores.

Do not use arbitrary unexplained numbers.

For a generic constraint, define something similar to:

```text
ViolationScore =
normalized deviation between
observed relationship and expected relationship
```

Clearly document:

- normalization;
- thresholds;
- tolerances;
- why thresholds are selected.

Where possible, use data-driven thresholds rather than arbitrary constants.

For historical constraints, consider robust statistics such as:

- median;
- MAD;
- percentile envelopes;
- rolling windows.

Explain why the selected method is appropriate.

---

# 14. TEMPORAL ESCALATION

Implement a temporal aggregation mechanism.

For example, maintain a time window:

```text
W = previous N minutes/hours
```

Track:

- number of violations;
- severity;
- persistence;
- recurrence;
- trend.

Do NOT simply sum everything without normalization.

Create a clearly defined temporal score.

Example conceptual form:

```text
TemporalScore =
weighted combination of
recent violation severity,
frequency,
and persistence
```

The exact formula must be explicitly defined and documented.

---

# 15. STRUCTURAL ESCALATION

Construct an entity/source relationship graph.

Example:

```text
Warehouse
   |
   +--- Storage Unit
   |
   +--- Inventory
   |
   +--- Sensor
   |
   +--- Operational Record
   |
   +--- Shipment
```

Use this structure to determine whether violations are related.

For example:

```text
Violation 1 → Warehouse W01
Violation 2 → Inventory W01
Violation 3 → Sensor S17 in W01
Violation 4 → Shipment associated with W01
```

These violations are structurally related.

Use this relationship as evidence.

Clearly document the graph/relationship model.

---

# 16. JOINT ESCALATION SCORE

Develop an explicit joint score combining:

- semantic violation evidence;
- temporal evidence;
- structural evidence.

For example conceptually:

```text
JointRisk =
f(
 semantic severity,
 temporal recurrence,
 structural relatedness
)
```

Do NOT blindly use arbitrary weights.

Provide justification and conduct a sensitivity analysis.

The final system should classify events into something such as:

```text
NORMAL
LOW-LEVEL INCONSISTENCY
SUSPICIOUS
POTENTIAL COORDINATED ATTACK
```

The exact labels can be refined during implementation.

---

# 17. EXPLAINABLE ALERTS

Every security alert must explain why it was generated.

Example:

```text
ALERT: Potential Data Integrity Attack

Warehouse: W01

Evidence:
1. Reported free capacity = 40 tonnes
2. Inventory = 42 tonnes
3. IoT occupancy indicates near-full storage
4. Historical free-capacity envelope = 5–10 tonnes
5. Capacity consistency constraint violated
6. Similar violations occurred 4 times in previous 30 minutes
7. Violations involve operational and inventory records
8. Joint temporal/structural score exceeded threshold

Conclusion:
Potential coordinated operational-data integrity attack.
```

Explainability is important for a security operator.

---

# 18. SYSTEM ARCHITECTURE

Build the architecture around:

```text
                    DATA SOURCES
                         |
        +----------------+----------------+
        |                |                |
       IoT          Operational       Historical
     telemetry        records           data
        |                |                |
        +----------------+----------------+
                         |
                  Data Ingestion
                         |
                Preprocessing /
                  Normalization
                         |
              +----------+----------+
              |                     |
       Anomaly Detection     Semantic Constraint
          (supporting)           Engine
              |                     |
              +----------+----------+
                         |
                Evidence Fusion
                         |
             Temporal Correlation
                         |
             Structural Correlation
                         |
                Joint Escalation
                         |
                 Security Decision
                         |
              Explainable Alert
```

---

# 19. TECHNOLOGY STACK

Prefer a simple research-friendly implementation.

Backend:

- Python
- FastAPI or Flask

Data processing:

- pandas
- NumPy
- scikit-learn

Database:

- SQLite for initial reproducibility

Graph/relationship processing:

- NetworkX if required

Frontend:

- simple HTML/CSS/JavaScript dashboard

Visualization:

- Plotly or another suitable Python-compatible visualization library

Do not over-engineer the system.

The objective is a reproducible research prototype, not a production enterprise platform.

---

# 20. DASHBOARD

Build a simple security dashboard.

It should display:

### System status

- normal sources;
- suspicious sources;
- active alerts.

### Timeline

Show semantic violations over time.

### Warehouse view

Show:

- reported capacity;
- estimated physical capacity;
- inventory;
- occupancy;
- constraint status.

### Alert details

Show the evidence behind each alert.

### Attack visualization

Allow the user to see when an attack begins and how the joint score changes.

---

# 21. BASELINES / COMPARISON METHODS

The project must be experimentally evaluated against meaningful baselines.

At minimum implement:

### Baseline 1 — Threshold/Rule-Based Detection

Detect abnormal individual values using predefined thresholds.

### Baseline 2 — ML Anomaly Detection

Use a standard unsupervised method such as Isolation Forest.

### Baseline 3 — Semantic Constraint Verification Only

Use the proposed semantic constraints without joint temporal/structural escalation.

### Proposed Method

Use:

```text
Semantic Constraint Verification
+
Temporal Correlation
+
Structural Correlation
+
Joint Escalation
```

If the faculty/project guidance specifies additional comparison arms, preserve them and document exactly what each arm tests.

Do not invent unsupported claims about superiority before experiments.

---

# 22. ABLATION STUDY

Perform ablation experiments.

At minimum compare:

```text
A. ML only

B. Semantic constraints only

C. Semantic + temporal

D. Semantic + structural

E. Semantic + temporal + structural
```

The purpose is to determine whether the proposed components actually contribute.

This is important for defending the novelty.

---

# 23. EVALUATION METRICS

Measure:

- Precision
- Recall
- F1-score
- False Positive Rate
- False Negative Rate
- Detection Delay
- Attack Detection Rate

For coordinated attacks, additionally measure:

- coordinated attack detection rate;
- time-to-escalation;
- number of violations required for escalation.

Report results separately for different attack types.

---

# 24. EXPERIMENTS

Perform controlled experiments.

At minimum:

### Experiment 1

Normal data only.

Expected:

Low false-positive rate.

### Experiment 2

Single plausible operational-record manipulation.

Expected:

Semantic constraints identify inconsistency.

### Experiment 3

Sensor manipulation.

Expected:

Supporting anomaly detection and/or semantic constraints identify the event depending on the attack.

### Experiment 4

Replay/stale data.

Expected:

Temporal/historical constraints provide evidence.

### Experiment 5

Multiple weak violations.

Expected:

Individual violations may be weak, but joint temporal/structural escalation identifies the larger pattern.

### Experiment 6

Vary attack severity.

Test:

- low;
- medium;
- high.

### Experiment 7

Vary attack duration.

Test short and persistent attacks.

### Experiment 8

Vary the number of compromised sources.

Measure how detection changes.

---

# 25. ROBUSTNESS TEST

Very important.

Test whether the proposed method can be defeated simply by manipulating multiple related sources consistently.

For example:

```text
Attacker changes:
inventory record
+
reported capacity
+
one sensor
```

The system should not assume that cross-source agreement automatically means truth.

Investigate what happens when compromised sources agree with each other.

This should be discussed honestly as a limitation/threat model issue.

Do not claim the system can detect every attack.

---

# 26. THREAT MODEL

Clearly define:

### Attacker capabilities

The attacker may compromise:

- an IoT sensor;
- an operational database record;
- one or more data sources;
- related sources in a coordinated attack.

### Attacker objective

Manipulate operational information while avoiding obvious numerical anomalies.

### Trusted components

Explicitly define which components are assumed trusted.

For example:

- constraint definitions;
- security monitor;
- protected historical reference data, if applicable.

### Out of scope

Do not claim protection against:

- complete infrastructure takeover;
- physical destruction;
- cryptographic key theft;
- denial-of-service unless specifically implemented;
- attacks that compromise every trusted component.

---

# 27. IMPORTANT SECURITY LIMITATION

The system must distinguish between:

```text
Data inconsistency
```

and:

```text
Confirmed attack
```

A semantic violation is evidence of inconsistency.

It does NOT automatically prove malicious activity.

Therefore use terminology such as:

- suspicious;
- potential integrity violation;
- potential attack;
- high-confidence security event.

Only call something a confirmed attack when the synthetic experiment knows it is an injected attack.

---

# 28. DATA GENERATION

Create a reproducible synthetic dataset generator.

It should support:

```text
--normal
--attack-type
--attack-rate
--attack-duration
--number-of-compromised-sources
--random-seed
```

Use fixed random seeds for reproducibility.

Save generated datasets so experiments can be repeated.

Do not manually fabricate experimental results.

---

# 29. REPRODUCIBILITY

Create:

```text
README.md
requirements.txt
environment configuration
dataset generator
training/evaluation scripts
experiment scripts
```

The README must explain exactly how to reproduce the results.

One command should ideally generate the dataset.

Another command should run the experiments.

Another should generate the evaluation results.

---

# 30. PROJECT STRUCTURE

Use a clean structure such as:

```text
project/
│
├── README.md
├── requirements.txt
├── config/
│
├── data/
│   ├── raw/
│   ├── generated/
│   └── processed/
│
├── src/
│   ├── data_generation/
│   ├── preprocessing/
│   ├── anomaly_detection/
│   ├── semantic_constraints/
│   ├── temporal_analysis/
│   ├── structural_analysis/
│   ├── escalation/
│   ├── alerting/
│   └── evaluation/
│
├── dashboard/
│
├── experiments/
│
├── results/
│
├── tests/
│
└── docs/
    ├── architecture.md
    ├── threat_model.md
    ├── novelty.md
    ├── methodology.md
    └── experiment_plan.md
```

Modify this structure if necessary, but maintain clear separation of components.

---

# 31. TESTING

Write unit tests for:

- data generation;
- constraint calculations;
- violation scores;
- temporal aggregation;
- structural relationship detection;
- escalation logic;
- attack injection;
- evaluation metrics.

Also create integration tests for the full pipeline.

---

# 32. RESEARCH DOCUMENTATION

Create a document explaining:

## Problem

What security problem is being solved?

## Existing approaches

What existing methods already address:

- anomaly detection;
- trust;
- cross-source checking;
- coordinated attack detection.

Do not claim these as novel.

## Gap

Explain that the focus is specifically on verifying whether heterogeneous operational/business claims satisfy semantic, physical, and historical constraints.

## Proposed method

Explain:

1. data ingestion;
2. anomaly evidence;
3. semantic constraints;
4. temporal analysis;
5. structural analysis;
6. joint escalation.

## Novelty

Clearly state:

### Novelty 1
Semantic constraint verification across heterogeneous operational/business and physical IoT information.

### Novelty 2
Joint temporal/structural escalation of individually weak semantic violations.

Do not add unrelated novelty claims.

---

# 33. LITERATURE REVIEW

Before writing novelty claims, perform a proper literature search.

Search IEEE Xplore and other scholarly sources for:

- semantic constraint verification IoT security;
- semantic data integrity attacks;
- business rule violation detection security;
- physical-logic constraints IoT security;
- temporal correlation data integrity attacks;
- structural correlation coordinated attacks;
- heterogeneous data integrity attacks;
- operational technology data integrity.

For every important claim, maintain:

```text
paper title
authors
year
venue
DOI
URL
problem addressed
method
limitations
relationship to our work
```

Do NOT claim:

> "No one has done this before."

unless the literature review genuinely supports such a statement.

Use careful wording such as:

> "Existing work largely focuses on X, while this work investigates Y."

---

# 34. BASE PAPER

Use relevant IEEE literature as the foundation/baseline.

One relevant existing work is:

**"Anomaly Detection using Machine Learning to Discover Sensor Tampering in IoT Systems"**

Aditya Kumar Pathak, Saguna, Karan Mitra, Christer Åhlund

IEEE International Conference on Communications (ICC), 2021.

DOI:

10.1109/ICC42927.2021.9500825

IEEE Xplore:

https://ieeexplore.ieee.org/document/9500825

Treat this as related/base work for sensor tampering/anomaly detection.

Do NOT pretend that the paper already contains the proposed semantic constraint contribution.

Clearly distinguish:

```text
Existing:
Sensor-level anomaly detection

Our proposed direction:
Semantic/business/physical constraint verification
+
joint temporal/structural escalation
```

---

# 35. EXPECTED RESEARCH QUESTION

Use the following as the central research question:

> **Can semantic relationships between heterogeneous business/operational records, physical IoT telemetry, and historical operating behaviour improve the detection of plausible-looking data-integrity attacks, and can temporal and structural correlation of weak semantic violations identify coordinated attacks more reliably than individual anomaly detection?**

Create supporting research questions:

### RQ1

Can semantic constraints detect plausible operational-record manipulation that is not clearly anomalous at the individual-value level?

### RQ2

Does semantic constraint verification reduce false negatives compared with individual anomaly detection?

### RQ3

Does temporal and structural escalation improve detection of coordinated attacks composed of multiple weak violations?

### RQ4

What is the trade-off between detection sensitivity and false-positive rate as constraint thresholds and escalation thresholds change?

---

# 36. EXPECTED HYPOTHESES

Possible hypotheses:

### H1

Semantic constraint verification detects a larger proportion of plausible operational-data integrity attacks than individual-value anomaly detection.

### H2

Combining semantic violations with temporal and structural evidence improves coordinated-attack detection compared with semantic verification alone.

### H3

Joint escalation can improve attack detection without producing an unacceptable increase in false positives.

These are hypotheses to TEST.

Do not write them as proven facts.

---

# 37. RESULTS

Generate results ONLY from actual execution.

Never:

- fabricate accuracy;
- fabricate precision;
- fabricate graphs;
- fabricate attack-detection rates;
- fabricate comparisons;
- write fake experimental conclusions.

If experiments have not been run, explicitly state:

**"Experiment pending."**

All graphs must be generated from actual stored experiment outputs.

---

# 38. FINAL DELIVERABLES

The finished project must contain:

1. Working source code.
2. Synthetic dataset generator.
3. Attack simulator.
4. Semantic constraint engine.
5. Temporal analysis module.
6. Structural relationship module.
7. Joint escalation module.
8. Supporting anomaly-detection module.
9. Security dashboard.
10. Automated evaluation pipeline.
11. Unit/integration tests.
12. Reproducible experiment scripts.
13. Documentation.
14. Architecture diagram.
15. Threat model.
16. Literature review.
17. Novelty justification.
18. Experiment results generated from actual runs.
19. Tables comparing baselines.
20. Figures suitable for an IEEE paper.

---

# 39. DEVELOPMENT ORDER

Do NOT attempt to build everything blindly at once.

Build in this order:

### Phase 1
Create the data model and synthetic dataset generator.

### Phase 2
Create normal operational behaviour.

### Phase 3
Create attack injection mechanisms.

### Phase 4
Implement basic anomaly detection baseline.

### Phase 5
Implement semantic constraint engine.

### Phase 6
Implement temporal correlation.

### Phase 7
Implement structural relationship model.

### Phase 8
Implement joint escalation.

### Phase 9
Create explainable alerts.

### Phase 10
Build dashboard.

### Phase 11
Implement baselines and ablation experiments.

### Phase 12
Run experiments.

### Phase 13
Generate tables and graphs.

### Phase 14
Perform robustness tests.

### Phase 15
Write final research documentation.

---

# 40. CRITICAL RULES

Follow these rules throughout the project:

1. **Information Security is the core domain.**
2. **Post-harvest/cold storage is only the case-study environment.**
3. Do not build logistics optimization.
4. Do not build a farmer marketplace.
5. Do not make ML the novelty.
6. Do not make trust scoring the novelty.
7. Do not claim cross-source verification alone as novelty.
8. Do not claim coordinated attack detection alone as novelty.
9. Primary novelty = semantic constraint verification.
10. Secondary novelty = joint temporal/structural escalation.
11. Every formula must be documented.
12. Every threshold must be justified.
13. Every experimental result must come from actual execution.
14. Never fabricate results.
15. Clearly distinguish anomaly, inconsistency, suspicion, and confirmed injected attack.
16. Test realistic plausible attacks.
17. Test attacks involving multiple compromised sources.
18. Document limitations honestly.
19. Perform literature verification before making novelty claims.
20. Keep the implementation simple enough that a student research team can understand and defend every component.

---

# 41. FINAL GOAL

At the end, the project should answer this security problem:

> **An attacker can manipulate an operational/business record so that the value remains individually plausible. Can we detect the manipulation by checking whether the claim violates semantic relationships with physical IoT telemetry, operational records, and historical behaviour, and can we identify coordinated attacks by jointly escalating weak violations across time and structurally related entities?**

The final system should demonstrate this experimentally using the cold-storage/post-harvest environment.

The project must be technically defensible, reproducible, explainable, and suitable as the foundation for an IEEE conference paper.

Before implementing any component, create a short `PROJECT_PLAN.md` containing:

- problem;
- threat model;
- existing approaches;
- research gap;
- proposed architecture;
- novelty;
- case study;
- datasets;
- attack scenarios;
- baselines;
- evaluation metrics;
- experiments;
- risks/limitations.

Then implement the project phase-by-phase according to the plan.