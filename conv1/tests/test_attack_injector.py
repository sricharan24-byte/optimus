"""Tests for attack injection engine."""

from src.data_generation.attack_injector import (
    inject_attack_a_capacity,
    inject_attack_b_inventory,
    inject_attack_c_sensor,
    inject_attack_d_replay,
    inject_attack_e_coordinated,
    inject_collusion_attack,
)
from src.data_generation.generator import generate_normal_stream


def test_attack_injections():
    base_df = generate_normal_stream(num_samples=100, seed=42)

    # Attack A
    df_a = inject_attack_a_capacity(base_df, start_idx=20, duration=10, tampered_free_capacity=39.0)
    assert df_a.loc[20:29, "is_attack"].sum() == 10
    assert (df_a.loc[20:29, "reported_free_capacity"] == 39.0).all()
    assert df_a.loc[0:19, "is_attack"].sum() == 0

    # Attack B
    df_b = inject_attack_b_inventory(base_df, start_idx=30, duration=10, inventory_delta=-12.0)
    assert df_b.loc[30:39, "is_attack"].sum() == 10
    assert df_b.loc[30, "attack_type"] == "ATTACK_B_INVENTORY"

    # Attack C
    df_c = inject_attack_c_sensor(base_df, start_idx=40, duration=10, spoofed_occupancy=0.10)
    assert (df_c.loc[40:49, "telemetry_occupancy"] == 0.10).all()

    # Attack E
    df_e = inject_attack_e_coordinated(base_df, start_idx=50, duration=10)
    assert df_e.loc[50:59, "is_attack"].sum() == 10
    assert df_e.loc[50, "attack_type"] == "ATTACK_E_COORDINATED"


if __name__ == "__main__":
    test_attack_injections()
    print("test_attack_injector passed.")
