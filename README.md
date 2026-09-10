# Organization Information Security Monitoring & Defender Platform

A real-time security monitoring and multi-layer data integrity verification platform for cyber-physical systems and simulated enterprise facilities (cold-storage warehouse operations).

## Overview

The platform monitors operational and IoT data to detect and flag subtle data integrity attacks, sensor spoofing, replay attacks, and coordinated cross-subsystem manipulations.

### Multi-Layer Security Pipeline

`	ext
Warehouse Observation (IoT Telemetry, Inventory, Shipments)
                        ↓
            1. Data Preprocessing & Validation
                        ↓
           2. ML Multivariate Anomaly Detector
                        ↓
         3. Semantic Verification Engine (C1, C2, C3)
                        ↓
           4. Temporal Analysis Engine (Decay & Persistence)
                        ↓
         5. Structural Analysis Engine (Knowledge Graph)
                        ↓
           6. Joint Security Decision & Alerting
`

- **Semantic Invariants Checked:**
  - **C1 (Capacity Consistency):** Inventory + Free Capacity = Total Capacity
  - **C2 (Inventory Flow Consistency):** Delta Inventory = Inbound - Outbound
  - **C3 (Historical Operating Envelope):** Telemetry (temperature, humidity) bounded within historical operating standards.
- **Temporal Engine:** Exponentially decayed violation scoring (0.85^k) and persistence tracking over sliding windows.
- **Structural Engine:** Knowledge-graph based dependency modeling across sensor, ledger, and physical domains to detect coordinated multi-vector tampering.
- **Joint Decision Engine:** Weighted synthesis (0.50 * Semantic + 0.20 * Temporal + 0.15 * Structural + 0.15 * ML) producing definitive risk classifications: NORMAL, LOW, SUSPICIOUS, POTENTIAL_ATTACK, and COORDINATED_ATTACK.

---

## Quick Start

### 1. Prerequisites
- Python 3.10+
- pip

### 2. Installation
Clone the repository and install dependencies:
`ash
pip install -r requirements.txt
`

### 3. Start the Platform
Run the platform server:
```bash
python run.py
```
The application will be available at:
- **Organization Security Portal:** http://127.0.0.1:8000
- **Live Operations & Sensor Monitor:** http://127.0.0.1:8000/operations
- **Interactive OpenAPI Documentation:** http://127.0.0.1:8000/docs

### 4. Running the Test Suite
Execute the comprehensive automated test suite (81 unit and integration tests):
```bash
pytest tests/ -v
```

---

## Controlled Attack Demonstration

The portal and API feature deterministic, controlled attack scenarios for evaluation:
- **Capacity Manipulation:** Desynchronizes inventory and reported free space (C1 violation).
- **Inventory Manipulation:** Spoofs shipment transfers without ledger matching (C2 violation).
- **Sensor Spoofing:** Injects out-of-envelope temperature excursions (C3 violation).
- **Replay Attack:** Replays static telemetry across changing operational steps.
- **Coordinated Weak Manipulation:** Sub-threshold deviations across multiple variables designed to bypass individual univariate thresholds.
- **Multi-Source Manipulation:** Cross-domain manipulation activating structural graph correlation.

---

## Project Structure

`	ext
.
├── app/
│   ├── api/             # FastAPI REST endpoints and routing
│   ├── defender/        # Multi-layer security pipeline (ML, Semantic, Temporal, Structural, Decision)
│   ├── frontend/        # Real-time Organization Security Portal (HTML, CSS, JS)
│   ├── simulator/       # Cold-storage warehouse simulation and telemetry engine
│   └── utils/           # Configuration and logging utilities
├── tests/               # 73 automated unit and integration tests
├── requirements.txt     # Production and testing dependencies
├── run.py               # Entry point script
└── README.md            # Platform documentation
`
