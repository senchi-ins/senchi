#!/usr/bin/env python3
"""
EPANET/WNTR Low-Fidelity Plumbing Leak Simulation
==================================================

This script creates a comprehensive residential plumbing network model based on
typical single-detached home specifications and runs Monte-Carlo leak
scenarios for leak prognosis training data.

Based on layout.md specifications and plan.md requirements.
"""

import wntr
from wntr.morph import split_pipe
import numpy as np
import pandas as pd
import json
import os
import math
import random
from datetime import datetime, timedelta
from pathlib import Path
from typing import Dict, List, Tuple, Optional
import logging
import matplotlib.pyplot as plt
import networkx as nx

# Import configuration
from config import *

# Configure logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

class HomePlumbingNetwork:
    """
    Models a typical single-detached home plumbing system
    based on layout.md specifications.
    """
    
    def __init__(self, supply_pressure_kpa: float = DEFAULT_SUPPLY_PRESSURE_KPA):
        """
        Initialize the plumbing network.
        
        Args:
            supply_pressure_kpa: Municipal water supply pressure (default from config)
        """
        self.supply_pressure_kpa = supply_pressure_kpa
        self.network = wntr.network.WaterNetworkModel()
        self._build_network()
        
    def _build_network(self):
        """Build the complete plumbing network based on layout.md specifications."""
        
        # Create nodes (fixtures and junctions)
        self._create_nodes()
        
        # Create pipes (supply and drain)
        self._create_pipes()
        
        # Create pumps and valves
        self._create_controls()
        
        # Set demand patterns
        self._set_demand_patterns()
        
        # Set simulation parameters
        self._set_simulation_params()
        
    def _create_nodes(self):
        """Create all nodes in the plumbing system."""
        
        # Service entry point (main shutoff valve location - SENSOR LOCATION)
        self.network.add_junction('SERVICE_ENTRY', base_demand=0, elevation=0)
        
        # Main floor fixtures
        self.network.add_junction('KITCHEN_SINK', base_demand=0, elevation=0)
        self.network.add_junction('DISHWASHER', base_demand=0, elevation=0)
        self.network.add_junction('POWDER_ROOM_WC', base_demand=0, elevation=0)
        self.network.add_junction('POWDER_ROOM_LAV', base_demand=0, elevation=0)
        self.network.add_junction('HOSE_BIBB_FRONT', base_demand=0, elevation=0)
        self.network.add_junction('HOSE_BIBB_BACK', base_demand=0, elevation=0)
        
        # Upper floor fixtures
        self.network.add_junction('ENSUITE_WC', base_demand=0, elevation=3.0)  # 3m elevation
        self.network.add_junction('ENSUITE_LAV', base_demand=0, elevation=3.0)
        self.network.add_junction('ENSUITE_SHOWER', base_demand=0, elevation=3.0)
        self.network.add_junction('FAMILY_BATH_WC', base_demand=0, elevation=3.0)
        self.network.add_junction('FAMILY_BATH_LAV', base_demand=0, elevation=3.0)
        self.network.add_junction('FAMILY_BATH_TUB', base_demand=0, elevation=3.0)
        
        # Basement fixtures
        self.network.add_junction('LAUNDRY_SINK', base_demand=0, elevation=-2.5)  # -2.5m elevation
        self.network.add_junction('WATER_HEATER', base_demand=0, elevation=-2.5)
        
        # Junction nodes for pipe routing
        self.network.add_junction('MAIN_TRUNK_1', base_demand=0, elevation=0)
        self.network.add_junction('MAIN_TRUNK_2', base_demand=0, elevation=0)
        self.network.add_junction('UPPER_FLOOR_BRANCH', base_demand=0, elevation=1.5)
        self.network.add_junction('KITCHEN_BRANCH', base_demand=0, elevation=0)
        self.network.add_junction('POWDER_ROOM_BRANCH', base_demand=0, elevation=0)
        
        # Reservoir (municipal water supply)
        self.network.add_reservoir('MUNICIPAL_SUPPLY', base_head=self.supply_pressure_kpa * 0.102, 
                                  coordinates=(0, 0))
        
    def _create_pipes(self):
        """Create all pipes in the plumbing system."""
        
        # Service line (municipal to house)
        self.network.add_pipe('SERVICE_LINE', 'MUNICIPAL_SUPPLY', 'SERVICE_ENTRY',
                             length=10, diameter=0.025, roughness=100, minor_loss=0)
        
        # Main trunk (3/4" PEX)
        # self.network.add_pipe('MAIN_TRUNK_1', 'SERVICE_ENTRY', 'MAIN_TRUNK_1',
        #                      length=5, diameter=0.019, roughness=100, minor_loss=0)
        self.network.add_pipe('MAIN_TRUNK_2', 'MAIN_TRUNK_1', 'MAIN_TRUNK_2',
                             length=8, diameter=0.019, roughness=100, minor_loss=0)
        
        # Kitchen branch (1/2" PEX)
        self.network.add_pipe('KITCHEN_BRANCH', 'MAIN_TRUNK_1', 'KITCHEN_BRANCH',
                             length=3, diameter=0.0127, roughness=100, minor_loss=0)
        self.network.add_pipe('KITCHEN_SINK_RUN', 'KITCHEN_BRANCH', 'KITCHEN_SINK',
                             length=2, diameter=0.0127, roughness=100, minor_loss=0)
        self.network.add_pipe('DISHWASHER_RUN', 'KITCHEN_BRANCH', 'DISHWASHER',
                             length=1.5, diameter=0.0127, roughness=100, minor_loss=0)
        
        # Powder room branch (1/2" PEX)
        self.network.add_pipe('POWDER_ROOM_BRANCH', 'MAIN_TRUNK_1', 'POWDER_ROOM_BRANCH',
                             length=4, diameter=0.0127, roughness=100, minor_loss=0)
        self.network.add_pipe('POWDER_WC_RUN', 'POWDER_ROOM_BRANCH', 'POWDER_ROOM_WC',
                             length=2, diameter=0.0127, roughness=100, minor_loss=0)
        self.network.add_pipe('POWDER_LAV_RUN', 'POWDER_ROOM_BRANCH', 'POWDER_ROOM_LAV',
                             length=1.5, diameter=0.0127, roughness=100, minor_loss=0)
        
        # Upper floor branch (1/2" PEX)
        self.network.add_pipe('UPPER_FLOOR_BRANCH', 'MAIN_TRUNK_2', 'UPPER_FLOOR_BRANCH',
                             length=6, diameter=0.0127, roughness=100, minor_loss=0)
        
        # Ensuite fixtures (1/2" PEX)
        self.network.add_pipe('ENSUITE_WC_RUN', 'UPPER_FLOOR_BRANCH', 'ENSUITE_WC',
                             length=3, diameter=0.0127, roughness=100, minor_loss=0)
        self.network.add_pipe('ENSUITE_LAV_RUN', 'UPPER_FLOOR_BRANCH', 'ENSUITE_LAV',
                             length=2.5, diameter=0.0127, roughness=100, minor_loss=0)
        self.network.add_pipe('ENSUITE_SHOWER_RUN', 'UPPER_FLOOR_BRANCH', 'ENSUITE_SHOWER',
                             length=2, diameter=0.0127, roughness=100, minor_loss=0)
        
        # Family bath fixtures (1/2" PEX)
        self.network.add_pipe('FAMILY_BATH_WC_RUN', 'UPPER_FLOOR_BRANCH', 'FAMILY_BATH_WC',
                             length=4, diameter=0.0127, roughness=100, minor_loss=0)
        self.network.add_pipe('FAMILY_BATH_LAV_RUN', 'UPPER_FLOOR_BRANCH', 'FAMILY_BATH_LAV',
                             length=3.5, diameter=0.0127, roughness=100, minor_loss=0)
        self.network.add_pipe('FAMILY_BATH_TUB_RUN', 'UPPER_FLOOR_BRANCH', 'FAMILY_BATH_TUB',
                             length=3, diameter=0.0127, roughness=100, minor_loss=0)
        
        # Basement fixtures (1/2" PEX)
        self.network.add_pipe('LAUNDRY_RUN', 'MAIN_TRUNK_2', 'LAUNDRY_SINK',
                             length=5, diameter=0.0127, roughness=100, minor_loss=0)
        self.network.add_pipe('WATER_HEATER_RUN', 'MAIN_TRUNK_2', 'WATER_HEATER',
                             length=3, diameter=0.0127, roughness=100, minor_loss=0)
        
        # Hose bibbs (1/2" PEX)
        self.network.add_pipe('HOSE_BIBB_FRONT_RUN', 'MAIN_TRUNK_1', 'HOSE_BIBB_FRONT',
                             length=8, diameter=0.0127, roughness=100, minor_loss=0)
        self.network.add_pipe('HOSE_BIBB_BACK_RUN', 'MAIN_TRUNK_2', 'HOSE_BIBB_BACK',
                             length=6, diameter=0.0127, roughness=100, minor_loss=0)
        
    def _create_controls(self):
        """Create pressure reducing valve and other controls."""
        
        # Pressure Reducing Valve (PRV) at service entry
        # Typical residential PRV reduces from 400-550 kPa to 275-350 kPa
        self.network.add_valve('PRV_MAIN', 'SERVICE_ENTRY', 'MAIN_TRUNK_1',
                              valve_type='PRV')
        
        # Set the valve setting after creation
        valve = self.network.get_link('PRV_MAIN')
        valve.initial_setting = TARGET_PRV_PRESSURE_KPA * 0.102
        
    def _set_demand_patterns(self):
        """Set realistic demand patterns for residential fixtures."""
        
                # Add demand patterns from config
        for pattern_name, pattern_values in DEMAND_PATTERNS.items():
            self.network.add_pattern(pattern_name, pattern_values)
        
        # Apply demands with patterns from config
        for node_name, base_demand in FIXTURE_DEMANDS.items():
            if node_name in self.network.nodes():
                node = self.network.get_node(node_name)
                node.base_demand = base_demand
                # Randomly assign patterns to create variety
                patterns = list(DEMAND_PATTERNS.keys())
                node.demand_pattern = random.choice(patterns)
        
    def _set_simulation_params(self):
        """Set simulation parameters for 24-hour extended period simulation."""
        
        # Set simulation parameters from config
        self.network.options.time.duration = SIMULATION_DURATION_HOURS * 3600  # hours to seconds
        self.network.options.time.hydraulic_timestep = TIME_STEP_SECONDS
        self.network.options.time.quality_timestep = TIME_STEP_SECONDS
        self.network.options.time.pattern_timestep = PATTERN_TIMESTEP_HOURS * 3600  # hours to seconds
        
        # Hydraulic solver options
        self.network.options.hydraulic.demand_model = 'DDA'  # Pressure Dependent Demand
        self.network.options.hydraulic.headloss = 'H-W'  # Hazen-Williams
        
    def visualize_network(self, save_path: Optional[str] = None, figsize: Tuple[int, int] = (15, 10)):
        """
        Visualize the plumbing network layout.
        
        Args:
            save_path: Optional path to save the visualization
            figsize: Figure size as (width, height) tuple
        """
        # Create figure
        plt.figure(figsize=figsize)
        
        # Get the network graph
        G = self.network.get_graph()
        
        # Set up the node positions using spring layout for better visualization
        pos = nx.spring_layout(G, k=1, iterations=50)
        
        # Draw nodes
        node_sizes = []
        node_colors = []
        labels = {}
        
        for node_name in G.nodes():
            node = self.network.get_node(node_name)
            
            # Size based on node type
            if node_name == 'MUNICIPAL_SUPPLY':
                node_sizes.append(300)
                node_colors.append('blue')
            elif 'TRUNK' in node_name:
                node_sizes.append(200)
                node_colors.append('gray')
            else:
                node_sizes.append(150)
                node_colors.append('lightblue')
            
            # Create labels
            if node.node_type == 'Junction':
                labels[node_name] = node_name.replace('_', '\n')
            else:
                labels[node_name] = f"{node_name}\n({node.node_type})"
        
        # Draw the network
        nx.draw_networkx_nodes(G, pos, node_size=node_sizes, node_color=node_colors, alpha=0.7)
        nx.draw_networkx_edges(G, pos, edge_color='gray', width=1, alpha=0.5)
        nx.draw_networkx_labels(G, pos, labels, font_size=8)
        
        # Add title and adjust layout
        plt.title('Residential Plumbing Network Layout', pad=20)
        plt.axis('off')
        plt.tight_layout()
        
        # Save if path provided
        if save_path:
            plt.savefig(save_path, dpi=300, bbox_inches='tight')
            print(f"Network visualization saved to: {save_path}")
        
        plt.show()

    def inject_leak(self, pipe_name: str, start_time: int, leak_area: float,  
                   duration: int = 1800) -> None:
        """
        Inject a leak into the specified pipe by cloning and splitting the network
        and then adding a leak to the new junction.
        
        Args:
            pipe_name: Name of the pipe to leak
            start_time: Start time in seconds
            leak_area: Leak area in m²
            duration: Duration of leak in seconds (default 30 minutes)
        """
        # Name for the new junction and the new pipe segment
        leak_node = f"leak_{pipe_name}"  
        new_pipe = f"{pipe_name}_after_leak"

        # 1) Clone the network and split the pipe at halfway, inserting our leak-junction
        self.network = split_pipe(
            self.network,
            pipe_name,            # original pipe to split
            new_pipe,             # name for the new downstream segment
            leak_node,            # name for the junction where leak will occur
            add_pipe_at_end=True,  # keep original pipe as upstream segment
            split_at_point=0.5,    # split at midpoint
            return_copy=True      # return a new WaterNetworkModel
        )

        # 2) Attach the leak on the newly created junction in the cloned network
        junc = self.network.get_node(leak_node)
        junc.add_leak(
            self.network,
            area=leak_area,                   # leak area in m²
            start_time=start_time,            # leak start time (s)
            end_time=start_time + duration    # leak end time (s)
        )

        
    def run_simulation(self) -> Tuple[pd.DataFrame, Dict]:
        """
        Run the hydraulic simulation.
        
        Returns:
            Tuple of (results DataFrame, metadata dict)
        """
        
        print("Creating simulator...")
        sim = wntr.sim.WNTRSimulator(self.network)
        
        print("Starting simulation...")
        try:
            results = sim.run_sim()
            print("Simulation completed!")
        except Exception as e:
            print(f"Simulation failed: {e}")
            # Try to get more info about the network state
            print(f"Network has {self.network.num_nodes} nodes and {self.network.num_links} links")
            print(f"Simulation duration: {self.network.options.time.duration} seconds")
            print(f"Time step: {self.network.options.time.hydraulic_timestep} seconds")
            raise
        
        # Extract pressure and flow data at the sensor location (SERVICE_ENTRY)
        sensor_data = pd.DataFrame({
            'timestamp': results.node['pressure'].index,
            'pressure_kpa': results.node['pressure']['SERVICE_ENTRY'] * 9.81,  # Convert m to kPa
            'flow_lps': results.link['flowrate']['SERVICE_LINE'] * 1000,  # Convert m³/s to L/s
        })
        
        # Add metadata
        metadata = {
            'supply_pressure_kpa': self.supply_pressure_kpa,
            'simulation_duration_hours': SIMULATION_DURATION_HOURS,
            'time_step_seconds': TIME_STEP_SECONDS,
            'total_nodes': self.network.num_nodes,
            'total_pipes': self.network.num_links,
            'sensor_location': SENSOR_LOCATION,
        }
        
        return sensor_data, metadata


