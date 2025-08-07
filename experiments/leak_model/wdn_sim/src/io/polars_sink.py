"""
polars_sink.py
--------------
Streaming I/O for massive simulation datasets using Polars.
Handles memory-efficient writes to Parquet/CSV without bloat.
"""

import polars as pl
import os
from pathlib import Path
from typing import Dict, Any, Optional, List, Union
import datetime
import numpy as np


class SimulationSchema:
    """Defines the standard simulation output schema."""
    
    SCHEMA = {
        "timestamp": pl.Datetime("ms"),
        "house_id": pl.Int32,
        "flow_m3_s": pl.Float64,  # Volumetric flow (m³/s)
        "flow_gpm": pl.Float64,  # Volumetric flow (gallons/min)
        "velocity": pl.Float64,  # Internal pipe velocity (m/s)
        "totalizer": pl.Float64,  # Cumulative consumption (L)
        "pressure": pl.Float64,  # Local static pressure (kPa)
        "downstream_wave_time": pl.Float64,  # Transit-time differentials
        "upstream_wave_time": pl.Float64,
        "delta_t_raw": pl.Float64,
        "theta": pl.Float64,  # Incidence angle (radians)
        "pipe_diameter": pl.Float64,  # Internal diameter (mm)
        "number_of_ultrasonic_reflections": pl.Int32,  # Signal quality metric
        "pipe_material": pl.Utf8,  # e.g. 'PEX', 'Copper', 'PVC'
        "leak": pl.Boolean,  # Binary indicator (True = leak/burst active)
        "location": pl.Utf8,  # Fixture or segment for the event
    }
    
    @classmethod
    def validate_data(cls, data: Dict[str, Any]) -> Dict[str, Any]:
        """Validate and cast data to match schema."""
        validated = {}
        
        # First pass: convert all data to lists and find max length
        max_length = 0
        for col, expected_type in cls.SCHEMA.items():
            if col in data:
                value = data[col]
                if isinstance(value, (list, np.ndarray)):
                    validated[col] = list(value)
                    max_length = max(max_length, len(validated[col]))
                else:
                    validated[col] = [value]  # Convert scalar to list
                    max_length = max(max_length, 1)
        
        # Second pass: ensure all columns have the same length
        for col, expected_type in cls.SCHEMA.items():
            if col not in validated:
                # Set default values for missing columns
                if expected_type == pl.Boolean:
                    validated[col] = [False] * max_length
                elif expected_type in [pl.Int32, pl.Float64]:
                    validated[col] = [None] * max_length
                elif expected_type == pl.Utf8:
                    validated[col] = [None] * max_length
                elif expected_type == pl.Datetime("ms"):
                    validated[col] = [None] * max_length
            else:
                # Pad existing columns to max_length if needed
                current_length = len(validated[col])
                if current_length < max_length:
                    # Extend with last value or None
                    if current_length > 0:
                        fill_value = validated[col][-1]
                    else:
                        fill_value = None
                    validated[col].extend([fill_value] * (max_length - current_length))
        
        return validated


class StreamingSink:
    """Handles streaming writes of simulation data to disk."""
    
    def __init__(self, 
                 output_dir: Union[str, Path],
                 file_format: str = "parquet",
                 batch_size: int = 10000,
                 compression: str = "snappy"):
        """
        Initialize streaming sink.
        
        Args:
            output_dir: Directory to write files
            file_format: 'parquet' or 'csv'
            batch_size: Number of rows to accumulate before flushing
            compression: Compression method ('snappy', 'gzip', 'lz4')
        """
        self.output_dir = Path(output_dir)
        self.output_dir.mkdir(parents=True, exist_ok=True)
        
        self.file_format = file_format.lower()
        if self.file_format not in ["parquet", "csv"]:
            raise ValueError("file_format must be 'parquet' or 'csv'")
            
        self.batch_size = batch_size
        self.compression = compression
        self._buffer = []
        self._file_counter = 0
        
    def add_batch(self, data: Dict[str, Any]) -> None:
        """Add a batch of simulation data to the buffer."""
        validated_data = SimulationSchema.validate_data(data)
        self._buffer.append(validated_data)
        
        if len(self._buffer) >= self.batch_size:
            self.flush()
    
    def flush(self) -> Optional[str]:
        """Write buffered data to disk and clear buffer."""
        if not self._buffer:
            return None
            
        # Combine all batches in buffer
        combined_data = {}
        for col in SimulationSchema.SCHEMA.keys():
            combined_data[col] = []
            for batch in self._buffer:
                if col in batch:
                    if isinstance(batch[col], list):
                        combined_data[col].extend(batch[col])
                    else:
                        combined_data[col].append(batch[col])
        
        # Create Polars DataFrame
        df = pl.DataFrame(combined_data, schema=SimulationSchema.SCHEMA)
        
        # Generate filename
        import os
        file_prefix = os.environ.get("SIM_FILE_PREFIX", "")
        if file_prefix:
            filename = f"{file_prefix}.{self.file_format}"
        else:
            # Fallback to original naming if no prefix is set
            timestamp = datetime.datetime.now().strftime("%Y%m%d_%H%M%S")
            filename = f"simulation_batch_{self._file_counter:04d}_{timestamp}.{self.file_format}"
        filepath = self.output_dir / filename
        
        # Write to disk
        if self.file_format == "parquet":
            df.write_parquet(filepath, compression=self.compression)
        else:  # csv
            df.write_csv(filepath)
        
        # Clear buffer and increment counter
        self._buffer.clear()
        self._file_counter += 1
        
        return str(filepath)
    
    def __enter__(self):
        return self
    
    def __exit__(self, exc_type, exc_val, exc_tb):
        self.flush()


