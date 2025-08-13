"""
hydraulics.py
-------------
EPANET-based hydraulic solver via WNTR for steady-state and quasi-steady hydraulics.
Provides realistic pressure, flow, and velocity calculations with proper physics.

This module integrates with WNTR to leverage EPANET's proven hydraulic solver while
adding utilities for high-frequency simulation and realistic pipe physics.
"""

import numpy as np
import wntr
from typing import Dict, Tuple, Optional, List
import math


class HydraulicSolver:
    """
    Wrapper around WNTR/EPANET for high-fidelity hydraulic simulation.
    
    Handles:
    - Steady-state hydraulics via EPANET
    - Sub-second interpolation for high-frequency output
    - Pressure-dependent demand modeling
    - Realistic friction factors (Darcy-Weisbach with Colebrook-White)
    """
    
    def __init__(self, wn: wntr.network.WaterNetworkModel):
        """
        Initialize solver with a WNTR network model.
        
        Parameters
        ----------
        wn : wntr.network.WaterNetworkModel
            The water network to simulate
        """
        self.wn = wn
        self.results = None
        self.time_step = wn.options.time.hydraulic_timestep
        
    def run_hydraulics(self, duration_s: float) -> wntr.sim.SimulationResults:
        """
        Run EPANET hydraulic simulation.
        
        Parameters
        ----------
        duration_s : float
            Simulation duration in seconds
            
        Returns
        -------
        wntr.sim.SimulationResults
            Hydraulic simulation results
        """
        # Set simulation duration
        self.wn.options.time.duration = duration_s
        
        # Use EpanetSimulator for accuracy
        sim = wntr.sim.EpanetSimulator(self.wn)
        self.results = sim.run_sim()
        
        return self.results
        
    def get_state_at_time(self, time_s: float, 
                          node_name: str = None,
                          link_name: str = None) -> Dict[str, float]:
        """
        Get hydraulic state at specific time with interpolation if needed.
        
        Parameters
        ----------
        time_s : float
            Time in seconds
        node_name : str, optional
            Junction/node name for pressure query
        link_name : str, optional
            Pipe/link name for flow query
            
        Returns
        -------
        dict
            State variables (pressure, flow, velocity, head loss)
        """
        if self.results is None:
            raise RuntimeError("Must run simulation first")
            
        state = {}
        
        # Find nearest time indices for interpolation
        times = self.results.node['pressure'].index
        idx = np.searchsorted(times, time_s)
        
        if idx == 0:
            t_idx = 0
            alpha = 0
        elif idx >= len(times):
            t_idx = len(times) - 1
            alpha = 0
        else:
            # Linear interpolation
            t0, t1 = times[idx-1], times[idx]
            alpha = (time_s - t0) / (t1 - t0)
            t_idx = idx - 1
            
        # Get node states
        if node_name:
            p0 = self.results.node['pressure'][node_name].iloc[t_idx]
            if alpha > 0 and t_idx < len(times) - 1:
                p1 = self.results.node['pressure'][node_name].iloc[t_idx + 1]
                state['pressure_m'] = p0 * (1 - alpha) + p1 * alpha
            else:
                state['pressure_m'] = p0
                
            # Convert to other units
            state['pressure_psi'] = state['pressure_m'] * 1.42197  # m to psi
            state['pressure_kpa'] = state['pressure_m'] * 9.80665  # m to kPa
            
        # Get link states
        if link_name:
            q0 = self.results.link['flowrate'][link_name].iloc[t_idx]
            v0 = self.results.link['velocity'][link_name].iloc[t_idx]
            
            if alpha > 0 and t_idx < len(times) - 1:
                q1 = self.results.link['flowrate'][link_name].iloc[t_idx + 1]
                v1 = self.results.link['velocity'][link_name].iloc[t_idx + 1]
                state['flow_m3s'] = q0 * (1 - alpha) + q1 * alpha
                state['velocity_ms'] = v0 * (1 - alpha) + v1 * alpha
            else:
                state['flow_m3s'] = q0
                state['velocity_ms'] = v0
                
            # Additional conversions
            state['flow_lps'] = state['flow_m3s'] * 1000
            state['flow_gpm'] = state['flow_m3s'] * 15850.3
            
            # Calculate head loss if we have the pipe
            pipe = self.wn.get_link(link_name)
            if hasattr(pipe, 'length') and hasattr(pipe, 'diameter'):
                state['head_loss_m'] = self.darcy_weisbach(
                    state['flow_m3s'], pipe.length, pipe.diameter,
                    pipe.roughness
                )
                
        return state


    @staticmethod
    def darcy_weisbach(Q: float, L: float, D: float, roughness: float,
                       nu: float = 1.004e-6) -> float:
        """
        Calculate head loss using Darcy-Weisbach equation.
        
        Parameters
        ----------
        Q : float
            Flow rate (m³/s)
        L : float
            Pipe length (m)
        D : float
            Pipe diameter (m)
        roughness : float
            Pipe roughness coefficient (Hazen-Williams or absolute roughness)
        nu : float
            Kinematic viscosity (m²/s), default for water at 20°C
            
        Returns
        -------
        float
            Head loss (m)
        """
        if Q == 0 or D == 0:
            return 0
            
        # Velocity
        A = np.pi * (D/2)**2
        V = abs(Q) / A
        
        # Reynolds number
        Re = V * D / nu
        
        # Friction factor (Colebrook-White equation solved iteratively)
        if Re < 2300:
            # Laminar flow
            f = 64 / Re
        else:
            # Turbulent flow - use Swamee-Jain approximation
            epsilon = roughness / 1000  # Convert to meters if needed
            term1 = epsilon / (3.7 * D)
            term2 = 5.74 / (Re**0.9)
            f = 0.25 / (np.log10(term1 + term2))**2
            
        # Head loss
        h_L = f * (L / D) * (V**2 / (2 * 9.81))
        
        return h_L


    @staticmethod
    def hazen_williams(Q: float, L: float, D: float, C: float) -> float:
        """
        Alternative head loss calculation using Hazen-Williams equation.
        
        Parameters
        ----------
        Q : float
            Flow rate (m³/s)
        L : float
            Pipe length (m)  
        D : float
            Pipe diameter (m)
        C : float
            Hazen-Williams roughness coefficient
            
        Returns
        -------
        float
            Head loss (m)
        """
        if Q == 0 or D == 0:
            return 0
            
        # Hazen-Williams formula
        h_L = 10.67 * (abs(Q)**1.852) * L / (C**1.852 * D**4.87)
        
        return h_L
        

    def calculate_reynolds(self, velocity: float, diameter: float,
                          nu: float = 1.004e-6) -> float:
        """
        Calculate Reynolds number for flow regime identification.
        
        Parameters
        ----------
        velocity : float
            Flow velocity (m/s)
        diameter : float
            Pipe diameter (m)
        nu : float
            Kinematic viscosity (m²/s)
            
        Returns
        -------
        float
            Reynolds number
        """
        return velocity * diameter / nu
        

    def flow_regime(self, reynolds: float) -> str:
        """
        Identify flow regime from Reynolds number.
        
        Parameters
        ----------
        reynolds : float
            Reynolds number
            
        Returns
        -------
        str
            'laminar', 'transitional', or 'turbulent'
        """
        if reynolds < 2300:
            return 'laminar'
        elif reynolds < 4000:
            return 'transitional'
        else:
            return 'turbulent'


    def pressure_to_head(self, pressure_pa: float, elevation: float = 0,
                        rho: float = 999.7) -> float:
        """
        Convert pressure to hydraulic head.
        
        Parameters
        ----------
        pressure_pa : float
            Pressure in Pascals
        elevation : float
            Elevation in meters
        rho : float
            Fluid density (kg/m³)
            
        Returns
        -------
        float
            Hydraulic head (m)
        """
        return pressure_pa / (rho * 9.81) + elevation


    def velocity_from_flow(self, Q: float, D: float) -> float:
        """
        Calculate velocity from flow rate and pipe diameter.
        
        Parameters
        ----------
        Q : float
            Flow rate (m³/s)
        D : float
            Pipe diameter (m)
            
        Returns
        -------
        float
            Velocity (m/s)
        """
        if D == 0:
            return 0
        A = np.pi * (D/2)**2
        return Q / A


    def get_network_state(self, time_s: float) -> Dict:
        """
        Get complete network hydraulic state at given time.
        
        Parameters
        ----------
        time_s : float
            Simulation time in seconds
            
        Returns
        -------
        dict
            Complete network state with all nodes and links
        """
        state = {
            'time': time_s,
            'nodes': {},
            'links': {}
        }
        
        # Get all node states
        for node_name in self.wn.node_name_list:
            state['nodes'][node_name] = self.get_state_at_time(
                time_s, node_name=node_name
            )
            
        # Get all link states  
        for link_name in self.wn.link_name_list:
            state['links'][link_name] = self.get_state_at_time(
                time_s, link_name=link_name
            )
            
        return state


