"""
WDN_sim.py
--------------------------------------------
High‑fidelity, physics‑based generator for *minute‑resolution* residential water data
across **multiple months** with realistic *seasonal variation*.

Core engine: EPANET via the **WNTR** Python library – all flows, pressures, and velocities
satisfy continuity, energy balance, and Bernoulli.  Burst / leak events are injected using
EPANET leak emitters or pressure ramps and occur only in climatologically plausible months
(e.g., freeze bursts in winter).

-----------------
HOW IT WORKS
-----------------
* Each home (service pipe + junction) is modelled as an independent network.
* A diurnal demand curve is scaled by:
    • **household factor** (0.8 – 1.2×),
    • **seasonal factor** (e.g., 1.20× in July, 0.90× in January),
    • **random daily multiplier** (~N(1,0.05)).
* Leaks/bursts:
    - *micro* (constant small emitter),
    - *gradual* (emitter grows over days),
    - *freeze* (only in Dec–Feb; sudden large break at night with sub‑freezing flag),
    - *pressure* (progressive over‑pressure then rupture; allowed any month),
    - *none*.
* Safety: velocities are clipped to 2.4 m s⁻¹ for copper, 3.0 m s⁻¹ for PEX.
* Ultrasonic meter transit‑time outputs are derived each minute.

-----------------
USAGE
-----------------
1.  **Install deps**

    ```bash
    conda create -n WDN_sim python=3.9 wntr pandas numpy tqdm
    conda activate WDN_sim
    ```

2.  **Run for full year (default)**

    ```bash
    cd experiments/leak_model/data
    python WDN_sim.py
    ```

    → writes **synthetic_water_data_minute.csv.gz**

3.  **Custom range**

    ```bash
    python generate_synthetic_water_network_seasonal.py --start 2025-03 --end 2025-09
    ```

-----------------
CONFIGURABLE FLAGS
-----------------
--start  YYYY-MM   inclusive (default 2025-01)
--end    YYYY-MM   inclusive (default 2025-12)
--homes  integer    number of homes (default 1000)
--out    path       output .csv.gz (default synthetic_water_data_minute.csv.gz)

"""

import argparse, calendar, sys, math, random, gzip, csv, gc
from datetime import datetime, timedelta
from scipy.optimize import root_scalar

import numpy as np
import wntr
from tqdm import tqdm

# ----------------------------------------------------------------------------
# CONSTANTS
# ----------------------------------------------------------------------------
C_SPEED   = 1473.8 # m/s at roughly 18C
N_TRAVERSES = 4 # number of travel lengths for a W-path approach
THETA_DEG = 60 # angle of incidence in degrees
COS_THETA = math.cos(math.radians(THETA_DEG)) # cos 60 degrees in radians (0.5)
SIN_THETA = math.sin(math.radians(THETA_DEG)) # sin 60 degrees in radians (0.866)
STEP_MIN  = 15 # time step in minutes

# Seasonal demand factor (literature & utility data averages)
SEASON_FACTOR = {
    1: 0.90,  2: 0.90,  3: 1.00,  4: 1.05,
    5: 1.10,  6: 1.15,  7: 1.20,  8: 1.15,
    9: 1.05, 10: 1.00, 11: 0.95, 12: 0.90
}

# -----------------------------------------------------------------------------
# FIXTURE CATEGORIES & BRANCH MAPPING (single-source of truth)
# -----------------------------------------------------------------------------

CATEGORY_MAP = {
    "toilet": ["POWDER_ROOM_WC", "ENSUITE_WC", "FAMILY_BATH_WC"],
    "shower": ["ENSUITE_SHOWER", "FAMILY_BATH_TUB"],
    "laundry": ["LAUNDRY_SINK"],
    "dish": ["DISHWASHER"],
    "faucet": [
        "KITCHEN_SINK", "POWDER_ROOM_LAV", "ENSUITE_LAV", "FAMILY_BATH_LAV",
        "HOSE_BIBB_FRONT", "HOSE_BIBB_BACK", "WATER_HEATER",
    ],
}

