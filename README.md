# Cold-Storage Security Monitor

Data integrity monitor and sensor telemetry simulator for a cold-storage warehouse (facility W01). Detects tampering in inventory counts, shipment flow, and IoT temperature/humidity feeds.

## System Pipeline

```text
Warehouse Observation (IoT Telemetry, Inventory, Shipments)
                        |
            1. Preprocessing and Validation
                        |
            2. ML Anomaly Detection (Isolation Forest)
                        |
            3. Semantic Invariant Verification (C1, C2, C3)
                        |
            4. Temporal Trend and Decay Tracking
                        |
            5. Structural Graph Correlation
                        |
            6. Joint Security Decision and Alerting
```

### Invariants Checked
- **C1 (Capacity):** inventory + free_capacity == total_capacity
- **C2 (Inventory Flow):** current_inventory == previous_inventory + inbound - outbound
- **C3 (Historical Bounds):** Temperature (1.0 to 7.0 deg C) and humidity (60% to 85%) inside normal operating range.

---

## Quick Start

### 1. Requirements
- Python 3.10+
- pip

### 2. Install Dependencies
```bash
pip install -r requirements.txt
```

### 3. Run the Service
```bash
python run.py
```

Endpoints:
- **Security Portal (Part 1 Defender):** http://127.0.0.1:8000
- **Operations Monitor (Part 1 Raw Telemetry):** http://127.0.0.1:8000/operations
- **Attack Gateway:** http://127.0.0.1:8000/api/attacker/*
- **Defender API Docs:** http://127.0.0.1:8000/docs

### 4. Run Part 2 (AI Attacker Application)
In a separate terminal:
```bash
python run_attacker.py --port 8001
```

Endpoints:
- **AI Attacker Console (Part 2):** http://127.0.0.1:8001
- **Attacker API Docs:** http://127.0.0.1:8001/docs

### 5. Run Tests
```bash
pytest tests/ -v
```

---

## Controlled Attack Scenarios

Deterministic attack scenarios exposed via the Attack Gateway:
- capacity_manipulation: Desynchronizes inventory and free capacity (breaks C1).
- inventory_manipulation: Alters inventory without shipment ledger records (breaks C2).
- sensor_spoofing: Forces temperature/humidity excursions outside operating limits (breaks C3).
- replay: Replays older observations into a changed warehouse state.
- coordinated_weak: Sub-threshold coordinated drift across variables.
- multi_source: Corrupts both physical telemetry and ledger records simultaneously.

---

## Project Structure

```text
.
├── app/                 # Part 1: Organization Defender Platform
│   ├── api/             # FastAPI REST endpoints, state, and Attack Gateway
│   ├── defender/        # Security engines (ML, semantic, temporal, structural, decision)
│   ├── frontend/        # Defender and Operations UI dashboards (HTML, CSS, JS)
│   ├── simulator/       # Cold-storage warehouse and telemetry simulator
│   └── config.py        # Central configuration settings
├── attacker_app/        # Part 2: Isolated AI Attacker Application
│   ├── gateway_client.py# Egress client restricted strictly to Attack Gateway
│   ├── planner.py       # Deterministic and LLM-based strategy planning
│   ├── providers.py     # LLM provider integration (OpenAI, Anthropic, Mock)
│   ├── validator.py     # Proposal bounds and whitelist validation
│   ├── schemas.py       # Pydantic data models for proposals and experiments
│   └── static/          # AI Attacker Console interface
├── tests/               # 136 automated unit, integration, and E2E tests
├── requirements.txt     # Dependencies
├── run.py               # Part 1 entrypoint
├── run_attacker.py      # Part 2 entrypoint
└── README.md            # Documentation
```
