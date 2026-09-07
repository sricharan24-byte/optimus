"""Explainable Alert Generator: generates multi-evidence diagnostic reports for security operators."""

from dataclasses import asdict, dataclass
from datetime import datetime
from typing import Any, Dict, List, Optional
from src.escalation.joint_escalator import EscalationDecision, JointEscalationEngine
from src.semantic_constraints.engine import ConstraintViolation


@dataclass
class ExplainableAlert:
    alert_id: str
    timestamp: str
    warehouse_id: str
    alert_level: str
    joint_risk_score: float
    evidence_summary: List[str]
    violated_constraints: List[Dict[str, Any]]
    affected_entities: List[str]
    temporal_context: Dict[str, Any]
    structural_context: Dict[str, Any]
    conclusion: str

    def to_dict(self) -> Dict[str, Any]:
        return asdict(self)

    def to_text_report(self) -> str:
        lines = [
            f"=== SECURITY ALERT: {self.alert_level} ===",
            f"Alert ID:     {self.alert_id}",
            f"Timestamp:    {self.timestamp}",
            f"Facility:     {self.warehouse_id}",
            f"Joint Risk:   {self.joint_risk_score:.3f} / 1.000",
            "",
            "Corroborating Evidence:",
        ]
        for idx, ev in enumerate(self.evidence_summary, 1):
            lines.append(f"  {idx}. {ev}")
        lines.append("")
        lines.append(f"Conclusion: {self.conclusion}")
        lines.append("=" * 45)
        return "\n".join(lines)


class ExplainabilityGenerator:
    """Translates raw mathematical escalation states into explainable security audit reports."""

    def __init__(self, warehouse_id: str = "WH_01"):
        self.warehouse_id = warehouse_id
        self._alert_counter = 0

    def generate_alert(
        self,
        timestamp: str,
        decision: EscalationDecision,
        violations: List[ConstraintViolation],
        active_entities: List[str],
        recent_violation_count: int,
        window_minutes: int = 60,
    ) -> Optional[ExplainableAlert]:
        if not decision.is_attack_alert:
            return None

        self._alert_counter += 1
        alert_id = f"ALT-{datetime.now().strftime('%Y%m%d')}-{self._alert_counter:04d}"

        evidence = []
        violated_details = []

        # 1. Semantic violations
        for v in violations:
            if v.violation_score > 0.15:
                evidence.append(f"[{v.constraint_id}] {v.description} (Severity: {v.violation_score:.2f})")
                violated_details.append(
                    {
                        "constraint_id": v.constraint_id,
                        "name": v.name,
                        "score": v.violation_score,
                        "observed": v.observed_value,
                        "expected": v.expected_value,
                    }
                )

        # 2. Temporal correlation
        evidence.append(
            f"Temporal recurrence: {recent_violation_count} active violations observed in prior {window_minutes}m window "
            f"(Temporal Score: {decision.temporal_score:.2f})."
        )

        # 3. Structural correlation
        evidence.append(
            f"Structural correlation: Discrepancies span {len(active_entities)} topologically linked entities: "
            f"{', '.join(active_entities)} (Structural Score: {decision.structural_score:.2f})."
        )

        # 4. Joint Synthesis
        evidence.append(
            f"Joint escalation score reached {decision.joint_risk_score:.2f}, crossing critical threshold."
        )

        conclusion = (
            "Potential coordinated operational-data integrity attack detected across distributed telemetry "
            "and business ledgers."
            if decision.alert_level == JointEscalationEngine.LEVEL_COORDINATED_ATTACK
            else "Suspicious multi-source operational inconsistency requiring manual security verification."
        )

        return ExplainableAlert(
            alert_id=alert_id,
            timestamp=str(timestamp),
            warehouse_id=self.warehouse_id,
            alert_level=decision.alert_level,
            joint_risk_score=decision.joint_risk_score,
            evidence_summary=evidence,
            violated_constraints=violated_details,
            affected_entities=active_entities,
            temporal_context={"recent_count": recent_violation_count, "temporal_score": decision.temporal_score},
            structural_context={"entities": active_entities, "structural_score": decision.structural_score},
            conclusion=conclusion,
        )
