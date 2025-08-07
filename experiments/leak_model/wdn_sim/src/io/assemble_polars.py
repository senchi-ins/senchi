"""
assemble_polars.py
------------------
Batch to Polars DataFrame helpers for simulation data assembly.
Converts simulation component outputs into structured DataFrames.
"""

import polars as pl
import numpy as np
from typing import Dict, Any, List, Optional, Union
from datetime import datetime, timedelta
import pandas as pd

from .polars_sink import SimulationSchema


def create_timestamp_series(start_time: Union[str, datetime],
                           duration_seconds: int,
                           resolution_seconds: float = 1.0) -> List[datetime]:
    """
    Create a timestamp series for simulation data.
    
    Args:
        start_time: Start time as string or datetime
        duration_seconds: Total duration in seconds
        resolution_seconds: Time step in seconds
        
    Returns:
        List of datetime objects
    """
    if isinstance(start_time, str):
        start_time = datetime.fromisoformat(start_time)
    
    n_steps = int(duration_seconds / resolution_seconds) + 1
    delta = timedelta(seconds=resolution_seconds)
    
    return [start_time + i * delta for i in range(n_steps)]


def assemble_demand_data(timestamps: List[datetime],
                        demand_L_s: np.ndarray,
                        house_id: int) -> Dict[str, Any]:
    """
    Assemble demand generator output into structured format.
    
    Args:
        timestamps: Time series
        demand_L_s: Demand in L/s
        house_id: House identifier
        
    Returns:
        Dictionary compatible with SimulationSchema
    """
    n_points = len(timestamps)
    
    return {
        "timestamp": timestamps,
        "house_id": [house_id] * n_points,
        "flow_gpm": (demand_L_s * 15.8503).tolist(),
        "velocity": [None] * n_points,  # To be filled by hydraulics
        "pressure": [None] * n_points,  # To be filled by hydraulics
        "flow_m3_s": [None] * n_points,   # To be filled by sensor
        "totalizer": np.cumsum(demand_L_s * 1.0).tolist(),  # Cumulative flow
        "downstream_wave_time": [None] * n_points,
        "upstream_wave_time": [None] * n_points,
        "delta_t_raw": [None] * n_points,
        "theta": [None] * n_points,
        "pipe_diameter": [None] * n_points,
        "number_of_ultrasonic_reflections": [None] * n_points,
        "pipe_material": [None] * n_points,
        "leak": [False] * n_points,
        "location": [None] * n_points,
    }


def merge_hydraulics_data(base_data: Dict[str, Any],
                         velocity_m_s: np.ndarray,
                         pressure_kpa: np.ndarray,
                         pipe_diameter_mm: float,
                         pipe_material: str) -> Dict[str, Any]:
    """
    Merge hydraulic simulation results into base data.
    
    Args:
        base_data: Base simulation data dictionary
        velocity_m_s: Velocity array from hydraulics
        pressure_kpa: Pressure array from hydraulics  
        pipe_diameter_mm: Pipe diameter in mm
        pipe_material: Pipe material string
        
    Returns:
        Updated data dictionary
    """
    base_data["velocity"] = velocity_m_s.tolist()
    base_data["pressure"] = pressure_kpa.tolist()
    base_data["pipe_diameter"] = [pipe_diameter_mm] * len(velocity_m_s)
    base_data["pipe_material"] = [pipe_material] * len(velocity_m_s)
    
    return base_data


def merge_events_data(base_data: Dict[str, Any],
                     leak_indicators: np.ndarray,
                     event_locations: List[str]) -> Dict[str, Any]:
    """
    Merge event data (leaks, blockages) into base data.
    
    Args:
        base_data: Base simulation data dictionary
        leak_indicators: Boolean array indicating leak presence
        event_locations: List of event locations per time step
        
    Returns:
        Updated data dictionary
    """
    base_data["leak"] = leak_indicators.tolist()
    base_data["location"] = event_locations
    
    return base_data


def merge_sensor_data(base_data: Dict[str, Any],
                     sensor_results: Dict[str, np.ndarray]) -> Dict[str, Any]:
    """
    Merge ultrasonic sensor simulation results into base data.
    
    Args:
        base_data: Base simulation data dictionary
        sensor_results: Dictionary from UltrasonicMeter.simulate()
        
    Returns:
        Updated data dictionary
    """
    # Map sensor outputs to schema columns
    if "flow_L_s" in sensor_results:
        base_data["flow_gpm"] = (sensor_results["flow_L_s"] * 15.8503).tolist()
        base_data["flow_m3_s"] = (sensor_results["flow_L_s"] / 1000.0).tolist()
    
    if "velocity_m_s" in sensor_results:
        base_data["velocity"] = sensor_results["velocity_m_s"].tolist()
        
    if "totalizer_L" in sensor_results:
        base_data["totalizer"] = sensor_results["totalizer_L"].tolist()
        
    if "t_up_s" in sensor_results:
        base_data["upstream_wave_time"] = sensor_results["t_up_s"].tolist()
        
    if "t_down_s" in sensor_results:
        base_data["downstream_wave_time"] = sensor_results["t_down_s"].tolist()
        
    if "delta_t_s" in sensor_results:
        base_data["delta_t_raw"] = sensor_results["delta_t_s"].tolist()
        
    if "signal_quality_percent" in sensor_results:
        # Assign a consistent number of ultrasonic reflections (2 or 4) for the whole run
        consistent_reflections = int(np.random.choice([2, 4]))
        n_samples = len(base_data["timestamp"])
        base_data["number_of_ultrasonic_reflections"] = [consistent_reflections] * n_samples
        
    # Add incidence angle if available
    if "theta_rad" in sensor_results:
        base_data["theta"] = sensor_results["theta_rad"].tolist()
    elif base_data["theta"][0] is None:
        # Default theta for typical clamp-on installation
        n_points = len(base_data["timestamp"])
        base_data["theta"] = [np.pi/4] * n_points  # 45 degrees
    
    return base_data