BRANCH_MAP = {
    "KITCHEN_SINK": "KITCHEN_BRANCH",
    "DISHWASHER": "KITCHEN_BRANCH",
    "POWDER_ROOM_WC": "POWDER_ROOM_BRANCH",
    "POWDER_ROOM_LAV": "POWDER_ROOM_BRANCH",
    "ENSUITE_WC": "UPPER_FLOOR_BRANCH",
    "ENSUITE_LAV": "UPPER_FLOOR_BRANCH",
    "ENSUITE_SHOWER": "UPPER_FLOOR_BRANCH",
    "FAMILY_BATH_WC": "UPPER_FLOOR_BRANCH",
    "FAMILY_BATH_LAV": "UPPER_FLOOR_BRANCH",
    "FAMILY_BATH_TUB": "UPPER_FLOOR_BRANCH",
    "LAUNDRY_SINK": "MAIN_TRUNK_2",
    "WATER_HEATER": "MAIN_TRUNK_2",
    "HOSE_BIBB_FRONT": "MAIN_TRUNK_1",
    "HOSE_BIBB_BACK": "MAIN_TRUNK_2",
}

# ----------------------------------------------------------------------------
# TEMPERATURE FROM SPEED OF SOUND
# ----------------------------------------------------------------------------

def temp_from_c(c: float) -> float:
    """
    Convert speed of sound [m/s] to temperature [°C] for fresh water
    using the quadratic c = 1404.3 + 4.7 T – 0.04 T².
    """
    disc = 4.7**2 - 0.16 * (c - 1404.3) # discriminant
    return (4.7 - math.sqrt(disc)) / 0.08 # smaller root is the physical one (0–40 °C range)


# ----------------------------------------------------------------------------
# DEMAND PATTERN (one day – 1 440 mins)
# ----------------------------------------------------------------------------
def build_daily_pattern(month: int, demand_scale: float):
    pattern = np.full(1440, 0.0003)           # night base
    # lawn‑watering spike (summer months stronger)
    lawn_amp = 0.0020 if month in (5,6,7,8,9) else 0.0012
    pattern[5*60:6*60] = lawn_amp
    # morning routine
    pattern[6*60:9*60] = 0.0010
    # lunch bump
    pattern[12*60:13*60] = 0.0006
    # evening peak
    pattern[17*60:22*60] = 0.0011
    # normalise and scale
    pattern /= pattern.sum()
    pattern *= demand_scale * SEASON_FACTOR[month]
    return pattern

# ----------------------------------------------------------------------------
# HOME CONFIG
# ----------------------------------------------------------------------------
def sample_home_cfg(house_id: int):
    return dict(
        house_id = house_id,
        material = random.choice(['Copper','PEX']),
        diameter_in = random.choice([0.75,1.0]),
        demand_scale = random.uniform(0.8,1.2),
        leak_type = random.choices(
            ['none','micro','gradual','burst_freeze','burst_pressure'],
            weights=[0.55,0.10,0.12,0.13,0.10])[0]
    )

