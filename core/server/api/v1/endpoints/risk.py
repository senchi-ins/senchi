import asyncio
from fastapi import APIRouter, HTTPException, Depends
from typing import List, Optional

from mgen.gmaps import get_streetview_image
from mgen.tripo import upload_file, generate_model, get_model_output

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
    response = get_streetview_image(address, heading, zoom)

    # Currently only using streetview image
    file = response["sv_response"]
    success = asyncio.run(upload_file(file, file_type))
    return success

@router.post("/generate-model")
async def generate_model_endpoint(
    file: dict, file_type: str, model_seed: int, texture: bool, style: str
    ):
    task = asyncio.run(generate_model(file, file_type, model_seed, texture, style))
    return task

@router.get("/get-model-output")
async def get_model_output_endpoint(task_id: str):
    result = asyncio.run(get_model_output(task_id))
    return result