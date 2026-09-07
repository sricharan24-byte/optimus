"""Semantic Constraint Engine: evaluates physical, operational, and historical invariants."""

from dataclasses import dataclass, field
from typing import Dict, List, Optional, Tuple
import numpy as np
import pandas as pd


@dataclass
class ConstraintViolation:
    constraint_id: str
    name: str
    violation_score: float  # [0.0, 1.0]
    deviation: float
    observed_value: dict
    expected_value: dict
    entities_involved: List[str]
    description: str


@dataclass
class HistoricalProfile:
    free_capacity_median: float
    free_capacity_mad: float
    free_capacity_p10: float
    free_capacity_p90: float
    inventory_median: float
    inventory_mad: float
    inventory_p10: float
    inventory_p90: float

    @classmethod
    def fit_from_normal(cls, df: pd.DataFrame) -> "HistoricalProfile":
        fc = df["reported_free_capacity"].to_numpy()
        inv = df["reported_inventory"].to_numpy()
        fc_med = float(np.median(fc))
        inv_med = float(np.median(inv))
        return cls(
            free_capacity_median=fc_med,
            free_capacity_mad=float(np.median(np.abs(fc - fc_med))) or 1.0,
            free_capacity_p10=float(np.percentile(fc, 10)),
            free_capacity_p90=float(np.percentile(fc, 90)),
            inventory_median=inv_med,
            inventory_mad=float(np.median(np.abs(inv - inv_med))) or 1.0,
            inventory_p10=float(np.percentile(inv, 10)),
            inventory_p90=float(np.percentile(inv, 90)),
        )


