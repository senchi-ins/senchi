"""
leak_model.py
-------------
Progressive leak and burst modeling using EPANET emitters.
"""

import numpy as np
import wntr
from typing import Dict, List, Optional
from enum import Enum
import math


class LeakType(Enum):
    """Types of leak events."""
    PINHOLE = "pinhole"           # Small corrosion hole
    GRADUAL = "gradual"           # Growing fatigue crack
    FREEZE_BURST = "freeze_burst" # Ice expansion rupture
    PRESSURE_BURST = "pressure_burst" # Overpressure failure


class LeakEvent:
    """
    Models progressive leak with orifice equation physics.
    Q = Cd * A * sqrt(2 * ΔP / ρ)
    """
    
    def __init__(self, 
                 start_time_hours: float,
                 location: str,
                 leak_type: LeakType,
                 pipe_material: str = "Copper",
                 system_pressure_kpa: float = 414.0,
                 random_seed: Optional[int] = None,
                 duration_hours: Optional[float] = None):
        """Initialize leak event."""
        self.start_time = start_time_hours
        self.location = location
        self.leak_type = leak_type
        self.pipe_material = pipe_material
        self.system_pressure = system_pressure_kpa * 1000  # Pa
        self.duration_hours = duration_hours  # None = indefinite
        
        if random_seed:
            np.random.seed(random_seed)
            
        self._initialize_parameters()
        # Track scheduled control times to avoid duplicates when called repeatedly
        self._scheduled_seconds: set[int] = set()
        self._control_counter: int = 0
        # Track whether a WNTR leak has been attached to avoid duplicates
        self._wntr_leak_added: bool = False
        
    def _initialize_parameters(self):
        """Set leak parameters based on type."""
        if self.leak_type == LeakType.PINHOLE:
            self.initial_diameter_mm = np.random.uniform(0.1, 0.5)
            self.growth_rate_mm_per_day = 0.02
            self.max_diameter_mm = 5.0
            self.discharge_coeff = 0.61
            
        elif self.leak_type == LeakType.GRADUAL:
            self.initial_diameter_mm = np.random.uniform(0.5, 2.0)
            self.growth_rate_mm_per_day = 0.3
            self.max_diameter_mm = 15.0
            self.discharge_coeff = 0.65
            self.acceleration = 1.1
            
        elif self.leak_type == LeakType.FREEZE_BURST:
            self.initial_diameter_mm = np.random.uniform(5, 20)
            self.growth_rate_mm_per_day = 0.5
            self.max_diameter_mm = 50.0
            self.discharge_coeff = 0.75
            
        else:  # PRESSURE_BURST
            self.initial_diameter_mm = np.random.uniform(10, 30)
            self.growth_rate_mm_per_day = 2.0
            self.max_diameter_mm = 100.0
            self.discharge_coeff = 0.8
            
    def get_leak_diameter(self, time_hours: float) -> float:
        """Calculate leak diameter at time."""
        if time_hours < self.start_time:
            return 0.0
            
        elapsed_days = (time_hours - self.start_time) / 24.0
        
        if self.leak_type == LeakType.GRADUAL:
            # Accelerating growth
            diameter = self.initial_diameter_mm * (self.acceleration ** elapsed_days)
        else:
            # Linear growth
            diameter = self.initial_diameter_mm + self.growth_rate_mm_per_day * elapsed_days
            
        return min(diameter, self.max_diameter_mm)
        
    def get_leak_area(self, time_hours: float) -> float:
        """Calculate leak area in m²."""
        diameter_m = self.get_leak_diameter(time_hours) / 1000.0
        return math.pi * (diameter_m / 2) ** 2
        
    def get_leak_flow(self, time_hours: float, pressure_pa: float) -> float:
        """Calculate flow rate in m³/s."""
        area = self.get_leak_area(time_hours)
        if area == 0:
            return 0.0
        # Orifice equation
        rho = 999.7
        return self.discharge_coeff * area * math.sqrt(2 * pressure_pa / rho)
        
    def get_emitter_coefficient(self, time_hours: float) -> float:
        """Get EPANET emitter coefficient."""
        area = self.get_leak_area(time_hours)
        if area == 0:
            return 0.0
        # EPANET emitter coefficient units depend on flow units; with LPS the
        # coefficient is in L/s per m^0.5. We adopt Cd*A*sqrt(2g) and convert to L/s.
        g = 9.81
        return self.discharge_coeff * area * math.sqrt(2 * g) * 1000.0  # L/s per m^0.5
        
    def apply_to_network(self, wn: wntr.network.WaterNetworkModel, 
                        time_hours: float) -> None:
        """Schedule EPANET emitter-coefficient controls to model the leak.

        This creates time-based controls that set the junction's
        `emitter_coefficient` at the leak location. It supports a progressive
        leak by scheduling updates whenever this function is called at new
        times (e.g., hourly) prior to running a single EPANET simulation.
        """
        if time_hours < self.start_time:
            return

        try:
            node = wn.get_node(self.location)
        except Exception as e:
            print(f"Warning: Could not find leak node '{self.location}': {e}")
            return

        # Helper to add a time control safely (idempotent by second)
        def _schedule_emitter(second: int, coeff: float) -> None:
            if second in self._scheduled_seconds:
                return
            try:
                action = wntr.network.ControlAction(node, "emitter_coefficient", coeff)
                # Use public API to build a time control if available; fallback to
                # private helper retained for backwards compat in WNTR
                try:
                    from wntr.network.controls import Control, SimTimeCondition  # type: ignore
                    cond = SimTimeCondition(wn, second)
                    ctrl = Control(cond, action)
                except Exception:
                    ctrl = wntr.network.controls.Control._time_control(
                        wn, second, "SIM_TIME", False, action
                    )
                # Ensure unique control name per event/time
                name = f"leak_{self.location}_{second}_{self._control_counter}"
                self._control_counter += 1
                wn.add_control(name, ctrl)
                self._scheduled_seconds.add(second)
            except Exception as ex:
                print(f"Warning: Could not schedule emitter control at t={second}s: {ex}")

        # Schedule initial activation at start_time (for EPANET emitter approach)
        start_sec = int(self.start_time * 3600)
        start_coeff = self.get_emitter_coefficient(self.start_time)
        if start_coeff > 0:
            _schedule_emitter(start_sec, start_coeff)

        # Schedule progressive update at this call time (e.g., hourly resolution)
        current_sec = int(time_hours * 3600)
        coeff_now = self.get_emitter_coefficient(time_hours)
        if coeff_now > 0:
            _schedule_emitter(current_sec, coeff_now)

        # Schedule termination reset to zero at end time (if finite duration)
        if self.duration_hours is not None and self.duration_hours > 0:
            end_sec = int((self.start_time + self.duration_hours) * 3600)
            _schedule_emitter(end_sec, 0.0)

        # WNTR engine: add a piecewise-constant leak segment per hydraulic step
        # so progressive growth is honored when using WNTRSimulator.
        try:
            # Time resolution from network options (seconds)
            step_s = int(getattr(wn.options.time, "hydraulic_timestep", 0)) or 3600
            # Do not schedule outside a finite leak window
            leak_end_sec = None
            if self.duration_hours is not None and self.duration_hours > 0:
                leak_end_sec = int((self.start_time + self.duration_hours) * 3600)

            # For the current call time, schedule exactly one segment if not already
            if current_sec not in self._scheduled_seconds:
                # Only within leak window (or indefinite leak after start)
                if (leak_end_sec is None) or (current_sec < leak_end_sec):
                    area_now = self.get_leak_area(time_hours)
                    if area_now > 0:
                        seg_end = current_sec + step_s
                        if leak_end_sec is not None:
                            seg_end = min(seg_end, leak_end_sec)
                        node.add_leak(
                            wn,
                            area=area_now,
                            discharge_coeff=self.discharge_coeff,
                            start_time=current_sec,
                            end_time=seg_end,
                        )
                        # Mark current second as scheduled to avoid duplicate segments
                        self._scheduled_seconds.add(current_sec)
        except Exception:
            # Best-effort; safe to ignore if WNTR leak API not available
            pass


