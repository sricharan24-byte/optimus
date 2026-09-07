"""Integration test for full end-to-end detection pipeline."""

from src.data_generation.attack_injector import inject_attack_a_capacity, inject_attack_e_coordinated
from src.data_generation.generator import generate_normal_stream
from src.pipeline import IntegrityDetectionPipeline


def test_full_pipeline_detection():
    normal_train = generate_normal_stream(num_samples=200, seed=42)
    pipeline = IntegrityDetectionPipeline()
    pipeline.calibrate(normal_train)

    # Test on attack stream
    test_stream = generate_normal_stream(num_samples=150, seed=99)
    test_stream = inject_attack_a_capacity(test_stream, start_idx=30, duration=20, tampered_free_capacity=38.0)
    test_stream = inject_attack_e_coordinated(test_stream, start_idx=80, duration=25)

    processed_df, alerts = pipeline.process_stream(test_stream)

    # Confirm columns are present
    assert "semantic_score_combined" in processed_df.columns
    assert "temporal_score" in processed_df.columns
    assert "structural_score" in processed_df.columns
    assert "joint_risk_score" in processed_df.columns
    assert "is_alert" in processed_df.columns

    # Verify that attacks produced alerts
    attack_alerts = [a for a in alerts if a.alert_level in ["SUSPICIOUS", "POTENTIAL_COORDINATED_ATTACK"]]
    assert len(attack_alerts) > 0, "Pipeline should generate alerts during attack periods."

    # First alert should have explainability details
    first_alert = attack_alerts[0]
    report_text = first_alert.to_text_report()
    assert "=== SECURITY ALERT:" in report_text
    assert "Corroborating Evidence:" in report_text


if __name__ == "__main__":
    test_full_pipeline_detection()
    print("test_pipeline_integration passed.")
