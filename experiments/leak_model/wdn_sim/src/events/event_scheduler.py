"""
event_scheduler.py
------------------
Event scheduling and coordination for simulation.

Manages timing and application of:
- Leak events
- Blockage events
- Valve operations
- Pump trips
- Demand surges

Integrates with WNTR network model for time-stepped simulation.
"""

import numpy as np
import wntr
from typing import Dict, List, Optional, Union, Tuple
from enum import Enum
from datetime import datetime, timedelta

from .leak_model import LeakEvent, LeakGenerator, LeakType
from .blockage_model import BlockageEvent, BlockageGenerator, BlockageType


class EventCategory(Enum):
    """Categories of simulation events."""
    LEAK = "leak"
    BLOCKAGE = "blockage"
    VALVE_OPERATION = "valve"
    PUMP_TRIP = "pump"
    DEMAND_SURGE = "demand"
    TRANSIENT = "transient"


class EventScheduler:
    """
    Manages all events during simulation.
    
    Coordinates timing, tracks active events, and applies
    them to the network model at each time step.
    """
    
    def __init__(self, 
                 wn: Optional[wntr.network.WaterNetworkModel] = None,
                 start_time: datetime = None):
        """
        Initialize event scheduler.
        
        Parameters
        ----------
        wn : wntr.network.WaterNetworkModel, optional
            Water network model
        start_time : datetime, optional
            Simulation start time for logging
        """
        self.wn = wn
        self.start_time = start_time or datetime.now()
        
        # Event storage
        self.events = {
            EventCategory.LEAK: [],
            EventCategory.BLOCKAGE: [],
            EventCategory.VALVE_OPERATION: [],
            EventCategory.PUMP_TRIP: [],
            EventCategory.DEMAND_SURGE: [],
            EventCategory.TRANSIENT: []
        }
        
        # Active events tracking
        self.active_events = []
        
        # Event history for analysis
        self.event_history = []
        
        # Statistics
        self.stats = {
            'total_events': 0,
            'active_leaks': 0,
            'active_blockages': 0,
            'water_loss_L': 0,
            'max_simultaneous_events': 0
        }
        
    def add_event(self, event: Union[LeakEvent, BlockageEvent], 
                 category: EventCategory) -> None:
        """Add an event to the schedule."""
        self.events[category].append(event)
        self.stats['total_events'] += 1
        
    def add_leak(self, leak: LeakEvent) -> None:
        """Add a leak event."""
        self.add_event(leak, EventCategory.LEAK)
        
    def add_blockage(self, blockage: BlockageEvent) -> None:
        """Add a blockage event."""
        self.add_event(blockage, EventCategory.BLOCKAGE)
        
    def generate_realistic_schedule(self,
                                   duration_days: int,
                                   network_info: Dict,
                                   random_seed: Optional[int] = None) -> None:
        """
        Generate a realistic event schedule.
        
        Parameters
        ----------
        duration_days : int
            Simulation duration
        network_info : dict
            Network characteristics (length, material, age, etc.)
        random_seed : int, optional
            For reproducibility
        """
        if random_seed:
            np.random.seed(random_seed)
            
        # Extract network properties
        network_length_km = network_info.get('length_km', 1.0)
        material = network_info.get('material', 'Copper')
        age_years = network_info.get('age_years', 20)
        water_hardness = network_info.get('water_hardness', 'medium')
        
        # Generate leaks
        leak_gen = LeakGenerator()
        node_list = self.wn.junction_name_list if self.wn else None
        # Filter out service connection points (too close to municipal supply)
        if node_list:
            excluded_nodes = {"StreetConnection", "SERVICE_ENTRY", "Meter"}  # Support both naming schemes
            node_list = [node for node in node_list if node not in excluded_nodes]
        leaks = leak_gen.generate_leaks(
            duration_days=duration_days,
            network_length_km=network_length_km,
            material=material,
            age_years=age_years,
            random_seed=random_seed,
            available_nodes=node_list
        )
        
        for leak in leaks:
            self.add_leak(leak)
            
        # ------------------------------------------------------------------
        # Blockage generation temporarily disabled for stability testing.
        # The code remains for future re-enablement
        # ------------------------------------------------------------------

        # blockage_gen = BlockageGenerator()
        # pipe_list = self.wn.pipe_name_list if self.wn else None
        # blockages = blockage_gen.generate_blockages(
        #     duration_days=duration_days,
        #     network_length_km=network_length_km,
        #     material=material,
        #     age_years=age_years,
        #     water_hardness=water_hardness,
        #     random_seed=random_seed + 1000 if random_seed else None,
        #     available_pipes=pipe_list
        # )
        # for blockage in blockages:
        #     self.add_blockage(blockage)

        blockages = []  # Placeholder so downstream print keeps same signature
        print(f"Generated schedule: {len(leaks)} leaks, {len(blockages)} blockages (blockages disabled)")
        
    def get_active_events(self, time_hours: float) -> List[Tuple[EventCategory, object]]:
        """Get all events active at given time."""
        active = []
        
        # Check leaks
        for leak in self.events[EventCategory.LEAK]:
            if time_hours >= leak.start_time:
                if getattr(leak, "duration_hours", None) is None:
                    active.append((EventCategory.LEAK, leak))
                else:
                    if time_hours <= leak.start_time + float(leak.duration_hours):
                        active.append((EventCategory.LEAK, leak))
                
        # Check blockages
        for blockage in self.events[EventCategory.BLOCKAGE]:
            if time_hours >= blockage.start_time:
                # Check if still progressing
                if time_hours <= blockage.start_time + blockage.duration:
                    active.append((EventCategory.BLOCKAGE, blockage))
                    
        return active
        
    def apply_events_to_network(self, time_hours: float) -> None:
        """
        Apply all active events to network at current time.
        
        Parameters
        ----------
        time_hours : float
            Current simulation time in hours
        """
        if self.wn is None:
            raise ValueError("No network model attached")
            
        # Get active events
        active = self.get_active_events(time_hours)
        
        # Update statistics
        self.stats['max_simultaneous_events'] = max(
            self.stats['max_simultaneous_events'],
            len(active)
        )
        
        # Apply each event
        for category, event in active:
            if category == EventCategory.LEAK:
                event.apply_to_network(self.wn, time_hours)
                self.stats['active_leaks'] = sum(1 for c, _ in active if c == EventCategory.LEAK)
                
            elif category == EventCategory.BLOCKAGE:
                event.apply_to_network(self.wn, time_hours)
                self.stats['active_blockages'] = sum(1 for c, _ in active if c == EventCategory.BLOCKAGE)
                
        # Log event transitions
        if len(active) != len(self.active_events):
            self.event_history.append({
                'time': time_hours,
                'active_count': len(active),
                'events': [(c.value, type(e).__name__) for c, e in active]
            })
            
        self.active_events = active
        
    def simulate_with_events(self,
                            duration_hours: float,
                            time_step_hours: float = 1.0) -> Dict:
        """
        Run simulation with events applied.
        
        Parameters
        ----------
        duration_hours : float
            Simulation duration
        time_step_hours : float
            Time step for simulation
            
        Returns
        -------
        dict
            Simulation results with event impacts
        """
        if self.wn is None:
            raise ValueError("No network model attached")
            
        results = {
            'time': [],
            'active_events': [],
            'water_loss_L': [],
            'pressure_impact': []
        }
        
        times = np.arange(0, duration_hours + time_step_hours, time_step_hours)
        
        for t in times:
            # Apply events
            self.apply_events_to_network(t)
            
            # Track results
            results['time'].append(t)
            results['active_events'].append(len(self.active_events))
            
            # Calculate water loss from leaks
            total_loss = 0
            for category, event in self.active_events:
                if category == EventCategory.LEAK:
                    # Estimate loss (simplified)
                    flow = event.get_leak_flow(t, event.system_pressure)
                    total_loss += flow * time_step_hours * 3600 * 1000  # L
                    
            results['water_loss_L'].append(total_loss)
            
            # Track pressure impact (placeholder)
            pressure_reduction = len(self.active_events) * 5  # kPa per event
            results['pressure_impact'].append(pressure_reduction)
            
        # Update total water loss
        self.stats['water_loss_L'] = sum(results['water_loss_L'])
        
        return results
        
    def get_event_summary(self) -> Dict:
        """Get summary of all scheduled events."""
        summary = {
            'total_events': self.stats['total_events'],
            'by_category': {},
            'timeline': []
        }
        
        # Count by category
        for category, events in self.events.items():
            summary['by_category'][category.value] = len(events)
            
        # Create timeline
        all_events = []
        for category, events in self.events.items():
            for event in events:
                all_events.append({
                    'category': category.value,
                    'type': type(event).__name__,
                    'start_time': event.start_time,
                    'location': getattr(event, 'location', 'unknown')
                })
                
        # Sort by time
        summary['timeline'] = sorted(all_events, key=lambda x: x['start_time'])
        
        return summary
        
    def plot_event_timeline(self) -> None:
        """Create visualization of event timeline."""
        try:
            import matplotlib.pyplot as plt
            
            fig, axes = plt.subplots(2, 1, figsize=(12, 8))
            
            # Plot 1: Event counts over time
            ax1 = axes[0]
            
            # Collect event start times by category
            for category, events in self.events.items():
                if events:
                    times = [e.start_time for e in events]
                    counts = [1] * len(times)
                    ax1.scatter(times, [category.value] * len(times), 
                              label=category.value, alpha=0.7, s=50)
                    
            ax1.set_xlabel('Time (hours)')
            ax1.set_ylabel('Event Category')
            ax1.set_title('Event Timeline')
            ax1.legend()
            ax1.grid(True, alpha=0.3)
            
            # Plot 2: Cumulative events
            ax2 = axes[1]
            
            all_times = []
            for events in self.events.values():
                all_times.extend([e.start_time for e in events])
                
            if all_times:
                all_times.sort()
                cumulative = list(range(1, len(all_times) + 1))
                ax2.plot(all_times, cumulative, 'b-', linewidth=2)
                ax2.fill_between(all_times, 0, cumulative, alpha=0.3)
                
            ax2.set_xlabel('Time (hours)')
            ax2.set_ylabel('Cumulative Events')
            ax2.set_title('Cumulative Event Count')
            ax2.grid(True, alpha=0.3)
            
            plt.tight_layout()
            plt.show()
            
        except ImportError:
            print("Matplotlib not available for plotting")


