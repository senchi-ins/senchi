"""wdn_sim main entry point

Run a small-scale (or large) cohort simulation from the command line.  It is a
thin wrapper around `src.simulate_all.simulate_cohort` so the heavy lifting is
still done in that module.

Example
-------
python -m experiments.leak_model.wdn_sim.main \
    --n-houses 4 \
    --days 1 \
    --output output/raw_demo \
    --light-mode
"""
from __future__ import annotations

import argparse
from datetime import datetime
from pathlib import Path

from src.simulate_all import simulate_cohort


def _parse_args() -> argparse.Namespace:
    p = argparse.ArgumentParser(description="Run residential water-network simulation cohort")
    p.add_argument("--n-houses", type=int, default=2, help="Number of unique houses to simulate")
    p.add_argument("--days", type=int, default=1, help="Consecutive days for each house")
    p.add_argument("--output", type=str, default="output/raw", help="Output directory for Parquet/CSV files")
    p.add_argument("--resolution", type=float, default=10.0, help="Simulation time-step in seconds")
    p.add_argument("--processes", type=int, default=2, help="Parallel worker processes (0 = all cores)")
    p.add_argument("--start", type=str, default=None, help="Simulation start date ISO (defaults today UTC)")
    p.add_argument("--profile", type=str, default="random", help="House profile ID. Use 'random' to sample weighted profiles per household.")
    p.add_argument("--enable-tsnet", action="store_true", help="Enable TSNet transient pulse if burst occurs")
    p.add_argument("--light-mode", action="store_true", help="Skip EPANET to speed up smoke-test runs")
    p.add_argument("--no-events", action="store_true", help="Disable automatic leak/blockage scheduling")
    return p.parse_args()


def main() -> None:  # pragma: no cover
    ns = _parse_args()
    simulate_cohort(
        n_houses=ns.n_houses,
        days=ns.days,
        start_date=datetime.fromisoformat(ns.start) if ns.start else None,
        output_dir=Path(ns.output),
        resolution_seconds=ns.resolution,
        processes=ns.processes if ns.processes > 0 else None,
        enable_tsnet=ns.enable_tsnet,
        light_mode=ns.light_mode,
        schedule_events=not ns.no_events,
        demand_profile=ns.profile,
    )


if __name__ == "__main__":
    main()
