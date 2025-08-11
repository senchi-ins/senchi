"""
sensor_model.py
----------------
Clamp-on ultrasonic flow-meter simulation.

This module converts physical variables (pipe velocity, temperature, pipe
geometry) into realistic ultrasonic meter outputs, then injects sensor
imperfections:

1. Transit-time measurements (upstream & downstream)
2. Delta-time (Δt) and volumetric flow rate
3. Gaussian electronic noise + acoustic noise + thermal drift
4. Bias drift (long-term calibration drift)
5. Missing-data bursts, outliers, temporary failures

Configuration is read from `config/sensor_config.json` so sensor specs can be
maintained externally without touching code.
"""

from __future__ import annotations

import json
import math
import numpy as np
from pathlib import Path
from typing import Dict, Optional, Tuple
# -----------------------------------------------------------------------------
# External physics utilities
# -----------------------------------------------------------------------------
from ..physics.temperature import speed_of_sound_water  # Centralised equation

# -----------------------------------------------------------------------------
# Helper functions
# -----------------------------------------------------------------------------

def deg2rad(deg: float) -> float:
    return deg * math.pi / 180.0

# -----------------------------------------------------------------------------
# Sensor Model Class
# -----------------------------------------------------------------------------

class UltrasonicMeter:
    """Clamp-on ultrasonic transit-time flow-meter simulator."""

    def __init__(self,
                 model_id: str = "gentos_GFR_DN20",
                 config_path: Optional[str] = None,
                 random_seed: Optional[int] = None):
        if config_path is None:
            config_path = Path(__file__).parent.parent.parent / "config" / "sensor_config.json"
        with open(config_path, "r") as f:
            cfg = json.load(f)
        
        self.config = cfg
        self.model_cfg = next((m for m in cfg["sensor_models"] if m["id"] == model_id), None)
        if self.model_cfg is None:
            raise ValueError(f"Sensor model '{model_id}' not found in config")
        
        self.specs = self.model_cfg["specifications"]
        self.ultra_cfg = cfg["ultrasonic_physics"]
        self.noise_cfg = cfg["noise_characteristics"]
        self.quality_cfg = cfg["signal_quality_factors"]
        self.data_quality_cfg = cfg["data_quality_simulation"]
        
        # Randomness
        if random_seed is not None:
            np.random.seed(random_seed)

        # Path configuration: use preferred angle & quadruple traverse by default
        self.theta_deg = self.ultra_cfg["transducer_configuration"]["preferred_angle_deg"]
        self.n_traverses = 4  # W-pattern default
        self.theta_rad = deg2rad(self.theta_deg)

        # Resolution & sampling specs
        self.dt_resolution_ns = self.specs["transit_time_resolution_ns"]
        self.sampling_rate_hz = self.specs["sampling_rate_hz"]
        self.dt = 1.0 / self.sampling_rate_hz

        # Bias drift (ppm per year converted later)
        self.bias_drift_ppm_year = self.noise_cfg["electronic_noise"]["time_jitter_ns"]["aging_drift_ns_year"]

    # ------------------------------------------------------------------
    # Core physics
    # ------------------------------------------------------------------

    def _calc_transit_times(self,
                            velocity: float,
                            pipe_diameter_m: float,
                            temperature_c: float,
                            n_traverses: int | None = None) -> Tuple[float, float]:
        """Calculate upstream & downstream transit times [s]."""
        if n_traverses is None:
            n_traverses = self.n_traverses

        # Speed of sound in water
        c = speed_of_sound_water(temperature_c)
        
        # Path length (W-pattern)
        L_path = n_traverses * pipe_diameter_m / math.sin(self.theta_rad)
        
        # Downstream & upstream transit times
        t_down = L_path / (c + velocity * math.cos(self.theta_rad))
        t_up = L_path / (c - velocity * math.cos(self.theta_rad))
        
        return t_up, t_down

    # ------------------------------------------------------------------
    # Noise & Imperfections
    # ------------------------------------------------------------------

    def _apply_noise(self, arr: np.ndarray, std: float) -> np.ndarray:
        return arr + np.random.normal(0, std, arr.shape)

    def _apply_missing_data(self, arr: np.ndarray) -> np.ndarray:
        cfg = self.data_quality_cfg["missing_data"]
        p_single = cfg["probability_per_sample"]
        missing = np.random.rand(*arr.shape) < p_single
        
        # Burst missing data
        if np.random.rand() < cfg["burst_missing_probability"]:
            burst_len = np.random.randint(cfg["burst_duration_samples"][0],
                                          cfg["burst_duration_samples"][1])
            start = np.random.randint(0, len(arr) - burst_len)
            missing[start:start+burst_len] = True
        
        arr[missing] = np.nan
        return arr

    def _apply_outliers(self, arr: np.ndarray) -> np.ndarray:
        cfg = self.data_quality_cfg["outliers"]
        mask = np.random.rand(*arr.shape) < cfg["probability_per_sample"]
        factors = np.random.uniform(cfg["magnitude_factor_range"][0],
                                     cfg["magnitude_factor_range"][1],
                                     size=arr.shape)
        arr[mask] *= factors[mask]
        return arr

    # ------------------------------------------------------------------
    # Public API
    # ------------------------------------------------------------------

    def simulate(self,
                 velocity_series: np.ndarray,
                 pipe_diameter_m: float,
                 temperature_c: float | np.ndarray = 18.0,
                 start_totalizer_L: float = 0.0) -> Dict[str, np.ndarray]:
        """Simulate sensor outputs for a velocity time-series.

        Parameters
        ----------
        velocity_series : np.ndarray
            Pipe velocity (m/s) per sample.
        pipe_diameter_m : float
            Internal pipe diameter (m).
        temperature_c : float or np.ndarray
            Water temperature.
        start_totalizer_L : float
            Initial cumulative volume (L).
        """
        n = len(velocity_series)
        if isinstance(temperature_c, (float, int)):
            temperature_c = float(temperature_c)
            temperature_c = np.full(n, temperature_c)
        
        # Transit times
        t_up, t_down = self._calc_transit_times(
            velocity_series, pipe_diameter_m, temperature_c)
        
        delta_t = t_down - t_up  # s

        # Speed of sound for each sample (m/s) based on supplied water temperature
        speed_m_s = speed_of_sound_water(temperature_c)
        
        # Add electronic time jitter (ns resolution)
        jitter_cfg = self.noise_cfg["electronic_noise"]["time_jitter_ns"]
        jitter_std = jitter_cfg["baseline_std"] * 1e-9  # Convert ns→s
        t_up_noisy = self._apply_noise(t_up.copy(), jitter_std)
        t_down_noisy = self._apply_noise(t_down.copy(), jitter_std)
        delta_t_noisy = t_down_noisy - t_up_noisy
        
        # Flow rate (L/s)
        area = math.pi * (pipe_diameter_m / 2) ** 2
        flow_L_s = velocity_series * area * 1000  # m³/s → L/s
        
        # Add amplitude noise (flow measurement noise)
        amp_cfg = self.noise_cfg["electronic_noise"]["amplitude_noise"]
        snr_db = np.random.uniform(*amp_cfg["snr_db_range"])
        snr_linear = 10 ** (snr_db / 20)
        noise_std_flow = np.mean(flow_L_s) / snr_linear if np.mean(flow_L_s) > 0 else 0.01
        flow_L_s_noisy = self._apply_noise(flow_L_s.copy(), noise_std_flow)
        
        # Totalizer (cumulative volume L)
        totalizer = np.cumsum(flow_L_s_noisy) * self.dt + start_totalizer_L
        
        # Apply missing data and outliers to flow & transit times
        flow_L_s_final = self._apply_missing_data(flow_L_s_noisy.copy())
        flow_L_s_final = self._apply_outliers(flow_L_s_final)
        
        delta_t_final = self._apply_missing_data(delta_t_noisy.copy())
        delta_t_final = self._apply_outliers(delta_t_final)
        
        # Signal quality (simplified proxy)
        signal_strength_db = np.random.uniform(30, 60, size=n)
        signal_quality_percent = np.clip((signal_strength_db - 20) / 40 * 100, 0, 100)
        measurement_confidence = signal_quality_percent / 100.0
        
        # Package results
        results = {
            "t_up_s": t_up_noisy,
            "t_down_s": t_down_noisy,
            "delta_t_s": delta_t_final,
            "flow_L_s": flow_L_s_final,
            "velocity_m_s": velocity_series,
            "totalizer_L": totalizer,
            "speed_of_sound_m_s": speed_m_s,
            "signal_strength_db": signal_strength_db,
            "signal_quality_percent": signal_quality_percent,
            "measurement_confidence": measurement_confidence
        }
        return results

# -----------------------------------------------------------------------------
# Convenience function
# -----------------------------------------------------------------------------

def simulate_ultrasonic_meter(velocity_series: np.ndarray,
                              pipe_diameter_m: float,
                              temperature_c: float | np.ndarray = 18.0,
                              model_id: str = "gentos_GFR_DN20",
                              random_seed: Optional[int] = None) -> Dict[str, np.ndarray]:
    """Quick helper to simulate ultrasonic meter outputs."""
    meter = UltrasonicMeter(model_id=model_id, random_seed=random_seed)
    return meter.simulate(velocity_series, pipe_diameter_m, temperature_c)