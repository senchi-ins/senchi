"""
temperature.py
--------------
Heat transfer modeling for water temperature in distribution pipes.

Calculates water temperature at sensor location based on:
- Supply temperature from municipal main
- Ambient temperature in building
- Pipe thermal properties
- Flow velocity and residence time
- Heat transfer through pipe walls
"""

import numpy as np
import math
from typing import Optional, Dict, Any


class TemperatureModel:
    """Models heat transfer in residential water distribution pipes."""
    
    def __init__(self, 
                 supply_temp_C: float = 10.0,
                 ambient_temp_C: float = 18.0,
                 pipe_material: str = "Copper",
                 pipe_diameter_m: float = 0.01905):
        """
        Initialize temperature model.
        
        Parameters
        ----------
        supply_temp_C : float
            Municipal supply water temperature (°C)
        ambient_temp_C : float
            Building ambient temperature (°C)
        pipe_material : str
            Pipe material for heat transfer coefficient
        pipe_diameter_m : float
            Internal pipe diameter (m)
        """
        self.T_supply = supply_temp_C
        self.T_ambient = ambient_temp_C
        self.pipe_material = pipe_material
        self.d_inner = pipe_diameter_m
        
        # Heat transfer coefficients by material (W/m²·K)
        self.heat_transfer_coeffs = {
            "Copper": 10.0,
            "PEX-B": 3.0,
            "PEX": 3.0,
            "CPVC": 2.5,
        }
        self.H_INDOOR = self.heat_transfer_coeffs.get(pipe_material, 5.0)
        
        # Water properties
        self.rho = 999.77  # kg/m³ - density of water at 10°C
        self.c_water = 4184.0  # J/kg·K - heat capacity of water
        
        # For zero-flow exponential cooling
        self.cooling_time_constant = 3600.0  # seconds (1 hour)
        
    def calculate_temperature(self,
                            flow_m3s: np.ndarray,
                            velocity_ms: np.ndarray,
                            pipe_length_m: float,
                            resolution_seconds: float) -> np.ndarray:
        """
        Calculate water temperature at sensor location.
        
        Parameters
        ----------
        flow_m3s : np.ndarray
            Volumetric flow rate (m³/s) time series
        velocity_ms : np.ndarray
            Water velocity (m/s) time series
        pipe_length_m : float
            Total pipe length from supply to sensor (m)
        resolution_seconds : float
            Time step between samples (s)
            
        Returns
        -------
        np.ndarray
            Water temperature (°C) time series
        """
        n_steps = len(flow_m3s)
        temp_water = np.full(n_steps, self.T_supply)
        
        # Track stagnant water temperature for zero-flow periods
        stagnant_temp = self.T_supply
        stagnant_start_time = None
        
        for i in range(n_steps):
            Q = flow_m3s[i]
            
            if Q > 1e-9:  # Active flow
                # Reset stagnant tracking
                stagnant_temp = self.T_supply
                stagnant_start_time = None
                
                # Calculate exponential cooling factor
                beta = (self.H_INDOOR * math.pi * self.d_inner * pipe_length_m) / (
                    self.rho * self.c_water * Q
                )
                
                # Handle extreme values
                if math.isinf(beta) or math.isnan(beta):
                    beta = 1e9
                
                # Temperature estimate with exponential cooling
                temp_water[i] = self.T_ambient + (
                    self.T_supply - self.T_ambient
                ) * math.exp(-beta)
                
            else:  # Zero flow - exponential approach to ambient
                if stagnant_start_time is None:
                    stagnant_start_time = i
                    stagnant_temp = temp_water[i-1] if i > 0 else self.T_supply
                
                # Time since flow stopped
                stagnant_duration = (i - stagnant_start_time) * resolution_seconds
                
                # Exponential decay to ambient temperature
                decay_factor = math.exp(-stagnant_duration / self.cooling_time_constant)
                temp_water[i] = self.T_ambient + (
                    stagnant_temp - self.T_ambient
                ) * decay_factor
        
        return temp_water
    
    def get_seasonal_supply_temperature(self, month: int) -> float:
        """
        Get seasonally-adjusted supply temperature.
        
        Parameters
        ----------
        month : int
            Month of year (1-12)
            
        Returns
        -------
        float
            Supply temperature (°C)
        """
        # Seasonal variation in groundwater/municipal supply temperature
        if month in [12, 1, 2]:  # Winter
            return self.T_supply - 2.0
        elif month in [6, 7, 8]:  # Summer  
            return self.T_supply + 3.0
        else:  # Spring/Fall
            return self.T_supply

    # -------------------------------------------------------------
    # NEW: Seasonal indoor/ambient temperature helper
    # -------------------------------------------------------------
    def get_seasonal_ambient_temperature(self, month: int) -> float:
        """Return typical indoor ambient temperature (°C) for season."""
        if month in {12, 1, 2}:  # Winter
            return 16.0
        elif month in {6, 7, 8}:  # Summer
            return 19.0
        else:  # Spring / Fall
            return 18.0
    
    @classmethod
    def from_house_profile(cls, 
                          profile_data: Dict[str, Any],
                          month: int = 6) -> 'TemperatureModel':
        """
        Create temperature model from house profile configuration.
        
        Parameters
        ----------
        profile_data : dict
            House profile characteristics
        month : int
            Month for seasonal adjustment
            
        Returns
        -------
        TemperatureModel
            Configured temperature model
        """
        main_dist = profile_data.get("main_distribution", {})

        pipe_material = main_dist.get("material", "Copper")
        pipe_diameter_mm = main_dist.get("diameter_mm", 19.05)

        # Create model with default baseline values; seasonals applied below
        model = cls(
            pipe_material=pipe_material,
            pipe_diameter_m=pipe_diameter_mm / 1000.0,
        )
        
        # Apply seasonal adjustment
        model.T_supply = model.get_seasonal_supply_temperature(month)

        # Apply seasonal ambient adjustment (new helper)
        model.T_ambient = model.get_seasonal_ambient_temperature(month)
        
        return model



