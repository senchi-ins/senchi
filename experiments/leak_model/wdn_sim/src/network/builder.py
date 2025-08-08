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

import wntr

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


def build_default_network() -> wntr.network.WaterNetworkModel:
    """Create a realistic default household plumbing network.

    This default mirrors the structure used in the legacy simulator
    (reservoir → service entry → main trunks → fixture branches) and
    provides a robust topology for EPANET.

    Naming convention aligns with the legacy WDN model to ease downstream
    event and leak placement:
      - Nodes: "MUNICIPAL_SUPPLY", "SERVICE_ENTRY", "MAIN_TRUNK_1", ...
      - Pipes: "SERVICE_LINE", "P_MAIN_1", "P_MAIN_2", ...
    """
    wn = wntr.network.WaterNetworkModel()

    # Supply head ~ 60 psi ≈ 138.6 ft ≈ 42.27 m; use a round 60 m for margin
    wn.add_reservoir("MUNICIPAL_SUPPLY", base_head=60)
    wn.add_junction("SERVICE_ENTRY", elevation=0.0, base_demand=0.0)

    # Routing / branch manifold junctions
    wn.add_junction("MAIN_TRUNK_1", elevation=0.0, base_demand=0.0)
    wn.add_junction("MAIN_TRUNK_2", elevation=0.0, base_demand=0.0)
    wn.add_junction("UPPER_FLOOR_BRANCH", elevation=1.5, base_demand=0.0)
    wn.add_junction("KITCHEN_BRANCH", elevation=0.0, base_demand=0.0)
    wn.add_junction("POWDER_ROOM_BRANCH", elevation=0.0, base_demand=0.0)

    # Fixtures (representative elevations in metres)
    fixtures = {
        # Main floor
        "KITCHEN_SINK": 0.0,
        "DISHWASHER": 0.0,
        "POWDER_ROOM_WC": 0.0,
        "POWDER_ROOM_LAV": 0.0,
        "HOSE_BIBB_FRONT": 0.0,
        "HOSE_BIBB_BACK": 0.0,
        # Upper floor
        "ENSUITE_WC": 3.0,
        "ENSUITE_LAV": 3.0,
        "ENSUITE_SHOWER": 3.0,
        "FAMILY_BATH_WC": 3.0,
        "FAMILY_BATH_LAV": 3.0,
        "FAMILY_BATH_TUB": 3.0,
        # Basement / lower
        "LAUNDRY_SINK": -2.5,
        "WATER_HEATER": -2.5,
    }
    for node, elev in fixtures.items():
        # Keep base_demand at 0; demand will be injected by simulator
        wn.add_junction(node, elevation=elev, base_demand=0.0)

    # Pipe parameters: 0.75 in service (or 1.0 in in some homes)
    service_diam_m = 0.75 * 0.0254  # 0.01905 m
    branch_diam_m = 0.5 * 0.0254    # 0.0127 m
    rough_main = 130.0  # Hazen-Williams C ~130 for Copper
    rough_branch = 130.0

    def add_pipe(name: str, n1: str, n2: str, length: float, diameter: float, rough: float):
        wn.add_pipe(name, n1, n2, length=length, diameter=diameter, roughness=rough)

    # Service line & main trunks (match service diameter)
    add_pipe("SERVICE_LINE", "MUNICIPAL_SUPPLY", "SERVICE_ENTRY", 10.0, service_diam_m, rough_main)
    add_pipe("P_MAIN_1", "SERVICE_ENTRY", "MAIN_TRUNK_1", 5.0, service_diam_m, rough_main)
    add_pipe("P_MAIN_2", "MAIN_TRUNK_1", "MAIN_TRUNK_2", 8.0, service_diam_m, rough_main)

    # Kitchen branch
    add_pipe("P_KITCHEN_BRANCH", "MAIN_TRUNK_1", "KITCHEN_BRANCH", 3.0, branch_diam_m, rough_branch)
    add_pipe("P_KITCHEN_SINK", "KITCHEN_BRANCH", "KITCHEN_SINK", 2.0, branch_diam_m, rough_branch)
    add_pipe("P_DISHWASHER", "KITCHEN_BRANCH", "DISHWASHER", 1.5, branch_diam_m, rough_branch)

    # Powder room branch
    add_pipe("P_POWDER_BRANCH", "MAIN_TRUNK_1", "POWDER_ROOM_BRANCH", 4.0, branch_diam_m, rough_branch)
    add_pipe("P_POWDER_WC", "POWDER_ROOM_BRANCH", "POWDER_ROOM_WC", 2.0, branch_diam_m, rough_branch)
    add_pipe("P_POWDER_LAV", "POWDER_ROOM_BRANCH", "POWDER_ROOM_LAV", 1.5, branch_diam_m, rough_branch)

    # Upper floor branch
    add_pipe("P_UPPER_BRANCH", "MAIN_TRUNK_2", "UPPER_FLOOR_BRANCH", 6.0, branch_diam_m, rough_branch)
    add_pipe("P_ENS_WC", "UPPER_FLOOR_BRANCH", "ENSUITE_WC", 3.0, branch_diam_m, rough_branch)
    add_pipe("P_ENS_LAV", "UPPER_FLOOR_BRANCH", "ENSUITE_LAV", 2.5, branch_diam_m, rough_branch)
    add_pipe("P_ENS_SHWR", "UPPER_FLOOR_BRANCH", "ENSUITE_SHOWER", 2.0, branch_diam_m, rough_branch)
    add_pipe("P_FAM_WC", "UPPER_FLOOR_BRANCH", "FAMILY_BATH_WC", 4.0, branch_diam_m, rough_branch)
    add_pipe("P_FAM_LAV", "UPPER_FLOOR_BRANCH", "FAMILY_BATH_LAV", 3.5, branch_diam_m, rough_branch)
    add_pipe("P_FAM_TUB", "UPPER_FLOOR_BRANCH", "FAMILY_BATH_TUB", 3.0, branch_diam_m, rough_branch)

    # Basement / lower fixtures
    add_pipe("P_LAUNDRY", "MAIN_TRUNK_2", "LAUNDRY_SINK", 5.0, branch_diam_m, rough_branch)
    add_pipe("P_WATER_HEATER", "MAIN_TRUNK_2", "WATER_HEATER", 3.0, branch_diam_m, rough_branch)

    # Hose bibbs
    add_pipe("P_HOSE_FRONT", "MAIN_TRUNK_1", "HOSE_BIBB_FRONT", 8.0, branch_diam_m, rough_branch)
    add_pipe("P_HOSE_BACK", "MAIN_TRUNK_2", "HOSE_BIBB_BACK", 6.0, branch_diam_m, rough_branch)

    wn.options.hydraulic.inpfile_units = "LPS"
    # Simulation timing defaults (can be overridden by simulator)
    wn.options.time.hydraulic_timestep = 300
    wn.options.time.pattern_timestep = 300
    

    return wn


