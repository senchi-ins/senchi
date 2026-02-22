"""Verify that scheduled leaks increase flow and reduce pressure in EPANET mode.

We run a short simulation with events enabled so that a leak is attached to a
downstream junction. The hydraulic engine should switch to WNTR automatically to
honor time-controls on emitter coefficients, and the resulting flow/pressure
time series should reflect the leak onset.
"""
from datetime import datetime

import numpy as np

from src.simulate_house import HouseSimulator


def test_leak_increases_flow_and_reduces_pressure_epanet_mode():
    sim = HouseSimulator(
        house_id=42,
        start_time=datetime.utcnow(),
        duration_seconds=600,  # 10 minutes
        resolution_seconds=10.0,
        demand_profile_id="modern_pex_small",
        light_mode=False,
        enable_tsnet=False,
    )

    # Generate a realistic schedule with at least one leak and force it to a known node
    network_info = {"length_km": 0.1, "material": "Copper", "age_years": 20}
    sim.scheduler.generate_realistic_schedule(duration_days=1, network_info=network_info, random_seed=123)

    df = sim.run()

    # Use the leak flag to detect onset
    leak_indices = np.where(df["leak"].to_numpy())[0]
    assert leak_indices.size > 0, "No leak flagged in results"

    onset = leak_indices.min()
    # Give a few steps before and after onset to compute deltas
    pre_idx = max(0, onset - 1)
    post_idx = min(df.height - 1, onset + 1)

    flow = df["flow_m3_s"].to_numpy()
    pressure = df["pressure"].to_numpy()

    assert flow[post_idx] > flow[pre_idx], "Flow did not increase after leak onset"
    assert pressure[post_idx] < pressure[pre_idx], "Pressure did not decrease after leak onset"
