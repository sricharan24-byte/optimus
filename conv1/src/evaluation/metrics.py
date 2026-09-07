"""Evaluation metrics for security and attack detection performance."""

from typing import Dict, List, Optional
import numpy as np


def compute_binary_metrics(y_true: np.ndarray, y_pred: np.ndarray) -> Dict[str, float]:
    """Computes standard precision, recall, F1, FPR, and FNR."""
    y_true = np.asarray(y_true).astype(int)
    y_pred = np.asarray(y_pred).astype(int)

    tp = int(np.sum((y_true == 1) & (y_pred == 1)))
    fp = int(np.sum((y_true == 0) & (y_pred == 1)))
    fn = int(np.sum((y_true == 1) & (y_pred == 0)))
    tn = int(np.sum((y_true == 0) & (y_pred == 0)))

    precision = tp / (tp + fp) if (tp + fp) > 0 else 0.0
    recall = tp / (tp + fn) if (tp + fn) > 0 else 0.0
    f1 = (2 * precision * recall / (precision + recall)) if (precision + recall) > 0 else 0.0
    fpr = fp / (fp + tn) if (fp + tn) > 0 else 0.0
    fnr = fn / (fn + tp) if (fn + tp) > 0 else 0.0

    return {
        "tp": tp,
        "fp": fp,
        "fn": fn,
        "tn": tn,
        "precision": round(float(precision), 4),
        "recall": round(float(recall), 4),
        "f1_score": round(float(f1), 4),
        "false_positive_rate": round(float(fpr), 4),
        "false_negative_rate": round(float(fnr), 4),
    }


def compute_temporal_attack_metrics(
    y_true: np.ndarray,
    y_pred: np.ndarray,
    sample_interval_min: float = 5.0,
) -> Dict[str, Optional[float]]:
    """Calculates attack detection delay and time-to-escalation."""
    y_true = np.asarray(y_true).astype(int)
    y_pred = np.asarray(y_pred).astype(int)

    attack_indices = np.where(y_true == 1)[0]
    if len(attack_indices) == 0:
        return {"detection_delay_min": None, "detected": False}

    first_attack_idx = attack_indices[0]
    # Find first true positive (y_pred == 1 at or after first attack index while attack is active)
    detected_indices = np.where((y_pred == 1) & (y_true == 1))[0]

    if len(detected_indices) > 0:
        first_detection_idx = detected_indices[0]
        delay_steps = max(0, first_detection_idx - first_attack_idx)
        delay_min = delay_steps * sample_interval_min
        return {"detection_delay_min": round(delay_min, 2), "detected": True, "delay_steps": delay_steps}

    return {"detection_delay_min": None, "detected": False, "delay_steps": None}
