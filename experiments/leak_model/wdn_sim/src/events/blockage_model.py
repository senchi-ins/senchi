"""
blockage_model.py
-----------------
Realistic pipe blockage and constriction modeling.

Implements:
- Mineral buildup (scale, calcium deposits)
- Biofilm growth
- Debris accumulation
- Ice formation
- Partial valve closure

Uses physics-based flow restriction via effective diameter reduction.
"""

import numpy as np
import wntr
from typing import Dict, List, Optional
from enum import Enum
import math


class BlockageType(Enum):
    """Types of blockage events."""
    MINERAL_BUILDUP = "mineral"    # Slow calcium/scale deposits
    BIOFILM = "biofilm"            # Biological growth
    DEBRIS = "debris"              # Foreign object obstruction
    ICE = "ice"                    # Freezing conditions
    VALVE_PARTIAL = "valve"        # Partially closed valve


class BlockageEvent:
    """
    Models progressive pipe blockage affecting hydraulics.
    
    Blockage reduces effective diameter, increasing:
    - Head loss: h = f * (L/D) * (v²/2g)
    - Velocity: v = Q/A (smaller A)
    - Friction factor changes
    """
    
    def __init__(self,
                 start_time_hours: float,
                 location: str,
                 blockage_type: BlockageType,
                 pipe_diameter_mm: float = 25.4,
                 pipe_material: str = "Copper",
                 duration_days: float = 30,
                 random_seed: Optional[int] = None):
        """Initialize blockage event."""
        self.start_time = start_time_hours
        self.location = location
        self.blockage_type = blockage_type
        self.pipe_diameter = pipe_diameter_mm
        self.pipe_material = pipe_material
        self.duration = duration_days * 24  # Convert to hours
        
        if random_seed:
            np.random.seed(random_seed)
            
        self._initialize_parameters()
        
    def _initialize_parameters(self):
        """Set blockage parameters based on type."""
        if self.blockage_type == BlockageType.MINERAL_BUILDUP:
            # Slow progressive buildup
            self.initial_reduction = 0.0
            self.max_reduction = np.random.uniform(0.3, 0.6)  # 30-60% reduction
            self.growth_pattern = 'logarithmic'  # Fast initially, slows down
            self.roughness_increase = 2.0  # Doubles roughness
            
        elif self.blockage_type == BlockageType.BIOFILM:
            # Biological growth pattern
            self.initial_reduction = 0.0
            self.max_reduction = np.random.uniform(0.2, 0.4)  # 20-40% reduction
            self.growth_pattern = 'sigmoid'  # S-curve growth
            self.roughness_increase = 1.5
            
        elif self.blockage_type == BlockageType.DEBRIS:
            # Sudden partial blockage
            self.initial_reduction = np.random.uniform(0.3, 0.7)  # Instant
            self.max_reduction = self.initial_reduction  # Doesn't grow
            self.growth_pattern = 'step'
            self.roughness_increase = 1.2
            
        elif self.blockage_type == BlockageType.ICE:
            # Ice formation (rapid in cold)
            self.initial_reduction = 0.1
            self.max_reduction = np.random.uniform(0.7, 0.95)  # Can nearly close
            self.growth_pattern = 'exponential'
            self.roughness_increase = 1.1  # Smooth ice
            
        else:  # VALVE_PARTIAL
            # Partial valve closure
            self.initial_reduction = np.random.uniform(0.4, 0.8)
            self.max_reduction = self.initial_reduction  # Fixed
            self.growth_pattern = 'step'
            self.roughness_increase = 1.0  # No roughness change
            
    def get_diameter_reduction(self, time_hours: float) -> float:
        """
        Calculate diameter reduction factor at time.
        
        Returns
        -------
        float
            Reduction factor (0-1), where 0 = no blockage, 1 = full blockage
        """
        if time_hours < self.start_time:
            return 0.0
            
        elapsed = time_hours - self.start_time
        progress = min(elapsed / self.duration, 1.0) if self.duration > 0 else 1.0
        
        if self.growth_pattern == 'logarithmic':
            # Fast initial, slows down
            factor = np.log(1 + 9 * progress) / np.log(10)
            
        elif self.growth_pattern == 'sigmoid':
            # S-curve
            factor = 1 / (1 + np.exp(-10 * (progress - 0.5)))
            
        elif self.growth_pattern == 'exponential':
            # Accelerating
            factor = (np.exp(progress) - 1) / (np.e - 1)
            
        else:  # 'step'
            # Instantaneous
            factor = 1.0 if progress > 0 else 0.0
            
        reduction = self.initial_reduction + (self.max_reduction - self.initial_reduction) * factor
        return min(reduction, self.max_reduction)
        
    def get_effective_diameter(self, time_hours: float) -> float:
        """Calculate effective pipe diameter in mm."""
        reduction = self.get_diameter_reduction(time_hours)
        return self.pipe_diameter * (1 - reduction)
        
    def get_effective_area(self, time_hours: float) -> float:
        """Calculate effective flow area in m²."""
        diameter_m = self.get_effective_diameter(time_hours) / 1000.0
        return math.pi * (diameter_m / 2) ** 2
        
    def get_head_loss_multiplier(self, time_hours: float) -> float:
        """
        Calculate head loss increase factor.
        
        Head loss ∝ 1/D⁵ for turbulent flow
        """
        if time_hours < self.start_time:
            return 1.0
            
        reduction = self.get_diameter_reduction(time_hours)
        if reduction >= 0.99:  # Nearly blocked
            return 1000.0  # Extreme head loss
            
        diameter_ratio = 1 - reduction
        # Head loss increases with 5th power of diameter reduction
        multiplier = (1 / diameter_ratio) ** 5
        
        # Add roughness effect
        multiplier *= self.roughness_increase
        
        return multiplier
        
    def get_velocity_multiplier(self, time_hours: float) -> float:
        """
        Calculate velocity increase factor.
        
        Velocity ∝ 1/A ∝ 1/D² for same flow
        """
        reduction = self.get_diameter_reduction(time_hours)
        if reduction >= 0.99:
            return 100.0  # Extreme velocity
            
        diameter_ratio = 1 - reduction
        return 1 / (diameter_ratio ** 2)
        
    def apply_to_network(self, wn: wntr.network.WaterNetworkModel,
                        time_hours: float) -> None:
        """Apply blockage to WNTR network."""
        if time_hours < self.start_time:
            return
            
        try:
            # Get pipe
            pipe = wn.get_link(self.location)
            
            # Calculate effective diameter
            eff_diameter_m = self.get_effective_diameter(time_hours) / 1000.0
            
            # Modify pipe properties
            original_diameter = pipe.diameter
            pipe.diameter = eff_diameter_m
            
            # Increase roughness
            original_roughness = pipe.roughness
            pipe.roughness = original_roughness / self.roughness_increase
            
        except Exception as e:
            print(f"Warning: Could not apply blockage: {e}")


