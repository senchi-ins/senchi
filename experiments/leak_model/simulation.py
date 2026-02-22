"""
High‑fidelity home plumbing simulation built on wdn_sim.

This module orchestrates a single-house simulation using EPANET (via WNTR)
for hydraulics, the built-in temperature model for water temperature, and the
event scheduler for realistic leak events. It returns a schema that includes:

- timestamp
- flow (m³/s and gpm)
- pressure (kPa)
- water temperature (°C)
- pipe diameter (mm)
- pipe material (string)
- leak flag (bool) and leak location

Usage (Python):
    from experiments.leak_model.simulation import run_home_plumbing_simulation
    df = run_home_plumbing_simulation(duration_hours=24, resolution_seconds=1.0)

CLI:
    python -m experiments.leak_model.simulation --hours 24 --resolution 1.0 \
        --profile modern_pex_small --out /tmp/home_run.parquet
"""

from __future__ import annotations

import sys
import os
from pathlib import Path
from datetime import datetime
from typing import Optional, Literal


def _add_wdn_sim_to_syspath() -> None:
    """Ensure wdn_sim is on sys.path so we can import the package `src`.

    We add the parent directory containing the `src` package so imports like
    `from src.simulate_house import HouseSimulator` resolve with proper package
    context, allowing relative imports inside that package to work.
    """
    here = Path(__file__).resolve()
    wdn_pkg_root = here.parent / "wdn_sim"
    if str(wdn_pkg_root) not in sys.path:
        sys.path.insert(0, str(wdn_pkg_root))


_add_wdn_sim_to_syspath()

# Local imports after path setup (import package `src.*`)
from src.simulate_house import HouseSimulator  # type: ignore
from src.simulate_all import simulate_cohort  # type: ignore
from src.io.assemble_polars import to_pandas_bridge  # type: ignore


