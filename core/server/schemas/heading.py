"""
Schemas for camera position and heading data.
"""
from pydantic import BaseModel
from typing import Dict, Any

class CameraPosition(BaseModel):
    """Camera position and heading information."""
    target_location: Dict[str, Any]
    camera_position: Dict[str, Any]
    heading: float

class CameraResponse(BaseModel):
    """Response model for camera position endpoints."""
    camera_data: CameraPosition
    message: str = "Successfully calculated optimal camera position" 