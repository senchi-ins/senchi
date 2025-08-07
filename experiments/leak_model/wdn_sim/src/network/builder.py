"""network.builder
-----------------
Utility to create a realistic EPANET household plumbing network from one of the
JSON profiles located in `config/house_profiles.json`.

The resulting WaterNetworkModel contains:
    Reservoir → StreetConnection → Meter → Main manifold → branch junctions

Branch junctions included:
    Kitchen, Bathroom1, Bathroom2 (if occupants >3), Laundry

All pipes inherit material, diameter and roughness from the profile.
Lengths are pulled from the JSON (total length and average branch length) but
kept very simple – the goal is to give hydraulics a realistic scale, not to
mirror exact floor-plans.
"""
from __future__ import annotations

import json
from pathlib import Path
from typing import Optional

import wntr  # type: ignore

CONFIG_PATH = Path(__file__).parent.parent.parent / "config" / "house_profiles.json"

def load_profile(profile_id: str, path: Path | str = CONFIG_PATH) -> dict:
    with open(path, "r") as f:
        data = json.load(f)
    for prof in data["profiles"]:
        if prof["id"] == profile_id:
            return prof["characteristics"]
    raise ValueError(f"Profile '{profile_id}' not found in {path}")

def build_network_from_profile(profile_id: str) -> wntr.network.WaterNetworkModel:
    char = load_profile(profile_id)

    main = char["main_distribution"]
    branch = char["branch_lines"]
    pressure = char["pressure_characteristics"]["supply_pressure_kPa"]

    wn = wntr.network.WaterNetworkModel()

    # Reservoir head (m)
    head = pressure / 9.80665
    wn.add_reservoir("Municipal", base_head=head)

    wn.add_junction("StreetConnection", base_demand=0.0, elevation=0.0)
    wn.add_junction("Meter", base_demand=0.0, elevation=0.5)
    wn.add_junction("Manifold", base_demand=0.001, elevation=1.5)  # demand overridden later

    # Fixtures
    occ_max = char["occupancy"]["max_people"]
    wn.add_junction("Kitchen", base_demand=0.0, elevation=1.5)
    wn.add_junction("Bathroom1", base_demand=0.0, elevation=1.5)
    if occ_max >= 4:
        wn.add_junction("Bathroom2", base_demand=0.0, elevation=4.0)
    wn.add_junction("Laundry", base_demand=0.0, elevation=0.5)

    # Pipe helpers
    def add_pipe(name: str, n1: str, n2: str, length: float, diameter_mm: float, rough: float):
        wn.add_pipe(name, n1, n2, length=length, diameter=diameter_mm / 1000.0, roughness=rough)

    # Service & main distribution
    add_pipe("ServiceLine", "Municipal", "StreetConnection", 20.0, main["diameter_mm"], main["roughness_mm"])
    add_pipe("ToMeter", "StreetConnection", "Meter", 2.0, main["diameter_mm"], main["roughness_mm"])
    add_pipe("MainSupply", "Meter", "Manifold", 6.0, main["diameter_mm"], main["roughness_mm"])

    # Branches – use avg_length_m from profile
    add_pipe("ToKitchen", "Manifold", "Kitchen", branch["avg_length_m"], branch["diameter_mm"], branch["roughness_mm"])
    add_pipe("ToBath1", "Manifold", "Bathroom1", branch["avg_length_m"], branch["diameter_mm"], branch["roughness_mm"])
    if "Bathroom2" in wn.junction_name_list:
        add_pipe("ToBath2", "Manifold", "Bathroom2", branch["avg_length_m"], branch["diameter_mm"], branch["roughness_mm"])
    add_pipe("ToLaundry", "Manifold", "Laundry", branch["avg_length_m"] * 0.5, branch["diameter_mm"], branch["roughness_mm"])

    # Simulation options – will be overridden by HouseSimulator
    wn.options.time.duration = 24 * 3600
    wn.options.time.hydraulic_timestep = 300  # default 5-min
    wn.options.time.pattern_timestep = 300

    return wn
