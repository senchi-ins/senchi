#!/usr/bin/env python3
"""
Test script for EPANET/WNTR simulation
======================================

This script tests the plumbing network simulation with a single scenario
to verify everything works correctly before running the full Monte-Carlo sweep.
"""

import sys
import pandas as pd
import matplotlib.pyplot as plt
from pathlib import Path

# Add current directory to path to import our module
sys.path.append(str(Path(__file__).parent))

from epanet_simulator import HomePlumbingNetwork, MonteCarloLeakSimulator

def test_basic_network():
    """Test basic network creation and simulation without leaks."""
    
    print("Testing basic network creation...")
    
    # Create network
    network = HomePlumbingNetwork(supply_pressure_kpa=400.0)
    
    print(f"Network created with {network.network.num_nodes} nodes and {network.network.num_links} links")
    
    # Visualize network
    print("\nGenerating network visualization...")
    network.visualize_network(save_path="dataset/network_layout.png")
    
    # Run simulation
    print("Running simulation...")
    sensor_data, metadata = network.run_simulation()
    
    print(f"Simulation completed. Data shape: {sensor_data.shape}")
    print(f"Pressure range: {sensor_data['pressure_kpa'].min():.1f} - {sensor_data['pressure_kpa'].max():.1f} kPa")
    print(f"Flow range: {sensor_data['flow_lps'].min():.3f} - {sensor_data['flow_lps'].max():.3f} L/s")
    
    return sensor_data, metadata

def test_leak_injection():
    """Test leak injection and simulation."""
    
    print("\nTesting leak injection...")
    
    # Create network
    network = HomePlumbingNetwork(supply_pressure_kpa=400.0)
    
    # Inject a leak
    leak_area_m2 = 3.14159 * (0.003 ** 2)  # 3mm diameter hole
    network.inject_leak(
        pipe_name='KITCHEN_SINK_RUN',
        start_time=3 * 3600,  # 3 hours
        leak_area=leak_area_m2,
        duration=1800  # 30 minutes
    )
    
    # Run simulation
    print("Running simulation with leak...")
    sensor_data, metadata = network.run_simulation()
    
    print(f"Leak simulation completed. Data shape: {sensor_data.shape}")
    print(f"Pressure range: {sensor_data['pressure_kpa'].min():.1f} - {sensor_data['pressure_kpa'].max():.1f} kPa")
    print(f"Flow range: {sensor_data['flow_lps'].min():.3f} - {sensor_data['flow_lps'].max():.3f} L/s")
    
    return sensor_data, metadata

def test_monte_carlo_simulator():
    """Test the Monte Carlo simulator with a few scenarios."""
    
    print("\nTesting Monte Carlo simulator...")
    
    # Create simulator
    simulator = MonteCarloLeakSimulator()
    
    # Generate a few test scenarios
    scenarios = simulator.generate_scenarios(num_scenarios=5)
    
    print(f"Generated {len(scenarios)} test scenarios:")
    for i, scenario in enumerate(scenarios):
        print(f"  Scenario {i+1}: {scenario['scenario_id']}, "
              f"Leak: {scenario['has_leak']}, "
              f"Location: {scenario['leak_location']}, "
              f"Size: {scenario['leak_area_mm']:.1f}mm")
    
    # Run one scenario
    print("\nRunning single scenario...")
    sensor_data, metadata = simulator.run_scenario(scenarios[0])
    
    print(f"Scenario completed. Data shape: {sensor_data.shape}")
    
    return sensor_data, metadata

def plot_results(healthy_data, leak_data, title="Pressure and Flow Comparison"):
    """Plot comparison of healthy vs leak scenarios."""
    
    fig, (ax1, ax2) = plt.subplots(2, 1, figsize=(12, 8))
    
    # Convert timestamp to hours for plotting
    hours = healthy_data.index / 3600
    
    # Plot pressure
    ax1.plot(hours, healthy_data['pressure_kpa'], label='Healthy', alpha=0.7)
    ax1.plot(hours, leak_data['pressure_kpa'], label='With Leak', alpha=0.7)
    ax1.set_ylabel('Pressure (kPa)')
    ax1.set_title('Pressure at Service Entry')
    ax1.legend()
    ax1.grid(True, alpha=0.3)
    
    # Plot flow
    ax2.plot(hours, healthy_data['flow_lps'], label='Healthy', alpha=0.7)
    ax2.plot(hours, leak_data['flow_lps'], label='With Leak', alpha=0.7)
    ax2.set_xlabel('Time (hours)')
    ax2.set_ylabel('Flow (L/s)')
    ax2.set_title('Flow at Service Entry')
    ax2.legend()
    ax2.grid(True, alpha=0.3)
    
    plt.suptitle(title)
    plt.tight_layout()
    
    # Save plot
    output_dir = Path("dataset")
    output_dir.mkdir(exist_ok=True)
    plt.savefig(output_dir / "test_simulation_results.png", dpi=300, bbox_inches='tight')
    plt.show()

def main():
    """Run all tests."""
    
    print("EPANET/WNTR Simulation Test Suite")
    print("=" * 40)
    
    try:
        # Test 1: Basic network
        healthy_data, healthy_metadata = test_basic_network()
        
        # Test 2: Leak injection
        leak_data, leak_metadata = test_leak_injection()
        
        # Test 3: Monte Carlo simulator
        mc_data, mc_metadata = test_monte_carlo_simulator()
        
        # Plot results
        print("\nGenerating comparison plot...")
        plot_results(healthy_data, leak_data, "Healthy vs Leak Scenario Comparison")
        
        print("\nAll tests completed successfully!")
        print("Check 'dataset/test_simulation_results.png' for visualization.")
        
    except Exception as e:
        print(f"Test failed with error: {e}")
        import traceback
        traceback.print_exc()
        return False
    
    return True

if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1)