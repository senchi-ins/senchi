"""simulate_all.py
Parallel driver for large-scale household simulations.

Example CLI usage
-----------------
python -m src.simulate_all \
    --n-houses 500 \
    --days 2 \
    --output output/raw \
    --processes 8 \
    --resolution 1.0 \
    --enable-tsnet

Notes
-----
* Each worker process instantiates its own `HouseSimulator` and writes its
  results directly to disk through the StreamingSink located in
  `<output>/house_<id>_<date>.parquet`.
* The driver purposely avoids injecting a burst event every time.  It leaves
  event scheduling to HouseSimulator – which may or may not include a
  PRESSURE_BURST depending on the stochastic leak generator – so that most
  datasets remain failure-free for ML balance.
"""
from __future__ import annotations

import argparse
import multiprocessing as mp
from datetime import datetime, timedelta
from pathlib import Path
import json
import os
from typing import Tuple, Dict, Any

# Path to house profiles JSON for weighted random selection
CONFIG_PATH = Path(__file__).parent.parent / "config" / "house_profiles.json"

from tqdm import tqdm  # type: ignore

from .simulate_house import HouseSimulator

# ---------------------------------------------------------------------------
# Helper – single job execution
# ---------------------------------------------------------------------------

def _run_job(job: Tuple[int, datetime, Dict[str, Any]]) -> str:
    """Worker function executed in each process.

    Parameters
    ----------
    job : tuple
        (house_id, day_start, cfg_dict)

    Returns
    -------
    str
        Path to written Parquet/CSV file (or empty string on failure)
    """
    house_id, day_start, cfg = job
    try:
        sim = HouseSimulator(
            house_id=house_id,
            start_time=day_start,
            duration_seconds=cfg["duration_seconds"],
            resolution_seconds=cfg["resolution_seconds"],
            demand_profile_id=cfg["profile"],
            enable_tsnet=cfg["enable_tsnet"],
            output_dir=cfg["output_dir"],
            light_mode=cfg["light_mode"],
            random_seed=house_id,
        )

        # Optional realistic schedule (24 h)
        if cfg["schedule_events"]:
            network_info = {"length_km": 0.1, "material": "Copper", "age_years": 20}
            sim.scheduler.generate_realistic_schedule(
                duration_days=cfg.get("duration_days", 1),
                network_info=network_info,
                random_seed=house_id,
            )

        sim.run()  # Writes data via StreamingSink
        return str(sim.output_dir) if sim.output_dir else ""
    except Exception as exc:  # pragma: no cover – log error
        print(f"[ERROR] House {house_id} on {day_start.date()}: {exc}")
        return ""

# ---------------------------------------------------------------------------
# Main driver function
# ---------------------------------------------------------------------------

