"""
transient_events.py
-------------------
TSNet wrapper for sub-second pressure transient simulation.
"""

import tsnet
import wntr
import numpy as np
import pandas as pd
from typing import Dict, Optional, Tuple, List


class TransientSimulator:
    """
    High-fidelity transient simulation using TSNet.
    """
    
    def __init__(self, wn: wntr.network.WaterNetworkModel):
        """Initialize with WNTR network model."""
        self.wn = wn
        self.tm = None
        self.results = None
        
    def setup_model(self, duration: float, dt: float = 0.01) -> tsnet.network.TransientModel:
        """
        Setup TSNet transient model.
        
        Parameters
        ----------
        duration : float
            Simulation period (seconds)
        dt : float
            Time step (seconds)
        """
        self.tm = tsnet.network.TransientModel(self.wn)
        self.tm.simulation_period = duration
        
        # Ensure stability with Courant condition
        if self.wn.pipes:
            min_length = min([p.length for _, p in self.wn.pipes()])
            max_dt = 0.5 * min_length / 1200  # Assume wave speed ~1200 m/s
            dt = min(dt, max_dt)
            
        self.tm.time_step = dt
        return self.tm
        
    def add_valve_closure(self, valve: str, t_start: float, t_end: float) -> None:
        """Add valve closure event (linear profile)."""
        if self.tm is None:
            raise RuntimeError("Call setup_model first")
            
        valve_obj = self.tm.get_node(valve)
        valve_obj.valve_coeff = [1, 0]  # Open to closed
        valve_obj.valve_curve = [t_start, t_end]
        
    def add_burst(self, node: str, t_burst: float, area: float) -> None:
        """Add burst event at node."""
        if self.tm is None:
            raise RuntimeError("Call setup_model first")
            
        node_obj = self.tm.get_node(node)
        # Emitter coefficient: k = Cd * A * sqrt(2g)
        k = 0.75 * area * np.sqrt(2 * 9.81)
        node_obj.emitter_coeff = [0, 0, k, k]
        node_obj.emitter_curve = [0, t_burst-0.001, t_burst, self.tm.simulation_period]
        
    def run(self) -> pd.DataFrame:
        """Run transient simulation and return results."""
        if self.tm is None:
            raise RuntimeError("Call setup_model first")
            
        # Run TSNet
        self.tm = tsnet.simulation.MOCSimulator(self.tm)
        
        # Extract results
        times = np.arange(0, self.tm.simulation_period + self.tm.time_step, 
                         self.tm.time_step)
        data = []
        
        for t_idx, t in enumerate(times):
            row = {'time': t}
            
            # Node pressures
            for node_name in self.tm.node_name_list:
                node = self.tm.get_node(node_name)
                if hasattr(node, 'head_results'):
                    head = node.head_results[t_idx] if t_idx < len(node.head_results) else 0
                    pressure = head - node.elevation  # Convert to pressure
                    row[f'P_{node_name}'] = pressure
                    
            # Link flows
            for link_name in self.tm.link_name_list:
                link = self.tm.get_link(link_name)
                if hasattr(link, 'flow_results'):
                    flow = link.flow_results[t_idx] if t_idx < len(link.flow_results) else 0
                    row[f'Q_{link_name}'] = flow
                    
                    # Velocity
                    if hasattr(link, 'diameter') and link.diameter > 0:
                        area = np.pi * (link.diameter/2)**2
                        row[f'V_{link_name}'] = flow / area if area > 0 else 0
                        
            data.append(row)
            
        self.results = pd.DataFrame(data)
        return self.results
        
    def get_trace(self, element: str, variable: str = 'P') -> Tuple[np.ndarray, np.ndarray]:
        """
        Get time series for element.
        
        Parameters
        ----------
        element : str
            Node or link name
        variable : str
            'P' for pressure, 'Q' for flow, 'V' for velocity
        """
        if self.results is None:
            raise RuntimeError("Run simulation first")
            
        col = f'{variable}_{element}'
        if col not in self.results.columns:
            raise ValueError(f"{col} not in results")
            
        return self.results['time'].values, self.results[col].values


def quick_transient(wn: wntr.network.WaterNetworkModel,
                   event_type: str,
                   **kwargs) -> pd.DataFrame:
    """
    Quick transient simulation.
    
    Parameters
    ----------
    wn : wntr.network.WaterNetworkModel
        Network model
    event_type : str
        'leak' or 'valve'
    **kwargs : dict
        Event parameters
        
    Returns
    -------
    pd.DataFrame
        Results
    """
    sim = TransientSimulator(wn)
    sim.setup_model(kwargs.get('duration', 10.0))
    
    if event_type == 'leak':
        sim.add_burst(kwargs['node'], kwargs['time'], kwargs['area'])
    elif event_type == 'valve':
        sim.add_valve_closure(kwargs['valve'], kwargs['start'], kwargs['end'])
        
    return sim.run()