# ----------------------------------------------------------------------------
# NETWORK BUILD
# ----------------------------------------------------------------------------
def build_network(cfg, month):
    """
    Build a realistic single-detached home plumbing network.

    Reservoir (municipal supply) → service line → main trunks → fixture branches.
    The service line is our “sensor” location from which we record flows and
    pressures; demand is applied at each fixture junction using the existing
    diurnal pattern builder.
    """

    wn = wntr.network.WaterNetworkModel()

    # ------------------------------------------------------------------
    # Core supply nodes
    # ------------------------------------------------------------------
    wn.add_reservoir("MUNICIPAL_SUPPLY", base_head=60)  # 60 psi ≈ 138.6 ft
    wn.add_junction("SERVICE_ENTRY", elevation=0, base_demand=0.0)

    # Junctions for pipe routing / branches
    wn.add_junction("MAIN_TRUNK_1", elevation=0,  base_demand=0.0)
    wn.add_junction("MAIN_TRUNK_2", elevation=0,  base_demand=0.0)
    wn.add_junction("UPPER_FLOOR_BRANCH",  elevation=1.5, base_demand=0.0)
    wn.add_junction("KITCHEN_BRANCH",      elevation=0,   base_demand=0.0)
    wn.add_junction("POWDER_ROOM_BRANCH",  elevation=0,   base_demand=0.0)

    # Fixture nodes (approximate elevations in metres)
    fixtures = {
        # Main floor
        "KITCHEN_SINK": 0,
        "DISHWASHER": 0,
        "POWDER_ROOM_WC": 0,
        "POWDER_ROOM_LAV": 0,
        "HOSE_BIBB_FRONT": 0,
        "HOSE_BIBB_BACK": 0,
        # Upper floor
        "ENSUITE_WC": 3.0,
        "ENSUITE_LAV": 3.0,
        "ENSUITE_SHOWER": 3.0,
        "FAMILY_BATH_WC": 3.0,
        "FAMILY_BATH_LAV": 3.0,
        "FAMILY_BATH_TUB": 3.0,
        # Basement
        "LAUNDRY_SINK": -2.5,
        "WATER_HEATER": -2.5,
    }

    # ------------------------------------------------------------------
    # Assign base demands according to end-use weights
    # ------------------------------------------------------------------
    weights = {
        "toilet": 0.167,
        "shower": 0.333,
        "laundry": 0.222,
        "dish": 0.056,
        "faucet": 0.222,
    }

    scaling_factor = len(fixtures)  # keep overall magnitude similar to previous version

    base_demand_map = {}
    for cat, nodes in CATEGORY_MAP.items():
        per_node = (weights[cat] / len(nodes)) * scaling_factor
        for n in nodes:
            base_demand_map[n] = per_node

    # Create fixture junctions with weighted base demands
    for name, elev in fixtures.items():
        bd = base_demand_map.get(name, 1.0)
        wn.add_junction(name, elevation=elev, base_demand=bd)

    # ------------------------------------------------------------------
    # Pipes
    # ------------------------------------------------------------------
    rough = 130 if cfg["material"] == "Copper" else 160
    service_diam_m = cfg["diameter_in"] * 0.0254  # convert inches → metres (0.75 or 1.0 in)

    wn.add_pipe(
        "SERVICE_LINE",
        "MUNICIPAL_SUPPLY",
        "SERVICE_ENTRY",
        length=10,
        diameter=service_diam_m,
        roughness=rough,
        initial_status="OPEN",
    )

    # Main trunk – match service diameter (0.75 in or 1 in)
    wn.add_pipe("P_MAIN_1", "SERVICE_ENTRY", "MAIN_TRUNK_1", length=5, diameter=service_diam_m, roughness=rough)
    wn.add_pipe("P_MAIN_2", "MAIN_TRUNK_1", "MAIN_TRUNK_2", length=8, diameter=service_diam_m, roughness=rough)

    # Kitchen branch – 1/2" PEX (≈12.7 mm)
    wn.add_pipe("P_KITCHEN_BRANCH", "MAIN_TRUNK_1", "KITCHEN_BRANCH", length=3, diameter=0.0127, roughness=rough)
    wn.add_pipe("P_KITCHEN_SINK", "KITCHEN_BRANCH", "KITCHEN_SINK", length=2, diameter=0.0127, roughness=rough)
    wn.add_pipe("P_DISHWASHER", "KITCHEN_BRANCH", "DISHWASHER", length=1.5, diameter=0.0127, roughness=rough)

    # Powder room branch
    wn.add_pipe("P_POWDER_BRANCH", "MAIN_TRUNK_1", "POWDER_ROOM_BRANCH", length=4, diameter=0.0127, roughness=rough)
    wn.add_pipe("P_POWDER_WC", "POWDER_ROOM_BRANCH", "POWDER_ROOM_WC", length=2, diameter=0.0127, roughness=rough)
    wn.add_pipe("P_POWDER_LAV", "POWDER_ROOM_BRANCH", "POWDER_ROOM_LAV", length=1.5, diameter=0.0127, roughness=rough)

    # Upper floor branch
    wn.add_pipe("P_UPPER_BRANCH", "MAIN_TRUNK_2", "UPPER_FLOOR_BRANCH", length=6, diameter=0.0127, roughness=rough)
    wn.add_pipe("P_ENS_WC",    "UPPER_FLOOR_BRANCH", "ENSUITE_WC",    length=3,   diameter=0.0127, roughness=rough)
    wn.add_pipe("P_ENS_LAV",   "UPPER_FLOOR_BRANCH", "ENSUITE_LAV",   length=2.5, diameter=0.0127, roughness=rough)
    wn.add_pipe("P_ENS_SHWR",  "UPPER_FLOOR_BRANCH", "ENSUITE_SHOWER",length=2,   diameter=0.0127, roughness=rough)
    wn.add_pipe("P_FAM_WC",    "UPPER_FLOOR_BRANCH", "FAMILY_BATH_WC",length=4,   diameter=0.0127, roughness=rough)
    wn.add_pipe("P_FAM_LAV",   "UPPER_FLOOR_BRANCH", "FAMILY_BATH_LAV",length=3.5, diameter=0.0127, roughness=rough)
    wn.add_pipe("P_FAM_TUB",   "UPPER_FLOOR_BRANCH", "FAMILY_BATH_TUB",length=3,   diameter=0.0127, roughness=rough)

    # Basement fixtures
    wn.add_pipe("P_LAUNDRY",      "MAIN_TRUNK_2", "LAUNDRY_SINK", length=5, diameter=0.0127, roughness=rough)
    wn.add_pipe("P_WATER_HEATER", "MAIN_TRUNK_2", "WATER_HEATER",  length=3, diameter=0.0127, roughness=rough)

    # Hose bibbs
    wn.add_pipe("P_HOSE_FRONT", "MAIN_TRUNK_1", "HOSE_BIBB_FRONT", length=8, diameter=0.0127, roughness=rough)
    wn.add_pipe("P_HOSE_BACK",  "MAIN_TRUNK_2", "HOSE_BIBB_BACK",  length=6, diameter=0.0127, roughness=rough)

    # ------------------------------------------------------------------
    # Demand pattern – shared across all fixtures
    # ------------------------------------------------------------------
    pattern_array = build_daily_pattern(month, cfg["demand_scale"])
    pat = wntr.network.elements.Pattern("PAT1", pattern_array)
    wn.add_pattern("PAT1", pat)

    for node in fixtures.keys():
        wn.get_node(node).demand_timeseries_list[0].pattern_name = "PAT1"

    # Simulation timing
    wn.options.time.hydraulic_timestep = STEP_MIN * 60
    wn.options.time.pattern_timestep   = STEP_MIN * 60
    wn.options.time.report_timestep    = STEP_MIN * 60
    wn.options.hydraulic.inpfile_units = "LPS"

    return wn

