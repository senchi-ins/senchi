"""Sensor model quick sanity check."""
import numpy as np

from src.sensor.sensor_model import UltrasonicMeter


def test_ultrasonic_meter_shapes():
    meter = UltrasonicMeter(random_seed=0)
    v = np.linspace(0, 1.0, 10)  # m/s
    res = meter.simulate(v, pipe_diameter_m=0.025, temperature_c=15.0)
    # every key should have length 10
    for key, arr in res.items():
        assert len(arr) == 10