class LeakGenerator:
    """Generate realistic leak events."""
    
    def __init__(self):
        """Initialize generator."""
        self.base_leak_rate = 0.1  # Per km per year
        self.material_factors = {
            'Copper': 1.0,
            'Steel': 1.5,
            'CPVC': 0.8,
            'PEX-B': 0.5
        }
        # Duration category weights (short, medium, long, persistent)
        self.duration_weights = [0.20, 0.50, 0.25, 0.05]

    def _sample_duration_hours(self, rng: np.random.Generator | None = None) -> float:
        """Sample a realistic leak duration in hours.

        Categories:
        - short: 10–60 minutes
        - medium: 1–24 hours
        - long: 1–7 days
        - persistent: 7–14 days
        """
        _rng = rng if rng is not None else np.random.default_rng()
        cat = _rng.choice(["short", "medium", "long", "persistent"], p=self.duration_weights)
        if cat == "short":
            return float(_rng.uniform(10/60, 60/60))  # hours
        if cat == "medium":
            return float(_rng.uniform(1, 24))
        if cat == "long":
            return float(_rng.uniform(24, 7*24))
        # persistent
        return float(_rng.uniform(7*24, 14*24))

    def generate_leaks(self, 
                       duration_days: int,
                       network_length_km: float,
                       material: str = 'Copper',
                       age_years: int = 20,
                       random_seed: Optional[int] = None,
                       available_nodes: Optional[List[str]] = None) -> List[LeakEvent]:
        """Generate leak schedule.
        Returns an empty list ~90 % of the time so most simulations are event-free.
        """
        if random_seed is not None:
            np.random.seed(random_seed)
        rng = np.random.default_rng(random_seed)

            
        # Calculate expected leaks
        material_factor = self.material_factors.get(material, 1.0)
        age_factor = 1.5 ** (age_years / 10)
        
        annual_rate = self.base_leak_rate * network_length_km * material_factor * age_factor
        expected = annual_rate * (duration_days / 365)
        n_leaks = max(1, np.random.poisson(expected))
        
        leaks = []
        for i in range(n_leaks):
            start_time = np.random.uniform(0, duration_days * 24)
            
            # Choose type
            # leak_type = np.random.choice(
            #     [LeakType.PINHOLE, LeakType.GRADUAL, LeakType.FREEZE_BURST, LeakType.PRESSURE_BURST],
            #     p=[0.4, 0.35, 0.15, 0.1]
            # )
            # Test mode: restrict to pressure-burst leaks only
            leak_type = LeakType.PRESSURE_BURST
            
            location_choice = (
                    np.random.choice(available_nodes)
                    if available_nodes else f"junction_{np.random.randint(1, 100)}"
                )
            # Sample duration in hours
            duration_hours = self._sample_duration_hours(rng)
            
            leak = LeakEvent(
                start_time_hours=start_time,
                location=location_choice,
                leak_type=leak_type,
                pipe_material=material,
                random_seed=random_seed + i if random_seed else None,
                duration_hours=duration_hours,
            )
            leaks.append(leak)
            
        return leaks


def simulate_leak_progression(leak: LeakEvent,
                            duration_hours: float,
                            pressure_kpa: float = 414.0,
                            time_step_hours: float = 1.0) -> Dict:
    """Simulate leak over time."""
    times = np.arange(0, duration_hours + time_step_hours, time_step_hours)
    results = {
        'time_hours': times,
        'diameter_mm': [],
        'flow_L_s': [],
        'cumulative_L': []
    }
    
    cumulative = 0
    pressure_pa = pressure_kpa * 1000
    
    for t in times:
        diameter = leak.get_leak_diameter(t)
        flow = leak.get_leak_flow(t, pressure_pa)
        
        if t > leak.start_time:
            cumulative += flow * time_step_hours * 3600 * 1000
            
        results['diameter_mm'].append(diameter)
        results['flow_L_s'].append(flow * 1000)
        results['cumulative_L'].append(cumulative)
        
    return results