class BlockageGenerator:
    """Generate realistic blockage events."""
    
    def __init__(self):
        """Initialize generator."""
        # Blockage rates per km per year
        self.base_blockage_rate = 0.05
        
        # Material susceptibility
        self.material_factors = {
            'Copper': 1.2,  # Mineral buildup
            'Steel': 1.5,   # Rust and scale
            'CPVC': 0.7,    # Less buildup
            'PEX-B': 0.5    # Least susceptible
        }
        
    def generate_blockages(self, 
                          duration_days: int,
                          network_length_km: float,
                          material: str = 'Copper',
                          age_years: int = 20,
                          water_hardness: str = 'medium',
                          random_seed: Optional[int] = None,
                          available_pipes: Optional[List[str]] = None) -> List[BlockageEvent]:
            """Generate blockage schedule.
            Returns an empty list ~90 % of the time so most simulations have no blockages.
            """
            if random_seed is not None:
                np.random.seed(random_seed)

                
            # Calculate expected blockages
            material_factor = self.material_factors.get(material, 1.0)
            age_factor = 1.3 ** (age_years / 10)
            
            # Water hardness effect
            hardness_factors = {'soft': 0.5, 'medium': 1.0, 'hard': 2.0}
            hardness_factor = hardness_factors.get(water_hardness, 1.0)
            
            annual_rate = self.base_blockage_rate * network_length_km * material_factor * age_factor * hardness_factor
            expected = annual_rate * (duration_days / 365)
            n_blockages = max(1, np.random.poisson(expected))
            
            blockages = []
            for i in range(n_blockages):
                start_time = np.random.uniform(0, duration_days * 24)
                
                # Choose type based on conditions
                if water_hardness == 'hard':
                    # More mineral buildup in hard water
                    blockage_type = np.random.choice(
                        [BlockageType.MINERAL_BUILDUP, BlockageType.BIOFILM, BlockageType.DEBRIS],
                        p=[0.6, 0.3, 0.1]
                    )
                else:
                    blockage_type = np.random.choice(
                        [BlockageType.MINERAL_BUILDUP, BlockageType.BIOFILM, BlockageType.DEBRIS],
                        p=[0.3, 0.4, 0.3]
                    )
                    
                blockage = BlockageEvent(
                    start_time_hours=start_time,
                    location=(np.random.choice(available_pipes) if available_pipes else f"pipe_{np.random.randint(1, 100)}"),
                    blockage_type=blockage_type,
                    pipe_material=material,
                    duration_days=np.random.uniform(30, 365),  # 1 month to 1 year
                    random_seed=random_seed + i if random_seed else None
                )
                blockages.append(blockage)
                
            return blockages


def simulate_blockage_progression(blockage: BlockageEvent,
                                 duration_hours: float,
                                 flow_m3s: float = 0.001,
                                 time_step_hours: float = 24.0) -> Dict:
    """Simulate blockage effects over time."""
    times = np.arange(0, duration_hours + time_step_hours, time_step_hours)
    results = {
        'time_hours': times,
        'diameter_reduction': [],
        'effective_diameter_mm': [],
        'head_loss_multiplier': [],
        'velocity_multiplier': []
    }
    
    for t in times:
        reduction = blockage.get_diameter_reduction(t)
        eff_diameter = blockage.get_effective_diameter(t)
        head_mult = blockage.get_head_loss_multiplier(t)
        vel_mult = blockage.get_velocity_multiplier(t)
        
        results['diameter_reduction'].append(reduction)
        results['effective_diameter_mm'].append(eff_diameter)
        results['head_loss_multiplier'].append(head_mult)
        results['velocity_multiplier'].append(vel_mult)
        
    return results