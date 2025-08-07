#!/bin/bash
set -euo pipefail

# Entrypoint script for wdn_sim Docker container
# Builds the command dynamically based on environment variables

# Base command parts  
CMD_ARGS=(
    "uv" "run" "main.py"
    "--n-houses" "${SIM_HOUSES:-100}"
    "--days" "${SIM_DAYS:-1}"
    "--output" "${SIM_OUTPUT:-/app/output/raw}"
    "--resolution" "${SIM_RESOLUTION:-10.0}"
    "--processes" "${SIM_PROCESSES:-0}"
    "--profile" "${SIM_PROFILE:-random}"
)

# Add conditional flags
if [[ "${SIM_ENABLE_TSNET:-false}" == "true" ]]; then
    CMD_ARGS+=("--enable-tsnet")
fi

if [[ "${SIM_LIGHT_MODE:-true}" == "true" ]]; then
    CMD_ARGS+=("--light-mode")
fi

if [[ "${SIM_NO_EVENTS:-false}" == "true" ]]; then
    CMD_ARGS+=("--no-events")
fi

# Execute the command
echo "Running: ${CMD_ARGS[*]}"
exec "${CMD_ARGS[@]}"