from fastapi import APIRouter, HTTPException
import tempfile
import os

from mgen.gmaps import get_streetview_image
from external.labeller import StreetViewLabeller
from external.TwoD2ThreeD import CoordinateConverter
from bucket.s3 import get_file_url
from schemas.coordinates import (
    CoordinateRequest,
    Coordinate2D,
    Coordinate3D,
    RecommendationCoordinates,
    CoordinateResponse
)

TAG = "Coordinate Conversion"
PREFIX = "/coordinates"

router = APIRouter()

# Initialize services
labeller = StreetViewLabeller()
converter = CoordinateConverter()

# Configuration
MODEL_BUCKET = "senchi-gen-dev"
MODEL_PREFIX = "models"

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
async def get_coordinates():
    """Health check endpoint"""
    return {"message": "coordinate conversion service activated"}

@router.post("/convert", response_model=CoordinateResponse)
async def convert_coordinates(request: CoordinateRequest):
    """
    Convert recommendations to 2D image coordinates and then to 3D model coordinates.
    
    Args:
        request: CoordinateRequest containing address, recommendations, and model info
    """
    temp_image_path = None
    try:
        # Step 1: Get street view image
        images = get_streetview_image(request.address, request.heading, request.zoom)
        
        # Save image bytes to temporary file
        temp_image_path = save_bytes_to_temp(images["sv_response"])
        
        # Step 2: Use labeller to identify locations on the image
        labelled_results = labeller.label_recommendations(
            temp_image_path,  # Pass temporary file path
            [rec.dict() for rec in request.recommendations]  # Convert to dict format
        )
        
        # Step 3: Get model path from S3
        model_url = get_file_url(
            MODEL_BUCKET,
            f"{MODEL_PREFIX}/{request.model_task_id}/model.glb"
        )
        
        # Step 4: Convert 2D coordinates to 3D
        conversion_results = converter.process_labeller_output(
            model_url,  # CoordinateConverter should handle URLs
            labelled_results
        )
        
        # Step 5: Format response
        recommendations_with_coords = []
        for rec_data in conversion_results['converted_recommendations']:
            original_rec = next(
                r for r in request.recommendations 
                if r.question == rec_data['recommendation']['question']
            )
            
            coords_2d = Coordinate2D(
                x_pixel=rec_data['pixel_coordinates']['x_pixel'],
                y_pixel=rec_data['pixel_coordinates']['y_pixel'],
                x_percent=rec_data['coordinates']['x_percent'],
                y_percent=rec_data['coordinates']['y_percent'],
                visible=rec_data['coordinates']['visible'],
                description=rec_data['coordinates']['description']
            )
            
            coords_3d = Coordinate3D(
                x=rec_data['3d_coordinates']['x'],
                y=rec_data['3d_coordinates']['y'],
                z=rec_data['3d_coordinates']['z'],
                scaling_info=rec_data['scaling_info']
            )
            
            recommendations_with_coords.append(
                RecommendationCoordinates(
                    recommendation=original_rec,
                    location_category=rec_data['location_category'],
                    coordinates_2d=coords_2d,
                    coordinates_3d=coords_3d
                )
            )
        
        return CoordinateResponse(
            image_dimensions=labelled_results['image_dimensions'],
            recommendations=recommendations_with_coords,
            model_info=conversion_results['glb_model_info']
        )
        
    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=f"Error converting coordinates: {str(e)}"
        )
    finally:
        if temp_image_path:
            cleanup_temp_file(temp_image_path) 