"""
LLM-based roof analysis module using multimodal models.
"""
from dataclasses import dataclass
from enum import Enum
from typing import Optional
from pathlib import Path
import base64
import io

import requests
from PIL import Image

from .image_processor import ProcessedRoof

class RoofQuality(str, Enum):
    """Possible roof quality assessments."""
    GOOD = "good"
    WORN = "worn"
    PATCHED = "patched"

class RoofShape(str, Enum):
    """Possible roof shapes."""
    GABLE = "gable"
    HIP = "hip"
    FLAT = "flat"
    HIP_AND_VALLEY = "hip and valley"
    PYRAMID = "pyramid"
    DORMER = "dormer"
    OTHER = "other"

class RoofMaterial(str, Enum):
    """Possible roof materials."""
    ASPHALT_SHINGLE = "asphalt_shingle"
    METAL = "metal"
    CLAY_TILE = "clay_tile"
    SLATE = "slate"
    WOOD = "wood"
    OTHER = "other"

class AgeRange(str, Enum):
    """Possible age ranges in years."""
    VERY_NEW = "0-5"
    NEW = "6-15"
    MATURE = "16-30"
    OLD = ">30"

@dataclass
class RoofAnalysis:
    """Results of the LLM roof analysis."""
    quality: RoofQuality
    shape: RoofShape
    material: RoofMaterial
    age_range: AgeRange
    confidence: float  # 0.0 to 1.0
    llm_explanation: str  # Detailed explanation from the LLM

class LLMAnalyzer:
    """
    Analyzes processed roof images using multimodal LLMs to determine
    roof characteristics.
    """
    
    def __init__(self, api_key: str, model: str = "gpt-4-vision-preview"):
        """
        Initialize the LLM analyzer.
        
        Args:
            api_key: OpenAI API key
            model: Model to use (default: GPT-4 Vision)
        """
        self.api_key = api_key
        self.model = model
        self.api_url = "https://api.openai.com/v1/chat/completions"
        
    def _encode_image(self, image: Image.Image) -> str:
        """Convert PIL Image to base64 string."""
        buffer = io.BytesIO()
        image.save(buffer, format="PNG")
        return base64.b64encode(buffer.getvalue()).decode('utf-8')
    
    def _prepare_prompt(self, processed_roof: ProcessedRoof) -> str:
        """Prepare the prompt for the LLM."""
        return """Analyze this satellite image of a roof and provide a detailed assessment. Focus on:

1. Quality (good, worn, or patched)
2. Shape (gable, hip, flat, hip and valley, pyramid, dormer, or other)
3. Material (asphalt shingle, metal, clay tile, slate, wood, or other)
4. Estimated age range (0-5, 6-15, 16-30, or >30 years)

Important context:
- This is a satellite view
- The image has been pre-processed to segment the roof
- Edge detection has been applied to highlight structural features
- The original, segmented, edge-detected, and enhanced versions are provided

Provide your assessment in this exact JSON format:
{
    "quality": "good|worn|patched",
    "shape": "gable|hip|flat|hip and valley|pyramid|dormer|other",
    "material": "asphalt_shingle|metal|clay_tile|slate|wood|other",
    "age_range": "0-5|6-15|16-30|>30",
    "confidence": 0.XX,
    "explanation": "Your detailed reasoning here"
}"""

    def analyze(self, processed_roof: ProcessedRoof) -> RoofAnalysis:
        """
        Analyze a processed roof image using the LLM.
        
        Args:
            processed_roof: ProcessedRoof object containing the original and processed images
            
        Returns:
            RoofAnalysis object containing the LLM's assessment
            
        Raises:
            ValueError: If the LLM response is invalid
            RuntimeError: If the API call fails
        """
        # Encode all four images
        images = [
            ("Original", processed_roof.original.image),
            ("Segmented", processed_roof.segmented_image),
            ("Edges", processed_roof.edge_map),
            ("Enhanced", processed_roof.enhanced_image)
        ]
        
        # Prepare the API request
        headers = {
            "Content-Type": "application/json",
            "Authorization": f"Bearer {self.api_key}"
        }
        
        # Construct the messages array with images
        messages = [{
            "role": "user",
            "content": [
                {
                    "type": "text",
                    "text": self._prepare_prompt(processed_roof)
                }
            ]
        }]
        
        # Add each image to the first message's content
        for label, img in images:
            messages[0]["content"].append({
                "type": "image_url",
                "image_url": {
                    "url": f"data:image/png;base64,{self._encode_image(img)}",
                    "detail": "high"
                }
            })
        
        # Make the API call
        try:
            response = requests.post(
                self.api_url,
                headers=headers,
                json={
                    "model": self.model,
                    "messages": messages,
                    "max_tokens": 1000,
                    "temperature": 0.2  # Lower temperature for more consistent results
                }
            )
            response.raise_for_status()
            
            # Parse the response
            result = response.json()
            content = result["choices"][0]["message"]["content"]
            
            # Extract the JSON part from the response
            import json
            import re
            
            # Find JSON block in the response
            json_match = re.search(r'\{[^}]+\}', content)
            if not json_match:
                raise ValueError("No JSON found in LLM response")
                
            analysis_dict = json.loads(json_match.group())
            
            # Validate and convert to enums
            return RoofAnalysis(
                quality=RoofQuality(analysis_dict["quality"]),
                shape=RoofShape(analysis_dict["shape"]),
                material=RoofMaterial(analysis_dict["material"]),
                age_range=AgeRange(analysis_dict["age_range"]),
                confidence=float(analysis_dict["confidence"]),
                llm_explanation=analysis_dict["explanation"]
            )
            
        except requests.exceptions.RequestException as e:
            raise RuntimeError(f"API call failed: {str(e)}")
        except (json.JSONDecodeError, KeyError, ValueError) as e:
            raise ValueError(f"Invalid LLM response: {str(e)}")
            
    def save_analysis(self, analysis: RoofAnalysis, output_path: Path) -> None:
        """
        Save the analysis results to a file.
        
        Args:
            analysis: RoofAnalysis object
            output_path: Path to save the results
        """
        result = {
            "quality": analysis.quality.value,
            "shape": analysis.shape.value,
            "material": analysis.material.value,
            "age_range": analysis.age_range.value,
            "confidence": analysis.confidence,
            "explanation": analysis.llm_explanation
        }
        
        with open(output_path, 'w') as f:
            import json
            json.dump(result, f, indent=2) 