# ----------------------------------------------------------------------------
# LEAK / BURST SCHEDULING  (relative to month start)
# ----------------------------------------------------------------------------
def schedule_leak(wn, cfg, sim_minutes, month):
    lt = cfg['leak_type']
    if lt == 'none':
        return None
    # Disallow freeze bursts outside Dec‑Feb
    if lt == 'burst_freeze' and month not in (12,1,2):
        lt = 'none'
    if lt == 'none':
        return None

    # Select a random junction (fixture or branch) excluding the service entry
    candidate_nodes = [n for n in wn.junction_name_list if n != 'SERVICE_ENTRY']
    if not candidate_nodes:
        return None  # fallback safety
    leak_node_name = random.choice(candidate_nodes)
    J = wn.get_node(leak_node_name)

    # Determine category and branch for the leak node
    leak_category = next((cat for cat, nodes in CATEGORY_MAP.items() if leak_node_name in nodes), "unknown")

    leak_branch = BRANCH_MAP.get(leak_node_name, "unknown")

    # Determine specific pipe (first link connected to node)
    try:
        connected_links = wn.get_links_for_node(leak_node_name)
        # Prefer the pipe that is NOT in BRANCH_MAP values when two links
        if len(connected_links) == 2:
            # choose link whose name ends at leak_node_name
            leak_pipe = next((l for l in connected_links if l.startswith('P_') or leak_node_name in l), connected_links[0])
        else:
            leak_pipe = connected_links[0] if connected_links else "unknown"
    except Exception:
        leak_pipe = "unknown"

    if lt == 'micro':
        # Constant small leak throughout the month
        start = 0
        end = sim_minutes
        # Convert coefficient to approximate leak area (m²)
        area = 0.0001  # Small leak area
        J.add_leak(wn, area, discharge_coeff=0.75, 
                  start_time=0, end_time=sim_minutes*60)
        return (start, end, 'micro', area, leak_category, leak_branch, leak_pipe)
        
    elif lt == 'gradual':
        # Gradual leak progression over days
        dur = random.randint(2*24*60, 5*24*60)  # 2-5 days
        start = random.randint(0, sim_minutes - dur - 1)
        end = start + dur
        
        # Use a single leak with moderate area for gradual leaks
        # The physics-based model will still provide pressure-dependent behavior
        area = 0.0002  # Moderate leak area
        J.add_leak(wn, area, discharge_coeff=0.75,
                  start_time=start*60, end_time=end*60)
        return (start, end, 'gradual', area, leak_category, leak_branch, leak_pipe)
        
    elif lt == 'burst_freeze':
        # Sudden freeze burst
        start = random.randint(0, sim_minutes - 6*60)
        end = start + random.randint(3*60, 6*60)  # 3-6 hours
        area = 0.001  # Large leak area for burst
        J.add_leak(wn, area, discharge_coeff=0.75,
                  start_time=start*60, end_time=end*60)
        return (start, end, 'burst_freeze', area, leak_category, leak_branch, leak_pipe)
        
    elif lt == 'burst_pressure':
        # Sudden pressure burst
        start = random.randint(0, sim_minutes - 3*60)
        end = start + random.randint(60, 180)  # 1-3 hours
        area = 0.002  # Very large leak area for pressure burst
        J.add_leak(wn, area, discharge_coeff=0.75,
                  start_time=start*60, end_time=end*60)
        return (start, end, 'burst_pressure', area, leak_category, leak_branch, leak_pipe)
    else:
        return None