def estimate_pipe_length_to_sensor(wn: Optional[object] = None) -> float:
    """
    Estimate pipe length from StreetConnection to main sensor location.
    
    Assumes supply temperature is measured at StreetConnection (first contact
    with home plumbing network), so only includes internal distribution.
    
    Parameters
    ----------
    wn : wntr.network.WaterNetworkModel, optional
        Water network model to extract actual pipe lengths from
        
    Returns
    -------
    float
        Total length from StreetConnection to sensor (m)
    """
    # Default lengths if network lookup fails
    to_meter_default = 2.0       # StreetConnection to Meter
    main_supply_default = 6.0    # Meter to Manifold (sensor location)
    
    if wn is not None:
        try:
            # Look up actual pipe lengths from network model
            to_meter_length = to_meter_default
            main_supply_length = main_supply_default
            
            # Get ToMeter pipe length
            if "ToMeter" in wn.pipe_name_list:
                to_meter_pipe = wn.get_link("ToMeter")
                to_meter_length = getattr(to_meter_pipe, "length", to_meter_default)
            
            # Get MainSupply pipe length  
            if "MainSupply" in wn.pipe_name_list:
                main_supply_pipe = wn.get_link("MainSupply")
                main_supply_length = getattr(main_supply_pipe, "length", main_supply_default)
            
            return to_meter_length + main_supply_length
            
        except Exception:
            # Fall back to defaults if lookup fails
            pass
    
    return to_meter_default + main_supply_default  # ~8m total

# -----------------------------------------------------------------------------
# Acoustics helper
# -----------------------------------------------------------------------------
def speed_of_sound_water(temperature_c: float | np.ndarray) -> float | np.ndarray:
    """
    Calculate the speed of sound in fresh water (m/s) using the empirical
    Marczak (1997) equation.

    Parameters
    ----------
    temperature_c : float or np.ndarray
        Water temperature in °C.

    Returns
    -------
    float or np.ndarray
        Speed of sound in water at the given temperature(s) in metres per second.
    """
    temp = np.asarray(temperature_c, dtype=float)
    return 1404.3 + 4.7 * temp - 0.04 * temp ** 2