def create_simple_event_schedule(duration_days: int = 30,
                                n_leaks: int = 3,
                                n_blockages: int = 2,
                                random_seed: Optional[int] = None) -> EventScheduler:
    """
    Create a simple event schedule for testing.
    
    Parameters
    ----------
    duration_days : int
        Simulation duration
    n_leaks : int
        Number of leak events
    n_blockages : int
        Number of blockage events
    random_seed : int, optional
        For reproducibility
        
    Returns
    -------
    EventScheduler
        Configured scheduler with events
    """
    if random_seed:
        np.random.seed(random_seed)
        
    scheduler = EventScheduler()
    
    # Add leaks
    for i in range(n_leaks):
        leak_type = np.random.choice(list(LeakType))
        leak = LeakEvent(
            start_time_hours=np.random.uniform(0, duration_days * 24),
            location=f"junction_{i+1}",
            leak_type=leak_type,
            random_seed=random_seed + i if random_seed else None
        )
        scheduler.add_leak(leak)
        
    # Add blockages
    for i in range(n_blockages):
        blockage_type = np.random.choice(list(BlockageType))
        blockage = BlockageEvent(
            start_time_hours=np.random.uniform(0, duration_days * 24),
            location=f"pipe_{i+1}",
            blockage_type=blockage_type,
            duration_days=np.random.uniform(7, 30),
            random_seed=random_seed + 100 + i if random_seed else None
        )
        scheduler.add_blockage(blockage)
        
    return scheduler