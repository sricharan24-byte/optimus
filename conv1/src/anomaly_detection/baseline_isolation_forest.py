"""Baseline ML Anomaly Detection using Isolation Forest (referencing Pathak et al., ICC 2021)."""

from typing import List, Tuple
import numpy as np
import pandas as pd
from sklearn.ensemble import IsolationForest


class BaselineIsolationForestDetector:
    """Unsupervised anomaly detector representing the ML baseline from existing literature."""

    DEFAULT_FEATURES = [
        "temperature_c",
        "humidity_pct",
        "telemetry_occupancy",
        "reported_free_capacity",
        "reported_inventory",
    ]

    def __init__(self, contamination: float = 0.02, random_state: int = 42, features: List[str] = None):
        self.features = features or self.DEFAULT_FEATURES
        self.model = IsolationForest(
            n_estimators=100,
            contamination=contamination,
            random_state=random_state,
            n_jobs=-1,
        )
        self.is_fitted = False

    def fit(self, normal_df: pd.DataFrame) -> "BaselineIsolationForestDetector":
        """Trains the isolation forest on normal operating data."""
        x = normal_df[self.features].to_numpy()
        self.model.fit(x)
        self.is_fitted = True
        return self

    def score(self, df: pd.DataFrame) -> Tuple[np.ndarray, np.ndarray]:
        """Calculates normalized anomaly score [0, 1] and binary anomaly predictions.
        Higher score indicates higher anomaly likelihood.
        """
        if not self.is_fitted:
            raise RuntimeError("Model must be fitted before scoring.")

        x = df[self.features].to_numpy()
        # decision_function returns negative for anomalies, positive for normal
        raw_scores = self.model.decision_function(x)
        # Normalize to [0, 1] inverted where 1 is highest anomaly
        # Typically raw_scores lie in [-0.5, 0.5]
        norm_scores = np.clip(0.5 - raw_scores, 0.0, 1.0)
        binary_pred = (self.model.predict(x) == -1).astype(int)

        return norm_scores, binary_pred
