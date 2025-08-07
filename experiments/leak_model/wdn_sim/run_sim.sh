#!/usr/bin/env bash

# -----------------------------------------------------------------------------
# Residential WDN Simulation Runner (wdn_sim)
#
# Helper script to build/run the Docker container with sensible presets.
# Usage:
#   ./run_sim.sh [small|medium|large|test|custom <houses> <days> [memory] [cpus]]
# -----------------------------------------------------------------------------
set -euo pipefail

# --- Defaults ---------------------------------------------------------------
export SIM_HOUSES="${SIM_HOUSES:-100}"
export SIM_DAYS="${SIM_DAYS:-1}"
export SIM_RESOLUTION="${SIM_RESOLUTION:-1.0}"
export SIM_PROCESSES="${SIM_PROCESSES:-0}"
export SIM_PROFILE="${SIM_PROFILE:-random}"
export SIM_LIGHT_MODE="${SIM_LIGHT_MODE:-true}"
export SIM_ENABLE_TSNET="${SIM_ENABLE_TSNET:-false}"
export SIM_NO_EVENTS="${SIM_NO_EVENTS:-false}"
export SIM_MEMORY_LIMIT="${SIM_MEMORY_LIMIT:-8G}"
export SIM_MEMORY_RESERVATION="${SIM_MEMORY_RESERVATION:-8G}"
export SIM_CPU_LIMIT="${SIM_CPU_LIMIT:-4}"

case "${1:-default}" in
  small)
    echo "Running SMALL simulation (100 houses, 7 days)"
    export SIM_HOUSES=100
    export SIM_DAYS=7
    export SIM_MEMORY_LIMIT="5G"
    export SIM_MEMORY_RESERVATION="5G"
    ;;
  medium)
    echo "Running MEDIUM simulation (500 houses, 10 days)"
    export SIM_HOUSES=500
    export SIM_DAYS=10
    export SIM_MEMORY_LIMIT="8G"
    export SIM_MEMORY_RESERVATION="8G"
    ;;
  large)
    echo "Running LARGE simulation (1000 houses, 21 days)"
    export SIM_HOUSES=1000
    export SIM_DAYS=21
    export SIM_MEMORY_LIMIT="12G"
    export SIM_MEMORY_RESERVATION="12G"
    ;;
  test)
    echo "Running TEST simulation (2 houses, 1 day)"
    export SIM_HOUSES=2
    export SIM_DAYS=1
    export SIM_MEMORY_LIMIT="2G"
    export SIM_MEMORY_RESERVATION="2G"
    export SIM_CPU_LIMIT="1"
    ;;
  custom)
    if [[ $# -lt 3 ]]; then
      echo "Usage: $0 custom <houses> <days> [memory_limit] [cpu_limit]" >&2
      exit 1
    fi
    export SIM_HOUSES="$2"
    export SIM_DAYS="$3"
    export SIM_MEMORY_LIMIT="${4:-8G}"
    export SIM_MEMORY_RESERVATION="${4:-8G}"
    export SIM_CPU_LIMIT="${5:-4}"
    shift $(( $# ))
    ;;
  *)
    echo "Usage: $0 [small|medium|large|test|custom]" >&2
    exit 1
    ;;
esac

# --- Derived paths ----------------------------------------------------------
# Generate timestamp and date for unique output directory
TIMESTAMP=$(date +"%Y%m%d_%H%M%S")
DATE_DIR=$(date +"%Y%m%d")

# Determine size type and file prefix for output naming
case "${1:-default}" in
  small)
    SIZE_TYPE="small"
    FILE_PREFIX="${SIM_HOUSES}h_${SIM_DAYS}d"
    ;;
  medium)
    SIZE_TYPE="medium"
    FILE_PREFIX="${SIM_HOUSES}h_${SIM_DAYS}d"
    ;;
  large)
    SIZE_TYPE="large"
    FILE_PREFIX="${SIM_HOUSES}h_${SIM_DAYS}d"
    ;;
  test)
    SIZE_TYPE="test"
    FILE_PREFIX="${SIM_HOUSES}h_${SIM_DAYS}d"
    ;;
  custom)
    SIZE_TYPE="custom"
    FILE_PREFIX="${SIM_HOUSES}h_${SIM_DAYS}d"
    ;;
  *)
    SIZE_TYPE="default"
    FILE_PREFIX="${SIM_HOUSES}h_${SIM_DAYS}d"
    ;;
esac

# Create unique output directory with size-based structure
OUTPUT_DIR="output/raw/${SIZE_TYPE}/${DATE_DIR}"
export SIM_OUTPUT="/app/${OUTPUT_DIR}"  # Container path (mapped via volume)
export SIM_FILE_PREFIX="${FILE_PREFIX}_${TIMESTAMP}"  # For filename customization
mkdir -p "${OUTPUT_DIR}"

# --- Kick off docker-compose ------------------------------------------------

echo "Starting simulation with Docker Compose..."
echo "Configuration: ${SIM_HOUSES} houses, ${SIM_DAYS} days, ${SIM_MEMORY_LIMIT} RAM, ${SIM_CPU_LIMIT} CPUs"
echo "Output directory: ${OUTPUT_DIR}"

docker compose up --build wdn-sim
