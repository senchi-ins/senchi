"""
Utility functions for camera position and heading calculations.
"""
from typing import Dict, Any

from external.heading_position import get_optimal_streetview_position
from server.schemas.heading import CameraPosition

async def get_camera_position(address: str) -> CameraPosition:
    """
    Get the optimal camera position and heading for a given address.
    
    Args:
        address: The target address to photograph
        
    Returns:
        CameraPosition: Object containing camera position and heading data
        
    Raises:
        ValueError: If address is invalid or Street View data is unavailable
    """
    result = get_optimal_streetview_position(address)
    return CameraPosition(**result) 