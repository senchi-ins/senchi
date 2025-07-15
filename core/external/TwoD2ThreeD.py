"""
Module for converting 2D street view coordinates to 3D GLB model coordinates.
"""

from typing import Dict, List, Union
import trimesh
import io

class CoordinateConverter:
    def __init__(self):
        """Initialize the coordinate converter."""
        # Z-depth assignments based on location categories
        self.location_z_mapping = {
            'roof': 0.5,        # Middle depth
            'exterior': 0.5,    # Middle depth
            'windows_doors': 0.3,  # Slightly forward
            'foundation': 0.2,  # Forward (lower Z)
            'landscaping': 0.1, # Front of house (lowest Z)
            'systems': 0.6,     # Slightly back
            'drainage': 0.4     # Middle-forward
        }
    
    def load_glb_model(self, glb_input: Union[str, bytes]) -> trimesh.Scene:
        """
        Load a GLB file from either a local path, URL, or raw bytes and return the trimesh scene.
        
        Args:
            glb_input: Path to GLB file or raw GLB bytes
            
        Returns:
            Trimesh scene object
        """
        try:
            if isinstance(glb_input, bytes):
                # Handle raw bytes (from proxy endpoint)
                glb_data = io.BytesIO(glb_input)
                scene = trimesh.load(glb_data, file_type='glb')
            else:
                # Handle local file path
                scene = trimesh.load(glb_input)
                
            return scene
        except Exception as e:
            raise ValueError(f"Error loading GLB file: {str(e)}")
    
    def get_3d_bounds(self, scene: trimesh.Scene) -> Dict[str, Dict[str, float]]:
        """
        Get the 3D bounding box dimensions of the GLB model.
        
        Args:
            scene: Trimesh scene object
            
        Returns:
            Dictionary containing min/max values for x, y, z coordinates
        """
        # Get the overall bounds of the scene
        bounds = scene.bounds
        
        return {
            'x': {'min': bounds[0][0], 'max': bounds[1][0], 'range': bounds[1][0] - bounds[0][0]},
            'y': {'min': bounds[0][1], 'max': bounds[1][1], 'range': bounds[1][1] - bounds[0][1]},
            'z': {'min': bounds[0][2], 'max': bounds[1][2], 'range': bounds[1][2] - bounds[0][2]}
        }
    
    def calculate_scaling_factors(self, image_dimensions: Dict[str, int], 
                                bounds_3d: Dict[str, Dict[str, float]]) -> Dict[str, float]:
        """
        Calculate scaling factors from 2D image to 3D model coordinates.
        
        Args:
            image_dimensions: Dictionary with 'width' and 'height' keys
            bounds_3d: 3D bounds from get_3d_bounds()
            
        Returns:
            Dictionary with scaling factors for x and y
        """
        # Calculate scaling factors
        # X: image width maps to 3D X range
        # Y: image height maps to 3D Y range (note: Y is typically up in 3D)
        scale_x = bounds_3d['x']['range'] / image_dimensions['width']
        scale_y = bounds_3d['y']['range'] / image_dimensions['height']
        
        return {
            'x': scale_x,
            'y': scale_y
        }
    
    def convert_2d_to_3d(self, labeled_recommendations: List[Dict], 
                        image_dimensions: Dict[str, int],
                        bounds_3d: Dict[str, Dict[str, float]]) -> List[Dict]:
        """
        Convert 2D pixel coordinates to 3D model coordinates.
        
        Args:
            labeled_recommendations: Output from labeller.py
            image_dimensions: Image dimensions from labeller.py
            bounds_3d: 3D bounds from get_3d_bounds()
            
        Returns:
            List of recommendations with 3D coordinates added
        """
        scaling_factors = self.calculate_scaling_factors(image_dimensions, bounds_3d)
        
        converted_recommendations = []
        
        for labeled_rec in labeled_recommendations:
            pixel_coords = labeled_rec['pixel_coordinates']
            location_category = labeled_rec['location_category']
            
            # Convert X coordinate (left-right)
            # Map from [0, image_width] to [x_min, x_max]
            x_normalized = pixel_coords['x_pixel'] / image_dimensions['width']
            x_3d = bounds_3d['x']['min'] + (x_normalized * bounds_3d['x']['range'])
            
            # Convert Y coordinate (up-down)
            # Note: Image Y=0 is top, but 3D Y=max is typically top
            # So we flip the Y coordinate
            y_normalized = 1.0 - (pixel_coords['y_pixel'] / image_dimensions['height'])
            y_3d = bounds_3d['y']['min'] + (y_normalized * bounds_3d['y']['range'])
            
            # Assign Z coordinate based on location category
            z_factor = self.location_z_mapping.get(location_category, 0.5)  # Default to middle
            z_3d = bounds_3d['z']['min'] + (z_factor * bounds_3d['z']['range'])
            
            # Create the enhanced recommendation
            converted_rec = labeled_rec.copy()
            converted_rec['3d_coordinates'] = {
                'x': float(x_3d),
                'y': float(y_3d),
                'z': float(z_3d)
            }
            converted_rec['scaling_info'] = {
                'x_scale': scaling_factors['x'],
                'y_scale': scaling_factors['y'],
                'z_factor': z_factor
            }
            
            converted_recommendations.append(converted_rec)
        
        return converted_recommendations
    
    def process_labeller_output(self, glb_input: Union[str, bytes], labeller_output: Dict) -> Dict:
        """
        Main processing function that takes labeller output and converts to 3D.
        
        Args:
            glb_input: Path to the GLB file or raw GLB bytes
            labeller_output: Complete output from labeller.py
            
        Returns:
            Dictionary containing:
                - original_2d_data: Original labeller output
                - glb_model_info: Information about the 3D model
                - converted_recommendations: Recommendations with 3D coordinates
        """
        # Load the GLB model
        scene = self.load_glb_model(glb_input)
        
        # Get 3D bounds
        bounds_3d = self.get_3d_bounds(scene)
        
        # Convert recommendations
        converted_recommendations = self.convert_2d_to_3d(
            labeller_output['labeled_recommendations'],
            labeller_output['image_dimensions'],
            bounds_3d
        )
        
        # Calculate scaling factors for reference
        scaling_factors = self.calculate_scaling_factors(
            labeller_output['image_dimensions'],
            bounds_3d
        )
        
        return {
            'original_2d_data': labeller_output,
            'glb_model_info': {
                'bounds_3d': bounds_3d,
                'scaling_factors': scaling_factors,
                'location_z_mapping': self.location_z_mapping
            },
            'converted_recommendations': converted_recommendations
        }

