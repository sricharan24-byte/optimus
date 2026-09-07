"""Tests for synthetic dataset generator and physical consistency."""

import pandas as pd
from src.data_generation.generator import SimulationConfig, generate_normal_stream


def test_generator_deterministic():
    df1 = generate_normal_stream(num_samples=100, seed=123)
    df2 = generate_normal_stream(num_samples=100, seed=123)
    assert len(df1) == 100
    assert df1.equals(df2), "Generator should be strictly deterministic for identical seed."


def test_generator_physical_invariants():
    cfg = SimulationConfig(total_capacity=50.0)
    df = generate_normal_stream(num_samples=200, seed=42, config=cfg)

    # In normal data, reported_free + reported_inventory should roughly equal total capacity
    sum_space = df["reported_free_capacity"] + df["reported_inventory"]
    max_discrepancy = (sum_space - cfg.total_capacity).abs().max()
    assert max_discrepancy < 2.0, f"Normal physical discrepancy too high: {max_discrepancy}"

    # Temperature and humidity within physical bounds
    assert (df["temperature_c"] > 1.0).all() and (df["temperature_c"] < 6.0).all()
    assert (df["humidity_pct"] > 75.0).all() and (df["humidity_pct"] < 100.0).all()


if __name__ == "__main__":
    test_generator_deterministic()
    test_generator_physical_invariants()
    print("test_generator passed.")
