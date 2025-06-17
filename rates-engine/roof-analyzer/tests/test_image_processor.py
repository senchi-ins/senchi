"""
Tests for the advanced image processing module.
"""
import os
import pytest
from datetime import datetime
import numpy as np
from PIL import Image

from src.satellite import RoofImage
from src.image_processor import RoofProcessor, ProcessedRoof, ImageProcessingError

def create_test_image(size=(256, 256)):
    """Create a test image with a simulated roof."""
    # Create a black background
    image = np.zeros((*size, 3), dtype=np.uint8)
    
    # Add a white rectangle in the middle (simulated roof)
    h, w = size
    roof_h, roof_w = h // 2, w // 2
    y1, y2 = (h - roof_h) // 2, (h + roof_h) // 2
    x1, x2 = (w - roof_w) // 2, (w + roof_w) // 2
    image[y1:y2, x1:x2] = 255
    
    return Image.fromarray(image)

def create_test_roof_image():
    """Create a RoofImage object with test data."""
    return RoofImage(
        image=create_test_image(),
        latitude=43.6532,
        longitude=-79.3832,
        capture_date=datetime.now(),
        resolution=10.0
    )

@pytest.fixture
def processor():
    """Create a RoofProcessor instance for testing."""
    return RoofProcessor()

def test_process_roof(processor):
    """Test basic roof processing workflow."""
    # Create test input
    roof_image = create_test_roof_image()
    
    # Process the roof
    result = processor.process_roof(roof_image)
    
    # Verify results
    assert isinstance(result, ProcessedRoof)
    assert isinstance(result.segmented_image, Image.Image)
    assert isinstance(result.edge_map, Image.Image)
    assert isinstance(result.enhanced_image, Image.Image)
    assert 0 <= result.confidence_score <= 1
    assert 0 <= result.roof_area_ratio <= 1

def test_process_roof_no_roof(processor):
    """Test processing an image with no visible roof."""
    # Create black image (no roof)
    image = Image.fromarray(np.zeros((256, 256, 3), dtype=np.uint8))
    roof_image = RoofImage(
        image=image,
        latitude=43.6532,
        longitude=-79.3832,
        capture_date=datetime.now(),
        resolution=10.0
    )
    
    # Should raise error when no roof is detected
    with pytest.raises(ImageProcessingError, match="No roof detected in image"):
        processor.process_roof(roof_image)

def test_visualization(processor, tmp_path):
    """Test visualization of processing results."""
    # Process a test image
    roof_image = create_test_roof_image()
    processed = processor.process_roof(roof_image)
    
    # Create visualization
    output_path = tmp_path / "visualization.png"
    processor.visualize_results(processed, str(output_path))
    
    # Verify visualization was created
    assert output_path.exists()
    
    # Load and check the visualization
    vis_image = Image.open(output_path)
    assert vis_image.size[0] > vis_image.size[1]  # Should be wider than tall
    assert vis_image.mode == 'RGB'

def test_edge_detection(processor):
    """Test edge detection on a simple image."""
    # Create test image with clear edges
    size = (256, 256)
    image = np.zeros((*size, 3), dtype=np.uint8)
    image[64:192, 64:192] = 255  # White square on black background
    
    # Detect edges
    edges = processor._detect_edges(image)
    
    # Verify edges were detected
    assert edges.shape == size
    assert np.sum(edges > 0) > 0  # Should have detected some edges

def test_image_enhancement(processor):
    """Test image enhancement on a low contrast image."""
    # Create low contrast test image
    size = (256, 256)
    image = np.ones((*size, 3), dtype=np.uint8) * 127  # Mid-gray image
    image[64:192, 64:192] = 157  # Slightly lighter square
    
    # Enhance image
    enhanced = processor._enhance_image(image)
    
    # Verify enhancement
    assert enhanced.shape == (*size, 3)
    assert np.std(enhanced) > np.std(image)  # Should have more contrast 