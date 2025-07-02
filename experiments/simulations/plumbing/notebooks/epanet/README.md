2# EPANET/WNTR Plumbing Leak Simulation

This directory contains the low-fidelity EPANET/WNTR simulation component for the hybrid multi-fidelity dataset generation for residential plumbing leak prognosis.

## Overview

The simulation models a typical Canadian single-detached home plumbing system based on specifications in `layout.md` and generates Monte-Carlo leak scenarios as outlined in `plan.md`. The sensor is placed at the main service entry point (just downstream of the shutoff valve) to capture both pressure and flow measurements.

## Files

- `epanet_simulator.py` - Main simulation script with network model and Monte-Carlo generator
- `test_simulation.py` - Test script to verify functionality
- `requirements.txt` - Python dependencies
- `plan.md` - Overall project plan and workflow
- `layout.md` - Plumbing system layout specifications

## Installation

1. Install Python dependencies:
```bash
pip install -r requirements.txt
```

2. Ensure EPANET is installed on your system:
   - **Windows**: Download from EPA website
   - **macOS**: `brew install epanet`
   - **Linux**: `sudo apt-get install epanet` or build from source

## Quick Start

### 1. Test the Simulation

Run the test script to verify everything works:

```bash
python test_simulation.py
```

This will:
- Create a basic plumbing network
- Run a simulation without leaks
- Inject a test leak and run simulation
- Generate comparison plots
- Save results to `dataset/test_simulation_results.png`

### 2. Run Full Monte-Carlo Sweep

For the complete dataset generation:

```bash
python epanet_simulator.py
```

**Note**: The default is set to 1,000 scenarios for testing. To generate the full 10,000+ scenarios, modify the `num_scenarios` parameter in the `main()` function.

## Network Model

The `CanadianHomePlumbingNetwork` class models:

### Fixtures (Nodes)
- **Main Floor**: Kitchen sink, dishwasher, powder room (WC + lavatory)
- **Upper Floor**: Ensuite (WC + lavatory + shower), family bath (WC + lavatory + tub)
- **Basement**: Laundry sink, water heater
- **Exterior**: Front and back hose bibbs

### Piping (Links)
- **Service Line**: 3/4" - 1" from municipal supply to house
- **Main Trunk**: 3/4" PEX distribution
- **Fixture Runs**: 1/2" PEX to individual fixtures
- **Pressure Reducing Valve**: At service entry (400-550 kPa → 325 kPa)

### Materials
- **PEX**: Primary material (Hazen-Williams C = 100)
- **Copper**: Alternative (C = 130)
- **PVC**: Alternative (C = 140)

## Monte-Carlo Parameters

The simulation varies these parameters:

| Parameter | Range | Description |
|-----------|-------|-------------|
| Leak Area | 0.5-10.0 mm | Hole diameter |
| Supply Pressure | 275-550 kPa | Municipal pressure |
| Leak Start Time | 3, 6, 9, 12, 15, 18, 21 hours | When leak begins |
| Leak Duration | 15, 30, 60 minutes | How long leak lasts |
| Leak Location | 14 pipe segments | Where leak occurs |
| Pipe Material | PEX, Copper, PVC | Material properties |
| Demand Pattern | Morning, Evening, Night | Usage patterns |

## Output Format

### Raw Data Files
Each scenario generates a CSV file in `dataset/epanet_raw/`:
```csv
timestamp,pressure_kpa,flow_lps
0,325.2,0.045
1,325.1,0.044
...
86399,324.8,0.042
```

### Metadata
Scenario parameters are stored in `dataset/metadata/scenarios.json`:
```json
{
  "scenario_id": "run_00001",
  "leak_area_mm": 3.2,
  "supply_pressure_kpa": 400.0,
  "leak_start_time_seconds": 10800,
  "leak_duration_seconds": 1800,
  "leak_location": "KITCHEN_SINK_RUN",
  "pipe_material": "PEX",
  "has_leak": true,
  "leak_type": "horizontal_pipe"
}
```

## Performance

- **Single Scenario**: ~30 seconds on laptop
- **1,000 Scenarios**: ~8 hours (can be parallelized)
- **10,000 Scenarios**: ~80 hours (recommend batch processing)

## Sensor Location

The sensor is placed at `SERVICE_ENTRY` node, which represents the point just downstream of the main house shutoff valve. This location captures:
- Pressure variations from all fixtures
- Total flow into the house
- Leak signatures from any location in the system

## Validation

The simulation includes:
- **20% healthy scenarios** (no leaks) for baseline learning
- **Realistic demand patterns** based on residential usage
- **Pressure-dependent demand** modeling
- **Proper hydraulic calculations** using Hazen-Williams formula

## Next Steps

After running the EPANET simulations:

1. **Step 2**: Generate high-fidelity SimScale CFD anchors
2. **Step 3**: Create Δ-model to align fidelities
3. **Step 4**: Train knowledge distillation model
5. **Step 5**: Validate and iterate

## Troubleshooting

### Common Issues

1. **EPANET not found**: Install EPANET and ensure it's in your PATH
2. **WNTR import error**: Check `pip install wntr` completed successfully
3. **Memory issues**: Reduce batch size or number of scenarios
4. **Slow performance**: Consider running on more powerful machine or cloud

### Debug Mode

Enable debug logging by modifying the logging level in `epanet_simulator.py`:
```python
logging.basicConfig(level=logging.DEBUG, ...)
```

## References

- [WNTR Documentation](https://wntr.readthedocs.io)
- [EPANET User Manual](https://www.epa.gov/water-research/epanet)
- [Hazen-Williams Formula](https://en.wikipedia.org/wiki/Hazen%E2%80%93Williams_equation)
- [Residential Water Usage Patterns](https://www.epa.gov/watersense/residential-indoor-uses-water) 