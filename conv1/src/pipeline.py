"""Unified end-to-end detection pipeline integrating all security modules."""

from typing import List, Optional, Tuple
import numpy as np
import pandas as pd
from src.alerting.explainability import ExplainabilityGenerator, ExplainableAlert
from src.anomaly_detection.baseline_isolation_forest import BaselineIsolationForestDetector
from src.escalation.joint_escalator import JointEscalationEngine
from src.semantic_constraints.engine import HistoricalProfile, SemanticConstraintEngine
from src.structural_analysis.graph_model import OperationalEntityGraph
from src.temporal_analysis.temporal_aggregator import TemporalAggregator


class IntegrityDetectionPipeline:
    """Orchestrates ingestion, constraint verification, ML baseline, temporal/structural correlation, and alerting."""

    def __init__(
        self,
        warehouse_id: str = "WH_01",
        total_capacity: float = 50.0,
        c1_tol: float = 1.5,
        c2_tol: float = 1.0,
        window_samples: int = 12,
        decay_lambda: float = 0.035,
        threshold_low: float = 0.20,
        threshold_suspicious: float = 0.40,
        threshold_attack: float = 0.70,
    ):
        self.warehouse_id = warehouse_id
        self.total_capacity = total_capacity

        self.constraint_engine = SemanticConstraintEngine(total_capacity=total_capacity, c1_tolerance=c1_tol, c2_tolerance=c2_tol)
        self.ml_detector = BaselineIsolationForestDetector()
        self.temporal_agg = TemporalAggregator(window_samples=window_samples, decay_lambda=decay_lambda)
        self.entity_graph = OperationalEntityGraph(warehouse_id=warehouse_id)
        self.escalator = JointEscalationEngine(
            threshold_low=threshold_low,
            threshold_suspicious=threshold_suspicious,
            threshold_attack=threshold_attack,
        )
        self.explainer = ExplainabilityGenerator(warehouse_id=warehouse_id)
        self.is_calibrated = False

    def calibrate(self, normal_df: pd.DataFrame):
        """Fits historical profile and ML detector from clean normal data."""
        hist_profile = HistoricalProfile.fit_from_normal(normal_df)
        self.constraint_engine.set_historical_profile(hist_profile)
        self.ml_detector.fit(normal_df)
        self.is_calibrated = True

    def process_stream(self, df: pd.DataFrame) -> Tuple[pd.DataFrame, List[ExplainableAlert]]:
        """Executes the full multi-tier detection pipeline on input stream."""
        if not self.is_calibrated:
            self.calibrate(df)

        # 1. Semantic Constraint Evaluation
        eval_df, violations_by_row = self.constraint_engine.evaluate_frame(df)
        semantic_scores = eval_df["semantic_score_combined"].to_numpy()

        # 2. Supporting ML Anomaly Detection Baseline
        ml_scores, ml_preds = self.ml_detector.score(df)
        eval_df["ml_anomaly_score"] = ml_scores
        eval_df["ml_anomaly_pred"] = ml_preds

        # 3. Temporal Correlation
        temporal_scores = self.temporal_agg.compute_temporal_score(semantic_scores)
        eval_df["temporal_score"] = temporal_scores

        # 4. Structural Correlation & Entity Graph Analysis
        structural_scores = np.zeros(len(df))
        active_entities_list = []
        for i, row_viols in enumerate(violations_by_row):
            active_ents = []
            for v in row_viols:
                if v.violation_score > 0.15:
                    active_ents.extend(v.entities_involved)
            unique_ents = list(set(active_ents))
            active_entities_list.append(unique_ents)
            structural_scores[i] = self.entity_graph.calculate_structural_relatedness(unique_ents)

        eval_df["structural_score"] = structural_scores

        # 5. Joint Escalation
        decisions = self.escalator.evaluate_series(semantic_scores, temporal_scores, structural_scores)
        eval_df["joint_risk_score"] = [d.joint_risk_score for d in decisions]
        eval_df["alert_level"] = [d.alert_level for d in decisions]
        eval_df["is_alert"] = [int(d.is_attack_alert) for d in decisions]

        # 6. Explainable Alerts Generation
        alerts = []
        for i, d in enumerate(decisions):
            if d.is_attack_alert:
                recent_count = int(np.sum(semantic_scores[max(0, i - 11) : i + 1] > 0.15))
                alert = self.explainer.generate_alert(
                    timestamp=str(eval_df.iloc[i]["timestamp"]),
                    decision=d,
                    violations=violations_by_row[i],
                    active_entities=active_entities_list[i],
                    recent_violation_count=recent_count,
                )
                if alert:
                    alerts.append(alert)

        return eval_df, alerts
