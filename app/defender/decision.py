"""Joint security decision engine combining multi-stage evidence.

Synthesizes ML anomaly scores, semantic constraint violations, temporal persistence,
and structural graph correlations into a final verified security classification.
"""

import logging
from datetime import datetime, timezone
from typing import Dict, Any

from app.defender.models import (
    MLResult,
    SemanticResult,
    TemporalResult,
    StructuralResult,
    SecurityDecision,
)

logger = logging.getLogger("defender.decision")


class JointDecisionEngine:
    """Combines multi-stage defender evidence into a grounded security classification."""

    def __init__(
        self,
        weight_semantic: float = 0.50,
        weight_temporal: float = 0.20,
        weight_structural: float = 0.15,
        weight_ml: float = 0.15,
    ):
        self.w_semantic = weight_semantic
        self.w_temporal = weight_temporal
        self.w_structural = weight_structural
        self.w_ml = weight_ml

    def decide(
        self,
        ml: MLResult,
        semantic: SemanticResult,
        temporal: TemporalResult,
        structural: StructuralResult,
    ) -> SecurityDecision:
        """Compute the joint security decision from stage outputs."""
        # 1. Compute weighted composite risk score in [0.0, 1.0]
        fused_risk = (
            self.w_semantic * semantic.semantic_score
            + self.w_temporal * temporal.temporal_score
            + self.w_structural * structural.structural_score
            + self.w_ml * ml.anomaly_score
        )
        risk_score = round(min(1.0, max(0.0, fused_risk)), 3)
        integrity_score = round(max(0.0, min(100.0, (1.0 - risk_score) * 100.0)), 1)

        # 2. Rule-grounded deterministic classification
        has_semantic_violation = len(semantic.violated_constraints) > 0
        has_semantic_warning = any(c.status == "WARNING" for c in semantic.constraints)

        if has_semantic_violation:
            # Semantic violations indicate a breach of operational/physical reality
            if structural.status == "MULTI_SOURCE" and temporal.status in ("ELEVATED", "ESCALATING"):
                classification = "COORDINATED_ATTACK"
                explanation = (
                    f"COORDINATED ATTACK DETECTED: Semantic violations ({', '.join(semantic.violated_constraints)}) "
                    f"span multiple organizational subsystems ({', '.join(structural.affected_nodes)}) "
                    f"with persistent temporal escalation (recurrence: {temporal.recurrence})."
                )
            else:
                classification = "POTENTIAL_ATTACK"
                violation_reasons = [c.message for c in semantic.constraints if c.status == "VIOLATED"]
                explanation = (
                    f"POTENTIAL DATA INTEGRITY ATTACK: Inconsistencies confirmed in operational records. "
                    f"{' '.join(violation_reasons)}"
                )

        elif has_semantic_warning:
            # Operational values are mathematically consistent, but environmental envelope is abnormal
            if ml.is_anomaly or temporal.status in ("ELEVATED", "ESCALATING"):
                classification = "SUSPICIOUS"
                explanation = (
                    f"SUSPICIOUS ACTIVITY: Operating conditions deviate from historical envelope "
                    f"with elevated temporal or ML anomaly markers (ML score: {ml.anomaly_score:.2f})."
                )
            else:
                classification = "LOW"
                explanation = (
                    f"LOW RISK: Environmental drift detected (Temp/Humidity) while operational "
                    f"inventory and capacity ledgers remain consistent."
                )

        elif ml.is_anomaly:
            # Pure statistical outlier without semantic violation
            if temporal.status in ("ELEVATED", "ESCALATING"):
                classification = "SUSPICIOUS"
                explanation = (
                    f"SUSPICIOUS OBSERVATION: Statistical ML detector flagged an outlier "
                    f"(score: {ml.anomaly_score:.2f}) with recurring temporal patterns."
                )
            else:
                classification = "LOW"
                explanation = (
                    f"LOW RISK: Statistically unusual pattern detected by ML (score: {ml.anomaly_score:.2f}), "
                    f"but all physical and semantic constraints pass."
                )

        else:
            # Clean current observation
            if temporal.status == "ESCALATING":
                classification = "SUSPICIOUS"
                explanation = (
                    f"SUSPICIOUS (POST-INCIDENT): Current observation is consistent, but temporal "
                    f"window reflects persistent recent violations (score: {temporal.temporal_score:.2f})."
                )
            elif temporal.status == "ELEVATED":
                classification = "LOW"
                explanation = (
                    f"LOW (RECOVERY): Current observation is consistent; system in cooldown as recent "
                    f"violation markers decay (score: {temporal.temporal_score:.2f})."
                )
            else:
                classification = "NORMAL"
                explanation = (
                    f"NORMAL: Operational records, IoT telemetry, and shipment ledgers "
                    f"are internally consistent and satisfy all integrity constraints."
                )

        contributing_evidence = {
            "ml": {
                "score": ml.anomaly_score,
                "status": ml.status,
                "is_anomaly": ml.is_anomaly,
            },
            "semantic": {
                "score": semantic.semantic_score,
                "status": semantic.status,
                "violated_constraints": semantic.violated_constraints,
            },
            "temporal": {
                "score": temporal.temporal_score,
                "status": temporal.status,
                "persistence": temporal.persistence,
                "recurrence": temporal.recurrence,
            },
            "structural": {
                "score": structural.structural_score,
                "status": structural.status,
                "affected_nodes": structural.affected_nodes,
            },
        }

        return SecurityDecision(
            classification=classification,
            risk_score=risk_score,
            integrity_score=integrity_score,
            contributing_evidence=contributing_evidence,
            explanation=explanation,
            timestamp=datetime.now(timezone.utc).isoformat(),
        )
