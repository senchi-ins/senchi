"""Leak and Blockage physics sanity checks."""
import math

from src.events.leak_model import LeakEvent, LeakType
from src.events.blockage_model import BlockageEvent, BlockageType


def test_leak_flow_increases():
    leak = LeakEvent(0, "loc", LeakType.PINHOLE, random_seed=42)
    flow0 = leak.get_leak_flow(1, 300_000)  # m³/s
    flow1 = leak.get_leak_flow(24, 300_000)
    assert flow1 > flow0 > 0


def test_blockage_headloss_multiplier():
    blk = BlockageEvent(0, "pipe", BlockageType.MINERAL_BUILDUP, duration_days=30)
    m0 = blk.get_head_loss_multiplier(0)
    m_end = blk.get_head_loss_multiplier(30 * 24)
    assert m_end > m0 >= 1.0


def test_leak_duration_window_active_only_within_bounds():
    # 2-hour duration
    leak = LeakEvent( start_time_hours=1.0, location="loc", leak_type=LeakType.PINHOLE, duration_hours=2.0 )
    from src.events.event_scheduler import EventScheduler, EventCategory
    es = EventScheduler(wn=None)
    es.add_leak(leak)

    # Before start
    assert len([e for e in es.get_active_events(0.5) if e[0] == EventCategory.LEAK]) == 0
    # During leak
    assert len([e for e in es.get_active_events(1.5) if e[0] == EventCategory.LEAK]) == 1
    assert len([e for e in es.get_active_events(2.9) if e[0] == EventCategory.LEAK]) == 1
    # After end (start 1.0 + 2.0 = 3.0)
    assert len([e for e in es.get_active_events(3.1) if e[0] == EventCategory.LEAK]) == 0