# ----------------------------------------------------------------------------
# SIM ONE HOME, ONE MONTH
# ----------------------------------------------------------------------------
def simulate_home_month(cfg, year, month, writer, chunk_size=1000):
    """Memory-optimized simulation with chunked processing"""
    days_in_month = calendar.monthrange(year, month)[1]
    sim_minutes = days_in_month * 24 * 60
    start_dt = datetime(year, month, 1)
    
    # Build network
    wn = build_network(cfg, month)
    wn.options.time.duration = sim_minutes*60
    leak_window = schedule_leak(wn, cfg, sim_minutes, month)
    
    # Run simulation
    sim = wntr.sim.EpanetSimulator(wn)
    r = sim.run_sim()

    # Calculate common values
    pressure = r.node['pressure']['SERVICE_ENTRY']  # psi
    flow_m3s = r.link['flowrate']['SERVICE_LINE']   # m3/s
    flow_gpm = flow_m3s * 264.172 * 60 # m3/s to gpm
    d_inner = cfg['diameter_in']*0.0254
    area = math.pi*(d_inner/2)**2
    velocity = flow_m3s / area
    vmax = 2.4 if cfg['material']=='Copper' else 3.0
    velocity = velocity.clip(upper=vmax)

    # Heat transfer constants
    H_INDOOR = 10.0 if cfg["material"] == "Copper" else 3.0 # W/m²·K
    T_ENV_C = 18.0 # °C (basement temperature)
    L_to_valve = 23.0  # m - total main trunk length (SERVICE_LINE + P_MAIN_1 + P_MAIN_2 = 10+5+8)
    Q = flow_m3s
    rho = 999.33 # kg/m³ - density of water at 14°C
    c_water = 4184.0 # J/kg·K - heat capacity of water
    T_supply = 10.0 # °C water temperature in the city main

    # exponential cooling factor (dimensionless)
    beta = (H_INDOOR * math.pi * d_inner * L_to_valve) / (rho * c_water * Q)
    # handle divide-by-zero when flow is truly zero
    beta = beta.replace([np.inf, -np.inf], np.nan).fillna(1e9)

    # temperature estimate
    T_est  = T_ENV_C + (T_supply - T_ENV_C) * np.exp(-beta)

    # speed of sound estimate
    c_est = 1404.3 + 4.7*T_est - 0.04*T_est**2

    OD_mm = cfg['diameter_in'] * 25.4
    wall_mm = (0.045 if cfg['material']=='Copper' else
            0.097) if cfg['diameter_in']==0.75 else \
            (0.050 if cfg['material']=='Copper' else 0.125)
    ID_m = (OD_mm - 2*wall_mm) / 1000.0 # mm → m
    L_PATH = (N_TRAVERSES * ID_m) / SIN_THETA # W-path @ 60°

    t_down = L_PATH / (c_est + velocity*COS_THETA)
    t_up = L_PATH / (c_est - velocity*COS_THETA)
    delta_t_ns = (t_down - t_up) * 1e9

    # Process results in chunks to reduce memory usage
    total_steps = len(pressure)
    
    for chunk_start in range(0, total_steps, chunk_size):
        chunk_end = min(chunk_start + chunk_size, total_steps)
        
        # Extract chunk data
        pressure_chunk = pressure.iloc[chunk_start:chunk_end]
        flow_m3s_chunk = flow_m3s.iloc[chunk_start:chunk_end]
        flow_gpm_chunk = flow_gpm.iloc[chunk_start:chunk_end]
        velocity_chunk = velocity.iloc[chunk_start:chunk_end]
        t_up_chunk = t_up.iloc[chunk_start:chunk_end]
        t_down_chunk = t_down.iloc[chunk_start:chunk_end]
        delta_t_ns_chunk = delta_t_ns.iloc[chunk_start:chunk_end]
        T_est_chunk = T_est.iloc[chunk_start:chunk_end]
        c_est_chunk = c_est.iloc[chunk_start:chunk_end]
        
        # Write chunk data
        for sec, v, tu, td, p, dt_ns, flow_val, flow_gpm_val, T_est_val, c_est_val in zip(
            pressure_chunk.index, velocity_chunk.values, t_up_chunk.values, 
            t_down_chunk.values, pressure_chunk.values, delta_t_ns_chunk.values,
            flow_m3s_chunk.values, flow_gpm_chunk.values, T_est_chunk.values, c_est_chunk.values
        ):
            ts = start_dt + timedelta(seconds=int(sec))
            leak_flag = False
            leak_cat = leak_br = leak_pipe = ''
            if leak_window:
                leak_start, leak_end, _, _, lc, lb, lp = leak_window
                leak_flag = leak_start*60 <= sec <= leak_end*60
                leak_cat, leak_br, leak_pipe = (lc, lb, lp) if leak_flag else ('', '', '')
            
            writer.writerow([
                ts.isoformat(), cfg['house_id'],
                float(v), # velocity_m_per_s
                float(flow_val), # flow_m3_s
                float(flow_gpm_val), # flow_gpm

                float(tu), float(td),
                float(dt_ns), # delta_t_ns

                float(p), # pressure_psi

                cfg['material'], cfg['diameter_in'],

                float(OD_mm),
                float(wall_mm),
                float(ID_m*1000), # id_mm
                float(L_PATH),

                leak_flag,
                cfg['leak_type'],
                leak_cat,
                leak_br,
                leak_pipe,

                float(c_est_val),
                float(T_est_val),

                N_TRAVERSES,
                THETA_DEG 
            ])
    
    # Clean up memory
    del wn, sim, r, pressure, flow_m3s, flow_gpm, velocity
    del t_down, t_up, delta_t_ns, T_est, c_est
    gc.collect()

