"""Ablation Study Engine: isolates contribution of semantic, temporal, and structural components."""

from typing import Dict
import numpy as np
import pandas as pd
from src.evaluation.metrics import compute_binary_metrics, compute_temporal_attack_metrics
from src.pipeline import IntegrityDetectionPipeline


class AblationStudyRunner:
    """Evaluates the 5 ablation arms: Arm A, B, C, D, and E."""

    def __init__(self, pipeline: IntegrityDetectionPipeline):
        self.pipeline = pipeline

    def run_ablation(self, eval_df: pd.DataFrame) -> Dict[str, Dict]:
        processed_df, _ = self.pipeline.process_stream(eval_df)
        y_true = processed_df["is_attack"].to_numpy()

        sem = processed_df["semantic_score_combined"].to_numpy()
        temp = processed_df["temporal_score"].to_numpy()
        struct = processed_df["structural_score"].to_numpy()

        thresh = self.pipeline.escalator.tau_suspicious

        # Arm A: ML Anomaly Detection Only
        pred_a = processed_df["ml_anomaly_pred"].to_numpy()

        # Arm B: Semantic Constraints Only
        pred_b = (sem >= thresh).astype(int)

        # Arm C: Semantic + Temporal
        score_c = 0.55 * sem + 0.45 * temp
        pred_c = (score_c >= thresh).astype(int)

        # Arm D: Semantic + Structural
        score_d = 0.70 * sem + 0.30 * struct
        pred_d = (score_d >= thresh).astype(int)

        # Arm E: Semantic + Temporal + Structural (Full Proposed)
        pred_e = processed_df["is_alert"].to_numpy()

        arms = {
            "Arm_A_ML_Only": pred_a,
            "Arm_B_Semantic_Only": pred_b,
            "Arm_C_Semantic_Temporal": pred_c,
            "Arm_D_Semantic_Structural": pred_d,
            "Arm_E_Proposed_Full": pred_e,
        }

        results = {}
        for name, pred in arms.items():
            metrics = compute_binary_metrics(y_true, pred)
            metrics.update(compute_temporal_attack_metrics(y_true, pred))
            results[name] = metrics

        return results