def create_simulation_dataframe(simulation_data: Dict[str, Any]) -> pl.DataFrame:
    """
    Create a Polars DataFrame from assembled simulation data.
    
    Args:
        simulation_data: Complete simulation data dictionary
        
    Returns:
        Polars DataFrame with validated schema
    """
    validated_data = SimulationSchema.validate_data(simulation_data)
    return pl.DataFrame(validated_data, schema=SimulationSchema.SCHEMA)


def batch_to_polars(batch_data: List[Dict[str, Any]]) -> pl.DataFrame:
    """
    Convert a batch of simulation dictionaries to a single Polars DataFrame.
    
    Args:
        batch_data: List of simulation data dictionaries
        
    Returns:
        Concatenated Polars DataFrame
    """
    if not batch_data:
        # Return empty DataFrame with correct schema
        return pl.DataFrame(schema=SimulationSchema.SCHEMA)
    
    # Convert each dict to DataFrame and concatenate
    dfs = [create_simulation_dataframe(data) for data in batch_data]
    return pl.concat(dfs)


def resample_simulation_data(df: pl.DataFrame,
                           new_resolution_seconds: float,
                           method: str = "linear") -> pl.DataFrame:
    """
    Resample simulation data to a different time resolution.
    
    Args:
        df: Input Polars DataFrame
        new_resolution_seconds: New time step in seconds
        method: Interpolation method ('linear', 'nearest', 'forward_fill')
        
    Returns:
        Resampled DataFrame
    """
    # Create new timestamp grid
    start_time = df["timestamp"].min()
    end_time = df["timestamp"].max()
    duration = (end_time - start_time).total_seconds()
    
    new_timestamps = create_timestamp_series(
        start_time, int(duration), new_resolution_seconds
    )
    
    # Create target DataFrame with new timestamps
    target_df = pl.DataFrame({
        "timestamp": new_timestamps,
        "house_id": [df["house_id"][0]] * len(new_timestamps)
    })
    
    # Join and interpolate numeric columns
    numeric_cols = [col for col, dtype in SimulationSchema.SCHEMA.items() 
                   if dtype in [pl.Float64, pl.Int32] and col not in ["house_id"]]
    
    # For simplicity, use forward fill (nearest neighbor)
    # More sophisticated interpolation would require pandas or custom logic
    result = target_df.join_asof(
        df.sort("timestamp"),
        on="timestamp",
        strategy="forward"
    )
    
    return result


def to_pandas_bridge(df: pl.DataFrame) -> pd.DataFrame:
    """
    Convert Polars DataFrame to Pandas for ML pipeline compatibility.
    
    Args:
        df: Polars DataFrame
        
    Returns:
        Pandas DataFrame
    """
    return df.to_pandas()


def from_pandas_bridge(df: pd.DataFrame) -> pl.DataFrame:
    """
    Convert Pandas DataFrame to Polars with schema validation.
    
    Args:
        df: Pandas DataFrame
        
    Returns:
        Polars DataFrame with validated schema
    """
    # Convert to Polars and cast to correct schema
    pl_df = pl.from_pandas(df)
    
    # Cast columns to match schema where possible
    for col, expected_type in SimulationSchema.SCHEMA.items():
        if col in pl_df.columns:
            try:
                pl_df = pl_df.with_columns(pl.col(col).cast(expected_type))
            except Exception:
                # If casting fails, keep original type
                pass
    
    return pl_df


def calculate_simulation_statistics(df: pl.DataFrame) -> Dict[str, Any]:
    """
    Calculate summary statistics for simulation data.
    
    Args:
        df: Simulation DataFrame
        
    Returns:
        Dictionary of statistics
    """
    stats = {}
    
    # Basic info
    stats["n_rows"] = df.height
    stats["duration_hours"] = (df["timestamp"].max() - df["timestamp"].min()).total_seconds() / 3600
    stats["house_id"] = df["house_id"][0] if df.height > 0 else None
    
    # Flow statistics
    if "flow_gpm" in df.columns:
        flow_data = df["flow_gpm"].drop_nulls()
        stats["flow_stats"] = {
            "mean_gpm": flow_data.mean(),
            "max_gpm": flow_data.max(),
            "total_gal": flow_data.sum() * (1/60),  # gpm*sec -> gallons approx
            "zero_flow_fraction": (flow_data == 0).mean(),
        }
    
    # Event statistics
    if "leak" in df.columns:
        leak_data = df["leak"].drop_nulls()
        stats["leak_stats"] = {
            "total_leak_hours": leak_data.sum() / 3600,
            "leak_events": len(df.filter(pl.col("leak") & ~pl.col("leak").shift(1, fill_value=False))),
        }
    
    # Data quality
    stats["data_quality"] = {}
    for col in df.columns:
        null_count = df[col].null_count()
        stats["data_quality"][col] = {
            "null_count": null_count,
            "null_fraction": null_count / df.height if df.height > 0 else 0,
        }
    
    return stats