def run_home_plumbing_simulation(
    duration_hours: float = 24.0,
    resolution_seconds: float = 1.0,
    start_time: Optional[datetime] = None,
    profile_id: str = "modern_pex_small",
    enable_tsnet: bool = False,
    schedule_events: bool = True,
    random_seed: Optional[int] = 42,
    output_path: Optional[str | Path] = None,
    output_format: Literal["parquet", "csv"] = "parquet",
):
    """Run a single high‑fidelity home plumbing simulation.

    Parameters
    ----------
    duration_hours: float
        Length of the simulation window.
    resolution_seconds: float
        Hydraulic time‑step; 1s is recommended for fidelity.
    start_time: datetime | None
        Simulation start timestamp.
    profile_id: str
        House demand/profile ID defined in wdn_sim config.
    enable_tsnet: bool
        If True and TSNet is available, compute short transient traces around burst leaks.
    schedule_events: bool
        If True, generate realistic leak events for the run.
    random_seed: int | None
        Seed for reproducibility.
    output_path: str | Path | None
        Optional file to write results (parquet or csv).
    output_format: Literal["parquet","csv"]
        Output format when output_path is provided.

    Returns
    -------
    pl.DataFrame
        Simulation results with requested fields and metadata.
    """
    from src.io import assemble_polars as ap  # type: ignore
    import polars as pl  # type: ignore

    start_time = start_time or datetime.utcnow()
    duration_seconds = int(duration_hours * 3600)

    sim = HouseSimulator(
        house_id=1,
        start_time=start_time,
        duration_seconds=duration_seconds,
        resolution_seconds=resolution_seconds,
        demand_profile_id=profile_id,
        enable_tsnet=enable_tsnet,
        output_dir=None,
        random_seed=random_seed,
        light_mode=False,
    )

    # Optionally create a realistic leak schedule using actual network metrics
    if schedule_events:
        try:
            # Estimate network length in km from EPANET model
            length_m = 0.0
            for _, pipe in sim.wn.pipes():
                length_m += float(getattr(pipe, "length", 0.0) or 0.0)
            network_info = {
                "length_km": max(length_m / 1000.0, 0.05),
                "material": getattr(sim, "main_pipe_material", "Copper"),
                "age_years": 20,
            }
            sim.scheduler.generate_realistic_schedule(
                duration_days=max(int(duration_hours // 24) or 1, 1),
                network_info=network_info,
                random_seed=random_seed,
            )
        except Exception:
            # Proceed without scheduled events if anything goes wrong
            pass

    df_pl = sim.run()

    # Select core outputs requested by the user while retaining timestamp
    required_cols = [
        "timestamp",
        "flow_m3_s",
        "flow_gpm",
        "pressure",
        "water_temperature_C",
        "pipe_diameter",
        "pipe_material",
        "leak",
        "location",
    ]
    existing = [c for c in required_cols if c in df_pl.columns]
    df_out = df_pl.select(existing) if existing else df_pl

    # Optional write
    if output_path is not None:
        output_path = Path(output_path)
        output_path.parent.mkdir(parents=True, exist_ok=True)
        if output_format == "parquet":
            df_out.write_parquet(output_path)
        else:
            df_out.write_csv(output_path)

    return df_out


def _parse_cli_args():
    import argparse
    p = argparse.ArgumentParser(description="High‑fidelity home plumbing simulation")
    p.add_argument("--hours", type=float, default=24.0, help="Duration in hours")
    p.add_argument("--resolution", type=float, default=1.0, help="Time‑step in seconds")
    p.add_argument("--start", type=str, default=None, help="Start time (ISO)")
    p.add_argument("--profile", type=str, default="modern_pex_small", help="House profile id")
    p.add_argument("--enable-tsnet", action="store_true", help="Enable TSNet transient analysis if available")
    p.add_argument("--no-events", action="store_true", help="Disable stochastic leak scheduling")
    p.add_argument("--seed", type=int, default=42, help="Random seed")
    p.add_argument("--out", type=str, default=None, help="Output file path (.parquet or .csv)")
    # Cohort options
    p.add_argument("--cohort-houses", type=int, default=0, help="If >0, run cohort for N houses instead of single run")
    p.add_argument("--months", type=float, default=3.0, help="Cohort duration in months (approx 30 days each)")
    p.add_argument("--cohort-out", type=str, default=None, help="Output directory for cohort (per-house parquet files)")
    p.add_argument("--processes", type=int, default=None, help="Worker process count (default: CPU cores)")
    p.add_argument("--cohort-prefix", type=str, default="", help="Filename prefix for cohort outputs")
    return p.parse_args()


def _cli_main() -> None:
    ns = _parse_cli_args()
    start_dt = datetime.fromisoformat(ns.start) if ns.start else None
    out_fmt: Literal["parquet", "csv"] = "parquet"
    if ns.out:
        suffix = Path(ns.out).suffix.lower()
        if suffix == ".csv":
            out_fmt = "csv"
        else:
            out_fmt = "parquet"

    if ns.cohort_houses and ns.cohort_houses > 0:
        # Configure prefix for file naming if provided
        if ns.cohort_prefix:
            os.environ["SIM_FILE_PREFIX"] = ns.cohort_prefix

        days = max(int(round(ns.months * 30)), 1)
        output_dir = Path(ns.cohort_out).absolute() if ns.cohort_out else (Path(__file__).parent / "wdn_sim" / "output" / "raw" / "default").absolute()
        output_dir.mkdir(parents=True, exist_ok=True)

        simulate_cohort(
            n_houses=ns.cohort_houses,
            days=days,
            start_date=start_dt,
            output_dir=str(output_dir),
            resolution_seconds=ns.resolution,
            processes=ns.processes,
            enable_tsnet=ns.enable_tsnet,
            light_mode=False,
            schedule_events=not ns.no_events,
            demand_profile="random",
        )
        print(f"Cohort complete. Files at {output_dir}")
        return
    else:
        df = run_home_plumbing_simulation(
            duration_hours=ns.hours,
            resolution_seconds=ns.resolution,
            start_time=start_dt,
            profile_id=ns.profile,
            enable_tsnet=ns.enable_tsnet,
            schedule_events=not ns.no_events,
            random_seed=ns.seed,
            output_path=ns.out,
            output_format=out_fmt,
        )

        # Print a quick summary to stdout
        try:
            import polars as pl  # type: ignore
            stats = {
                "rows": df.height,
                "start": df["timestamp"][0] if df.height else None,
                "end": df["timestamp"][df.height - 1] if df.height else None,
                "mean_flow_m3_s": float(df["flow_m3_s"].drop_nulls().mean()) if "flow_m3_s" in df.columns else None,
                "mean_pressure_kpa": float(df["pressure"].drop_nulls().mean()) if "pressure" in df.columns else None,
                "leak_fraction": float(df["leak"].cast(pl.Int32).mean()) if "leak" in df.columns else None,
            }
            print({k: v for k, v in stats.items()})
        except Exception:
            pass


if __name__ == "__main__":
    _cli_main()