def attach_default_demand_pattern(
    wn: wntr.network.WaterNetworkModel,
    house_profile: str = "modern_pex_small",
    month: int = 7,
    resolution_seconds: float = 300.0,
) -> None:
    """Attach a default 24h demand pattern built from DemandGenerator.

    The pattern is added but not assigned to any node by default; the caller
    can attach it to desired junctions (e.g., fixtures) as needed.
    """
    try:
        # Local import to avoid circulars at module import time
        from ..generators.demand_numpy import generate_daily_profile  # type: ignore
        import numpy as np

        demand_L_s = generate_daily_profile(
            house_profile=house_profile,
            resolution_seconds=resolution_seconds,
            month=month,
        )

        # Convert to a dimensionless multiplier pattern relative to mean flow
        demand_m3_s = demand_L_s / 1000.0
        mean_flow = float(np.maximum(np.mean(demand_m3_s), 1e-6))
        multipliers = (demand_m3_s / mean_flow).tolist()

        pattern_name = "PAT_DEFAULT"
        wn.add_pattern(pattern_name, multipliers)
    except Exception:
        # Best-effort only; safe to ignore if demand generator not available
        return


def assign_pattern_to_fixtures(
    wn: wntr.network.WaterNetworkModel,
    pattern_name: str = "PAT_DEFAULT",
) -> None:
    """Assign an existing pattern to all fixture junctions.

    Fixtures are all junctions except the routing/manifold nodes.
    Base demand is set to 1.0 as a multiplier; the pattern carries shape.
    """
    routing_nodes = {
        "SERVICE_ENTRY",
        "MAIN_TRUNK_1",
        "MAIN_TRUNK_2",
        "UPPER_FLOOR_BRANCH",
        "KITCHEN_BRANCH",
        "POWDER_ROOM_BRANCH",
    }
    for jn in wn.junction_name_list:
        if jn in routing_nodes:
            continue
        j = wn.get_node(jn)
        # Ensure there is at least one demand timeseries entry
        if not j.demand_timeseries_list:
            wn.add_demand(jn, 0.0, pattern_name)
        # Attach multiplicative pattern
        j.demand_timeseries_list[0].pattern_name = pattern_name
        j.demand_timeseries_list[0].base_value = 1.0


def configure_default_demands(
    wn: wntr.network.WaterNetworkModel,
    house_profile: str = "modern_pex_small",
    month: int = 7,
    resolution_seconds: float = 300.0,
) -> None:
    """Convenience: create a default demand pattern and assign to fixtures."""
    attach_default_demand_pattern(
        wn,
        house_profile=house_profile,
        month=month,
        resolution_seconds=resolution_seconds,
    )
    assign_pattern_to_fixtures(wn, pattern_name="PAT_DEFAULT")
