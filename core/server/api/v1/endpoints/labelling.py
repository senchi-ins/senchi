import asyncio
import hashlib
import os
from fastapi import APIRouter, HTTPException, Depends, Body, UploadFile, File
from typing import List, Optional
from pydantic import BaseModel
from mgen.gmaps import get_streetview_image
from mgen.house_labelling import label_house
from bucket.s3 import upload_file_from_bytes, get_file_url
from server.api.v1.utils.heading import get_camera_position

TAG = "Labelling"
PREFIX = "/labelling"

router = APIRouter()

class LabellingResponse(BaseModel):
    category_scores: List[dict]
    recommendations: List[dict]
    final_score: float

@router.get("/")
async def get_labelling():
    """Health check endpoint"""
    return {"message": "house labelling service activated"}

@router.post("/analyze-house", response_model=LabellingResponse)
async def analyze_house(
        address: str,
        bucket: str = "senchi-gen-dev",
        zoom: int = 21, 
        file_type: str = "png",
    ):
        try:
            print("starting upload-file")
            
            # Calculate optimal heading
            camera_data = await get_camera_position(address)
            heading = int(camera_data.heading)  # Convert to int for the API
            
            # Get Street View image
            image = get_streetview_image(address, heading, zoom)
            
            # Analyze the house using the streetview image
            result = await label_house([image["sv_response"]])
            
            if not result:
                return image
                raise HTTPException(
                    status_code=500,
                    detail="Failed to analyze house image"
                )
                
            return LabellingResponse(
                category_scores=result['category_scores'],
                recommendations=result['recommendations'],
                final_score=result['final_score']
            )
            
        except Exception as e:
            raise HTTPException(
                status_code=500,
                detail=f"Error processing request: {str(e)}"
            )
