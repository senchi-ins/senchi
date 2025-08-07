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
