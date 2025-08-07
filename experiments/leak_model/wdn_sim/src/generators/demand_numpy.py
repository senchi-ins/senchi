"""
demand_numpy.py
---------------
Advanced stochastic household water demand generation using vectorized NumPy operations.

Generates realistic sub-second resolution demand patterns based on:
- Fixture-specific usage patterns (toilets, showers, faucets, etc.)
- Household characteristics (occupancy, lifestyle, etc.)
- Seasonal and diurnal variations
- Stochastic modeling of appliance cycles
"""

import numpy as np
import json
from typing import Dict, List, Tuple, Optional
from pathlib import Path


class DemandGenerator:
    """Advanced stochastic water demand generator."""
    
    def __init__(self, config_path: Optional[str] = None):
        """Initialize demand generator."""
        if config_path is None:
            config_path = Path(__file__).parent.parent.parent / "config" / "house_profiles.json"
        
        with open(config_path, 'r') as f:
            self.config = json.load(f)
            
        self._load_fixture_models()
        
        # Seasonal factors (monthly multipliers)
        self.seasonal_factors = {
            1: 0.75, 2: 0.75, 3: 0.85, 4: 0.95, # Jan-Apr
            5: 1.20, 6: 1.40, 7: 1.50, 8: 1.40, # May-Aug
            9: 1.20, 10: 1.00, 11: 0.85, 12: 0.75 # Sep-Dec
        }
        
    def _load_fixture_models(self):
        """Load realistic fixture usage patterns."""
        self.fixtures = {
            'toilet': {
                'flow_rate': 6.0,  # L/flush
                'duration': 0.1,   # Effective duration
                'daily_uses_per_person': (4, 8),
                'peak_hours': [(6, 9), (17, 22)],
                'weekend_factor': 1.2
            },
            'shower': {
                'flow_rate': 8.5,  # L/min
                'duration': (300, 900),  # 5-15 minutes
                'daily_uses_per_person': (0.8, 1.2),
                'peak_hours': [(6, 9), (18, 23)],
                'weekend_factor': 1.3
            },
            'kitchen_sink': {
                'flow_rate': 6.0,  # L/min
                'duration': (30, 300),
                'daily_uses_per_person': (4, 8),
                'peak_hours': [(6, 10), (11, 14), (16, 20)],
                'weekend_factor': 1.4
            },
            'bathroom_sink': {
                'flow_rate': 3.0,  # L/min
                'duration': (10, 120),
                'daily_uses_per_person': (8, 15),
                'peak_hours': [(6, 9), (17, 23)],
                'weekend_factor': 1.1
            },
            'dishwasher': {
                'flow_rate': 6.0,   # L/min average
                'duration': 3600,   # 1 hour cycle
                'daily_uses_per_household': (0.5, 1.5),
                'peak_hours': [(19, 23)],
                'weekend_factor': 0.8
            },
            'washing_machine': {
                'flow_rate': 12.0,  # L/min average
                'duration': 2400,   # 40 minute cycle
                'daily_uses_per_household': (0.3, 1.2),
                'peak_hours': [(8, 12), (14, 18)],
                'weekend_factor': 1.5
            }
        }
        
    def generate_household_demand(self, 
                                house_profile: str,
                                duration_hours: float = 24,
                                resolution_seconds: float = 1.0,
                                month: int = 7,
                                is_weekend: bool = False,
                                random_seed: Optional[int] = None) -> np.ndarray:
        """
        Generate realistic demand time series for a household.
        
        Parameters
        ----------
        house_profile : str
            House profile ID from config
        duration_hours : float
            Simulation duration in hours
        resolution_seconds : float
            Time resolution in seconds
        month : int
            Month of year (1-12)
        is_weekend : bool
            Weekend flag
        random_seed : int, optional
            Random seed
            
        Returns
        -------
        np.ndarray
            Demand time series in L/s
        """
        if random_seed is not None:
            np.random.seed(random_seed)
            
        # Get house characteristics
        profile = self._get_house_profile(house_profile)
        occupancy = np.random.randint(
            profile['occupancy']['min_people'],
            profile['occupancy']['max_people'] + 1
        )
        
        # Generate time array
        n_points = int(duration_hours * 3600 / resolution_seconds)
        time_hours = np.linspace(0, duration_hours, n_points)
        demand = np.zeros(n_points)
        
        # Generate demand for each fixture
        for fixture_name, fixture_data in self.fixtures.items():
            fixture_demand = self._generate_fixture_demand(
                fixture_name, fixture_data, occupancy,
                time_hours, resolution_seconds, month, is_weekend
            )
            demand += fixture_demand
            
        # Apply seasonal scaling
        seasonal_mult = self.seasonal_factors.get(month, 1.0)
        demand *= seasonal_mult
        
        # Add base demand
        base_demand = np.random.uniform(0.0001, 0.0005)
        demand += base_demand
        
        # Scale to target consumption
        consumption_range = profile['occupancy']['daily_consumption_L']
        target_daily = np.random.uniform(consumption_range[0], consumption_range[1])
        current_daily = np.sum(demand) * resolution_seconds / 1000
        
        if current_daily > 0:
            scaling_factor = target_daily / current_daily
            demand *= scaling_factor
            
        # Add noise
        noise_std = 0.02 * np.mean(demand[demand > 0]) if np.any(demand > 0) else 0
        noise = np.random.normal(0, noise_std, len(demand))
        demand = np.maximum(0, demand + noise)
        
        return demand
        
    def _get_house_profile(self, profile_id: str) -> Dict:
        """Get house profile by ID."""
        for profile in self.config['profiles']:
            if profile['id'] == profile_id:
                return profile['characteristics']
        raise ValueError(f"Profile {profile_id} not found")
        
    def _generate_fixture_demand(self, 
                                fixture_name: str,
                                fixture_data: Dict,
                                occupancy: int,
                                time_hours: np.ndarray,
                                resolution_seconds: float,
                                month: int,
                                is_weekend: bool) -> np.ndarray:
        """Generate demand for a specific fixture."""
        demand = np.zeros(len(time_hours))
        
        # Calculate number of uses
        if 'daily_uses_per_person' in fixture_data:
            uses_range = fixture_data['daily_uses_per_person']
            n_uses = np.random.poisson(
                occupancy * np.random.uniform(uses_range[0], uses_range[1])
            )
        else:
            uses_range = fixture_data['daily_uses_per_household']
            n_uses = np.random.poisson(np.random.uniform(uses_range[0], uses_range[1]))
            
        # Apply weekend factor
        if is_weekend:
            n_uses = int(n_uses * fixture_data.get('weekend_factor', 1.0))
            
        # Generate usage events
        for _ in range(n_uses):
            # Choose time based on peak hours
            peak_hours = fixture_data['peak_hours']
            if peak_hours and np.random.random() < 0.7:
                peak_period = np.random.choice(len(peak_hours))
                start_hour, end_hour = peak_hours[peak_period]
                use_time = np.random.uniform(start_hour, end_hour)
            else:
                use_time = np.random.uniform(0, 24)
                
            # Find time index
            time_idx = np.searchsorted(time_hours, use_time)
            if time_idx >= len(time_hours):
                continue
                
            # Generate duration and flow
            if isinstance(fixture_data['duration'], tuple):
                duration_sec = np.random.uniform(*fixture_data['duration'])
            else:
                duration_sec = fixture_data['duration']
                
            flow_rate_lps = fixture_data['flow_rate'] / 60  # Convert L/min to L/s
            
            # Special handling for toilet (instantaneous)
            if fixture_name == 'toilet':
                duration_points = max(1, int(10 / resolution_seconds))
                end_idx = min(time_idx + duration_points, len(demand))
                if end_idx > time_idx:
                    demand[time_idx:end_idx] += flow_rate_lps / duration_points
            else:
                duration_points = int(duration_sec / resolution_seconds)
                end_idx = min(time_idx + duration_points, len(demand))
                if end_idx > time_idx:
                    demand[time_idx:end_idx] += flow_rate_lps
                    
        return demand
        
    def get_profile_ids(self) -> List[str]:
        """Get available profile IDs."""
        return [p['id'] for p in self.config['profiles']]


