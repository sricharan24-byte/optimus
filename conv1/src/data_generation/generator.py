"""Synthetic dataset generator for cold-storage operational and IoT telemetry."""

from dataclasses import dataclass
from datetime import datetime, timedelta
import numpy as np
import pandas as pd
import yaml


@dataclass
class SimulationConfig:
    warehouse_id: str = "WH_01"
    total_capacity: float = 50.0
    units: list = None
    sample_interval_sec: int = 300
    temp_target: float = 3.0
    temp_noise_std: float = 0.15
    hum_target: float = 90.0
    hum_noise_std: float = 1.2
    occ_noise_std: float = 0.015

    @classmethod
    def from_yaml(cls, path: str):
        with open(path, "r") as f:
            raw = yaml.safe_load(f)
        wh = raw["warehouse"]
        tel = raw["telemetry"]
        return cls(
            warehouse_id=wh["id"],
            total_capacity=float(wh["total_capacity_tonnes"]),
            units=wh.get("units", []),
            sample_interval_sec=int(tel.get("sample_interval_sec", 300)),
            temp_target=float(tel.get("temp_target_c", 3.0)),
            temp_noise_std=float(tel.get("temp_std_c", 0.15)),
            hum_target=float(tel.get("humidity_target_pct", 90.0)),
            hum_noise_std=float(tel.get("humidity_std_pct", 1.2)),
            occ_noise_std=float(tel.get("occupancy_noise_std", 0.015)),
        )


def generate_normal_stream(
    num_samples: int = 2016,  # 7 days at 5-min intervals
    start_time: datetime = datetime(2026, 9, 1, 0, 0),
    seed: int = 42,
    config: SimulationConfig = None,
) -> pd.DataFrame:
    """Generates physically consistent, normal cold-storage operational & IoT records."""
    if config is None:
        config = SimulationConfig()
    rng = np.random.default_rng(seed)

    timestamps = [start_time + timedelta(seconds=i * config.sample_interval_sec) for i in range(num_samples)]
    hours = np.array([ts.hour + ts.minute / 60.0 for ts in timestamps])

    # Inventory dynamics: baseline ~41.5t, periodic small shipments
    inventory = np.zeros(num_samples)
    inbound = np.zeros(num_samples)
    outbound = np.zeros(num_samples)

    current_inv = 42.0
    for i in range(num_samples):
        # Daily deliveries around 08:00 and dispatches around 17:00
        in_qty, out_qty = 0.0, 0.0
        if 8.0 <= hours[i] < 8.2 and rng.random() < 0.15:
            in_qty = rng.uniform(1.0, 3.5)
        elif 17.0 <= hours[i] < 17.2 and rng.random() < 0.15:
            out_qty = rng.uniform(1.0, 3.0)

        current_inv = np.clip(current_inv + in_qty - out_qty, 30.0, config.total_capacity - 1.0)
        inventory[i] = current_inv
        inbound[i] = in_qty
        outbound[i] = out_qty

    # IoT physical measurements with realistic diurnal drift + sensor noise
    diurnal_temp = 0.25 * np.sin(2 * np.pi * (hours - 14.0) / 24.0)
    temperature = config.temp_target + diurnal_temp + rng.normal(0, config.temp_noise_std, num_samples)
    humidity = config.hum_target - 0.5 * diurnal_temp + rng.normal(0, config.hum_noise_std, num_samples)

    true_occupancy = inventory / config.total_capacity
    telemetry_occupancy = np.clip(true_occupancy + rng.normal(0, config.occ_noise_std, num_samples), 0.0, 1.0)

    # Operational claims: truthful reporting with minor measurement tolerance (+-0.2 tonnes)
    true_free = np.maximum(0.0, config.total_capacity - inventory)
    reported_free = np.clip(true_free + rng.normal(0, 0.2, num_samples), 0.0, config.total_capacity)
    reported_inventory = inventory + rng.normal(0, 0.1, num_samples)

    df = pd.DataFrame(
        {
            "timestamp": timestamps,
            "warehouse_id": config.warehouse_id,
            "storage_unit_id": "SU_ALL",
            "total_capacity": config.total_capacity,
            "actual_inventory": np.round(inventory, 2),
            "inbound_qty": np.round(inbound, 2),
            "outbound_qty": np.round(outbound, 2),
            "temperature_c": np.round(temperature, 2),
            "humidity_pct": np.round(humidity, 1),
            "telemetry_occupancy": np.round(telemetry_occupancy, 3),
            "reported_free_capacity": np.round(reported_free, 2),
            "reported_inventory": np.round(reported_inventory, 2),
            "operational_status": "NORMAL",
            "is_attack": 0,
            "attack_type": "NONE",
        }
    )
    return df
