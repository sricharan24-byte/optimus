"""Attack injection engine supporting plausible-looking integrity attacks."""

from typing import Optional
import numpy as np
import pandas as pd


def inject_attack_a_capacity(
    df: pd.DataFrame,
    start_idx: int,
    duration: int = 24,
    tampered_free_capacity: float = 38.0,
) -> pd.DataFrame:
    """Attack A: Plausible operational free capacity tampering.
    Alters reported_free_capacity to a plausible number (e.g. 38t) that contradicts inventory & occupancy.
    """
    df = df.copy()
    end_idx = min(len(df), start_idx + duration)
    df.loc[start_idx:end_idx - 1, "reported_free_capacity"] = tampered_free_capacity
    df.loc[start_idx:end_idx - 1, "is_attack"] = 1
    df.loc[start_idx:end_idx - 1, "attack_type"] = "ATTACK_A_CAPACITY"
    return df


def inject_attack_b_inventory(
    df: pd.DataFrame,
    start_idx: int,
    duration: int = 24,
    inventory_delta: float = -15.0,
) -> pd.DataFrame:
    """Attack B: Inventory ledger manipulation.
    Alters reported_inventory without corresponding inbound/outbound movements.
    """
    df = df.copy()
    end_idx = min(len(df), start_idx + duration)
    df.loc[start_idx:end_idx - 1, "reported_inventory"] = np.clip(
        df.loc[start_idx:end_idx - 1, "reported_inventory"] + inventory_delta, 0.0, 50.0
    )
    df.loc[start_idx:end_idx - 1, "is_attack"] = 1
    df.loc[start_idx:end_idx - 1, "attack_type"] = "ATTACK_B_INVENTORY"
    return df


def inject_attack_c_sensor(
    df: pd.DataFrame,
    start_idx: int,
    duration: int = 24,
    spoofed_occupancy: float = 0.20,
) -> pd.DataFrame:
    """Attack C: IoT sensor spoofing.
    Occupancy telemetry falsified to claim warehouse is nearly empty when inventory is high.
    """
    df = df.copy()
    end_idx = min(len(df), start_idx + duration)
    df.loc[start_idx:end_idx - 1, "telemetry_occupancy"] = spoofed_occupancy
    df.loc[start_idx:end_idx - 1, "is_attack"] = 1
    df.loc[start_idx:end_idx - 1, "attack_type"] = "ATTACK_C_SENSOR"
    return df


def inject_attack_d_replay(
    df: pd.DataFrame,
    start_idx: int,
    duration: int = 24,
    source_history_start: int = 0,
) -> pd.DataFrame:
    """Attack D: Stale/replay state injection.
    Replays a historical slice of telemetry and operational claims from an earlier timestamp.
    """
    df = df.copy()
    end_idx = min(len(df), start_idx + duration)
    replay_len = end_idx - start_idx
    hist_slice = df.iloc[source_history_start:source_history_start + replay_len]
    if len(hist_slice) == replay_len:
        df.loc[start_idx:end_idx - 1, "reported_free_capacity"] = hist_slice["reported_free_capacity"].values
        df.loc[start_idx:end_idx - 1, "reported_inventory"] = hist_slice["reported_inventory"].values
        df.loc[start_idx:end_idx - 1, "telemetry_occupancy"] = hist_slice["telemetry_occupancy"].values
    df.loc[start_idx:end_idx - 1, "is_attack"] = 1
    df.loc[start_idx:end_idx - 1, "attack_type"] = "ATTACK_D_REPLAY"
    return df


def inject_attack_e_coordinated(
    df: pd.DataFrame,
    start_idx: int,
    duration: int = 36,
    subtle_cap_offset: float = 7.5,
    subtle_inv_offset: float = 2.0,
    subtle_occ_offset: float = -0.05,
) -> pd.DataFrame:
    """Attack E: Coordinated multi-source low-severity manipulation.
    Individually small discrepancies across capacity, inventory, and occupancy
    designed to evade single-point threshold detection while collectively indicating attack.
    """
    df = df.copy()
    end_idx = min(len(df), start_idx + duration)
    df.loc[start_idx:end_idx - 1, "reported_free_capacity"] += subtle_cap_offset
    df.loc[start_idx:end_idx - 1, "reported_inventory"] += subtle_inv_offset
    df.loc[start_idx:end_idx - 1, "telemetry_occupancy"] = np.clip(
        df.loc[start_idx:end_idx - 1, "telemetry_occupancy"] + subtle_occ_offset, 0.0, 1.0
    )
    df.loc[start_idx:end_idx - 1, "is_attack"] = 1
    df.loc[start_idx:end_idx - 1, "attack_type"] = "ATTACK_E_COORDINATED"
    return df


def inject_collusion_attack(
    df: pd.DataFrame,
    start_idx: int,
    duration: int = 24,
    falsified_inventory: float = 15.0,
    total_capacity: float = 50.0,
) -> pd.DataFrame:
    """Robustness Benchmark: Multi-source colluding attack.
    Attacker compromises operational record, inventory ledger, AND sensor simultaneously,
    keeping them mutually consistent to test the fundamental boundary of cross-source validation.
    """
    df = df.copy()
    end_idx = min(len(df), start_idx + duration)
    df.loc[start_idx:end_idx - 1, "reported_inventory"] = falsified_inventory
    df.loc[start_idx:end_idx - 1, "reported_free_capacity"] = total_capacity - falsified_inventory
    df.loc[start_idx:end_idx - 1, "telemetry_occupancy"] = falsified_inventory / total_capacity
    df.loc[start_idx:end_idx - 1, "is_attack"] = 1
    df.loc[start_idx:end_idx - 1, "attack_type"] = "ATTACK_COLLUSION"
    return df
