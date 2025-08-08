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

Output will be saved to `output/raw/[sim_size]/[date]/[#_of_houses]h_[#_of_days]_[date]_[time]_all_houses.parquet


# Synthetic Home Plumbing System Simulation

## Purpose

This repository generates **physics‑based synthetic time‑series data** that mimic the readings captured by a clamp‑on ultrasonic water‑flow meter installed on a household’s main valve line.  The data include realistic demand patterns, hydraulic behaviour (Darcy–Weisbach, Bernoulli, Joukowsky water‑hammer effects), sensor noise, progressive leak/burst events, and blockage scenarios.  The resulting dataset—spanning thousands of homes at second cadence—is intended for training machine‑learning models that predict pipe failures **six hours before they occur**.

---

## High‑Level Simulation Architecture

```text
main.py ─┐
          │  generates job list →  simulate_all.py  →  multiprocess pool
          │                                         ↘
          │                                           simulate_house.py  (per home)
          │                                             ├─ generators/demand_numpy.py     (stochastic usage)
          │                                             ├─ physics/
          │                                             │   ├─ hydraulics.py              (Darcy–Weisbach, Bernoulli)
          │                                             │   └─ joukowsky.py               (wave‑speed regression)
          │                                             ├─ events/
          │                                             │   ├─ leak_model.py              (leak progression)
          │                                             │   ├─ blockage_model.py          (constrictions)
          │                                             │   └─ transient_events.py        (TSNet wrapper)
          │                                             ├─ sensor/sensor_model.py         (meter noise & bias)
          │                                             └─ io/polars_sink.py              (streaming Parquet/CSV)
          └─ config/  (JSON/YAML profiles feeding every module)
```

Each household simulation executes the following pipeline:

1. **Demand generation** – family‑specific daily water‑use curve.
2. **Hydraulic solver** – computes pressure, flow, velocity for every second.
3. **Event injection** – leaks, bursts, blockages; water‑hammer transients via TSNet.
4. **Sensor modelling** – converts physical variables into meter outputs with realistic noise and missing data.
5. **Polars sink** – streams rows to disk (Parquet or CSV) without memory bloat.

---

## Simulation Output

For each house‑day the engine writes a table with the schema below (matching the sample screenshot):

| Column                                                     | Description                                          |
| ---------------------------------------------------------- | ---------------------------------------------------- |
| `timestamp`                                                | UTC timestamp at 1 s or finer resolution             |
| `house_id`                                                 | Integer identifier of the dwelling                   |
| `flow_m3_s`                                                | Volumetric flow (m³ s⁻¹) computed from meter geometry |
| `flow_gpm`                                                 | Volumetric flow (gal min⁻¹) computed from meter geometry |
| `velocity`                                                 | Internal pipe velocity (m s⁻¹)                       |
| `totalizer`                                                | Cumulative consumption counter (L)                   |
| `pressure`                                                 | Local static pressure (kPa)                          |
| `downstream_wave_time`, `upstream_wave_time`, `delta_t_raw` | Transit‑time differentials from TSNet transients     |
| `theta`                                                    | Incidence angle of ultrasound through pipe wall      |
| `pipe_diameter`                                            | Internal diameter (mm)                               |
| `number_of_ultrasonic_reflections`                         | Quality metric for signal path                       |
| `pipe_material`                                            | e.g. *PEX*, *Copper*, *PVC*                          |
| `leak`                                                     | Binary indicator (1 = leak/burst active)             |
| `location`                                                 | Approximate fixture or segment for the event         |

Aggregated daily Parquet files live in `output/raw/` and can be post‑processed into ML‑ready datasets inside `output/final/`.

---

## Repository Layout

| Path                     | Meaning                                                                                                       |
| ------------------------ | ------------------------------------------------------------------------------------------------------------- |
| **`config/`**            | JSON/YAML files describing house archetypes, leak growth profiles, blockage severities, and sensor specs      |
| **`src/`**               | Top‑level Python package for simulation code                                                                  |
| `src/generators/`        | Demand‑curve creation utilities (vectorised NumPy)                                                            |
| `src/physics/`           | Deterministic hydraulics: `hydraulics.py` (Darcy–Weisbach, Bernoulli) and `joukowsky.py` (water‑hammer)       |
| `src/events/`            | Stochastic event models: `leak_model.py`, `blockage_model.py`, and `transient_events.py` wrapper around TSNet |
| `src/sensor/`            | `sensor_model.py` converts physical states to noisy meter signals                                             |
| `src/io/`                | `polars_sink.py` handles streaming writes to Parquet/CSV                                                      |
| `src/simulate_house.py`  | Orchestrates all modules to simulate one house‑day                                                            |
| `src/simulate_all.py`    | Parallel driver for large cohorts (1000 + homes)                                                              |
| **`output/raw/`**        | One Parquet/CSV per house‑day (huge)                                                                          |
| **`output/final/`**      | Curated, feature‑engineered slices for ML                                                                     |
| **`tests/`**             | PyTest unit tests for physics and event logic                                                                 |
| **`main.py`**            | CLI entry point to kick off full‑scale simulations                                                            |

```
wdn_sim/
├── config/
│   ├── house_profiles.json      # Household demand archetypes
│   ├── leak_profiles.json       # Leak growth & burst parameters
│   └── sensor_config.json       # Sensor noise, bias, and sample-rate settings
├── src/
│   ├── generators/
│   │   ├── demand_numpy.py      # Vectorised demand-curve generator
│   │   └── assemble_polars.py    # batch ↔ polars DataFrame helpers
│   ├── physics/
│   │   ├── hydraulics.py         # Darcy–Weisbach & Bernoulli helpers
│   │   └── joukowsky.py          # Water-hammer & wave-speed regression
│   ├── events/
│   │   ├── leak_model.py         # Progressive leaks & burst logic
│   │   ├── blockage_model.py     # Pipe constriction archetypes
│   │   └── transient_events.py   # TSNet-based transient solver wrapper
│   ├── sensor/
│   │   └── sensor_model.py       # Ultrasonic meter noise & bias simulation
│   ├── io/
│   │   ├── polars_sink.py        # Streaming Parquet/CSV I/O via Polars
│   │   └── pandas_bridge.py        # pl→pd conversions for ML
│   ├── simulate_house.py         # One household simulation pipeline
│   └── simulate_all.py           # Parallel runner for 1k+ homes
├── output/
│   ├── raw/                      # Per-house-day Parquet/CSV outputs
│   └── final/                    # Curated ML-ready datasets
├── tests/
│   └── test_hydraulics.py        # Unit tests for physics modules
├── main.py                       # CLI entry point for mass simulation
└── README.md                     # This guide
```
