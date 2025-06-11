"""
Tests for the LLM-based roof analyzer.
"""
import os
from pathlib import Path
import json
from datetime import datetime

import pytest
from PIL import Image
from dotenv import load_dotenv

from src.llm_analyzer import (
    LLMAnalyzer,
    RoofAnalysis,
    RoofQuality,
    RoofShape,
    RoofMaterial,
    AgeRange
)
from src.satellite import RoofImage
from src.image_processor import RoofProcessor, ProcessedRoof

# Load environment variables
load_dotenv()

@pytest.fixture
def api_key():
    """Get OpenAI API key from environment."""
    key = os.getenv("OPENAI_API_KEY")
    if not key:
        pytest.skip("OPENAI_API_KEY not found in environment")
    return key

@pytest.fixture
def analyzer(api_key):
    """Create an LLMAnalyzer instance."""
    return LLMAnalyzer(api_key)

@pytest.fixture
def processor():
    """Create a RoofProcessor instance."""
    return RoofProcessor()

@pytest.fixture
def output_dir():
    """Create and return output directory."""
    output_path = Path("test_output")
    output_path.mkdir(exist_ok=True)
    return output_path

def create_processed_roof(image_path: Path, processor: RoofProcessor) -> ProcessedRoof:
    """Helper function to create a ProcessedRoof object from an image."""
    # Load and process the image
    image = Image.open(image_path)
    
    # Create RoofImage object
    roof_image = RoofImage(
        image=image,
        latitude=43.6532,
        longitude=-79.3832,
        capture_date=datetime.now(),
        resolution=0.5
    )
    
    # Process the image
    return processor.process_roof(roof_image)

@pytest.mark.parametrize("image_name", ["roof1.png", "roof2.png", "roof3.png", "roof4.png", "roof5.png"])
def test_llm_analysis(analyzer, processor, output_dir, image_name):
    """
    Test the LLM analysis on sample roof images.
    """
    # Process the image
    image_path = Path("tests/test_data") / image_name
    processed_roof = create_processed_roof(image_path, processor)
    
    # Run LLM analysis
    analysis = analyzer.analyze(processed_roof)
    
    # Save results
    output_path = output_dir / f"{image_name.replace('.png', '')}_analysis.json"
    analyzer.save_analysis(analysis, output_path)
    
    # Basic validation
    assert isinstance(analysis, RoofAnalysis)
    assert isinstance(analysis.quality, RoofQuality)
    assert isinstance(analysis.shape, RoofShape)
    assert isinstance(analysis.material, RoofMaterial)
    assert isinstance(analysis.age_range, AgeRange)
    assert 0 <= analysis.confidence <= 1
    assert len(analysis.llm_explanation) > 0
    
    # Print results
    print(f"\nAnalysis results for {image_name}:")
    print(f"Quality: {analysis.quality.value}")
    print(f"Shape: {analysis.shape.value}")
    print(f"Material: {analysis.material.value}")
    print(f"Age Range: {analysis.age_range.value}")
    print(f"Confidence: {analysis.confidence:.2%}")
    print(f"Explanation: {analysis.llm_explanation[:100]}...")

def test_invalid_api_key():
    """Test behavior with invalid API key."""
    analyzer = LLMAnalyzer("invalid_key")
    image_path = Path("tests/test_data/roof1.png")
    processor = RoofProcessor()
    processed_roof = create_processed_roof(image_path, processor)
    
    with pytest.raises(RuntimeError, match="API call failed"):
        analyzer.analyze(processed_roof)

def test_save_and_load_analysis(analyzer, processor, output_dir):
    """Test saving and loading analysis results."""
    # Create and save an analysis
    image_path = Path("tests/test_data/roof1.png")
    processed_roof = create_processed_roof(image_path, processor)
    analysis = analyzer.analyze(processed_roof)
    
    output_path = output_dir / "test_analysis.json"
    analyzer.save_analysis(analysis, output_path)
    
    # Load and verify
    with open(output_path) as f:
        loaded = json.load(f)
    
    assert loaded["quality"] == analysis.quality.value
    assert loaded["shape"] == analysis.shape.value
    assert loaded["material"] == analysis.material.value
    assert loaded["age_range"] == analysis.age_range.value
    assert loaded["confidence"] == analysis.confidence
    assert loaded["explanation"] == analysis.llm_explanation 