"""Temporal Aggregation Module: tracks violation recurrence, frequency, and persistence over a sliding window."""

import numpy as np
import pandas as pd


class TemporalAggregator:
    """Aggregates instantaneous semantic violations over sliding time window W with exponential decay."""

    def __init__(self, window_samples: int = 12, decay_lambda: float = 0.035, noise_floor: float = 0.05):
        self.window = window_samples
        self.decay_lambda = decay_lambda
        self.noise_floor = noise_floor

        # Precompute decay weights for the window [k = 0 ... W-1] where 0 is most recent
        steps = np.arange(self.window)
        weights = np.exp(-self.decay_lambda * steps)
        self.norm_weights = weights / np.sum(weights)

    def compute_temporal_score(self, scores: np.ndarray) -> np.ndarray:
        """Computes normalized temporal risk score [0, 1] for a sequence of instantaneous violation scores.

        Formula:
            S_decay = weighted sum with exponential decay over W
            F_freq = fraction of steps in W exceeding noise floor
            P_persist = normalized consecutive run-length of active violations
            S_temporal = 0.50 * S_decay + 0.30 * F_freq + 0.20 * P_persist
        """
        n = len(scores)
        temporal_scores = np.zeros(n)
        active_counts = np.zeros(n)

        for i in range(n):
            start_idx = max(0, i - self.window + 1)
            window_slice = scores[start_idx : i + 1]
            w_len = len(window_slice)

            # Reversing so index 0 is most recent
            rev_slice = window_slice[::-1]
            sub_weights = self.norm_weights[:w_len] / np.sum(self.norm_weights[:w_len])

            s_decay = float(np.sum(rev_slice * sub_weights))
            non_zero_count = int(np.sum(window_slice > self.noise_floor))
            active_counts[i] = non_zero_count
            f_freq = non_zero_count / float(self.window)

            # Persistence: consecutive run length from current step backward
            consec = 0
            for val in rev_slice:
                if val > self.noise_floor:
                    consec += 1
                else:
                    break
            p_persist = min(1.0, consec / (self.window / 2.0))

            t_score = np.clip(0.50 * s_decay + 0.30 * f_freq + 0.20 * p_persist, 0.0, 1.0)
            temporal_scores[i] = t_score

        return temporal_scores
