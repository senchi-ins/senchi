"""
Configuration file for EPANET/WNTR plumbing leak simulation
==========================================================

Centralized configuration for all simulation parameters.
"""

# Simulation Parameters
SIMULATION_DURATION_HOURS = 1
TIME_STEP_SECONDS = 1
PATTERN_TIMESTEP_HOURS = 1

# Network Parameters
DEFAULT_SUPPLY_PRESSURE_KPA = 400.0
TARGET_PRV_PRESSURE_KPA = 325.0

# Pipe Materials (Hazen-Williams C factors)
PIPE_MATERIALS = {
    'PEX': 100,
    'Copper': 130,
    'PVC': 140,
}

# Leak Parameters
LEAK_AREAS_MM = [0.5, 1.0, 1.5, 2.0, 2.5, 3.0, 3.5, 4.0, 4.5, 5.0, 6.0, 7.0, 8.0, 9.0, 10.0]
SUPPLY_PRESSURES_KPA = [275, 300, 325, 350, 375, 400, 425, 450, 475, 500, 525, 550]
LEAK_START_TIMES_HOURS = [3, 6, 9, 12, 15, 18, 21]
LEAK_DURATIONS_MINUTES = [15, 30, 60]

# Leak Locations (pipe names)
LEAK_LOCATIONS = [
    'KITCHEN_SINK_RUN',
    'DISHWASHER_RUN', 
    'POWDER_WC_RUN',
    'POWDER_LAV_RUN',
    'ENSUITE_WC_RUN',
    'ENSUITE_LAV_RUN',
    'ENSUITE_SHOWER_RUN',
    'FAMILY_BATH_WC_RUN',
    'FAMILY_BATH_LAV_RUN',
    'FAMILY_BATH_TUB_RUN',
    'LAUNDRY_RUN',
    'WATER_HEATER_RUN',
    'HOSE_BIBB_FRONT_RUN',
    'HOSE_BIBB_BACK_RUN'
]

# Fixture Demands (L/s)
FIXTURE_DEMANDS = {
    'KITCHEN_SINK': 0.1,
    'DISHWASHER': 0.05,
    'POWDER_ROOM_WC': 0.02,
    'POWDER_ROOM_LAV': 0.05,
    'ENSUITE_WC': 0.02,
    'ENSUITE_LAV': 0.05,
    'ENSUITE_SHOWER': 0.15,
    'FAMILY_BATH_WC': 0.02,
    'FAMILY_BATH_LAV': 0.05,
    'FAMILY_BATH_TUB': 0.15,
    'LAUNDRY_SINK': 0.1,
    'WATER_HEATER': 0.0,
    'HOSE_BIBB_FRONT': 0.0,
    'HOSE_BIBB_BACK': 0.0,
}

# Demand Patterns (24-hour, hourly multipliers)
DEMAND_PATTERNS = {
    'MORNING_PEAK': [0.1, 0.1, 0.1, 0.1, 0.1, 0.3, 0.8, 1.0, 0.9, 0.4, 0.2, 0.2,
                     0.3, 0.3, 0.2, 0.2, 0.3, 0.4, 0.6, 0.8, 0.7, 0.5, 0.3, 0.2],
    'EVENING_PEAK': [0.1, 0.1, 0.1, 0.1, 0.1, 0.2, 0.3, 0.4, 0.2, 0.2, 0.2, 0.2,
                     0.3, 0.3, 0.2, 0.2, 0.3, 0.4, 0.8, 1.0, 0.9, 0.7, 0.4, 0.2],
    'NIGHT_LOW': [0.1, 0.05, 0.05, 0.05, 0.05, 0.1, 0.2, 0.3, 0.2, 0.2, 0.2, 0.2,
                  0.2, 0.2, 0.2, 0.2, 0.2, 0.3, 0.4, 0.5, 0.3, 0.2, 0.1, 0.1],
}

# Monte Carlo Parameters
HEALTHY_SCENARIO_RATIO = 0.2  # 20% of scenarios have no leaks
DEFAULT_NUM_SCENARIOS = 10
DEFAULT_BATCH_SIZE = 50

# Output Configuration
OUTPUT_DIRS = {
    'raw_data': 'dataset/epanet_raw',
    'corrected_data': 'dataset/epanet_corrected', 
    'metadata': 'dataset/metadata',
    'simscale_anchors': 'dataset/simscale_anchors',
}

# Sensor Configuration
SENSOR_LOCATION = 'SERVICE_ENTRY'
SENSOR_MEASUREMENTS = ['pressure_kpa', 'flow_lps']

# Validation Targets (from plan.md)
VALIDATION_TARGETS = {
    'pressure_rmse_kpa': 5.0,
    'leak_detection_f1': 0.95,
    'localization_error_pipes': 1,
    'time_to_leak_c_index': 0.80,
    'leak_risk_brier_score': 0.15,
} 