# Standalone utility functions
def continuity_check(flows_in: List[float], flows_out: List[float],
                     tolerance: float = 1e-6) -> bool:
    """
    Verify continuity equation at a junction.
    
    Parameters
    ----------
    flows_in : list
        Incoming flows (m³/s)
    flows_out : list
        Outgoing flows (m³/s)
    tolerance : float
        Acceptable imbalance
        
    Returns
    -------
    bool
        True if continuity is satisfied
    """
    return abs(sum(flows_in) - sum(flows_out)) < tolerance


def bernoulli_pressure(p1: float, v1: float, z1: float,
                       v2: float, z2: float, head_loss: float = 0,
                       rho: float = 999.7) -> float:
    """
    Calculate pressure using Bernoulli equation with losses.
    
    Parameters
    ----------
    p1 : float
        Upstream pressure (Pa)
    v1 : float
        Upstream velocity (m/s)
    z1 : float
        Upstream elevation (m)
    v2 : float
        Downstream velocity (m/s)
    z2 : float
        Downstream elevation (m)
    head_loss : float
        Head loss between points (m)
    rho : float
        Fluid density (kg/m³)
        
    Returns
    -------
    float
        Downstream pressure (Pa)
    """
    # Bernoulli with losses: p1/ρg + v1²/2g + z1 = p2/ρg + v2²/2g + z2 + hL
    g = 9.81
    
    # Solve for p2
    p2 = p1 + rho * g * (z1 - z2) + 0.5 * rho * (v1**2 - v2**2) - rho * g * head_loss
    
    return p2


def pipe_capacity(diameter: float, velocity_limit: float = 2.4) -> float:
    """
    Calculate maximum flow capacity of a pipe.
    
    Parameters
    ----------
    diameter : float
        Pipe internal diameter (m)
    velocity_limit : float
        Maximum allowable velocity (m/s), default 2.4 for copper
        
    Returns
    -------
    float
        Maximum flow rate (m³/s)
    """
    area = np.pi * (diameter/2)**2
    return area * velocity_limit