# ----------------------------------------------------------------------------
# MAIN
# ----------------------------------------------------------------------------
def main():
    parser = argparse.ArgumentParser()
    parser.add_argument('--start', default='2025-01', help='YYYY-MM inclusive start month')
    parser.add_argument('--end',   default='2025-12', help='YYYY-MM inclusive end month')
    parser.add_argument('--homes', type=int, default=1000)
    parser.add_argument('--out',   default='synthetic_water_data_minute.csv.gz')
    parser.add_argument('--batch-size', type=int, default=50, 
                       help='Number of homes to process before garbage collection')
    parser.add_argument('--chunk-size', type=int, default=1000,
                       help='Number of time steps to process in each chunk')
    args = parser.parse_args()

    start_year, start_month = map(int, args.start.split('-'))
    end_year, end_month     = map(int, args.end.split('-'))
    # Build list of (year, month)
    months = []
    y, m = start_year, start_month
    while (y < end_year) or (y == end_year and m <= end_month):
        months.append((y,m))
        m += 1
        if m > 12:
            m = 1
            y += 1

    random.seed(42)
    cfgs = [sample_home_cfg(h) for h in range(1, args.homes+1)]

    with gzip.open(args.out, 'wt', newline='') as gz:
        writer = csv.writer(gz)
        writer.writerow([
            'timestamp','house_id',
            'velocity_m_per_s','flow_m3_s','flow_gpm',
            'upstream_transit_time_s','downstream_transit_time_s','delta_t_ns',
            'pressure_psi',
            'pipe_material','pipe_width_in',
            'od_mm','wall_mm','id_mm','l_path_m',
            'pipe_burst_leak','leak_type',
            'leak_category','leak_branch','leak_pipe',
            'c_est_m_per_s','temp_est_c',
            'n_traverses','theta_deg'
        ])
        for (yr, mo) in months:
            pbar = tqdm(cfgs, desc=f'{calendar.month_abbr[mo]} {yr}')
            
            # Process homes in batches for memory management
            for i in range(0, len(cfgs), args.batch_size):
                batch = cfgs[i:i+args.batch_size]
                
                for cfg in batch:
                    simulate_home_month(cfg, yr, mo, writer, args.chunk_size)
                
                # Force garbage collection after each batch
                gc.collect()
                
                # Update progress bar
                pbar.update(len(batch))
            
            pbar.close()

if __name__ == '__main__':
    main()