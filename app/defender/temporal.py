"""Temporal analysis engine for stateful persistence, frequency, and decay tracking.

Aggregates observations across a sliding window to escalate recurring anomalies
and decay isolated or transient blips.
"""

import collections
import logging
from typing import Deque, Dict, Any
from app.config import settings
from app.defender.models import TemporalResult, SemanticResult, MLResult

logger = logging.getLogger("defender.temporal")


class TemporalEngine:
    """Tracks time-series persistence, frequency, and decay of integrity violations."""

    def __init__(
        self,
        window_size: int = settings.TEMPORAL_WINDOW_SIZE,
        decay_factor: float = settings.TEMPORAL_DECAY_FACTOR,
    ):
        self.window_size = window_size
        self.decay_factor = decay_factor

        # Sliding window history of (step, semantic_score, ml_score, has_violation)
        self.window: Deque[Dict[str, Any]] = collections.deque(maxlen=window_size)
        self.consecutive_violations = 0

    def update(
        self,
        step: int,
        semantic_result: SemanticResult,
        ml_result: MLResult,
    ) -> TemporalResult:
        """Record observation outcomes and calculate updated temporal escalation metrics."""
        has_semantic_violation = len(semantic_result.violated_constraints) > 0
        has_anomaly = ml_result.is_anomaly

        is_violation = has_semantic_violation or (has_anomaly and ml_result.anomaly_score > 0.70)

        # Update consecutive persistence
        if is_violation:
            self.consecutive_violations += 1
        else:
            self.consecutive_violations = 0

        # Record into sliding window
        record = {
            "step": step,
            "semantic_score": semantic_result.semantic_score,
            "ml_score": ml_result.anomaly_score,
            "is_violation": is_violation,
            "violated_constraints": semantic_result.violated_constraints,
        }
        self.window.append(record)

        # Calculate metrics over the sliding window
        total_in_window = len(self.window)
        if total_in_window == 0:
            return TemporalResult(
                temporal_score=0.0,
                persistence=0,
                frequency=0.0,
                recurrence=0,
                window_size=self.window_size,
                status="STABLE",
            )

        recurrence = sum(1 for r in self.window if r["is_violation"])
        frequency = round(recurrence / total_in_window, 2)

        # Recency-weighted decay: newest items have weight 1.0, older items scaled by decay_factor^k
        weighted_sum = 0.0
        max_possible_weight = 0.0
        # Iterate from most recent (index 0) backwards
        for i, item in enumerate(reversed(self.window)):
            weight = self.decay_factor ** i
            if item["is_violation"]:
                severity = max(item["semantic_score"], item["ml_score"])
                weighted_sum += weight * severity
            max_possible_weight += weight

        recency_weighted_score = (
            round(weighted_sum / max_possible_weight, 3) if max_possible_weight > 0 else 0.0
        )

        # Persistence amplifier: consecutive violations rapidly escalate the temporal score
        persistence_bonus = min(0.35, self.consecutive_violations * 0.10)

        temporal_score = round(min(1.0, recency_weighted_score + persistence_bonus), 2)

        # Classification of temporal state
        if temporal_score >= 0.50 or self.consecutive_violations >= 3:
            status = "ESCALATING"
        elif temporal_score >= 0.20 or recurrence >= 2:
            status = "ELEVATED"
        else:
            status = "STABLE"

        return TemporalResult(
            temporal_score=temporal_score,
            persistence=self.consecutive_violations,
            frequency=frequency,
            recurrence=recurrence,
            window_size=self.window_size,
            status=status,
            details={
                "recency_score": recency_weighted_score,
                "consecutive_steps": self.consecutive_violations,
                "recorded_steps": total_in_window,
            },
        )

    def reset(self) -> None:
        """Reset temporal state buffer."""
        self.window.clear()
        self.consecutive_violations = 0
