"""
Tests for the satellite imagery module.
"""
import pytest
from datetime import datetime
from unittest.mock import Mock, patch
import numpy as np
from PIL import Image

from src.satellite import Sentinel2Fetcher, RoofImage, SatelliteError

def create_test_image(size=(100, 100)):
    """Helper function to create a test image."""
    return Image.fromarray(np.random.randint(0, 255, (*size, 3), dtype=np.uint8))

@patch.dict('os.environ', {
    'SENTINEL_INSTANCE_ID': 'test-instance',
    'SENTINEL_CLIENT_ID': 'test-client',
    'SENTINEL_CLIENT_SECRET': 'test-secret'
})
def test_sentinel_fetcher_init():
    """Test Sentinel2Fetcher initialization with environment variables."""
    fetcher = Sentinel2Fetcher()
    assert fetcher.config.instance_id == 'test-instance'
    assert fetcher.config.sh_client_id == 'test-client'
    assert fetcher.config.sh_client_secret == 'test-secret'

def test_sentinel_fetcher_init_missing_credentials():
    """Test Sentinel2Fetcher initialization with missing credentials."""
    with pytest.raises(SatelliteError, match="Sentinel Hub credentials not found"):
        Sentinel2Fetcher()

@patch('src.satellite.SentinelHubRequest')
def test_get_roof_image(mock_request):
    """Test fetching a roof image."""
    # Mock the response from Sentinel Hub
    test_image = np.random.randint(0, 255, (100, 100, 3), dtype=np.uint8)
    mock_request.return_value.get_data.return_value = [test_image]
    
    fetcher = Sentinel2Fetcher(
        instance_id='test-instance',
        client_id='test-client',
        client_secret='test-secret'
    )
    
    # Test with Toronto coordinates
    result = fetcher.get_roof_image(43.6532, -79.3832)
    
    assert isinstance(result, RoofImage)
    assert isinstance(result.image, Image.Image)
    assert result.latitude == 43.6532
    assert result.longitude == -79.3832
    assert isinstance(result.capture_date, datetime)
    assert result.resolution == fetcher.DEFAULT_RESOLUTION

def test_preprocess_image():
    """Test image preprocessing."""
    # Create a test RoofImage
    test_image = create_test_image()
    roof_image = RoofImage(
        image=test_image,
        latitude=43.6532,
        longitude=-79.3832,
        capture_date=datetime.now(),
        resolution=10.0
    )
    
    fetcher = Sentinel2Fetcher(
        instance_id='test-instance',
        client_id='test-client',
        client_secret='test-secret'
    )
    
    # Test preprocessing
    target_size = (256, 256)
    processed = fetcher.preprocess_image(roof_image, target_size)
    
    assert isinstance(processed, RoofImage)
    assert processed.image.size == target_size
    assert processed.latitude == roof_image.latitude
    assert processed.longitude == roof_image.longitude
    assert processed.capture_date == roof_image.capture_date
    assert processed.resolution == roof_image.resolution

@patch('src.satellite.SentinelHubRequest')
def test_get_roof_image_no_results(mock_request):
    """Test handling of no images found."""
    mock_request.return_value.get_data.return_value = []
    
    fetcher = Sentinel2Fetcher(
        instance_id='test-instance',
        client_id='test-client',
        client_secret='test-secret'
    )
    
    with pytest.raises(SatelliteError, match="No images found"):
        fetcher.get_roof_image(43.6532, -79.3832) 