class SemanticConstraintEngine:
    """Core verification engine evaluating heterogeneous cross-source invariants."""

    def __init__(
        self,
        total_capacity: float = 50.0,
        c1_tolerance: float = 1.5,
        c2_tolerance: float = 1.0,
        weights: Optional[Dict[str, float]] = None,
    ):
        self.total_capacity = total_capacity
        self.c1_tol = c1_tolerance
        self.c2_tol = c2_tolerance
        self.weights = weights or {"C1_CAPACITY": 0.45, "C2_INVENTORY": 0.35, "C3_HISTORICAL": 0.20}
        self.history_profile: Optional[HistoricalProfile] = None

    def set_historical_profile(self, profile: HistoricalProfile):
        self.history_profile = profile

    def evaluate_c1_capacity(self, row: pd.Series) -> ConstraintViolation:
        """C1: Capacity Consistency Invariant.
        Total Capacity ≈ Reported Free Capacity + Occupied Space (cross-checked against inventory & IoT telemetry).
        """
        rep_free = float(row["reported_free_capacity"])
        rep_inv = float(row["reported_inventory"])
        occ_telemetry = float(row.get("telemetry_occupancy", rep_inv / self.total_capacity))
        occ_tonnes = occ_telemetry * self.total_capacity

        sum_inv = rep_free + rep_inv
        sum_telemetry = rep_free + occ_tonnes

        dev_inv = abs(sum_inv - self.total_capacity)
        dev_occ = abs(sum_telemetry - self.total_capacity)
        max_dev = max(dev_inv, dev_occ)

        # Scale deviation to [0, 1] beyond tolerance
        if max_dev <= self.c1_tol:
            score = 0.0
        else:
            scale = self.total_capacity * 0.4  # e.g., 20 tonnes deviation saturates to 1.0
            score = float(np.clip((max_dev - self.c1_tol) / scale, 0.0, 1.0))

        entities = [row.get("warehouse_id", "WH_01"), "OPERATIONAL_LEDGER", "IOT_OCCUPANCY_SENSOR"]

        return ConstraintViolation(
            constraint_id="C1_CAPACITY",
            name="Physical Capacity Consistency",
            violation_score=score,
            deviation=max_dev,
            observed_value={"reported_free_t": rep_free, "reported_inv_t": rep_inv, "occ_sensor_t": occ_tonnes},
            expected_value={"total_capacity_t": self.total_capacity, "expected_free_t": max(0.0, self.total_capacity - rep_inv)},
            entities_involved=entities,
            description=f"Claimed free space ({rep_free:.1f}t) conflicts with total capacity ({self.total_capacity:.1f}t) and current inventory/occupancy.",
        )

    def evaluate_c2_inventory(self, curr_row: pd.Series, prev_row: Optional[pd.Series]) -> ConstraintViolation:
        """C2: Inventory Reconciliation Invariant.
        Current Inventory ≈ Previous Inventory + Inbound Movements - Outbound Movements.
        """
        entities = [curr_row.get("warehouse_id", "WH_01"), "INVENTORY_LEDGER", "DISPATCH_INBOUND_GATEWAY"]
        if prev_row is None:
            return ConstraintViolation("C2_INVENTORY", "Inventory Reconciliation", 0.0, 0.0, {}, {}, entities, "Initial record.")

        prev_inv = float(prev_row["reported_inventory"])
        curr_inv = float(curr_row["reported_inventory"])
        inbound = float(curr_row.get("inbound_qty", 0.0))
        outbound = float(curr_row.get("outbound_qty", 0.0))

        expected_inv = max(0.0, prev_inv + inbound - outbound)
        dev = abs(curr_inv - expected_inv)

        if dev <= self.c2_tol:
            score = 0.0
        else:
            scale = 15.0  # 15 tonnes unexplained shift saturates to 1.0
            score = float(np.clip((dev - self.c2_tol) / scale, 0.0, 1.0))

        return ConstraintViolation(
            constraint_id="C2_INVENTORY",
            name="Inventory Movement Reconciliation",
            violation_score=score,
            deviation=dev,
            observed_value={"current_reported_inv_t": curr_inv},
            expected_value={"expected_reconciled_inv_t": expected_inv, "inbound_t": inbound, "outbound_t": outbound},
            entities_involved=entities,
            description=f"Inventory shift ({prev_inv:.1f}t -> {curr_inv:.1f}t) cannot be reconciled with inbound ({inbound:.1f}t) or outbound ({outbound:.1f}t) logs.",
        )

    def evaluate_c3_historical(self, row: pd.Series) -> ConstraintViolation:
        """C3: Historical Operating Envelope Invariant.
        Verifies reported values against robust historical percentile bounds.
        """
        entities = [row.get("warehouse_id", "WH_01"), "HISTORICAL_BASELINE_PROFILE"]
        if self.history_profile is None:
            return ConstraintViolation("C3_HISTORICAL", "Historical Envelope Verification", 0.0, 0.0, {}, {}, entities, "No history.")

        rep_free = float(row["reported_free_capacity"])
        p10 = self.history_profile.free_capacity_p10
        p90 = self.history_profile.free_capacity_p90
        iqr = max(1.0, p90 - p10)

        dev = 0.0
        if rep_free < p10:
            dev = p10 - rep_free
        elif rep_free > p90:
            dev = rep_free - p90

        score = float(np.clip(dev / (2.0 * iqr), 0.0, 1.0))

        return ConstraintViolation(
            constraint_id="C3_HISTORICAL",
            name="Historical Operating Envelope",
            violation_score=score,
            deviation=dev,
            observed_value={"reported_free_t": rep_free},
            expected_value={"historical_envelope_p10_p90": [p10, p90], "historical_median_t": self.history_profile.free_capacity_median},
            entities_involved=entities,
            description=f"Reported value ({rep_free:.1f}t) falls significantly outside historical operating envelope [{p10:.1f}t, {p90:.1f}t].",
        )

    def evaluate_frame(self, df: pd.DataFrame) -> Tuple[pd.DataFrame, List[List[ConstraintViolation]]]:
        """Evaluates semantic constraints for each row in the given time-series DataFrame."""
        violations_all = []
        c1_scores, c2_scores, c3_scores = [], [], []
        aggregate_scores = []

        w1 = self.weights.get("C1_CAPACITY", 0.45)
        w2 = self.weights.get("C2_INVENTORY", 0.35)
        w3 = self.weights.get("C3_HISTORICAL", 0.20)
        norm_factor = w1 + w2 + w3

        for i in range(len(df)):
            curr_row = df.iloc[i]
            prev_row = df.iloc[i - 1] if i > 0 else None

            v1 = self.evaluate_c1_capacity(curr_row)
            v2 = self.evaluate_c2_inventory(curr_row, prev_row)
            v3 = self.evaluate_c3_historical(curr_row)

            violations_all.append([v1, v2, v3])
            c1_scores.append(v1.violation_score)
            c2_scores.append(v2.violation_score)
            c3_scores.append(v3.violation_score)

            # Combined instantaneous semantic violation severity
            combined = (w1 * v1.violation_score + w2 * v2.violation_score + w3 * v3.violation_score) / norm_factor
            aggregate_scores.append(combined)

        res_df = df.copy()
        res_df["semantic_score_c1"] = c1_scores
        res_df["semantic_score_c2"] = c2_scores
        res_df["semantic_score_c3"] = c3_scores
        res_df["semantic_score_combined"] = aggregate_scores

        return res_df, violations_all
