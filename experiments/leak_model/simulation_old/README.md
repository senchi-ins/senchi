## Setup

Install uv and run:
```bash
uv sync
```

## Running a simulation

To run a simulation, simply run the following command:

```bash
./run_sim.sh [sim_size] # either small, medium, or large
```

This will run the simulation and output the results to the `data` directory.

More granular options are available:

```bash
./run_sim.sh custom [homes] [start] [end] [memory_limit] [cpu_limit]
```

Output will be saved to `output/synthetic_water_data_minute_${homes}.csv.gz`