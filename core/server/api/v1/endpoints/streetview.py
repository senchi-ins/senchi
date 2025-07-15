from fastapi import APIRouter, HTTPException
import tempfile
import os

from mgen.gmaps import get_streetview_image
from external.labeller import StreetViewLabeller
from schemas.coordinates import CoordinateRequest

TAG = "Street View"
PREFIX = "/streetview"

router = APIRouter()

# Initialize services
labeller = StreetViewLabeller()

def save_bytes_to_temp(image_bytes: bytes, suffix: str = '.jpg') -> str:
    """Save bytes to a temporary file and return the path."""
    temp_file = tempfile.NamedTemporaryFile(delete=False, suffix=suffix)
    temp_file.write(image_bytes)
    temp_file.close()
    return temp_file.name

def cleanup_temp_file(file_path: str):
    """Clean up a temporary file."""
    try:
        os.unlink(file_path)
    except Exception as e:
        print(f"Error cleaning up temp file {file_path}: {e}")

@router.get("/")
async def get_streetview():
    """Health check endpoint"""
    return {"message": "street view service activated"}

@router.post("/preview")
async def preview_coordinates(request: CoordinateRequest):
    """
    Generate a preview of the coordinate mapping without 3D conversion.
    Useful for testing and visualization.
    """
    temp_image_path = None
    try:
        # Get street view image
        images = get_streetview_image(request.address, request.heading, request.zoom)
        
        # Save image bytes to temporary file
        temp_image_path = save_bytes_to_temp(images["sv_response"])
        
        # Use labeller to identify locations
        labelled_results = labeller.label_recommendations(
            temp_image_path,
            [rec.dict() for rec in request.recommendations]
        )
        
        return {
            "image_dimensions": labelled_results['image_dimensions'],
            "labeled_recommendations": labelled_results['labeled_recommendations']
        }
        
    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=f"Error generating preview: {str(e)}"
        )
    finally:
        if temp_image_path:
            cleanup_temp_file(temp_image_path) 