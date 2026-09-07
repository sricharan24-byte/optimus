"""Tests for semantic constraint engine and violation scoring."""

from src.data_generation.attack_injector import inject_attack_a_capacity
from src.data_generation.generator import generate_normal_stream
from src.semantic_constraints.engine import HistoricalProfile, SemanticConstraintEngine


def test_constraints_on_normal_and_attack():
    normal_df = generate_normal_stream(num_samples=200, seed=42)
    engine = SemanticConstraintEngine(total_capacity=50.0, c1_tolerance=1.5, c2_tolerance=1.0)
    profile = HistoricalProfile.fit_from_normal(normal_df)
    engine.set_historical_profile(profile)

    # On normal data, semantic violation score should be low (< 0.15)
    res_normal, _ = engine.evaluate_frame(normal_df)
    assert res_normal["semantic_score_combined"].mean() < 0.05
    assert (res_normal["semantic_score_combined"] < 0.20).all()

    # On Attack A (capacity tampered to 38t), C1 violation must be very high (> 0.70)
    attack_df = inject_attack_a_capacity(normal_df, start_idx=50, duration=15, tampered_free_capacity=38.0)
    res_attack, viols = engine.evaluate_frame(attack_df)
    tampered_scores = res_attack.loc[50:64, "semantic_score_c1"]
    assert (tampered_scores > 0.70).all(), f"Expected high C1 violation, got min: {tampered_scores.min()}"


if __name__ == "__main__":
    test_constraints_on_normal_and_attack()
    print("test_constraints passed.")
