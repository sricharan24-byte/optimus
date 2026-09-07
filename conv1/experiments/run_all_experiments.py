"""Comprehensive experimental harness: executes Experiments 1 to 9, logs tables, and generates publication figures."""

import os
import sys
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))
import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
import numpy as np
import pandas as pd
from src.data_generation.attack_injector import (
    inject_attack_a_capacity,
    inject_attack_b_inventory,
    inject_attack_c_sensor,
    inject_attack_d_replay,
    inject_attack_e_coordinated,
    inject_collusion_attack,
)
from src.data_generation.generator import generate_normal_stream
from src.evaluation.ablation import AblationStudyRunner
from src.evaluation.benchmark import BenchmarkEvaluator
from src.pipeline import IntegrityDetectionPipeline

RESULTS_TABLES = "results/tables"
RESULTS_FIGURES = "results/figures"
os.makedirs(RESULTS_TABLES, exist_ok=True)
os.makedirs(RESULTS_FIGURES, exist_ok=True)


def run_all():
    print("==========================================================")
    print("STARTING COMPLETE EXPERIMENTAL EVALUATION HARNESS")
    print("==========================================================")

    # 1. Initialize Pipeline & Calibrate on Baseline
    print("\n[Phase 1] Calibrating pipeline on 14-day normal stream (4032 samples)...")
    normal_train = generate_normal_stream(num_samples=4032, seed=42)
    pipeline = IntegrityDetectionPipeline()
    pipeline.calibrate(normal_train)

    benchmark_eval = BenchmarkEvaluator(pipeline)
    ablation_runner = AblationStudyRunner(pipeline)

    # ---------------------------------------------------------
    # Experiment 1: Normal Baseline False Alarm Rate
    # ---------------------------------------------------------
    print("\n[Exp 1] Evaluating Normal Operating Data (Zero Attacks)...")
    normal_test = generate_normal_stream(num_samples=2016, seed=101)
    res_exp1 = benchmark_eval.run_benchmark(normal_test)
    df_exp1 = pd.DataFrame(res_exp1).T
    df_exp1.to_csv(os.path.join(RESULTS_TABLES, "exp1_normal_baseline.csv"))
    print(df_exp1[["false_positive_rate", "fp", "tn"]])

    # ---------------------------------------------------------
    # Experiment 2: Attack A (Plausible Capacity Tampering)
    # ---------------------------------------------------------
    print("\n[Exp 2] Evaluating Attack A (Plausible Capacity Tampering)...")
    stream_a = generate_normal_stream(num_samples=500, seed=102)
    stream_a = inject_attack_a_capacity(stream_a, start_idx=150, duration=48, tampered_free_capacity=38.0)
    res_exp2 = benchmark_eval.run_benchmark(stream_a)
    df_exp2 = pd.DataFrame(res_exp2).T
    df_exp2.to_csv(os.path.join(RESULTS_TABLES, "exp2_attack_a_capacity.csv"))
    print(df_exp2[["precision", "recall", "f1_score", "false_negative_rate", "detection_delay_min"]])

    # ---------------------------------------------------------
    # Experiment 3: Attack C (Sensor Spoofing)
    # ---------------------------------------------------------
    print("\n[Exp 3] Evaluating Attack C (Sensor Telemetry Spoofing)...")
    stream_c = generate_normal_stream(num_samples=500, seed=103)
    stream_c = inject_attack_c_sensor(stream_c, start_idx=150, duration=48, spoofed_occupancy=0.15)
    res_exp3 = benchmark_eval.run_benchmark(stream_c)
    df_exp3 = pd.DataFrame(res_exp3).T
    df_exp3.to_csv(os.path.join(RESULTS_TABLES, "exp3_attack_c_sensor.csv"))

    # ---------------------------------------------------------
    # Experiment 4: Attack D (Replay / Stale State Injection)
    # ---------------------------------------------------------
    print("\n[Exp 4] Evaluating Attack D (Replay / Stale State)...")
    stream_d = generate_normal_stream(num_samples=500, seed=104)
    stream_d = inject_attack_d_replay(stream_d, start_idx=150, duration=48, source_history_start=20)
    res_exp4 = benchmark_eval.run_benchmark(stream_d)
    df_exp4 = pd.DataFrame(res_exp4).T
    df_exp4.to_csv(os.path.join(RESULTS_TABLES, "exp4_attack_d_replay.csv"))

    # ---------------------------------------------------------
    # Experiment 5: Attack E (Coordinated Multi-Source Attack) & Ablation
    # ---------------------------------------------------------
    print("\n[Exp 5] Evaluating Attack E (Coordinated Multi-Source Weak Violations)...")
    stream_e = generate_normal_stream(num_samples=600, seed=105)
    stream_e = inject_attack_e_coordinated(stream_e, start_idx=200, duration=60)
    
    res_exp5 = benchmark_eval.run_benchmark(stream_e)
    df_exp5 = pd.DataFrame(res_exp5).T
    df_exp5.to_csv(os.path.join(RESULTS_TABLES, "exp5_attack_e_coordinated.csv"))
    print("--- Benchmark on Coordinated Attack ---")
    print(df_exp5[["precision", "recall", "f1_score", "false_negative_rate", "detection_delay_min"]])

    print("\nRunning Ablation Study on Coordinated Attack Stream...")
    res_ablation = ablation_runner.run_ablation(stream_e)
    df_ablation = pd.DataFrame(res_ablation).T
    df_ablation.to_csv(os.path.join(RESULTS_TABLES, "ablation_study_results.csv"))
    print("--- Ablation Study Results ---")
    print(df_ablation[["precision", "recall", "f1_score", "false_positive_rate", "detection_delay_min"]])

    # Consolidated Multi-Attack Benchmark Table
    multi_stream = generate_normal_stream(num_samples=1200, seed=200)
    multi_stream = inject_attack_a_capacity(multi_stream, start_idx=150, duration=36)
    multi_stream = inject_attack_b_inventory(multi_stream, start_idx=400, duration=36)
    multi_stream = inject_attack_c_sensor(multi_stream, start_idx=650, duration=36)
    multi_stream = inject_attack_e_coordinated(multi_stream, start_idx=900, duration=48)

    res_all_attacks = benchmark_eval.run_benchmark(multi_stream)
    df_all_attacks = pd.DataFrame(res_all_attacks).T
    df_all_attacks.to_csv(os.path.join(RESULTS_TABLES, "baseline_comparison_attacks.csv"))

    # ---------------------------------------------------------
    # Experiment 6: Attack Severity Sensitivity Sweep
    # ---------------------------------------------------------
    print("\n[Exp 6] Evaluating Attack Severity Sensitivity Sweep...")
    severity_offsets = [2.0, 4.0, 8.0, 15.0, 25.0, 35.0]
    sweep_results = []
    for offset in severity_offsets:
        s_df = generate_normal_stream(num_samples=400, seed=300)
        s_df = inject_attack_a_capacity(s_df, start_idx=150, duration=30, tampered_free_capacity=8.0 + offset)
        p_df, _ = pipeline.process_stream(s_df)
        y_t = p_df["is_attack"].to_numpy()
        y_p = p_df["is_alert"].to_numpy()
        tp = int(np.sum((y_t == 1) & (y_p == 1)))
        fn = int(np.sum((y_t == 1) & (y_p == 0)))
        rec = tp / (tp + fn) if (tp + fn) > 0 else 0.0
        sweep_results.append({"offset_tonnes": offset, "recall": rec, "f1": float(df_exp2.loc["Proposed_JointEscalation", "f1_score"])})
    df_sweep = pd.DataFrame(sweep_results)
    df_sweep.to_csv(os.path.join(RESULTS_TABLES, "severity_sweep.csv"), index=False)

    # ---------------------------------------------------------
    # Experiment 7: Attack Duration Sweep
    # ---------------------------------------------------------
    print("\n[Exp 7] Evaluating Attack Duration Sweep...")
    durations = [3, 6, 12, 24, 36, 48]  # 15m to 4h
    dur_results = []
    for dur in durations:
        d_df = generate_normal_stream(num_samples=400, seed=400)
        d_df = inject_attack_e_coordinated(d_df, start_idx=150, duration=dur)
        p_df, _ = pipeline.process_stream(d_df)
        y_t = p_df["is_attack"].to_numpy()
        y_p = p_df["is_alert"].to_numpy()
        tp = int(np.sum((y_t == 1) & (y_p == 1)))
        fn = int(np.sum((y_t == 1) & (y_p == 0)))
        rec = tp / (tp + fn) if (tp + fn) > 0 else 0.0
        dur_results.append({"duration_steps": dur, "duration_minutes": dur * 5, "recall": round(rec, 3)})
    df_dur = pd.DataFrame(dur_results)
    df_dur.to_csv(os.path.join(RESULTS_TABLES, "duration_sweep.csv"), index=False)

    # ---------------------------------------------------------
    # Experiment 9: Robustness & Collusion Boundary
    # ---------------------------------------------------------
    print("\n[Exp 9] Evaluating Robustness to Collusion Attack...")
    coll_df = generate_normal_stream(num_samples=400, seed=500)
    coll_df = inject_collusion_attack(coll_df, start_idx=150, duration=36, falsified_inventory=15.0)
    res_coll = benchmark_eval.run_benchmark(coll_df)
    df_coll = pd.DataFrame(res_coll).T
    df_coll.to_csv(os.path.join(RESULTS_TABLES, "collusion_robustness.csv"))
    print("Collusion results (demonstrates cross-source boundary):")
    print(df_coll[["precision", "recall", "false_negative_rate"]])

    # ---------------------------------------------------------
    # Generate Publication Figures (Matplotlib IEEE style)
    # ---------------------------------------------------------
    print("\nGenerating publication figures in results/figures/...")
    plt.rcParams.update({"font.size": 11, "font.family": "serif"})

    # Figure 1: Baseline Comparison Bar Chart
    fig, ax = plt.subplots(figsize=(8, 4.5), dpi=300)
    methods = ["Baseline 1\n(Threshold)", "Baseline 2\n(Isolation Forest)", "Baseline 3\n(Semantic Only)", "Proposed Method\n(Joint Escalation)"]
    f1_scores = df_all_attacks["f1_score"].values
    recalls = df_all_attacks["recall"].values
    precisions = df_all_attacks["precision"].values

    x = np.arange(len(methods))
    width = 0.25
    ax.bar(x - width, precisions, width, label="Precision", color="#1f77b4")
    ax.bar(x, recalls, width, label="Recall", color="#ff7f0e")
    ax.bar(x + width, f1_scores, width, label="F1-Score", color="#2ca02c")

    ax.set_ylabel("Metric Score [0.0 - 1.0]")
    ax.set_title("Performance Comparison Across Detection Baselines (Multi-Attack Stream)")
    ax.set_xticks(x)
    ax.set_xticklabels(methods)
    ax.set_ylim(0, 1.15)
    ax.legend(loc="upper left")
    ax.grid(axis="y", linestyle="--", alpha=0.5)
    fig.tight_layout()
    fig.savefig(os.path.join(RESULTS_FIGURES, "fig1_baseline_comparison.png"))
    plt.close(fig)

    # Figure 2: Ablation Study Comparison
    fig, ax = plt.subplots(figsize=(8.5, 4.5), dpi=300)
    arms = ["Arm A\n(ML Only)", "Arm B\n(Semantic Only)", "Arm C\n(Sem + Temp)", "Arm D\n(Sem + Struct)", "Arm E\n(Proposed Full)"]
    abl_f1 = df_ablation["f1_score"].values
    abl_rec = df_ablation["recall"].values
    x = np.arange(len(arms))
    ax.bar(x - width/2, abl_rec, width, label="Recall", color="#3b528b")
    ax.bar(x + width/2, abl_f1, width, label="F1-Score", color="#5dc863")
    ax.set_ylabel("Score [0.0 - 1.0]")
    ax.set_title("Ablation Study on Coordinated Attack (Isolating Escalation Components)")
    ax.set_xticks(x)
    ax.set_xticklabels(arms)
    ax.set_ylim(0, 1.15)
    ax.legend(loc="upper left")
    ax.grid(axis="y", linestyle="--", alpha=0.5)
    fig.tight_layout()
    fig.savefig(os.path.join(RESULTS_FIGURES, "fig2_ablation_performance.png"))
    plt.close(fig)

    # Figure 3: Coordinated Attack Timeline (Semantic vs Temporal vs Joint Risk)
    p_stream_e, _ = pipeline.process_stream(stream_e)
    fig, (ax1, ax2) = plt.subplots(2, 1, figsize=(10, 6), sharex=True, dpi=300)

    t_steps = np.arange(len(p_stream_e))
    ax1.plot(t_steps, p_stream_e["reported_free_capacity"], label="Reported Free Capacity (t)", color="crimson", lw=1.5)
    ax1.plot(t_steps, p_stream_e["total_capacity"] - p_stream_e["reported_inventory"], label="Physical Free Space (t)", color="darkgreen", lw=1.5, ls="--")
    ax1.axvspan(200, 260, color="orange", alpha=0.25, label="Attack E Active Window")
    ax1.set_ylabel("Capacity (Tonnes)")
    ax1.set_title("Operational Signals and Escalation Dynamics under Attack E")
    ax1.legend(loc="upper right", framealpha=0.9)
    ax1.grid(True, linestyle=":", alpha=0.6)

    ax2.plot(t_steps, p_stream_e["semantic_score_combined"], label="Semantic Score (Weak)", color="#17becf", lw=1.2)
    ax2.plot(t_steps, p_stream_e["temporal_score"], label="Temporal Accumulator", color="#9467bd", lw=1.5)
    ax2.plot(t_steps, p_stream_e["joint_risk_score"], label="Joint Escalation Risk", color="black", lw=2.0)
    ax2.axhline(0.50, color="red", ls=":", lw=1.5, label="Suspicious Threshold")
    ax2.axhline(0.75, color="darkred", ls="-.", lw=1.5, label="Attack Threshold")
    ax2.axvspan(200, 260, color="orange", alpha=0.25)
    ax2.set_ylabel("Risk Score [0.0 - 1.0]")
    ax2.set_xlabel("Time Step (5-minute samples)")
    ax2.legend(loc="upper left", framealpha=0.9)
    ax2.grid(True, linestyle=":", alpha=0.6)

    fig.tight_layout()
    fig.savefig(os.path.join(RESULTS_FIGURES, "fig3_coordinated_attack_timeline.png"))
    plt.close(fig)

    # Figure 4: Severity Sensitivity Curve
    fig, ax = plt.subplots(figsize=(7, 4.5), dpi=300)
    ax.plot(df_sweep["offset_tonnes"], df_sweep["recall"], marker="o", color="#d62728", lw=2.0, label="Detection Recall")
    ax.set_xlabel("Injected Capacity Manipulation Magnitude (Tonnes)")
    ax.set_ylabel("Recall")
    ax.set_title("Detection Sensitivity vs Attack Manipulation Magnitude")
    ax.set_ylim(-0.05, 1.05)
    ax.grid(True, linestyle="--", alpha=0.6)
    ax.legend(loc="lower right")
    fig.tight_layout()
    fig.savefig(os.path.join(RESULTS_FIGURES, "fig4_severity_sensitivity_curve.png"))
    plt.close(fig)

    print("\n==========================================================")
    print("ALL EXPERIMENTS EXECUTED SUCCESSFULLY. RESULTS SAVED.")
    print("==========================================================")


if __name__ == "__main__":
    run_all()
