"""Tests for temporal decay aggregator and structural entity graph."""

import numpy as np
from src.structural_analysis.graph_model import OperationalEntityGraph
from src.temporal_analysis.temporal_aggregator import TemporalAggregator


def test_temporal_aggregator():
    agg = TemporalAggregator(window_samples=12, decay_lambda=0.035)

    # All zeros should return zeros
    zeros = np.zeros(20)
    scores_zeros = agg.compute_temporal_score(zeros)
    assert np.allclose(scores_zeros, 0.0)

    # Sustained violation should increase temporal score over time
    sustained = np.ones(20) * 0.8
    scores_sustained = agg.compute_temporal_score(sustained)
    assert scores_sustained[-1] > scores_sustained[0]
    assert scores_sustained[-1] > 0.7


def test_structural_graph():
    graph = OperationalEntityGraph(warehouse_id="WH_01")

    # Single entity has low relatedness
    assert graph.calculate_structural_relatedness(["WH_01"]) == 0.1

    # Multiple directly connected entities have high relatedness
    score_connected = graph.calculate_structural_relatedness(
        ["WH_01", "OPERATIONAL_LEDGER", "IOT_OCCUPANCY_SENSOR"]
    )
    assert score_connected > 0.40


if __name__ == "__main__":
    test_temporal_aggregator()
    test_structural_graph()
    print("test_temporal_structural passed.")