class MonteCarloLeakSimulator:
    """
    Runs Monte-Carlo simulations with varying leak parameters.
    """
    
    def __init__(self, output_dir: str = OUTPUT_DIRS['raw_data']):
        self.output_dir = Path(output_dir)
        self.output_dir.mkdir(parents=True, exist_ok=True)
        
        # Leak parameter ranges from config
        self.leak_areas_mm = LEAK_AREAS_MM
        self.supply_pressures_kpa = SUPPLY_PRESSURES_KPA
        self.leak_start_times = [t * 3600 for t in LEAK_START_TIMES_HOURS]  # Convert to seconds
        self.leak_durations = [d * 60 for d in LEAK_DURATIONS_MINUTES]  # Convert to seconds
        
        # Pipe materials from config
        self.pipe_materials = PIPE_MATERIALS
        
        # Leak locations from config
        self.leak_locations = LEAK_LOCATIONS
        
        # Store all scenario metadata
        self.scenarios = []
        
    def generate_scenarios(self, num_scenarios: int = 10000) -> List[Dict]:
        """
        Generate Monte-Carlo scenarios.
        
        Args:
            num_scenarios: Number of scenarios to generate
            
        Returns:
            List of scenario parameter dictionaries
        """
        
        scenarios = []
        
        for i in range(num_scenarios):
            # Randomly select parameters
            leak_area_mm = random.choice(self.leak_areas_mm)
            leak_area_m2 = math.pi * (leak_area_mm / 2000) ** 2  # Convert mm to m²
            
            supply_pressure = random.choice(self.supply_pressures_kpa)
            leak_start_time = random.choice(self.leak_start_times)
            leak_duration = random.choice(self.leak_durations)
            leak_location = random.choice(self.leak_locations)
            pipe_material = random.choice(list(self.pipe_materials.keys()))
            
            # Healthy scenario ratio from config
            has_leak = random.random() > HEALTHY_SCENARIO_RATIO
            
            scenario = {
                'scenario_id': f"run_{i+1:05d}",
                'leak_area_mm': leak_area_mm if has_leak else 0.0,
                'leak_area_m2': leak_area_m2 if has_leak else 0.0,
                'supply_pressure_kpa': supply_pressure,
                'leak_start_time_seconds': leak_start_time if has_leak else None,
                'leak_duration_seconds': leak_duration if has_leak else None,
                'leak_location': leak_location if has_leak else None,
                'pipe_material': pipe_material,
                'has_leak': has_leak,
                'leak_type': 'horizontal_pipe' if has_leak else 'none',
            }
            
            scenarios.append(scenario)
            
        return scenarios
    
    def run_scenario(self, scenario: Dict) -> Tuple[pd.DataFrame, Dict]:
        """
        Run a single scenario simulation.
        
        Args:
            scenario: Scenario parameter dictionary
            
        Returns:
            Tuple of (sensor data DataFrame, metadata dict)
        """
        
        # Create network with specified parameters
        network = HomePlumbingNetwork(
            supply_pressure_kpa=scenario['supply_pressure_kpa']
        )
        
        # Update pipe material roughness if specified
        if scenario['pipe_material'] != 'PEX':
            for link_name, link in network.network.links():
                if link.link_type == 'Pipe':
                    link.roughness = self.pipe_materials[scenario['pipe_material']]
        
        # Inject leak if specified
        if scenario['has_leak']:
            network.inject_leak(
                pipe_name=scenario['leak_location'],
                start_time=scenario['leak_start_time_seconds'],
                leak_area=scenario['leak_area_m2'],
                duration=scenario['leak_duration_seconds']
            )
        
        # Run simulation
        sensor_data, metadata = network.run_simulation()
        
        # Add scenario metadata
        metadata.update(scenario)
        
        return sensor_data, metadata
    
    def run_all_scenarios(self, num_scenarios: int = 10000, 
                         batch_size: int = 100) -> None:
        """
        Run all Monte-Carlo scenarios and save results.
        
        Args:
            num_scenarios: Number of scenarios to run
            batch_size: Number of scenarios to process in each batch
        """
        
        logger.info(f"Generating {num_scenarios} Monte-Carlo scenarios...")
        scenarios = self.generate_scenarios(num_scenarios)
        
        # Save scenarios metadata
        scenarios_file = Path(OUTPUT_DIRS['metadata']) / "scenarios.json"
        scenarios_file.parent.mkdir(parents=True, exist_ok=True)
        
        with open(scenarios_file, 'w') as f:
            json.dump(scenarios, f, indent=2)
        
        logger.info(f"Saved scenarios metadata to {scenarios_file}")
        
        # Process scenarios in batches
        for batch_start in range(0, len(scenarios), batch_size):
            batch_end = min(batch_start + batch_size, len(scenarios))
            batch_scenarios = scenarios[batch_start:batch_end]
            
            logger.info(f"Processing batch {batch_start//batch_size + 1}: "
                       f"scenarios {batch_start+1}-{batch_end}")
            
            for scenario in batch_scenarios:
                try:
                    # Run simulation
                    sensor_data, metadata = self.run_scenario(scenario)
                    
                    # Save results
                    output_file = self.output_dir / f"{scenario['scenario_id']}.csv"
                    sensor_data.to_csv(output_file, index=False)
                    
                    logger.debug(f"Saved {output_file}")
                    
                except Exception as e:
                    logger.error(f"Error in scenario {scenario['scenario_id']}: {e}")
                    continue
        
        logger.info(f"Completed {num_scenarios} simulations. "
                   f"Results saved to {self.output_dir}")


def main():
    """Main execution function."""
    
    # Set random seed for reproducibility
    random.seed(42)
    np.random.seed(42)
    
    # Create simulator
    simulator = MonteCarloLeakSimulator()
    
    # Run simulations (start with smaller number for testing)
    num_scenarios = DEFAULT_NUM_SCENARIOS
    simulator.run_all_scenarios(num_scenarios=num_scenarios, batch_size=DEFAULT_BATCH_SIZE)
    
    logger.info("EPANET/WNTR simulation complete!")


if __name__ == "__main__":
    main() 