def simulate_cohort(
    n_houses: int = 100,
    days: int = 1,
    start_date: datetime | None = None,
    output_dir: str | Path = "output/raw",
    resolution_seconds: float = 1.0,
    processes: int | None = None,
    enable_tsnet: bool = False,
    light_mode: bool = False,
    schedule_events: bool = True,
    demand_profile: str = "random",
) -> None:
    """Launch a cohort simulation.
    All files are written under `output_dir`.
    """
    start_date = start_date or datetime.utcnow()
    output_dir = Path(output_dir).absolute()
    output_dir.mkdir(parents=True, exist_ok=True)

    # Build job list
    jobs = []
    seconds_per_day = 24 * 3600
    import random

    # ------------------------------------------------------------------
    # Prepare weighted random selection of house profiles if requested
    # ------------------------------------------------------------------
    weighted_profiles = None
    weights = None
    if demand_profile in {"random", "weighted", "auto"}:
        try:
            with open(CONFIG_PATH, "r") as f:
                _data = json.load(f)
            weighted_profiles = [p["id"] for p in _data.get("profiles", [])]
            weights = [p.get("weight", 1.0) for p in _data.get("profiles", [])]
        except Exception as exc:  # pragma: no cover
            print(f"[WARN] Could not load house profiles for weighted selection: {exc}")

    event_incidence = 0.50  # Probability that a house will experience any events in its continuous run

    duration_seconds = days * seconds_per_day

    for h in range(n_houses):
        # Decide once per house whether to enable leak/blockage scheduling
        house_has_events = schedule_events and (random.random() < event_incidence)

        # Randomise simulation start date uniformly within the calendar year
        base_year = start_date.year
        year_start = datetime(base_year, 1, 1)
        rand_day_offset = random.randint(0, 364)
        day_start = year_start + timedelta(days=rand_day_offset)

        # Select a profile for this household
        if weighted_profiles is not None:
            chosen_profile = random.choices(weighted_profiles, weights=weights, k=1)[0]  # type: ignore[arg-type]
        else:
            chosen_profile = demand_profile

        cfg: Dict[str, Any] = {
            "duration_seconds": duration_seconds,
            "duration_days": days,
            "resolution_seconds": resolution_seconds,
            "enable_tsnet": enable_tsnet,
            "light_mode": light_mode,
            "output_dir": output_dir,
            "schedule_events": house_has_events,
            "profile": chosen_profile,
        }
        jobs.append((h + 1, day_start, cfg))

    # Choose process pool size
    procs = processes if processes and processes > 0 else mp.cpu_count()

    # Run in parallel with progress bar
    with mp.Pool(processes=procs) as pool:
        results_iter = pool.imap_unordered(_run_job, jobs, chunksize=4)
        for _ in tqdm(results_iter, total=len(jobs), desc="Simulating"):
            pass  # tqdm consumes iterator to update bar

    print("Simulation batch finished. Individual files written to:", output_dir)

    # ------------------------------------------------------------------
    # Consolidate individual house files into a single dataset
    # ------------------------------------------------------------------
    try:
        from .io.polars_sink import concatenate_simulation_files  # Lazy import

        file_format = "parquet"  # StreamingSink currently writes parquet by default
        prefix = os.environ.get("SIM_FILE_PREFIX", "")
        
        # Find all individual house files (now with house_id in filename)
        if prefix:
            pattern = f"{prefix}_house_*.{file_format}"  # prefix_house_000001_0000.parquet
        else:
            pattern = f"simulation_house_*.{file_format}"

        files_to_concat = list(output_dir.glob(pattern))
        # Exclude the consolidated file if it already exists
        combined_name = f"{prefix or 'combined'}_all_houses.{file_format}"
        files_to_concat = [f for f in files_to_concat if f.name != combined_name]
        
        print(f"Found {len(files_to_concat)} individual house files to consolidate")
        if files_to_concat:
            combined_name = f"{prefix or 'combined'}_all_houses.{file_format}"
            combined_path = output_dir / combined_name
            concatenate_simulation_files(files_to_concat, combined_path, file_format=file_format)
            print("Consolidated file written to", combined_path)

            # Remove per-house files now that they have been merged into a single dataset
            for f in files_to_concat:
                try:
                    f.unlink(missing_ok=True)
                except Exception:
                    pass
            print(f"Deleted {len(files_to_concat)} individual house files after consolidation.")

            # --------------------------------------------------------------
            # Bulk COPY into Postgres
            # --------------------------------------------------------------
            try:
                import psycopg2
                from psycopg2.extras import execute_values
                import polars as pl

                db_info = {
                    "host": os.getenv("DB_HOST", "postgres"),
                    "port": int(os.getenv("DB_PORT", "5432")),
                    "dbname": os.getenv("DB_NAME", "wdn"),
                    "user": os.getenv("DB_USER", "wdn"),
                    "password": os.getenv("DB_PASSWORD", "wdn_pass"),
                }
                conn = psycopg2.connect(**db_info)
                cur = conn.cursor()

                table_name = "simulation_data"

                # Create table if not exists
                cur.execute(
                    f"""
                    CREATE TABLE IF NOT EXISTS {table_name} (
                        timestamp TIMESTAMPTZ,
                        house_id INT,
                        flow_m3_s DOUBLE PRECISION,
                        flow_gpm DOUBLE PRECISION,
                        velocity DOUBLE PRECISION,
                        totalizer DOUBLE PRECISION,
                        pressure DOUBLE PRECISION,
                        downstream_wave_time DOUBLE PRECISION,
                        upstream_wave_time DOUBLE PRECISION,
                        delta_t_raw DOUBLE PRECISION,
                        theta DOUBLE PRECISION,
                        pipe_diameter DOUBLE PRECISION,
                        number_of_traverses INT,
                        pipe_material TEXT,
                        leak BOOLEAN,
                        location TEXT
                    );
                    """
                )
                conn.commit()

                # Stream Parquet as CSV to COPY FROM STDIN
                tmp_csv = combined_path.with_suffix(".csv")
                pl.scan_parquet(combined_path).sink_csv(tmp_csv)

                with open(tmp_csv, "r", encoding="utf-8") as f:
                    cur.copy_expert(f"COPY {table_name} FROM STDIN WITH (FORMAT CSV, HEADER TRUE)", f)
                conn.commit()
                tmp_csv.unlink(missing_ok=True)
                print("Bulk COPY completed into Postgres table", table_name)

                # Delete intermediate per-house files
                for f in files_to_concat:
                    try:
                        f.unlink(missing_ok=True)
                    except Exception:
                        pass
                print("Intermediate per-house files deleted.")
            except Exception as exc:
                print("[WARN] Bulk COPY into Postgres failed:", exc)
        else:
            print("[WARN] No individual house files found for consolidation using pattern", pattern)
    except Exception as exc:
        print("[WARN] Consolidation step failed:", exc)

# ---------------------------------------------------------------------------
# CLI entry-point
# ---------------------------------------------------------------------------


def _parse_cli() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="Bulk household simulation driver")
    parser.add_argument("--n-houses", type=int, default=100, help="Number of unique houses")
    parser.add_argument("--days", type=int, default=1, help="Number of consecutive days to simulate")
    parser.add_argument("--start", type=str, default=None, help="Start date ISO-format (defaults to today UTC)")
    parser.add_argument("--output", type=str, default="output/raw", help="Output directory for Parquet/CSV files")
    parser.add_argument("--resolution", type=float, default=1.0, help="Time-step in seconds")
    parser.add_argument("--processes", type=int, default=None, help="Worker process count (default: CPU cores)")
    parser.add_argument("--enable-tsnet", action="store_true", help="Run TSNet transient pulse where bursts exist")
    parser.add_argument("--light-mode", action="store_true", help="Skip EPANET for faster unit-test style run")
    parser.add_argument("--no-events", action="store_true", help="Disable automatic leak/blockage scheduling")
    parser.add_argument(
        "--profile",
        type=str,
        default="random",
        help="House profile ID (see config JSON). Use 'random' to sample weighted profiles per household.",
    )
    return parser.parse_args()


def main_cli() -> None:  # pragma: no cover
    ns = _parse_cli()
    simulate_cohort(
        n_houses=ns.n_houses,
        days=ns.days,
        start_date=datetime.fromisoformat(ns.start) if ns.start else None,
        output_dir=ns.output,
        resolution_seconds=ns.resolution,
        processes=ns.processes,
        enable_tsnet=ns.enable_tsnet,
        light_mode=ns.light_mode,
        schedule_events=not ns.no_events,
        demand_profile=ns.profile,
    )


if __name__ == "__main__":  # pragma: no cover
    main_cli()
