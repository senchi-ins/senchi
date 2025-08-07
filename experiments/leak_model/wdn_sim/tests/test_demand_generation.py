"""Demand generator unit tests (minimal).

Ensures that the NumPy-vectorised generator returns sensible arrays and that
basic statistics fall inside the bounds specified in the profile JSON.
"""
from datetime import datetime

import numpy as np

from src.generators.demand_numpy import DemandGenerator


def test_daily_profile_volume():
    gen = DemandGenerator()
    prof_id = "modern_pex_small"

    demand = gen.generate_household_demand(
        house_profile=prof_id,
        duration_hours=24,
        resolution_seconds=60.0,  # coarse grid for speed
        month=datetime.utcnow().month,
        random_seed=1,
    )

    # basic shape
    assert len(demand) == int(24 * 3600 / 60)  # 24h at 60-s resolution
    assert np.all(demand >= 0)

    total_L = np.sum(demand) * 60.0 / 1000  # L/s × s → L
    # modern_pex_small profile defines 180-250 L/day
    assert 150 < total_L < 300
