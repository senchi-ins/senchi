from fastapi import APIRouter, HTTPException, Body
from typing import Dict
from external.camera import RiskPhotoManager

TAG = "Risk Photos"
PREFIX = "/photos"

router = APIRouter()

# Initialize core services
photo_manager = RiskPhotoManager()

@router.get("/")
async def get_photos():
    """Health check endpoint"""
    return {"message": "photo upload service activated"}

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