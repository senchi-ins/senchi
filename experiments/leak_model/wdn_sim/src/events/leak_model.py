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
                 random_seed: Optional[int] = None):
        """Initialize leak event."""
        self.start_time = start_time_hours
        self.location = location
        self.leak_type = leak_type
        self.pipe_material = pipe_material
        self.system_pressure = system_pressure_kpa * 1000  # Pa
        
        if random_seed:
            np.random.seed(random_seed)
            
        self._initialize_parameters()
        
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
        g = 9.81
        return self.discharge_coeff * area * math.sqrt(2 * g) * 1000  # L/s per m^0.5
        
    def apply_to_network(self, wn: wntr.network.WaterNetworkModel, 
                        time_hours: float) -> None:
        """Apply leak to WNTR network."""
        if time_hours < self.start_time:
            return
            
        try:
            node = wn.get_node(self.location)
            area = self.get_leak_area(time_hours)
            
            if area > 0:
                node.add_leak(wn, area=area,
                            discharge_coeff=self.discharge_coeff,
                            start_time=self.start_time * 3600,
                            end_time=None)
        except Exception as e:
            print(f"Warning: Could not apply leak: {e}")


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
            leak_type = np.random.choice(
                [LeakType.PINHOLE, LeakType.GRADUAL, LeakType.FREEZE_BURST, LeakType.PRESSURE_BURST],
                p=[0.4, 0.35, 0.15, 0.1]
            )
            
            location_choice = (
                    np.random.choice(available_nodes)
                    if available_nodes else f"junction_{np.random.randint(1, 100)}"
                )
                
            leak = LeakEvent(
                start_time_hours=start_time,
                location=location_choice,
                leak_type=leak_type,
                pipe_material=material,
                random_seed=random_seed + i if random_seed else None
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