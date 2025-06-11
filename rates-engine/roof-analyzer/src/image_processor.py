"""
Advanced image processing module for roof analysis.
"""
import os
from pathlib import Path
from typing import Optional, Tuple, List
from dataclasses import dataclass

import cv2
import numpy as np
from PIL import Image, ImageEnhance
from skimage import exposure, feature, filters
import torch
from segment_anything import sam_model_registry, SamPredictor
from groundingdino.util.inference import Model

from .satellite import RoofImage

@dataclass
class ProcessedRoof:
    """Represents a fully processed roof image with segmentation and enhancements."""
    original: RoofImage
    segmented_image: Image.Image  # Isolated roof
    edge_map: Image.Image         # Edge detection result
    enhanced_image: Image.Image   # Final enhanced version
    confidence_score: float       # Confidence in roof detection (0-1)
    roof_area_ratio: float       # Ratio of roof area to total image area

class ImageProcessingError(Exception):
    """Custom exception for image processing errors."""
    pass

class RoofProcessor:
    """Handles advanced image processing for roof analysis."""
    
    def __init__(self, sam_checkpoint: Optional[str] = None, grounding_checkpoint: Optional[str] = None):
        """
        Initialize the roof processor.
        
        Args:
            sam_checkpoint: Path to SAM model checkpoint. If None, will download default.
            grounding_checkpoint: Path to Grounding DINO checkpoint. If None, will download default.
        """
        self.device = torch.device("cuda" if torch.cuda.is_available() else "cpu")
        
        # Initialize Segment Anything Model (SAM)
        if sam_checkpoint is None:
            model_dir = Path("models")
            model_dir.mkdir(exist_ok=True)
            sam_checkpoint = model_dir / "sam_vit_h_4b8939.pth"
            if not sam_checkpoint.exists():
                # Download default model
                import urllib.request
                url = "https://dl.fbaipublicfiles.com/segment_anything/sam_vit_h_4b8939.pth"
                urllib.request.urlretrieve(url, sam_checkpoint)
        
        sam = sam_model_registry["vit_h"](checkpoint=str(sam_checkpoint))
        sam.to(device=self.device)
        self.predictor = SamPredictor(sam)
        
        # Initialize Grounding DINO for text-to-box
        if grounding_checkpoint is None:
            model_dir = Path("models")
            model_dir.mkdir(exist_ok=True)
            grounding_checkpoint = model_dir / "groundingdino_swint_ogc.pth"
            if not grounding_checkpoint.exists():
                import urllib.request
                url = "https://github.com/IDEA-Research/GroundingDINO/releases/download/v0.1.0-alpha/groundingdino_swint_ogc.pth"
                urllib.request.urlretrieve(url, grounding_checkpoint)
        
        self.grounding_model = Model(model_config_path="GroundingDINO/groundingdino/config/GroundingDINO_SwinT_OGC.py",
                                   model_checkpoint_path=str(grounding_checkpoint))
        
    def process_roof(self, roof_image: RoofImage) -> ProcessedRoof:
        """
        Perform advanced processing on a roof image.
        
        Args:
            roof_image: RoofImage object containing the original image
            
        Returns:
            ProcessedRoof object containing processed images and metadata
            
        Raises:
            ImageProcessingError: If processing fails
        """
        try:
            # Convert PIL Image to numpy array
            image_np = np.array(roof_image.image)
            
            # 1. Roof Segmentation
            segmented, confidence = self._segment_roof(image_np)
            
            # 2. Edge Detection
            edges = self._detect_edges(segmented)
            
            # 3. Image Enhancement
            enhanced = self._enhance_image(segmented)
            
            # Calculate roof area ratio
            total_pixels = segmented.shape[0] * segmented.shape[1]
            roof_pixels = np.sum(segmented > 0)
            roof_area_ratio = roof_pixels / total_pixels
            
            return ProcessedRoof(
                original=roof_image,
                segmented_image=Image.fromarray(segmented),
                edge_map=Image.fromarray(edges),
                enhanced_image=Image.fromarray(enhanced),
                confidence_score=confidence,
                roof_area_ratio=roof_area_ratio
            )
            
        except Exception as e:
            raise ImageProcessingError(f"Error processing roof image: {str(e)}")
    
    def _segment_roof(self, image: np.ndarray) -> Tuple[np.ndarray, float]:
        """
        Segment the roof from the image using SAM with text prompting.
        
        Args:
            image: Input image as numpy array
            
        Returns:
            Tuple of (segmented image, confidence score)
        """
        # Set image in SAM predictor
        self.predictor.set_image(image)
        
        # First use Grounding DINO to get bounding box from text prompt
        detections = self.grounding_model.predict_with_caption(
            image=image,
            caption="roof of house or building",
            box_threshold=0.35,
            text_threshold=0.25
        )
        
        if len(detections.xyxy) == 0:
            raise ImageProcessingError("No roof detected in image")
        
        # Get the most confident roof detection
        best_box_idx = np.argmax(detections.confidence)
        best_box = detections.xyxy[best_box_idx]
        
        # Use the box to guide SAM
        input_box = best_box[None, :]  # Add batch dimension
        masks, scores, _ = self.predictor.predict(
            point_coords=None,
            point_labels=None,
            box=input_box,
            multimask_output=True
        )
        
        if len(masks) == 0:
            raise ImageProcessingError("Failed to segment roof")
            
        # Select the most confident mask
        best_mask_idx = np.argmax(scores)
        best_mask = masks[best_mask_idx]
        confidence = float(scores[best_mask_idx] * detections.confidence[best_box_idx])
        
        # Apply mask to image
        segmented = image.copy()
        segmented[~best_mask] = 0
        
        return segmented, confidence
    
    def _detect_edges(self, image: np.ndarray) -> np.ndarray:
        """
        Detect edges in the segmented roof image.
        
        Args:
            image: Segmented roof image
            
        Returns:
            Edge map as numpy array
        """
        # Convert to grayscale if needed
        if len(image.shape) == 3:
            gray = cv2.cvtColor(image, cv2.COLOR_RGB2GRAY)
        else:
            gray = image
            
        # Apply Canny edge detection
        edges = feature.canny(
            gray,
            sigma=2.0,
            low_threshold=0.55,
            high_threshold=0.8
        )
        
        # Dilate edges for better visibility
        kernel = np.ones((3,3), np.uint8)
        edges = cv2.dilate(edges.astype(np.uint8), kernel, iterations=1)
        
        return edges * 255  # Convert to 0-255 range
    
    def _enhance_image(self, image: np.ndarray) -> np.ndarray:
        """
        Enhance the segmented roof image.
        
        Args:
            image: Segmented roof image
            
        Returns:
            Enhanced image as numpy array
        """
        # Convert to PIL Image for enhancement
        pil_image = Image.fromarray(image)
        
        # Enhance contrast
        enhancer = ImageEnhance.Contrast(pil_image)
        contrast_enhanced = enhancer.enhance(1.3)  # Increase contrast by 30%
        
        # Enhance sharpness
        enhancer = ImageEnhance.Sharpness(contrast_enhanced)
        sharp_enhanced = enhancer.enhance(1.2)  # Increase sharpness by 20%
        
        # Convert back to numpy array
        enhanced = np.array(sharp_enhanced)
        
        # Apply adaptive histogram equalization for better detail visibility
        if len(enhanced.shape) == 3:
            # Process each channel separately
            for i in range(3):
                enhanced[:,:,i] = exposure.equalize_adapthist(
                    enhanced[:,:,i],
                    clip_limit=0.03
                ) * 255
                
        return enhanced.astype(np.uint8)
    
    def visualize_results(self, processed: ProcessedRoof, output_path: str):
        """
        Save visualization of processing results.
        
        Args:
            processed: ProcessedRoof object
            output_path: Path to save visualization
        """
        # Create a figure with all processing steps
        fig_size = (15, 5)
        dpi = 100
        width = int(fig_size[0] * dpi)
        height = int(fig_size[1] * dpi)
        canvas = Image.new('RGB', (width, height), 'white')
        
        # Resize all images to fit in the visualization
        target_height = height
        target_width = height
        
        images = [
            ("Original", processed.original.image),
            ("Segmented", processed.segmented_image),
            ("Edges", processed.edge_map),
            ("Enhanced", processed.enhanced_image)
        ]
        
        # Place images side by side
        x_offset = 0
        for title, img in images:
            # Resize image
            img_resized = img.resize((target_width, target_height))
            canvas.paste(img_resized, (x_offset, 0))
            x_offset += target_width
            
        # Save the visualization
        canvas.save(output_path) 