def write_house_simulation(house_id: int,
                          simulation_data: Dict[str, Any],
                          output_dir: Union[str, Path],
                          file_format: str = "parquet") -> str:
    """
    Write a complete house simulation to a single file.
    
    Args:
        house_id: House identifier
        simulation_data: Dictionary with simulation results
        output_dir: Output directory
        file_format: 'parquet' or 'csv'
    
    Returns:
        Path to written file
    """
    output_dir = Path(output_dir)
    output_dir.mkdir(parents=True, exist_ok=True)
    
    # Ensure house_id is in data
    if "house_id" not in simulation_data:
        n_rows = len(next(iter(simulation_data.values())))
        simulation_data["house_id"] = [house_id] * n_rows
    
    # Validate and create DataFrame
    validated_data = SimulationSchema.validate_data(simulation_data)
    df = pl.DataFrame(validated_data, schema=SimulationSchema.SCHEMA)
    
    # Generate filename
    date_str = datetime.datetime.now().strftime("%Y%m%d")
    filename = f"house_{house_id:06d}_{date_str}.{file_format}"
    filepath = output_dir / filename
    
    # Write to disk
    if file_format == "parquet":
        df.write_parquet(filepath, compression="snappy")
    else:
        df.write_csv(filepath)
    
    return str(filepath)


def read_simulation_batch(filepath: Union[str, Path]) -> pl.DataFrame:
    """
    Read a simulation batch file into a Polars DataFrame.
    
    Args:
        filepath: Path to the file
        
    Returns:
        Polars DataFrame with simulation data
    """
    filepath = Path(filepath)
    
    if filepath.suffix.lower() == ".parquet":
        return pl.read_parquet(filepath)
    elif filepath.suffix.lower() == ".csv":
        return pl.read_csv(filepath, schema=SimulationSchema.SCHEMA)
    else:
        raise ValueError(f"Unsupported file format: {filepath.suffix}")


def concatenate_simulation_files(file_paths: List[Union[str, Path]],
                                output_path: Union[str, Path],
                                file_format: str = "parquet") -> str:
    """
    Concatenate multiple simulation files into a single file.
    
    Args:
        file_paths: List of paths to concatenate
        output_path: Output file path
        file_format: Output format ('parquet' or 'csv')
        
    Returns:
        Path to concatenated file
    """
    if not file_paths:
        raise ValueError("No files provided for concatenation")
    
    # Read all files lazily and concatenate
    lazy_dfs = []
    for path in file_paths:
        if Path(path).suffix.lower() == ".parquet":
            lazy_dfs.append(pl.scan_parquet(path))
        else:
            lazy_dfs.append(pl.scan_csv(path, schema=SimulationSchema.SCHEMA))
    
    # Concatenate and write
    combined_lazy = pl.concat(lazy_dfs)
    
    if file_format == "parquet":
        combined_lazy.sink_parquet(output_path, compression="snappy")
    else:
        combined_lazy.sink_csv(output_path)
    
    return str(output_path)


def estimate_memory_usage(n_rows: int, n_houses: int = 1) -> Dict[str, float]:
    """
    Estimate memory usage for simulation data.
    
    Args:
        n_rows: Number of time steps
        n_houses: Number of houses
        
    Returns:
        Dictionary with memory estimates in MB
    """
    # Estimate bytes per row based on schema
    bytes_per_row = (
        8 +   # timestamp (datetime64)
        4 +   # house_id (int32)
        8 * 9 +  # 9 float64 columns
        4 +   # int32 reflections
        20 +  # pipe_material string (estimate)
        1 +   # leak boolean
        15    # location string (estimate)
    )
    
    total_bytes = bytes_per_row * n_rows * n_houses
    
    return {
        "raw_data_mb": total_bytes / (1024 * 1024),
        "with_overhead_mb": (total_bytes * 1.5) / (1024 * 1024),  # 50% overhead
        "recommended_batch_size": max(1000, min(50000, 100_000_000 // bytes_per_row))
    }