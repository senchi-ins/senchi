from fastapi import APIRouter, HTTPException
from typing import Dict, List
from pydantic import BaseModel

from external.geoencoding import GoogleMapsGeocoder
from external.risk_lookup import RiskLookup
from external.question_master import QuestionMaster

TAG = "Location Risk Assessment"
PREFIX = "/location"

router = APIRouter()

# Initialize core services
geocoder = GoogleMapsGeocoder()
risk_lookup = RiskLookup()
question_master = QuestionMaster()

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

@router.get("/")
async def get_location_assessment():
    """Health check endpoint"""
    return {"message": "location risk assessment service activated"}

@router.post("/assess")
async def assess_location(address: str) -> LocationRiskResponse:
    """
    Get location-specific risks and assessment questions.
    
    Args:
        address: Street address to assess
    """
    try:
        # Step 1: Geocode the address
        location_data = geocoder.geocode_address(address)
        
        # Step 2: Look up location-specific risks
        risks = dict(risk_lookup.get_location_risks(location_data))  # Convert Mapping to Dict
        
        # Step 3: Generate relevant questions
        questions = question_master.get_relevant_questions(risks)
        
        return LocationRiskResponse(
            location_risks=risks,
            questions=[
                RiskQuestion(
                    question=q["question"],
                    risk_type=q["risk_type"],
                    importance=q["importance"],
                    rubric=q["rubric"],
                    requires_photo=question_master.questions_data["risk_questions"][i].get("requires_photo", False),
                    risk_level=risks.get(q["risk_type"], "Relatively Low")
                ) for i, q in enumerate(questions)
            ]
        )
        
    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=f"Error assessing location: {str(e)}"
        ) 