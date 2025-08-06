from typing import Dict, List, Optional
from pydantic import BaseModel


class UserAnswer(BaseModel):
    """Model for user's answer to a risk question"""
    question: str
    answer: str
    photos: Optional[List[str]] = []

class RecommendationItem(BaseModel):
    """Model for a single recommendation item"""
    question: str
    risk_type: str
    risk_level: str
    importance: str
    answer: str
    points_possible: float
    requires_photo: bool
    photo_validated: bool
    points_earned: float
    score_percentage: float

class AssessmentResponse(BaseModel):
    """Model for risk assessment response"""
    total_score: float
    points_earned: float
    points_possible: float
    breakdown: Dict
    recommendations: List[RecommendationItem]

class RiskQuestion(BaseModel):
    """Model for a risk assessment question"""
    question: str
    risk_type: str
    importance: str
    rubric: Dict[str, int]
    requires_photo: bool
    risk_level: str

class LocationRiskResponse(BaseModel):
    """Model for location risk assessment response"""
    location_risks: Dict[str, str]
    questions: List[RiskQuestion]

class AddressRequest(BaseModel):
    address: str
