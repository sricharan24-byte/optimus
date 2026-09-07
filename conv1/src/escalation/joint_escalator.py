"""Joint Escalation Engine: synthesizes semantic, temporal, and structural evidence."""

from dataclasses import dataclass
from typing import Dict, List, Tuple
import numpy as np


@dataclass
class EscalationDecision:
    joint_risk_score: float  # [0.0, 1.0]
    alert_level: str  # NORMAL, LOW_LEVEL_INCONSISTENCY, SUSPICIOUS, POTENTIAL_COORDINATED_ATTACK
    semantic_score: float
    temporal_score: float
    structural_score: float
    is_attack_alert: bool


class JointEscalationEngine:
    """Combines heterogeneous security evidence into a unified, calibrated decision score."""

    LEVEL_NORMAL = "NORMAL"
    LEVEL_INCONSISTENCY = "LOW_LEVEL_INCONSISTENCY"
    LEVEL_SUSPICIOUS = "SUSPICIOUS"
    LEVEL_COORDINATED_ATTACK = "POTENTIAL_COORDINATED_ATTACK"

    def __init__(
        self,
        weight_semantic: float = 0.45,
        weight_temporal: float = 0.35,
        weight_structural: float = 0.20,
        threshold_low: float = 0.20,
        threshold_suspicious: float = 0.40,
        threshold_attack: float = 0.70,
    ):
        total_w = weight_semantic + weight_temporal + weight_structural
        self.w_sem = weight_semantic / total_w
        self.w_temp = weight_temporal / total_w
        self.w_struct = weight_structural / total_w

        self.tau_low = threshold_low
        self.tau_suspicious = threshold_suspicious
        self.tau_attack = threshold_attack

    def evaluate_step(
        self,
        semantic_score: float,
        temporal_score: float,
        structural_score: float,
    ) -> EscalationDecision:
        """Evaluates instantaneous joint risk score and maps to alert level."""
        joint_score = float(
            np.clip(
                self.w_sem * semantic_score + self.w_temp * temporal_score + self.w_struct * structural_score,
                0.0,
                1.0,
            )
        )

        if joint_score >= self.tau_attack:
            level = self.LEVEL_COORDINATED_ATTACK
            is_alert = True
        elif joint_score >= self.tau_suspicious:
            level = self.LEVEL_SUSPICIOUS
            is_alert = True
        elif joint_score >= self.tau_low:
            level = self.LEVEL_INCONSISTENCY
            is_alert = False
        else:
            level = self.LEVEL_NORMAL
            is_alert = False

        return EscalationDecision(
            joint_risk_score=joint_score,
            alert_level=level,
            semantic_score=semantic_score,
            temporal_score=temporal_score,
            structural_score=structural_score,
            is_attack_alert=is_alert,
        )

    def evaluate_series(
        self,
        semantic_scores: np.ndarray,
        temporal_scores: np.ndarray,
        structural_scores: np.ndarray,
    ) -> List[EscalationDecision]:
        """Vectorized execution across entire time series."""
        n = len(semantic_scores)
        decisions = []
        for i in range(n):
            d = self.evaluate_step(
                float(semantic_scores[i]),
                float(temporal_scores[i]),
                float(structural_scores[i]),
            )
            decisions.append(d)
        return decisions
