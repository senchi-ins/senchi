#!/bin/bash

# Leak Model Simulation Runner
# Usage: ./run_sim.sh [config] or ./run_sim.sh custom [homes] [start] [end]

set -e

# Default configuration
export SIM_HOMES=${SIM_HOMES:-1000}
export SIM_START=${SIM_START:-2025-01}
export SIM_END=${SIM_END:-2025-12}
export SIM_MEMORY_LIMIT=${SIM_MEMORY_LIMIT:-12G}
export SIM_MEMORY_RESERVATION=${SIM_MEMORY_RESERVATION:-12G}
export SIM_CPU_LIMIT=${SIM_CPU_LIMIT:-4}
export SIM_BATCH_SIZE=${SIM_BATCH_SIZE:-50}
export SIM_CHUNK_SIZE=${SIM_CHUNK_SIZE:-1000}

case "${1:-default}" in
    "small")
        echo "Running small simulation (100 homes, 3 months)"
        export SIM_HOMES=100
        export SIM_START="2025-01"
        export SIM_END="2025-03"
        export SIM_MEMORY_LIMIT="4G"
        export SIM_MEMORY_RESERVATION="4G"
        export SIM_CPU_LIMIT="4"
        export SIM_BATCH_SIZE=25
        ;;
    "medium")
        echo "Running medium simulation (500 homes, 6 months)"
        export SIM_HOMES=500
        export SIM_START="2025-01"
        export SIM_END="2025-06"
        export SIM_MEMORY_LIMIT="8G"
        export SIM_MEMORY_RESERVATION="8G"
        export SIM_CPU_LIMIT="3"
        export SIM_BATCH_SIZE=50
        ;;
    "large")
        echo "Running large simulation (1000 homes, 12 months)"
        export SIM_HOMES=1000
        export SIM_START="2025-01"
        export SIM_END="2025-12"
        export SIM_MEMORY_LIMIT="12G"
        export SIM_MEMORY_RESERVATION="12G"
        export SIM_CPU_LIMIT="4"
        export SIM_BATCH_SIZE=50
        ;;
    "test")
        echo "Running test simulation (10 homes, 1 month)"
        export SIM_HOMES=10
        export SIM_START="2025-01"
        export SIM_END="2025-01"
        export SIM_MEMORY_LIMIT="2G"
        export SIM_MEMORY_RESERVATION="2G"
        export SIM_CPU_LIMIT="1"
        export SIM_BATCH_SIZE=10
        ;;
    "custom")
        if [ $# -lt 4 ]; then
            echo "Usage: $0 custom [homes] [start] [end] [memory_limit] [cpu_limit]"
            echo "Example: $0 custom 500 2025-01 2025-06 8G 3"
            exit 1
        fi
        echo "Running custom simulation ($2 homes, $3 to $4)"
        export SIM_HOMES=$2
        export SIM_START=$3
        export SIM_END=$4
        export SIM_MEMORY_LIMIT=${5:-8G}
        export SIM_MEMORY_RESERVATION=${5:-8G}
        export SIM_CPU_LIMIT=${6:-3}
        ;;
    *)
        echo "Usage: $0 [small|medium|large|test|custom homes start end [memory cpu]]"
        echo "  small  - 100 homes, 3 months (4GB RAM)"
        echo "  medium - 500 homes, 6 months (8GB RAM)"
        echo "  large  - 1000 homes, 12 months (12GB RAM)"
        echo "  test   - 10 homes, 1 month (2GB RAM)"
        echo "  custom - Custom configuration"
        echo ""
        echo "Environment variables:"
        echo "  SIM_HOMES, SIM_START, SIM_END, SIM_MEMORY_LIMIT, SIM_CPU_LIMIT"
        echo "  SIM_BATCH_SIZE, SIM_CHUNK_SIZE"
        exit 1
        ;;
esac

export SIM_OUTPUT="data/output/synthetic_water_data_minute_${SIM_HOMES}.csv.gz"

# Create output directory
mkdir -p data/output

# Run with Docker Compose
echo "Starting simulation with Docker Compose..."
echo "Configuration: $SIM_HOMES homes, $SIM_START to $SIM_END, $SIM_MEMORY_LIMIT RAM, $SIM_CPU_LIMIT CPUs"

docker compose up --build leak-sim

echo "Simulation complete! Output saved to data/output/${SIM_OUTPUT}" 