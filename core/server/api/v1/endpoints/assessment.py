from fastapi import APIRouter, HTTPException
from typing import Dict, List, Optional
from pydantic import BaseModel

from external.question_master import QuestionMaster
from external.grader import RiskGrader
from external.recommendations import RecommendationEngine
from external.camera import RiskPhotoValidator

TAG = "Risk Assessment"
PREFIX = "/assessment"

router = APIRouter()

# Initialize core services
question_master = QuestionMaster()
grader = RiskGrader()
recommendation_engine = RecommendationEngine()
photo_validator = RiskPhotoValidator()

class UserAnswer(BaseModel):
    """Model for user's answer to a risk question"""
    question: str
    answer: str
    photos: Optional[List[str]] = []

class AssessmentResponse(BaseModel):
    """Model for risk assessment response"""
    total_score: float
    points_earned: float
    points_possible: float
    breakdown: Dict
    recommendations: List[Dict]

@router.get("/")
async def get_assessment():
    """Health check endpoint"""
    return {"message": "risk assessment service activated"}

@router.post("/submit/{user_id}")
async def submit_assessment(
    user_id: str,
    answers: List[UserAnswer]
) -> AssessmentResponse:
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
            
            # Validate photos if required and provided
            photo_score_adjustment = 0
            if question_data.get("requires_photo", False) and answer.photos:
                # Validate each photo and get score adjustment
                for photo_url in answer.photos:
                    validation_result = photo_validator.validate_photo(
                        photo_url,
                        question_data["risk"][0],  # Use primary risk type
                        answer.answer
                    )
                    photo_score_adjustment += validation_result.get("score_adjustment", 0)
                
            formatted_answers.append({
                "question": answer.question,
                "risk_type": question_data["risk"][0],  # Use primary risk type
                "importance": question_data["importance"][0],  # Use primary importance
                "answer": answer.answer,
                "rubric": question_data["rubric"],
                "risk_level": "Very High",  # This should come from the assess-location step
                "photos": answer.photos,
                "photo_score_adjustment": photo_score_adjustment
            })
        
        # Calculate scores with photo validation adjustments
        results = grader.calculate_score(formatted_answers, user_id)
        
        # Generate recommendations
        recommendations = recommendation_engine.get_improvement_recommendations(results)
        
        return AssessmentResponse(
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