import jwt
from fastapi import APIRouter, HTTPException, Body, Request
from typing import Dict, List, Optional
from pydantic import BaseModel

from external import services
from schemas.external import (
    UserAnswer, 
    AssessmentResponse, 
    RiskQuestion, 
    LocationRiskResponse, 
    AddressRequest,
    WebAssessmentRequest
)
from server.api.v1.utils.utils import decode_jwt


TAG = "External"
PREFIX = "/external"

router = APIRouter()

@router.get("/")
async def get_external():
    return {"message": "external model activated"}

@router.post("/survey")
async def assess_location(request: AddressRequest) -> LocationRiskResponse:
    """
    Get location-specific risks and assessment questions.
    
    Args:
        address: Street address to assess
    """
    address = request.address
    # try:
    # Step 1: Geocode the address
    location_data = services['geocoder'].geocode_address(address)
    print(location_data)
    
    # Step 2: Look up location-specific risks
    risks = dict(services['risk_lookup'].get_location_risks(location_data))  # Convert Mapping to Dict
    print(risks)
    
    # Step 3: Generate relevant questions
    questions = services['question_master'].get_relevant_questions(risks)
    
    return LocationRiskResponse(
        location_risks=risks,
        questions=[
            RiskQuestion(
                question=q["question"],
                risk_type=q["risk_type"],
                importance=q["importance"],
                rubric=q["rubric"],
                requires_photo=services['question_master'].questions_data["risk_questions"][i].get("requires_photo", False),
                risk_level=risks.get(q["risk_type"], "Relatively Low")
            ) for i, q in enumerate(questions)
        ]
    )
        
    # except Exception as e:
    #     raise HTTPException(
    #         status_code=500,
    #         detail=f"Error assessing location: {str(e)}"
    #     ) 

@router.post("/upload/{user_id}/{question_id}")
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
    photo_url = services['photo_manager'].upload_photo(photo_data, question_id, user_id)
    if not photo_url:
        raise HTTPException(
            status_code=500,
            detail="Failed to upload photo"
        )
    return {"photo_url": photo_url}

@router.post("/submit-web")
async def submit_assessment(
    answers: List[UserAnswer],
    request: Request
) -> AssessmentResponse:
    """
    Submit answers to risk assessment questions and get recommendations on the website.
    """
    try:
        formatted_answers = []
        # Use the correct questions list from question_master
        questions_data = services['question_master'].questions_data["risk_questions"]
        for answer in answers:
            # Match the question by its text
            question_data = next(
                (q for q in questions_data if q["question"] == answer.question),
                None
            )
            if not question_data:
                continue
            photo_score_adjustment = 0
            if question_data.get("requires_photo", False) and answer.photos:
                for photo_url in answer.photos:
                    validation_result = services['photo_validator'].validate_photo(
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
        results = services['grader'].calculate_score(formatted_answers)
        # Generate recommendations
        recommendations = services['recommendation_engine'].get_improvement_recommendations(results)
        assessment_response = AssessmentResponse(
            total_score=results["total_score"],
            points_earned=results["points_earned"],
            points_possible=results["points_possible"],
            breakdown=results["breakdown"],
            recommendations=recommendations
        )
        # TODO: Find a better way to get the user_id
        user_id = "04e81e1e-c044-44d1-8f2d-ae95eebb0d79"
        request.app.state.db.insert_assessment_response(user_id, assessment_response.model_dump())
        return assessment_response
    except Exception as e:
        print(e)
        raise HTTPException(
            status_code=500,
            detail=f"Error processing answers: {str(e)}"
        ) 

@router.post("/submit")
async def submit_assessment(
    answers: List[UserAnswer],
    request: Request
) -> AssessmentResponse:
    """
    Submit answers to risk assessment questions and get recommendations.
    
    Args:
        user_id: Identifier for the user
        answers: List of answers with optional photo evidence
    """
    # TODO: Clean up and remove unnecessary branches
    auth_header = request.headers.get("Authorization")
    if not auth_header:
        raise HTTPException(status_code=401, detail="Authorization header missing")
    try:
        scheme, token = auth_header.split()
        if scheme.lower() != "bearer":
            raise HTTPException(status_code=401, detail="Invalid authentication scheme")
    except ValueError:
        raise HTTPException(status_code=401, detail="Invalid authorization header format")
    try:
        decoded_jwt = decode_jwt(token)
        user_id = decoded_jwt["user_id"]
    except jwt.InvalidTokenError:
        raise HTTPException(status_code=401, detail="Invalid token")
    try:
        formatted_answers = []
        for answer in answers:
            question_data = next(
                (q for q in services['question_master'].questions_data["risk_questions"] 
                 if q["question"] == answer.question),
                None
            )
            
            if not question_data:
                continue
            
            photo_score_adjustment = 0
            if question_data.get("requires_photo", False) and answer.photos:
                for photo_url in answer.photos:
                    validation_result = services['photo_validator'].validate_photo(
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
        results = services['grader'].calculate_score(formatted_answers, user_id)
        
        # Generate recommendations
        recommendations = services['recommendation_engine'].get_improvement_recommendations(results)
        
        assessment_response = AssessmentResponse(
            total_score=results["total_score"],
            points_earned=results["points_earned"],
            points_possible=results["points_possible"],
            breakdown=results["breakdown"],
            recommendations=recommendations
        )
        # TODO: Add to database for persistence
        request.app.state.db.insert_assessment_response(user_id, assessment_response.model_dump())
        return assessment_response
        
    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=f"Error processing answers: {str(e)}"
        ) 

@router.get("/assessments/{user_id}")
async def get_assessment_responses(
    user_id: str,
    request: Request
) -> List[dict]:
    """
    Get all assessment responses for a user.
    """
    try:
        responses = request.app.state.db.get_assessment_responses(user_id)
        if not responses:
            return []
        return responses
    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=f"Error retrieving assessment responses: {str(e)}"
        )

@router.get("/assessments/property/{property_id}")
async def get_assessment_responses_by_property(
    property_id: str,
    request: Request
) -> List[dict]:
    """
    Get all assessment responses for a property.
    """
    try:
        responses = request.app.state.db.get_assessment_responses_by_property(property_id)
        if not responses:
            return []
        return responses
    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=f"Error retrieving assessment responses: {str(e)}"
        ) 