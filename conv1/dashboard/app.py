"""FastAPI Security Dashboard for Semantic Constraint-Based Integrity Detection."""

import os
import sys
from typing import Dict, Optional
import pandas as pd
from fastapi import FastAPI, Request
from fastapi.responses import HTMLResponse, JSONResponse
from fastapi.staticfiles import StaticFiles

# Ensure project root in sys.path
PROJECT_ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))
if PROJECT_ROOT not in sys.path:
    sys.path.insert(0, PROJECT_ROOT)

from src.data_generation.attack_injector import (
    inject_attack_a_capacity,
    inject_attack_b_inventory,
    inject_attack_c_sensor,
    inject_attack_d_replay,
    inject_attack_e_coordinated,
    inject_collusion_attack,
)
from src.data_generation.generator import generate_normal_stream
from src.pipeline import IntegrityDetectionPipeline

app = FastAPI(title="Operational Data Integrity Security Monitor", version="1.0.0")

# Mount static directory if it exists
static_dir = os.path.join(os.path.dirname(__file__), "static")
if os.path.exists(static_dir):
    app.mount("/static", StaticFiles(directory=static_dir), name="static")

# Shared in-memory pipeline state
PIPELINE = IntegrityDetectionPipeline()
TRAIN_DF = generate_normal_stream(num_samples=2016, seed=42)
PIPELINE.calibrate(TRAIN_DF)

# Current active simulation stream
CURRENT_STREAM: pd.DataFrame = None
CURRENT_ALERTS: list = []


def run_default_simulation(scenario: str = "attack_e"):
    global CURRENT_STREAM, CURRENT_ALERTS
    base_df = generate_normal_stream(num_samples=400, seed=100)

    if scenario == "attack_a":
        stream = inject_attack_a_capacity(base_df, start_idx=150, duration=48, tampered_free_capacity=38.0)
    elif scenario == "attack_b":
        stream = inject_attack_b_inventory(base_df, start_idx=150, duration=48, inventory_delta=-15.0)
    elif scenario == "attack_c":
        stream = inject_attack_c_sensor(base_df, start_idx=150, duration=48, spoofed_occupancy=0.15)
    elif scenario == "attack_d":
        stream = inject_attack_d_replay(base_df, start_idx=150, duration=48, source_history_start=20)
    elif scenario == "attack_e":
        stream = inject_attack_e_coordinated(base_df, start_idx=150, duration=60)
    elif scenario == "collusion":
        stream = inject_collusion_attack(base_df, start_idx=150, duration=48)
    else:
        stream = base_df

    proc_df, alerts = PIPELINE.process_stream(stream)
    CURRENT_STREAM = proc_df
    CURRENT_ALERTS = alerts
    return proc_df, alerts


# Initialize default simulation
run_default_simulation("attack_e")


@app.get("/", response_class=HTMLResponse)
def serve_dashboard():
    template_path = os.path.join(os.path.dirname(__file__), "templates", "index.html")
    if os.path.exists(template_path):
        with open(template_path, "r", encoding="utf-8") as f:
            return f.read()
    return "<h1>Security Dashboard template missing</h1>"


@app.get("/api/status")
def get_status():
    global CURRENT_STREAM, CURRENT_ALERTS
    if CURRENT_STREAM is None:
        return {"status": "NO_DATA"}

    last_row = CURRENT_STREAM.iloc[-1]
    active_alerts = len(CURRENT_ALERTS)
    attack_alerts = sum(1 for a in CURRENT_ALERTS if a.alert_level == "POTENTIAL_COORDINATED_ATTACK")
    suspicious_alerts = sum(1 for a in CURRENT_ALERTS if a.alert_level == "SUSPICIOUS")

    return {
        "warehouse_id": "WH_01",
        "total_capacity_tonnes": 50.0,
        "total_records": len(CURRENT_STREAM),
        "total_alerts": active_alerts,
        "critical_attack_alerts": attack_alerts,
        "suspicious_alerts": suspicious_alerts,
        "current_alert_level": str(last_row["alert_level"]),
        "current_joint_risk": round(float(last_row["joint_risk_score"]), 3),
        "current_semantic_score": round(float(last_row["semantic_score_combined"]), 3),
        "current_temporal_score": round(float(last_row["temporal_score"]), 3),
        "current_structural_score": round(float(last_row["structural_score"]), 3),
    }


@app.get("/api/stream")
def get_stream():
    global CURRENT_STREAM
    if CURRENT_STREAM is None:
        return {"data": []}

    records = []
    # Subsample if large, here stream is ~400 points
    for idx, row in CURRENT_STREAM.iterrows():
        records.append(
            {
                "step": int(idx),
                "timestamp": str(row["timestamp"]),
                "reported_free_capacity": round(float(row["reported_free_capacity"]), 2),
                "physical_free_capacity": round(float(50.0 - row["reported_inventory"]), 2),
                "reported_inventory": round(float(row["reported_inventory"]), 2),
                "telemetry_occupancy": round(float(row["telemetry_occupancy"]), 3),
                "temperature_c": round(float(row["temperature_c"]), 2),
                "semantic_score": round(float(row["semantic_score_combined"]), 3),
                "temporal_score": round(float(row["temporal_score"]), 3),
                "structural_score": round(float(row["structural_score"]), 3),
                "joint_risk_score": round(float(row["joint_risk_score"]), 3),
                "is_attack": int(row["is_attack"]),
                "is_alert": int(row["is_alert"]),
                "alert_level": str(row["alert_level"]),
            }
        )
    return {"data": records}


@app.get("/api/alerts")
def get_alerts():
    global CURRENT_ALERTS
    return {"alerts": [a.to_dict() for a in CURRENT_ALERTS[-50:]]}


@app.get("/api/graph")
def get_graph():
    return PIPELINE.entity_graph.get_graph_data()


@app.get("/api/benchmark_summary")
def get_benchmark_summary():
    tables_dir = os.path.join(PROJECT_ROOT, "results", "tables")
    res = {}
    f_baseline = os.path.join(tables_dir, "baseline_comparison_attacks.csv")
    f_ablation = os.path.join(tables_dir, "ablation_study_results.csv")

    if os.path.exists(f_baseline):
        res["baseline_comparison"] = pd.read_csv(f_baseline).to_dict(orient="records")
    if os.path.exists(f_ablation):
        res["ablation_study"] = pd.read_csv(f_ablation).to_dict(orient="records")
    return res


@app.post("/api/simulate")
def trigger_simulation(scenario: str = "attack_e"):
    run_default_simulation(scenario)
    return {"status": "SUCCESS", "scenario": scenario, "records": len(CURRENT_STREAM), "alerts": len(CURRENT_ALERTS)}
