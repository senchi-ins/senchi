"""
Google Earth Engine integration module for fetching high-resolution imagery.
"""
import os
from datetime import datetime
from typing import Optional, Tuple
from dataclasses import dataclass

import ee
import numpy as np
from PIL import Image, ImageEnhance
from dotenv import load_dotenv

import requests
from io import BytesIO

@dataclass
class RoofImage:
    """Represents a processed roof image with metadata from Google Earth Engine."""
    image: Image.Image
    latitude: float
    longitude: float
    capture_date: datetime
    resolution: float
    cloud_coverage: float = 0.0

class GEEError(Exception):
    """Custom exception for Google Earth Engine related errors."""
    pass

class GEEFetcher:
    """Handles satellite imagery operations using Google Earth Engine."""
    
    def __init__(self, service_account: Optional[str] = None, key_file: Optional[str] = None):
        """
        Initialize the Google Earth Engine fetcher.
        """

        load_dotenv()
        
        try:
            ee.Initialize(project=os.getenv('GEE_PROJECT_ID'))
        except Exception as e:
            raise GEEError(f"Failed to initialize Google Earth Engine: {str(e)}")
            
    def get_roof_image(
        self,
        latitude: float,
        longitude: float,
        size_meters: float = 30,
        start_date: Optional[str] = None,
        end_date: Optional[str] = None,
        max_cloud_coverage: float = 20.0
    ) -> RoofImage:
        """
        Fetch a Sentinel-2 image centered on the given coordinates.
        
        Args:
            latitude: Latitude of the center point
            longitude: Longitude of the center point
            size_meters: Size of the bounding box in meters
            start_date: Start date for image search (YYYY-MM-DD)
            end_date: End date for image search (YYYY-MM-DD)
            max_cloud_coverage: Maximum allowed cloud coverage percentage (0-100)
            
        Returns:
            RoofImage object containing the processed image and metadata
            
        Raises:
            GEEError: If image cannot be fetched or processed
        """
        # Validate inputs
        if not -90 <= latitude <= 90:
            raise GEEError("Latitude must be between -90 and 90 degrees")
        if not -180 <= longitude <= 180:
            raise GEEError("Longitude must be between -180 and 180 degrees")
        if not 0 <= max_cloud_coverage <= 100:
            raise GEEError("Cloud coverage must be between 0 and 100 percent")
            
        try:
            # Create point and buffer geometry
            point = ee.Geometry.Point([longitude, latitude])
            region = point.buffer(size_meters / 2)
            
            # Set date range
            if not end_date:
                end_date = datetime.now().strftime('%Y-%m-%d')
            if not start_date:
                start_date = '2020-01-01'  # Default to recent imagery
                
            # Get Sentinel-2 imagery
            s2 = ee.ImageCollection('COPERNICUS/S2_SR_HARMONIZED')\
                .filterBounds(region)\
                .filterDate(start_date, end_date)\
                .filter(ee.Filter.lt('CLOUDY_PIXEL_PERCENTAGE', max_cloud_coverage))\
                .sort('CLOUDY_PIXEL_PERCENTAGE')\
                .sort('system:time_start', False)
                
            if s2.size().getInfo() == 0:
                raise GEEError(f"No suitable imagery found for location ({latitude}, {longitude}) in date range {start_date} to {end_date}")
                
            # Get the first image
            original = s2.first()
            
            # Get metadata before any transformations
            timestamp = original.get('system:time_start').getInfo()
            if timestamp is None:
                raise GEEError("Image found but missing timestamp metadata")
            capture_date = datetime.fromtimestamp(timestamp / 1000)
            
            cloud_coverage = float(original.get('CLOUDY_PIXEL_PERCENTAGE').getInfo() or 0)
            
            # Sentinel-2 has 10m resolution for RGB bands
            resolution = 10.0

            # Visualization parameters to stretch reflectance values
            vis_params = {
                'bands': ['R', 'G', 'B'],
                'min': 0,
                'max': 3000,
                'gamma': 1.2
            }
            
            # Process the image while maintaining projection
            rgb_bands = original.select(['B4', 'B3', 'B2'])\
                .rename(['R', 'G', 'B'])\
                .clip(region)\
                .visualize(**vis_params)
                
            # Get the image data
            image_data = rgb_bands.getThumbUrl({
                'region': region,
                'dimensions': resolution,
                'format': 'png',
            })
            
            # Convert to PIL Image
    
            
            response = requests.get(image_data)
            if response.status_code != 200 or 'image' not in response.headers.get('Content-Type', ''):
                raise GEEError(f"Failed to fetch image thumbnail: HTTP {response.status_code}")
            
            pil_image = Image.open(BytesIO(response.content))
            if pil_image.mode == 'RGBA':
                pil_image = pil_image.convert('RGB')
            
            return RoofImage(
                image=pil_image,
                latitude=latitude,
                longitude=longitude,
                capture_date=capture_date,
                resolution=resolution,
                cloud_coverage=cloud_coverage
            )
        
        except GEEError:
            raise

        except Exception as e:
            raise GEEError(f"Error fetching image from Google Earth Engine: {str(e)}")
            
    def preprocess_image(self, roof_image: RoofImage, target_size: Tuple[int, int] = (256, 256)) -> RoofImage:
        """
        Preprocess the roof image for model input.
        
        Args:
            roof_image: RoofImage object containing the original image
            target_size: Desired output size in pixels (width, height)
            
        Returns:
            RoofImage object with preprocessed image
        """
        try:
            # Resize image
            resized_image = roof_image.image.resize(target_size, Image.Resampling.LANCZOS)
            
            # Enhance contrast
            enhancer = ImageEnhance.Contrast(resized_image)
            enhanced_image = enhancer.enhance(1.2)  # Increase contrast by 20%
            
            # Create new RoofImage with processed image
            return RoofImage(
                image=enhanced_image,
                latitude=roof_image.latitude,
                longitude=roof_image.longitude,
                capture_date=roof_image.capture_date,
                resolution=roof_image.resolution,
                cloud_coverage=roof_image.cloud_coverage
            )
            
        except Exception as e:
            raise GEEError(f"Error preprocessing image: {str(e)}") 