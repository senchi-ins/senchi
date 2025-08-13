"""
joukowsky.py
------------
Water-hammer analysis using Joukowsky equation and wave-speed calculations.
Integrates with TSNet for high-fidelity transient simulation.
"""

import numpy as np
from typing import Tuple, Optional, Dict
import math
from .temperature import speed_of_sound_water  # Centralised helper


class WaterHammerAnalyzer:
    """
    Analyzes water-hammer effects using Joukowsky equation.
    """
    
    def __init__(self, pipe_material: str = 'PEX-B', 
                 fluid_bulk_modulus: float = 2.2e9,
                 fluid_density: float = 999.7):
        """
        Initialize water-hammer analyzer.
        
        Parameters
        ----------
        pipe_material : str
            Pipe material type ('Copper', 'PEX-B', 'CPVC')
        fluid_bulk_modulus : float
            Bulk modulus of fluid (Pa)
        fluid_density : float
            Fluid density (kg/m³)
        """
        self.material = pipe_material
        self.K = fluid_bulk_modulus
        self.rho = fluid_density
        
        # Material properties (Young's modulus in Pa)
        self.material_properties = {
            'Copper': {'E': 110e9, 'nu': 0.35},
            'PEX-B': {'E': 0.8e9, 'nu': 0.46},
            'CPVC': {'E': 3.4e9, 'nu': 0.40}
        }
        
    def calculate_wave_speed(self, diameter: float, wall_thickness: float,
                           pipe_material: str = None) -> float:
        """
        Calculate pressure wave speed using Korteweg-Joukowsky formula.
        
        Parameters
        ----------
        diameter : float
            Internal pipe diameter (m)
        wall_thickness : float
            Pipe wall thickness (m)
        pipe_material : str, optional
            Override default material
            
        Returns
        -------
        float
            Wave speed (m/s)
        """
        material = pipe_material or self.material
        
        if material not in self.material_properties:
            # Rigid pipe assumption
            return math.sqrt(self.K / self.rho)
            
        props = self.material_properties[material]
        E = props['E']  # Young's modulus
        nu = props['nu']  # Poisson's ratio
        
        # Anchored pipe constraint factor
        C = 1 - nu**2
        
        # Korteweg-Joukowsky formula
        # Ensure minimum wall thickness for realistic calculations
        e = max(wall_thickness, 0.0005)  # Minimum 0.5mm wall
        denominator = 1 + (self.K * diameter * C) / (E * e)
        a = math.sqrt(self.K / self.rho) / math.sqrt(denominator)
        
        # Realistic bounds for wave speed in water pipes
        return max(200, min(a, 1400))  # Between 200-1400 m/s
        
    def joukowsky_pressure(self, velocity_change: float, 
                          wave_speed: float) -> float:
        """
        Calculate pressure surge using Joukowsky equation.
        
        Parameters
        ----------
        velocity_change : float
            Change in velocity (m/s)
        wave_speed : float
            Wave speed (m/s)
            
        Returns
        -------
        float
            Pressure change (Pa)
        """
        # Joukowsky equation: ΔP = ρ * a * ΔV
        return self.rho * wave_speed * abs(velocity_change)
        
    def critical_closure_time(self, pipe_length: float,
                            wave_speed: float) -> float:
        """
        Calculate critical valve closure time.
        
        Parameters
        ----------
        pipe_length : float
            Length of pipe (m)
        wave_speed : float
            Pressure wave speed (m/s)
            
        Returns
        -------
        float
            Critical time (s)
        """
        return 2 * pipe_length / wave_speed
        
    def valve_operation_surge(self, initial_velocity: float,
                             closure_time: float,
                             pipe_length: float,
                             diameter: float,
                             wall_thickness: float) -> Dict[str, float]:
        """
        Calculate surge from valve operation.
        
        Parameters
        ----------
        initial_velocity : float
            Initial flow velocity (m/s)
        closure_time : float
            Time to close valve (s)
        pipe_length : float
            Pipe length (m)
        diameter : float
            Pipe diameter (m)
        wall_thickness : float
            Wall thickness (m)
            
        Returns
        -------
        dict
            Surge characteristics
        """
        wave_speed = self.calculate_wave_speed(diameter, wall_thickness)
        critical_time = self.critical_closure_time(pipe_length, wave_speed)
        
        if closure_time <= critical_time:
            # Rapid closure - full Joukowsky surge
            pressure_surge = self.joukowsky_pressure(initial_velocity, wave_speed)
        else:
            # Slow closure - reduced surge
            reduction = critical_time / closure_time
            pressure_surge = self.joukowsky_pressure(initial_velocity, wave_speed) * reduction
            
        return {
            'pressure_surge_pa': pressure_surge,
            'pressure_surge_psi': pressure_surge * 0.000145038,
            'wave_speed_ms': wave_speed,
            'critical_time_s': critical_time,
            'closure_time_s': closure_time
        }


# Utility functions
def water_density(temperature_c: float) -> float:
    """
    Calculate water density as function of temperature.
    
    Parameters
    ----------
    temperature_c : float
        Water temperature (°C)
        
    Returns
    -------
    float
        Density (kg/m³)
    """
    T = max(0, min(40, temperature_c))
    return 999.8395 + 0.0673952*T - 0.00909529*T**2 + 0.000100685*T**3