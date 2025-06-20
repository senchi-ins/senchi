import asyncio
import hashlib
from fastapi import APIRouter, HTTPException, Depends, Body
from typing import List, Optional
from pydantic import BaseModel

from mgen.gmaps import get_streetview_image
from mgen.tripo import upload_file_to_tripo, generate_model, get_model_output
from mgen.vector_image import process_vector_image
from mgen.house_labelling import label_house
from openai import OpenAI
from bucket.s3 import upload_file_from_bytes, get_file_url

TAG = "Risk"
PREFIX = "/risk"

router = APIRouter()

class GenerateModelRequest(BaseModel):
    file: dict
    file_type: str
    model_type: str = "image_to_model"

@router.get("/")
async def get_risk():
    return {"message": "risk model activated"}

@router.post("/upload-file")
async def upload_file_endpoint(
        address: str,
        heading: int,
        bucket: str = "senchi-gen-dev",
        zoom: int = 21, 
        file_type: str = "png",
    ):
        try:
            print("starting upload-file")
            # Get Street View image
            response = get_streetview_image(address, heading, zoom)
            object_name = address + "_" + str(heading)

            # Hash the object name to avoid leaking sensitive information
            object_name = hashlib.sha256(object_name.encode()).hexdigest()
            # object_name = "house_testing"
            sv_success = upload_file_from_bytes(
                stream=response["sv_response"],
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
                
            # Process the image
            result = await process_vector_image(file_url)

            # Add the file to the bucket
            gen_success = upload_file_from_bytes(
                stream=result,
                bucket=bucket,
                object_name=f"{object_name}_vector.png"
            )

            if gen_success:
                print(f"Uploaded vector image to S3: {object_name}_vector.png")
                file_url = get_file_url(bucket, f"{object_name}_vector.png")
            else:
                raise HTTPException(
                    status_code=500,
                    detail="Failed to upload file to S3"
                )
            
            try:
                print("Uploading to Tripo...")
                success = await upload_file_to_tripo(file_url, file_type)
                print("Tripo upload successful:", success)
                return success
            except Exception as e:
                print(f"Tripo upload failed: {str(e)}")
                raise HTTPException(
                    status_code=500,
                    detail=f"Failed to upload file to tripo: {str(e)}"
                )
        except HTTPException:
            # Re-raise HTTP exceptions as-is
            raise
        except Exception as e:
            print(f"Unexpected error in upload-file endpoint: {str(e)}")
            import traceback
            traceback.print_exc()
            raise HTTPException(
                status_code=500,
                detail=f"Internal server error: {str(e)}"
            )


@router.post("/generate-model")
async def generate_model_endpoint(request: GenerateModelRequest):
    try:
        task = await generate_model(request.file, request.file_type, model_type=request.model_type)
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
