"""
Satellite imagery module for fetching and processing roof images using Sentinel-2.
"""
import os
from datetime import datetime, timedelta
from typing import Optional, Tuple
from dataclasses import dataclass

import numpy as np
from PIL import Image
from sentinelhub import (
    SHConfig,
    BBox,
    CRS,
    DataCollection,
    SentinelHubRequest,
    MimeType,
    bbox_to_dimensions,
)

@dataclass
class RoofImage:
    """Represents a processed roof image with metadata."""
    image: Image.Image
    latitude: float
    longitude: float
    capture_date: datetime
    resolution: float  # Ground resolution in meters per pixel
    cloud_coverage: float = 0.0  # Cloud coverage percentage (0-100)

class SatelliteError(Exception):
    """Custom exception for satellite imagery-related errors."""
    pass

class Sentinel2Fetcher:
    """Handles satellite imagery operations using Sentinel-2."""
    
    def __init__(self, instance_id: Optional[str] = None, client_id: Optional[str] = None, client_secret: Optional[str] = None):
        """
        Initialize the Sentinel-2 fetcher.
        
        Args:
            instance_id: Sentinel Hub instance ID
            client_id: Sentinel Hub OAuth client ID
            client_secret: Sentinel Hub OAuth client secret
        """
        # Load credentials from environment if not provided
        if not all([instance_id, client_id, client_secret]):
            from dotenv import load_dotenv
            load_dotenv()
            instance_id = instance_id or os.getenv('SENTINEL_INSTANCE_ID')
            client_id = client_id or os.getenv('SENTINEL_CLIENT_ID')
            client_secret = client_secret or os.getenv('SENTINEL_CLIENT_SECRET')
            
        if not all([instance_id, client_id, client_secret]):
            raise SatelliteError(
                "Sentinel Hub credentials not found. Please set SENTINEL_INSTANCE_ID, "
                "SENTINEL_CLIENT_ID, and SENTINEL_CLIENT_SECRET environment variables."
            )
            
        # Configure Sentinel Hub
        self.config = SHConfig()
        self.config.instance_id = instance_id
        self.config.sh_client_id = client_id
        self.config.sh_client_secret = client_secret
        
        # Default parameters
        self.DEFAULT_RESOLUTION = 10  # 10m per pixel
        self.HOUSE_SIZE = 30  # Approximate house size in meters
        
    def get_roof_image(
        self,
        latitude: float,
        longitude: float,
        size_meters: float = None,
        resolution: float = None,
        max_cloud_coverage: float = 20.0,  # Percentage (0-100)
        time_from: datetime = None,
        time_to: datetime = None
    ) -> RoofImage:
        """
        Fetch a satellite image centered on the given coordinates.
        
        Args:
            latitude: Latitude of the center point
            longitude: Longitude of the center point
            size_meters: Size of the bounding box in meters (default: HOUSE_SIZE)
            resolution: Ground resolution in meters per pixel (default: DEFAULT_RESOLUTION)
            max_cloud_coverage: Maximum allowed cloud coverage percentage (0-100)
            time_from: Start date for image search (default: 6 months ago)
            time_to: End date for image search (default: now)
            
        Returns:
            RoofImage object containing the processed image and metadata
            
        Raises:
            SatelliteError: If image cannot be fetched or processed
        """
        size_meters = size_meters or self.HOUSE_SIZE
        resolution = resolution or self.DEFAULT_RESOLUTION
        
        # Convert cloud coverage percentage to decimal (0-1)
        max_cloud_coverage_decimal = max_cloud_coverage / 100.0
        if not 0 <= max_cloud_coverage_decimal <= 1:
            raise SatelliteError("Cloud coverage must be between 0 and 100 percent")
        
        # Set time range if not provided
        if not time_from:
            time_from = datetime.now() - timedelta(days=180)  # Last 6 months
        if not time_to:
            time_to = datetime.now()
            
        try:
            # Calculate bounding box
            half_size = size_meters / 2
            # Convert meters to degrees (approximate at the given latitude)
            meters_to_deg = 1 / 111320.0  # 1 degree is approximately 111.32 km at the equator
            deg_size = half_size * meters_to_deg
            
            # Create bounding box coordinates
            bbox_coords = [
                longitude - deg_size,  # min_x
                latitude - deg_size,   # min_y
                longitude + deg_size,  # max_x
                latitude + deg_size    # max_y
            ]
            
            # Create BBox with correct format
            bbox = BBox(bbox_coords, CRS.WGS84)
            
            # Calculate pixel dimensions
            bbox_size = bbox_to_dimensions(bbox, resolution=resolution)
            
            # Configure the request
            request = SentinelHubRequest(
                data_folder="sentinel_data",
                evalscript="""
                    //VERSION=3
                    function setup() {
                        return {
                            input: [{
                                bands: ["B02", "B03", "B04"],
                                units: "DN"
                            }],
                            output: {
                                bands: 3,
                                sampleType: "AUTO"
                            }
                        };
                    }

                    function evaluatePixel(sample) {
                        return [sample.B04, sample.B03, sample.B02];
                    }
                """,
                input_data=[
                    SentinelHubRequest.input_data(
                        data_collection=DataCollection.SENTINEL2_L2A,
                        time_interval=(time_from, time_to),
                        mosaicking_order='leastCC',
                        maxcc=max_cloud_coverage_decimal  # Use decimal value
                    )
                ],
                responses=[SentinelHubRequest.output_response("default", MimeType.PNG)],
                bbox=bbox,
                size=bbox_size,
                config=self.config
            )
            
            # Get the image
            images = request.get_data()
            if not images or len(images) == 0:
                raise SatelliteError("No images found for the specified location and criteria")
                
            # Convert to PIL Image
            image_array = images[0]
            image = Image.fromarray(np.uint8(image_array))
            
            return RoofImage(
                image=image,
                latitude=latitude,
                longitude=longitude,
                capture_date=time_from,  # Using start of time range as approximate capture date
                resolution=resolution
            )
            
        except Exception as e:
            raise SatelliteError(f"Error fetching satellite image: {str(e)}")
            
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
            from PIL import ImageEnhance
            enhancer = ImageEnhance.Contrast(resized_image)
            enhanced_image = enhancer.enhance(1.2)  # Increase contrast by 20%
            
            # Create new RoofImage with processed image
            return RoofImage(
                image=enhanced_image,
                latitude=roof_image.latitude,
                longitude=roof_image.longitude,
                capture_date=roof_image.capture_date,
                resolution=roof_image.resolution
            )
            
        except Exception as e:
            raise SatelliteError(f"Error preprocessing image: {str(e)}") 