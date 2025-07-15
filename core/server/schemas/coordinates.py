from typing import List, Dict, Optional
from pydantic import BaseModel

class RecommendationInput(BaseModel):
    """Model for input recommendations"""
    question: str
    risk_type: str
    importance: str
    risk_level: str
    points_possible: float
    points_earned: float
    score_percentage: float

class CoordinateRequest(BaseModel):
    """Model for coordinate conversion request"""
    address: str
    heading: int = 0  # Default to front view
    zoom: int = 21    # Default zoom level
    recommendations: List[RecommendationInput]
    model_task_id: str  # Task ID from risk.py generate-model endpoint

class Coordinate2D(BaseModel):
    """Model for 2D coordinates"""
    x_pixel: int
    y_pixel: int
    x_percent: float
    y_percent: float
    visible: bool
    description: str

class Coordinate3D(BaseModel):
    """Model for 3D coordinates"""
    x: float
    y: float
    z: float
    scaling_info: Dict[str, float]

class RecommendationCoordinates(BaseModel):
    """Model for recommendation with coordinates"""
    recommendation: RecommendationInput
    location_category: str
    coordinates_2d: Coordinate2D
    coordinates_3d: Optional[Coordinate3D] = None

class CoordinateResponse(BaseModel):
    """Model for coordinate conversion response"""
    image_dimensions: Dict[str, int]
    recommendations: List[RecommendationCoordinates]
    model_info: Optional[Dict] = None 