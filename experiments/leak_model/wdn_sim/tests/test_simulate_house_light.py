"""End-to-end pipeline test in light_mode to keep runtime minimal."""
from datetime import datetime

from src.simulate_house import HouseSimulator


def test_house_simulator_light():
    sim = HouseSimulator(
        house_id=1,
        start_time=datetime.utcnow(),
        duration_seconds=120,  # 2 minutes
        resolution_seconds=10.0,
        demand_profile_id="modern_pex_small",
        light_mode=True,
        enable_tsnet=False,
    )
    df = sim.run()
    # expected rows = duration/resolution +1
    assert df.height == 13  # 0..120 every 10 s
    # key columns exist
    for col in ["flow_gpm", "pressure", "velocity", "leak"]:
        assert col in df.columns
