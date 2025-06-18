import asyncio
from fastapi import APIRouter, HTTPException, Depends
from typing import List, Optional

from mgen.gmaps import get_streetview_image
from mgen.tripo import upload_file, generate_model, get_model_output
from mgen.vector_image import process_vector_image
from mgen.house_labelling import label_house
from openai import OpenAI

TAG = "Risk"
PREFIX = "/risk"

router = APIRouter()

@router.get("/")
async def get_risk():
    return {"message": "risk model activated"}

@router.post("/upload-file")
async def upload_file_endpoint(
        address: str, 
        heading: int, 
        zoom: int = 21, 
        file_type: str = "png",
    ):
    try:
        # Get Street View image
        response = get_streetview_image(address, heading, zoom)
        if not response or not response.get("sv_response"):
            raise HTTPException(
                status_code=400,
                detail="Failed to fetch Street View image - no response received"
            )
            
        # Process the image
        try:
            result = await process_vector_image(response["sv_response"])
        except Exception as e:
            raise HTTPException(
                status_code=500,
                detail=f"Failed to process vector image: {str(e)}"
            )
            
        # Upload the processed image
        try:
            success = await upload_file(result, file_type)
            return success
        except Exception as e:
            raise HTTPException(
                status_code=500,
                detail=f"Failed to upload processed image: {str(e)}"
            )
            
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))
    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=f"An unexpected error occurred: {str(e)}"
        )

@router.post("/generate-model")
async def generate_model_endpoint(
    file: dict, file_type: str, model_seed: int, texture: bool, style: str
    ):
    try:
        task = await generate_model(file, file_type, model_seed, texture, style)
        return task
    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=f"Failed to generate model: {str(e)}"
        )

@router.get("/get-model-output")
async def get_model_output_endpoint(task_id: str):
    try:
        result = await get_model_output(task_id)
        return result
    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=f"Failed to get model output: {str(e)}"
        )

# @router.post("/analyze-house")
# async def analyze_house_endpoint(
#     address: str,
#     heading: int,
#     zoom: int = 21,
# ):
#     response = get_streetview_image(address, heading, zoom)
#     result = asyncio.run(label_house(response["sv_response"]))
#     return result