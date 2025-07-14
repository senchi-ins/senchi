from fastapi import APIRouter, HTTPException, Depends, Body
from typing import List, Dict, Optional
from pydantic import BaseModel

from external.geoencoding import GoogleMapsGeocoder
from external.risk_lookup import RiskLookup
from external.question_master import QuestionMaster
from external.camera import RiskPhotoManager, RiskPhotoValidator
from external.grader import RiskGrader
from external.recommendations import RecommendationEngine

TAG = "Risk Assessment"
PREFIX = "/risk"

router = APIRouter()

# Initialize core services
geocoder = GoogleMapsGeocoder()
risk_lookup = RiskLookup()
question_master = QuestionMaster()
photo_manager = RiskPhotoManager()
grader = RiskGrader()
recommendation_engine = RecommendationEngine()

class RiskQuestion(BaseModel):
    """Model for a risk assessment question"""
    question: str
    risk_type: str
    importance: str
    rubric: Dict[str, int]
    requires_photo: bool
    risk_level: str

class UserAnswer(BaseModel):
    """Model for user's answer to a risk question"""
    question: str
    answer: str
    photos: Optional[List[str]] = []

class RiskAssessmentResponse(BaseModel):
    """Model for risk assessment response"""
    location_risks: Dict[str, Optional[str]]
    questions: List[RiskQuestion]
    total_score: Optional[float] = None
    points_earned: Optional[float] = None
    points_possible: Optional[float] = None
    breakdown: Optional[Dict] = None
    recommendations: Optional[List[Dict]] = None

@router.get("/")
async def get_risk_assessment():
    """Health check endpoint"""
    return {"message": "risk assessment service activated"}

@router.post("/assess-location")
async def assess_location(address: str) -> RiskAssessmentResponse:
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
        
        return RiskAssessmentResponse(
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

@router.post("/submit-answers/{user_id}")
async def submit_answers(
    user_id: str,
    answers: List[UserAnswer]
) -> RiskAssessmentResponse:
    """
    Submit answers to risk assessment questions and get recommendations.
    
    Args:
        user_id: Identifier for the user
        answers: List of answers with optional photo evidence
    """
    try:
        # Format answers for grading
        formatted_answers = []
        for answer in answers:
            # Get the original question data
            question_data = next(
                (q for q in question_master.questions_data["risk_questions"] 
                 if q["question"] == answer.question),
                None
            )
            
            if not question_data:
                continue
                
            formatted_answers.append({
                "question": answer.question,
                "risk_type": question_data["risk"][0],  # Use primary risk type
                "importance": question_data["importance"][0],  # Use primary importance
                "answer": answer.answer,
                "rubric": question_data["rubric"],
                "risk_level": "Very High",  # This should come from the assess-location step
                "photos": answer.photos
            })
        
        # Calculate scores
        results = grader.calculate_score(formatted_answers, user_id)
        
        # Generate recommendations
        recommendations = recommendation_engine.get_improvement_recommendations(results)
        
        return RiskAssessmentResponse(
            location_risks={},  # Would come from previous assess-location call
            questions=[],  # Would come from previous assess-location call
            total_score=results["total_score"],
            points_earned=results["points_earned"],
            points_possible=results["points_possible"],
            breakdown=results["breakdown"],
            recommendations=recommendations
        )
        
    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=f"Error processing answers: {str(e)}"
        )

@router.post("/upload-photo/{user_id}/{question_id}")
async def upload_photo(
    user_id: str,
    question_id: str,
    photo_data: bytes = Body(...),
) -> Dict[str, str]:
    """
    Upload a photo for risk assessment validation.
    
    Args:
        user_id: Identifier for the user
        question_id: Identifier for the question
        photo_data: Raw photo data in bytes
    """
    try:
        photo_url = photo_manager.upload_photo(photo_data, question_id, user_id)
        
        if not photo_url:
            raise HTTPException(
                status_code=500,
                detail="Failed to upload photo"
            )
            
        return {"photo_url": photo_url}
        
    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=f"Error uploading photo: {str(e)}"
        )