# Convenience functions
def generate_daily_profile(house_profile: str = "modern_pex_small",
                         resolution_seconds: float = 1.0,
                         month: int = 7,
                         random_seed: Optional[int] = None) -> np.ndarray:
    """Generate single household daily demand profile."""
    generator = DemandGenerator()
    return generator.generate_household_demand(
        house_profile, 24, resolution_seconds, month, 
        random_seed=random_seed
    )


def calculate_demand_statistics(demand: np.ndarray,
                              resolution_seconds: float = 1.0) -> Dict[str, float]:
    """Calculate demand time series statistics."""
    stats = {}
    
    # Total daily consumption (L)
    stats['daily_total_L'] = np.sum(demand) * resolution_seconds / 1000
    
    # Peak flow rate
    stats['peak_flow_L_s'] = np.max(demand)
    stats['peak_flow_L_min'] = stats['peak_flow_L_s'] * 60
    
    # Average when flowing
    flowing = demand[demand > 0.001]
    stats['avg_when_flowing_L_s'] = np.mean(flowing) if len(flowing) > 0 else 0
    
    # Usage events
    usage_events = np.diff((demand > 0.001).astype(int)) == 1
    stats['usage_events_per_day'] = np.sum(usage_events)
    
    # Time flowing
    flowing_time = np.sum(demand > 0.001) * resolution_seconds / 3600
    stats['hours_flowing'] = flowing_time
    stats['hours_idle'] = 24 - flowing_time
    
    return stats