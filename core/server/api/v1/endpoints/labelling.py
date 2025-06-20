import asyncio
import hashlib
import os
from fastapi import APIRouter, HTTPException, Depends, Body, UploadFile, File
from typing import List, Optional
from pydantic import BaseModel
from mgen.gmaps import get_streetview_image
from mgen.house_labelling import label_house
from bucket.s3 import upload_file_from_bytes, get_file_url

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
        heading: int,
        bucket: str = "senchi-gen-dev",
        zoom: int = 21, 
        file_type: str = "png",
    ):
        try:
            print("starting upload-file")
            # Get Street View image
            images = get_streetview_image(address, heading, zoom)
            object_name = address + "_" + str(heading)

            # Hash the object name to avoid leaking sensitive information
            object_name = hashlib.sha256(object_name.encode()).hexdigest()
            # object_name = "house_testing"
            sv_success = upload_file_from_bytes(
                stream=images["sv_response"],
                bucket=bucket,
                object_name=f"{object_name}.png"
            )

            if sv_success:
                print(f"Uploaded streetview image to S3: {object_name}.png")
                file_url = get_file_url(bucket, f"{object_name}.png")
            else:
                raise HTTPException(
                    status_code=500,
                    detail="Failed to upload file to S3"
                )
        
            # Analyze the house using the streetview image
            result = await label_house([images["sv_response"]])
            
            if not result:
                return images
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
