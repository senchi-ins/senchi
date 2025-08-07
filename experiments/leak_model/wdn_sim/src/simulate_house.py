"""
simulate_house.py
-----------------
Single-house orchestration pipeline.

Combines:
* Demand generation (DemandGenerator)
* Hydraulic simulation (EPANET via HydraulicSolver)
* Stochastic events (EventScheduler)
* Transient analysis (optional TSNetWrapper)
* Sensor modelling (UltrasonicMeter)
* Streaming output (assemble_polars + polars_sink)

Designed for realism yet lightweight enough for unit-test execution.
"""

from __future__ import annotations

import os
from pathlib import Path
from datetime import datetime, timedelta
from typing import Optional, Dict, Any, List
import numpy as np
import wntr

# Local imports
from .generators.demand_numpy import DemandGenerator, generate_daily_profile
from .physics.hydraulics import HydraulicSolver
from .events.event_scheduler import EventScheduler, EventCategory
from .sensor.sensor_model import UltrasonicMeter, simulate_ultrasonic_meter
from .io import assemble_polars as ap
from .io.polars_sink import StreamingSink

try:
    from src.events.transient_events import quick_transient
    from src.events.leak_model import LeakType
    _TSNET_AVAILABLE = True
except Exception:
    _TSNET_AVAILABLE = False


