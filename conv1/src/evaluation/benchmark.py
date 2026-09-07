"""Benchmark evaluation: compares Baselines 1, 2, 3 against the Proposed Pipeline."""

from typing import Dict
import numpy as np
import pandas as pd
from src.evaluation.metrics import compute_binary_metrics, compute_temporal_attack_metrics
from src.pipeline import IntegrityDetectionPipeline


class BenchmarkEvaluator:
    """Runs standard baselines and proposed system across evaluation datasets."""

    def __init__(self, pipeline: IntegrityDetectionPipeline):
        self.pipeline = pipeline

    def evaluate_baseline_1_threshold(self, df: pd.DataFrame) -> np.ndarray:
        """Baseline 1: Static threshold and boundary checks."""
        tot = self.pipeline.total_capacity
        p_free = (df["reported_free_capacity"] < 0.0) | (df["reported_free_capacity"] > tot)
        p_inv = (df["reported_inventory"] < 0.0) | (df["reported_inventory"] > tot)
        p_temp = (df["temperature_c"] < 0.0) | (df["temperature_c"] > 10.0)
        p_hum = (df["humidity_pct"] < 60.0) | (df["humidity_pct"] > 100.0)
        preds = (p_free | p_inv | p_temp | p_hum).astype(int).to_numpy()
        return preds

    def run_benchmark(self, eval_df: pd.DataFrame) -> Dict[str, Dict]:
        """Runs all comparison baselines and proposed method, returning metrics dictionary."""
        processed_df, _ = self.pipeline.process_stream(eval_df)
        y_true = processed_df["is_attack"].to_numpy()

        # 1. Baseline 1: Rule/Threshold
        y_pred_b1 = self.evaluate_baseline_1_threshold(processed_df)
        m_b1 = compute_binary_metrics(y_true, y_pred_b1)
        m_b1.update(compute_temporal_attack_metrics(y_true, y_pred_b1))

        # 2. Baseline 2: ML Isolation Forest
        y_pred_b2 = processed_df["ml_anomaly_pred"].to_numpy()
        m_b2 = compute_binary_metrics(y_true, y_pred_b2)
        m_b2.update(compute_temporal_attack_metrics(y_true, y_pred_b2))

        # 3. Baseline 3: Semantic Constraints Only (evaluated at same decision threshold)
        thresh = self.pipeline.escalator.tau_suspicious
        y_pred_b3 = (processed_df["semantic_score_combined"] >= thresh).astype(int).to_numpy()
        m_b3 = compute_binary_metrics(y_true, y_pred_b3)
        m_b3.update(compute_temporal_attack_metrics(y_true, y_pred_b3))

        # 4. Proposed Method: Joint Temporal & Structural Escalation
        y_pred_proposed = processed_df["is_alert"].to_numpy()
        m_prop = compute_binary_metrics(y_true, y_pred_proposed)
        m_prop.update(compute_temporal_attack_metrics(y_true, y_pred_proposed))

        return {
            "Baseline_1_Threshold": m_b1,
            "Baseline_2_IsolationForest": m_b2,
            "Baseline_3_SemanticOnly": m_b3,
            "Proposed_JointEscalation": m_prop,
        }