def main():
    """Example usage of CoordinateConverter."""
    from labeller import StreetViewLabeller
    from recommendations import RecommendationEngine
    from grader import RiskGrader
    
    # Initialize all classes
    grader = RiskGrader()
    recommendation_engine = RecommendationEngine()
    labeller = StreetViewLabeller()
    converter = CoordinateConverter()
    
    # Example test data
    example_answers = [
        {
            'question': 'Does your roof have any shingles that are missing, cracked, curled or otherwise damaged?',
            'risk_type': 'Winter',
            'importance': 'High',
            'answer': 'Yes',
            'rubric': {'Yes': 0, 'No': 1},
            'risk_level': 'Very High'
        },
        {
            'question': 'Are your eavesdrops, drains, gutters, and roof free of debris?',
            'risk_type': 'Winter',
            'importance': 'High',
            'answer': 'No',
            'rubric': {'Yes': 1, 'No': 0},
            'risk_level': 'Very High'
        },
        {
            'question': 'Is your landscaping and driveway graded away from your foundation?',
            'risk_type': 'Flooding',
            'importance': 'Medium',
            'answer': 'No',
            'rubric': {'Yes': 1, 'No': 0},
            'risk_level': 'Very High'
        }
    ]
    
    # Calculate scores and get recommendations
    results = grader.calculate_score(example_answers)
    recommendations = recommendation_engine.get_improvement_recommendations(results)
    top_3 = recommendation_engine.get_top_recommendations()
    
    # Example paths (replace with actual paths)
    image_path = "example_street_view.jpg"
    glb_path = "example_house.glb"
    
    try:
        # Get 2D coordinates from labeller
        labeller_output = labeller.label_recommendations(image_path, top_3)
        
        # Convert to 3D coordinates
        result_3d = converter.process_labeller_output(glb_path, labeller_output)
        
        print("2D to 3D Conversion Results:")
        print("=" * 60)
        
        print(f"\nImage Dimensions: {result_3d['original_2d_data']['image_dimensions']['width']} x {result_3d['original_2d_data']['image_dimensions']['height']}")
        
        print("\n3D Model Bounds:")
        bounds = result_3d['glb_model_info']['bounds_3d']
        print(f"X: {bounds['x']['min']:.3f} to {bounds['x']['max']:.3f} (range: {bounds['x']['range']:.3f})")
        print(f"Y: {bounds['y']['min']:.3f} to {bounds['y']['max']:.3f} (range: {bounds['y']['range']:.3f})")
        print(f"Z: {bounds['z']['min']:.3f} to {bounds['z']['max']:.3f} (range: {bounds['z']['range']:.3f})")
        
        print("\nScaling Factors:")
        scales = result_3d['glb_model_info']['scaling_factors']
        print(f"X Scale: {scales['x']:.6f} (3D units per pixel)")
        print(f"Y Scale: {scales['y']:.6f} (3D units per pixel)")
        
        print("\nConverted Recommendations:")
        print("-" * 60)
        for i, rec in enumerate(result_3d['converted_recommendations'], 1):
            print(f"\n{i}. {rec['recommendation']['question']}")
            print(f"   Category: {rec['location_category']}")
            
            # 2D coordinates
            pixel_coords = rec['pixel_coordinates']
            print(f"   2D Pixel: ({pixel_coords['x_pixel']}, {pixel_coords['y_pixel']})")
            
            # 3D coordinates
            coords_3d = rec['3d_coordinates']
            print(f"   3D Coords: ({coords_3d['x']:.3f}, {coords_3d['y']:.3f}, {coords_3d['z']:.3f})")
            
            # Scaling info
            scale_info = rec['scaling_info']
            print(f"   Z Factor: {scale_info['z_factor']} (based on {rec['location_category']})")
            
    except FileNotFoundError as e:
        print(f"File not found: {str(e)}")
        print("Please provide valid image and GLB file paths to test the conversion.")
    except Exception as e:
        print(f"Error during conversion: {str(e)}")

if __name__ == '__main__':
    main()