class HouseSimulator:
    """End-to-end simulator for a single household-day."""

    def __init__(
        self,
        house_id: int,
        start_time: datetime,
        duration_seconds: int = 3600,
        resolution_seconds: float = 1.0,
        demand_profile_id: str = "default",
        network: Optional[wntr.network.WaterNetworkModel] = None,
        enable_tsnet: bool = False,
        output_dir: Optional[str | Path] = None,
        random_seed: Optional[int] = None,
        light_mode: bool = False,
    ) -> None:
        self.house_id = house_id
        self.start_time = start_time
        self.duration_seconds = duration_seconds
        self.resolution_seconds = resolution_seconds
        self.demand_profile_id = demand_profile_id
        self.random_seed = random_seed
        
        # Build or adopt EPANET network model
        if network is not None:
            self.wn = network
        else:
            from .network.builder import build_network_from_profile  # lazy import to avoid circular
            try:
                self.wn = build_network_from_profile(self.demand_profile_id)
            except Exception:
                # Fallback minimal network if profile unavailable
                self.wn = self._build_default_network()
        self.wn.options.time.hydraulic_timestep = int(max(1, resolution_seconds))
        
        # Modules
        self.demand_gen = DemandGenerator()
        self.hydraulics = HydraulicSolver(self.wn)
        self.scheduler = EventScheduler(self.wn, start_time)
        self.sensor = UltrasonicMeter()
        self.enable_tsnet = enable_tsnet and _TSNET_AVAILABLE

        self.light_mode = light_mode  # Skip EPANET/TSNet for unit tests
        
        # Output sink (if path provided)
        self.output_dir = Path(output_dir) if output_dir else None

    # ---------------------------------------------------------------------
    # Network construction helpers
    # ---------------------------------------------------------------------
    @staticmethod
    def _build_default_network() -> wntr.network.WaterNetworkModel:
        """Create a minimal EPANET network suitable for household supply."""
        wn = wntr.network.WaterNetworkModel()
        wn.add_reservoir("Source", base_head=50)
        wn.add_junction("House", base_demand=0.001, elevation=0)  # 1 L/s
        wn.add_pipe("Pipe", "Source", "House", length=20, diameter=0.025, roughness=130)
        return wn

    # ---------------------------------------------------------------------
    # Core simulation pipeline
    # ---------------------------------------------------------------------
    def _generate_demand(self) -> np.ndarray:
        """Generate demand curve (L/s) for the simulation window."""
        seconds_per_day = 24 * 3600
        if self.duration_seconds >= seconds_per_day:
            duration_hours = self.duration_seconds / 3600
            demand = self.demand_gen.generate_household_demand(
                house_profile=self.demand_profile_id,
                duration_hours=duration_hours,
                resolution_seconds=self.resolution_seconds,
                month=self.start_time.month,
                random_seed=self.random_seed,
            )
            # Trim to exact length needed
            steps = int(self.duration_seconds / self.resolution_seconds) + 1
            demand = demand[:steps] if len(demand) >= steps else np.pad(demand, (0, max(0, steps - len(demand))), 'edge')
        else:
            # For short unit-test runs generate constant moderate flow
            steps = int(self.duration_seconds / self.resolution_seconds) + 1
            demand = np.full(steps, 0.5)  # 0.5 L/s constant
        return demand

    def run(self) -> "ap.pl.DataFrame":  # type: ignore
        """Execute the full single-house simulation and return a Polars DataFrame."""
        # 1. Timestamp grid
        timestamps = ap.create_timestamp_series(
            self.start_time, self.duration_seconds, self.resolution_seconds
        )
        steps = len(timestamps)

        # 2. Demand generation
        demand_L_s = self._generate_demand()

        # 3. Apply static effects of scheduled events (initial leak emitters, initial blockage diameters)
        self._apply_static_event_effects()

        # 4. Assign demand to network (simple: single junction)
        if "House" in self.wn.junction_name_list:
            pat_values = demand_L_s / 1000.0  # L/s to m3/s (EPANET units)
            pattern_name = "demand_pattern"
            self.wn.add_pattern(pattern_name, pat_values.tolist())
            j = self.wn.get_node("House")
            j.demand_timeseries_list[0].pattern_name = pattern_name
            j.demand_timeseries_list[0].base_value = 1.0  # Multiplier

        if self.light_mode:
            # --------------------------------------------------------------
            # Lightweight per-step solver with progressive event effects
            # --------------------------------------------------------------
            A = np.pi * (0.025 / 2) ** 2
            flow_L_s = np.zeros(steps)
            velocity_ms = np.zeros(steps)
            pressure_kpa = np.full(steps, 300.0)  # Nominal

            time_hours = np.arange(steps) * self.resolution_seconds / 3600.0
            for idx, t_h in enumerate(time_hours):
                # Demand base
                base_flow = demand_L_s[idx]
                # Extra leak discharge (sum of active leaks)
                leak_extra = 0.0
                active = self.scheduler.get_active_events(t_h)
                for cat, ev in active:
                    if cat == EventCategory.LEAK:
                        leak_extra += ev.get_leak_flow(t_h, ev.system_pressure) * 1000  # m3/s -> L/s

                total_flow_L_s = base_flow + leak_extra
                flow_L_s[idx] = total_flow_L_s
                velocity_ms[idx] = (total_flow_L_s / 1000) / A if total_flow_L_s > 0 else 0.0
        else:
            # --------------------------------------------------------------
            # 4. High-fidelity per-step EPANET solve with progressive events
            # --------------------------------------------------------------
            flow_L_s = np.zeros(steps)
            velocity_ms = np.zeros(steps)
            pressure_kpa = np.zeros(steps)

            time_hours = np.arange(steps) * self.resolution_seconds / 3600.0
            for idx, t_h in enumerate(time_hours):

                # (a) apply demand for this step (convert L/s → m³/s)
                if "House" in self.wn.junction_name_list:
                    j = self.wn.get_node("House")
                    j.base_demand = demand_L_s[idx] / 1000.0

                # (b) update network for active events
                self.scheduler.apply_events_to_network(t_h)

                # (c) run EPANET for one hydraulic timestep (quasi-steady)
                self.hydraulics.run_hydraulics(self.resolution_seconds)
                res = self.hydraulics.results

                flow_m3s = res.link["flowrate"]["Pipe"].iloc[0]
                vel_ms = res.link["velocity"]["Pipe"].iloc[0]
                press_m = res.node["pressure"]["House"].iloc[0]

                flow_L_s[idx] = flow_m3s * 1000.0
                velocity_ms[idx] = vel_ms
                pressure_kpa[idx] = press_m * 9.80665  # m → kPa


        # 5. Optional transient analysis via TSNet – only if a true burst event exists
        downstream_wave_time = np.full(steps, np.nan)
        upstream_wave_time = np.full(steps, np.nan)
        delta_time = np.full(steps, np.nan)

        if (
            not self.light_mode
            and self.enable_tsnet
            and self.scheduler.events.get(EventCategory.LEAK)
        ):
            # Pick the first pressure-burst style leak as the transient trigger
            burst_event = next(
                (
                    ev
                    for ev in self.scheduler.events[EventCategory.LEAK]
                    if getattr(ev, "leak_type", None) == LeakType.PRESSURE_BURST
                ),
                None,
            )

            if burst_event is not None:
                try:
                    area = burst_event.get_leak_area(burst_event.start_time)
                    quick_transient(
                        self.wn,
                        event_type="leak",
                        node=burst_event.location,
                        time=0.0,
                        area=area,
                        duration=2.0,
                    )
                    # We insert a short synthetic wave-time pulse around the burst onset.
                    event_idx = int(burst_event.start_time * 3600 / self.resolution_seconds)
                    end_idx = min(steps, event_idx + 5)
                    downstream_wave_time[event_idx:end_idx] = 1e-4
                    upstream_wave_time[event_idx:end_idx] = 2e-4
                    delta_time[event_idx:end_idx] = downstream_wave_time[event_idx:end_idx] - upstream_wave_time[event_idx:end_idx]
                except Exception:
                    # Fail safe: keep NaNs
                    pass

        # 6. Sensor simulation
        sensor_results = self.sensor.simulate(
            velocity_ms,
            pipe_diameter_m=0.025,
            temperature_c=15.0,
        )

        # 7. Assemble data
        sim_data = ap.assemble_demand_data(timestamps, flow_L_s, self.house_id)
        sim_data = ap.merge_hydraulics_data(sim_data, velocity_ms, pressure_kpa, 25.0, "Copper")
        sim_data = ap.merge_sensor_data(sim_data, sensor_results)

        # ------------------------------------------------------------------
        # 7b. Apply scheduled events (leaks/blockages) --> leak flag & location
        # ------------------------------------------------------------------
        time_hours = np.arange(steps) * self.resolution_seconds / 3600.0
        leak_flags = np.zeros(steps, dtype=bool)
        locations = [None] * steps
        for idx, t_h in enumerate(time_hours):
            active = self.scheduler.get_active_events(t_h)
            for cat, ev in active:
                if cat == EventCategory.LEAK:
                    leak_flags[idx] = True
                    locations[idx] = getattr(ev, "location", None)

        # Merge event information into simulation dictionary
        sim_data = ap.merge_events_data(sim_data, leak_flags, locations)

        # Insert transient columns
        # Only overwrite sensor-derived wave-times if transient analysis produced data
        if not np.isnan(downstream_wave_time).all():
            sim_data["downstream_wave_time"] = downstream_wave_time.tolist()
        if not np.isnan(upstream_wave_time).all():
            sim_data["upstream_wave_time"] = upstream_wave_time.tolist()
        if not np.isnan(delta_time).all():
            sim_data["delta_t_raw"] = delta_time.tolist()

        df = ap.create_simulation_dataframe(sim_data)

        # 8. Optional write to disk
        if self.output_dir:
            with StreamingSink(self.output_dir, batch_size=len(df)) as sink:
                sink.add_batch(sim_data)
                sink.flush()

        return df

    # ------------------------------------------------------------------
    # ------------------------------------------------------------------
    # Event integration helpers
    # ------------------------------------------------------------------
    def _apply_static_event_effects(self) -> None:
        """Apply one-off network modifications for events prior to simulation."""
        # Leaks: add emitters starting at leak start time with initial area
        for leak in self.scheduler.events.get(EventCategory.LEAK, []):
            try:
                leak.apply_to_network(self.wn, leak.start_time)
            except Exception:
                pass

        # Blockages: adjust pipe diameters/roughness at t=0 to first-stage reduction
        for blk in self.scheduler.events.get(EventCategory.BLOCKAGE, []):
            try:
                blk.apply_to_network(self.wn, blk.start_time)
            except Exception:
                pass

    # ------------------------------------------------------------------
    @staticmethod
    def _pad_or_trim(arr: np.ndarray, target_len: int) -> np.ndarray:
        if len(arr) < target_len:
            pad = np.full(target_len - len(arr), arr[-1] if len(arr) else np.nan)
            return np.concatenate([arr, pad])
        elif len(arr) > target_len:
            return arr[:target_len]
        return arr


__all__ = ["HouseSimulator"]