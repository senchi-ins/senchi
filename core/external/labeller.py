"""
Module for labeling street view images with improvement recommendations.
"""
import os
import json
import base64
from typing import Dict, List, Tuple
from openai import OpenAI
from dotenv import load_dotenv
from PIL import Image

# Load environment variables
load_dotenv()

class StreetViewLabeller:
    def __init__(self):
        """Initialize the labeller with OpenAI client."""
        self.client = OpenAI(api_key=os.getenv("OPENAI_API_KEY"))
        
        # Mapping of question types to house locations
        self.question_to_location = {
            # Roof-related questions
            'roof': ['roof', 'shingles', 'gutters', 'eavesdrops', 'drains', 'ridge', 'soffit', 'gable', 'attic vents', 'skylights'],
            # Foundation-related questions
            'foundation': ['foundation', 'basement', 'elevated', 'ground', 'flood vents', 'sump pump'],
            # Windows and doors
            'windows_doors': ['windows', 'doors', 'weather stripping', 'caulking', 'sealed'],
            # Exterior walls and siding
            'exterior': ['walls', 'siding', 'materials', 'fire resistant', 'flood-resistant'],
            # Landscaping and driveway
            'landscaping': ['landscaping', 'driveway', 'graded', 'tree limbs', 'branches'],
            # Systems and utilities
            'systems': ['HVAC', 'water heater', 'furnace', 'plumbing', 'hose bibs', 'screens', 'mesh', 'vents', 'chimneys'],
            # Flood barriers and drainage
            'drainage': ['flood barriers', 'blackflow valves', 'downspouts', 'gutters', 'pointed away']
        }

    def _get_image_dimensions(self, image_path: str) -> Tuple[int, int]:
        """Get the actual dimensions of the image."""
        try:
            with Image.open(image_path) as img:
                return img.size  # Returns (width, height)
        except Exception as e:
            print(f"Error getting image dimensions: {str(e)}")
            # Return common default dimensions if unable to read
            return (1920, 1080)

    def _encode_image(self, image_path: str) -> str:
        """Encode image to base64 string."""
        with open(image_path, "rb") as image_file:
            return base64.b64encode(image_file.read()).decode('utf-8')

    def _categorize_recommendation(self, recommendation: Dict) -> str:
        """Categorize a recommendation based on its question text."""
        question_text = recommendation['question'].lower()
        
        # Check each category for keyword matches
        for category, keywords in self.question_to_location.items():
            if any(keyword in question_text for keyword in keywords):
                return category
        
        # Default to exterior if no specific match
        return 'exterior'

    def _get_coordinates_for_locations(self, image_path: str, locations: List[str]) -> List[Dict]:
        """
        Use OpenAI to determine coordinates for specific house locations in the image.
        
        Args:
            image_path: Path to the street view image
            locations: List of house locations to find coordinates for
            
        Returns:
            List of dictionaries with location and coordinates
        """
        base64_image = self._encode_image(image_path)
        
        # Create a prompt for coordinate detection
        location_descriptions = {
            'roof': 'the roof area, including shingles, gutters, and roof line',
            'foundation': 'the foundation or base of the house near ground level',
            'windows_doors': 'windows and doors on the front facade',
            'exterior': 'exterior walls and siding',
            'landscaping': 'landscaping, driveway, or yard areas around the house',
            'systems': 'visible systems like vents, chimneys, or utility areas',
            'drainage': 'gutters, downspouts, or drainage areas'
        }
        
        prompt = f"""
        Analyze this street view image of a house and identify coordinates for the following locations:
        {', '.join([f"{loc} ({location_descriptions.get(loc, loc)})" for loc in locations])}
        
        For each location, provide:
        1. The location name
        2. X,Y coordinates as percentages (0-100) of image width/height
        3. Whether the location is clearly visible
        
        If multiple items of the same type are requested (e.g., multiple roof locations), 
        space them out appropriately across different areas (e.g., left side of roof, right side of roof).
        
        For windows, choose different windows if multiple are needed.
        For roof areas, use different sections (left, center, right, or front/back edges).
        
        Return the response as a JSON array with this format:
        [
            {{
                "location": "roof",
                "x_percent": 45.5,
                "y_percent": 25.0,
                "visible": true,
                "description": "center of roof area"
            }},
            ...
        ]
        
        Image dimensions should be treated as 100% width x 100% height.
        Coordinates should be precise enough to point to the specific house feature.
        """
        
        try:
            response = self.client.chat.completions.create(
                model="gpt-4o",
                messages=[
                    {
                        "role": "user",
                        "content": [
                            {"type": "text", "text": prompt},
                            {
                                "type": "image_url",
                                "image_url": {
                                    "url": f"data:image/jpeg;base64,{base64_image}"
                                }
                            }
                        ]
                    }
                ],
                max_tokens=1000
            )
            
            # Parse the JSON response
            content = response.choices[0].message.content
            # Extract JSON from the response (in case there's extra text)
            json_start = content.find('[')
            json_end = content.rfind(']') + 1
            json_str = content[json_start:json_end]
            
            return json.loads(json_str)
            
        except Exception as e:
            print(f"Error getting coordinates: {str(e)}")
            # Return default coordinates if API fails
            default_coords = []
            for i, location in enumerate(locations):
                default_coords.append({
                    "location": location,
                    "x_percent": 50 + (i * 15),  # Spread out horizontally
                    "y_percent": 40 + (i * 10),  # Spread out vertically
                    "visible": True,
                    "description": f"default position for {location}"
                })
            return default_coords

    def label_recommendations(self, image_path: str, top_recommendations: List[Dict]) -> Dict:
        """
        Generate label coordinates for top recommendations on a street view image.
        
        Args:
            image_path: Path to the street view image
            top_recommendations: List of top 3 recommendations from RecommendationEngine
            
        Returns:
            Dictionary containing:
                - image_dimensions: Dict with width and height in pixels
                - labeled_recommendations: List of dictionaries containing:
                    - recommendation: The original recommendation dict
                    - location_category: The categorized location type
                    - coordinates: Dict with x_percent, y_percent, visible, description
                    - pixel_coordinates: Dict with x_pixel, y_pixel (calculated from percentages)
        """
        if not top_recommendations:
            return {
                'image_dimensions': {'width': 0, 'height': 0},
                'labeled_recommendations': []
            }
        
        # Get image dimensions
        width, height = self._get_image_dimensions(image_path)
        
        # Categorize each recommendation
        categorized_recs = []
        location_counts = {}
        
        for rec in top_recommendations:
            category = self._categorize_recommendation(rec)
            categorized_recs.append({
                'recommendation': rec,
                'category': category
            })
            location_counts[category] = location_counts.get(category, 0) + 1
        
        # Create list of locations to find, accounting for multiples
        locations_to_find = []
        location_instances = {}
        
        for cat_rec in categorized_recs:
            category = cat_rec['category']
            if category not in location_instances:
                location_instances[category] = 0
            location_instances[category] += 1
            
            # Add location with instance number for spacing
            location_key = f"{category}_{location_instances[category]}"
            locations_to_find.append(location_key)
        
        # Get coordinates from OpenAI
        unique_locations = list(set([loc.split('_')[0] for loc in locations_to_find]))
        coordinates = self._get_coordinates_for_locations(image_path, unique_locations)
        
        # Create coordinate lookup by location type
        coord_lookup = {}
        for coord in coordinates:
            location_type = coord['location']
            if location_type not in coord_lookup:
                coord_lookup[location_type] = []
            coord_lookup[location_type].append(coord)
        
        # Assign coordinates to recommendations
        labeled_recommendations = []
        location_usage = {}
        
        for i, cat_rec in enumerate(categorized_recs):
            category = cat_rec['category']
            
            # Get the next available coordinate for this category
            if category not in location_usage:
                location_usage[category] = 0
            
            available_coords = coord_lookup.get(category, [])
            if available_coords and location_usage[category] < len(available_coords):
                coord = available_coords[location_usage[category]]
                location_usage[category] += 1
            else:
                # Fallback coordinate if no specific coordinate available
                coord = {
                    "location": category,
                    "x_percent": 50 + (i * 15),
                    "y_percent": 40 + (i * 10),
                    "visible": True,
                    "description": f"fallback position for {category}"
                }
            
            # Calculate pixel coordinates from percentages
            x_pixel = int((coord['x_percent'] / 100) * width)
            y_pixel = int((coord['y_percent'] / 100) * height)
            
            labeled_recommendations.append({
                'recommendation': cat_rec['recommendation'],
                'location_category': category,
                'coordinates': coord,
                'pixel_coordinates': {
                    'x_pixel': x_pixel,
                    'y_pixel': y_pixel
                }
            })
        
        return {
            'image_dimensions': {
                'width': width,
                'height': height
            },
            'labeled_recommendations': labeled_recommendations
        }

