"""
Test the full pipeline from address to segmented roof image.
"""
import os
from datetime import datetime
from pathlib import Path

import pytest
from dotenv import load_dotenv

from src.geocoding import GoogleMapsGeocoder
from src.satellite import Sentinel2Fetcher, RoofImage
from src.image_processor import RoofProcessor, ProcessedRoof

# Load environment variables
load_dotenv()

# Test addresses - a mix of different roof types
TEST_ADDRESSES = [
    "2920 Matheson Blvd E, Mississauga, ON",  # Commercial building with flat roof
    "25 Sunrise Ave, Toronto, ON",            # Residential with pitched roof
    "55 Bloor St W, Toronto, ON",            # High-rise with complex roof
]

@pytest.fixture
def output_dir():
    """Create and return output directory for test images."""
    output_path = Path("test_output")
    output_path.mkdir(exist_ok=True)
    return output_path

@pytest.fixture
def geocoder():
    """Initialize the geocoder."""
    api_key = os.getenv("GOOGLE_MAPS_API_KEY")
    if not api_key:
        pytest.skip("GOOGLE_MAPS_API_KEY not found in environment")
    return GoogleMapsGeocoder(api_key)

@pytest.fixture
def satellite():
    """Initialize the satellite image fetcher."""
    client_id = os.getenv("SENTINEL_CLIENT_ID")
    client_secret = os.getenv("SENTINEL_CLIENT_SECRET")
    if not client_id or not client_secret:
        pytest.skip("Sentinel hub credentials not found in environment")
    return Sentinel2Fetcher(client_id, client_secret)

@pytest.fixture
def processor():
    """Initialize the image processor."""
    return RoofProcessor()

def test_full_pipeline(geocoder, satellite, processor, output_dir):
    """
    Test the full pipeline from address to processed roof image.
    
    This test will:
    1. Convert addresses to coordinates
    2. Fetch satellite images
    3. Process images with our roof segmentation
    4. Save visualizations of the results
    """
    for address in TEST_ADDRESSES:
        # 1. Geocoding
        coordinates = geocoder.geocode(address)
        assert coordinates is not None
        
        # 2. Satellite Image
        image = satellite.get_roof_image(
            coordinates.latitude,
            coordinates.longitude,
            size_meters=50  # Capture 50x50 meter area
        )
        assert isinstance(image, RoofImage)
        
        # 3. Process Image
        processed = processor.process_roof(image)
        assert isinstance(processed, ProcessedRoof)
        
        # 4. Save Results
        # Create a clean filename from address
        clean_address = address.replace(" ", "_").replace(",", "").replace(".", "")
        output_path = output_dir / f"{clean_address}_results.png"
        
        # Save visualization
        processor.visualize_results(processed, str(output_path))
        assert output_path.exists()
        
        # Print results
        print(f"\nResults for {address}:")
        print(f"Confidence Score: {processed.confidence_score:.2%}")
        print(f"Roof Area Ratio: {processed.roof_area_ratio:.2%}")

@pytest.mark.parametrize("image_name", ["roof1.png", "roof2.png", "roof3.png", "roof4.png", "roof5.png"])
def test_individual_components(processor, output_dir, image_name):
    """
    Test the image processing components with sample roof images.
    This helps isolate any issues in the processing pipeline.
    """
    test_image_path = Path("tests/test_data") / image_name
    assert test_image_path.exists(), f"Test image {image_name} not found"
        
    from PIL import Image
    import numpy as np
    
    # Load test image
    image = Image.open(test_image_path)
    
    # Create RoofImage object
    roof_image = RoofImage(
        image=image,
        latitude=43.6532,  # Example coordinates (Toronto)
        longitude=-79.3832,
        capture_date=datetime.now(),
        resolution=0.5  # 0.5 meters per pixel
    )
    
    try:
        # Process the image
        processed = processor.process_roof(roof_image)
        
        # Save visualization
        output_path = output_dir / f"{image_name.replace('.png', '')}_processed.png"
        processor.visualize_results(processed, str(output_path))
        
        # Print results
        print(f"\nResults for {image_name}:")
        print(f"Confidence Score: {processed.confidence_score:.2%}")
        print(f"Roof Area Ratio: {processed.roof_area_ratio:.2%}")
        
        # Basic assertions
        assert processed.confidence_score > 0, "No confidence in roof detection"
        assert processed.roof_area_ratio > 0, "No roof area detected"
        assert output_path.exists(), "Visualization was not saved"
        
    except Exception as e:
        pytest.fail(f"Processing failed for {image_name}: {str(e)}") 