# TODO: Delete this function
def main():
    """Example usage of StreetViewLabeller."""
    from recommendations import RecommendationEngine
    from grader import RiskGrader
    
    # Initialize classes
    grader = RiskGrader()
    recommendation_engine = RecommendationEngine()
    labeller = StreetViewLabeller()
    
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
    
    # Example image path (replace with actual path)
    image_path = "example_street_view.jpg"
    
    # Label the recommendations (this would work with an actual image)
    try:
        result = labeller.label_recommendations(image_path, top_3)
        
        print("Image Analysis Results:")
        print("-" * 50)
        print(f"Image Dimensions: {result['image_dimensions']['width']} x {result['image_dimensions']['height']} pixels")
        
        print("\nLabeled Recommendations:")
        for i, labeled in enumerate(result['labeled_recommendations'], 1):
            rec = labeled['recommendation']
            coord = labeled['coordinates']
            pixel_coord = labeled['pixel_coordinates']
            print(f"\n{i}. {rec['question']}")
            print(f"   Category: {labeled['location_category']}")
            print(f"   Percentage Coordinates: ({coord['x_percent']:.1f}%, {coord['y_percent']:.1f}%)")
            print(f"   Pixel Coordinates: ({pixel_coord['x_pixel']}, {pixel_coord['y_pixel']})")
            print(f"   Visible: {coord['visible']}")
            print(f"   Description: {coord['description']}")
            
    except FileNotFoundError:
        print(f"Image file not found: {image_path}")
        print("Please provide a valid street view image path to test the labelling functionality.")

if __name__ == '__main__':
    main()
