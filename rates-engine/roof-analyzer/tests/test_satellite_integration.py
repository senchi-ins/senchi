"""
Integration tests for the complete roof analyzer workflow.
"""
import os
import pytest
from datetime import datetime
from PIL import Image
from dotenv import load_dotenv

from src.gee_satellite import GEEFetcher, GEEError, RoofImage

# Load environment variables
load_dotenv()

# Skip tests if Google Maps API key is not available
requires_credentials = pytest.mark.skipif(
    not os.getenv('GOOGLE_MAPS_API_KEY'),
    reason="Missing required Google Maps API key"
)

class TestCompleteWorkflow:
    """Test the complete workflow from address to satellite image."""
    
    def setup_method(self):
        """Set up test instances."""
        # self.geocoder = GoogleMapsGeocoder()  # Commented out for direct coordinate testing
        self.satellite = GEEFetcher()
        
        # Original test addresses
        # self.test_addresses = [
        #     "362 Howland Ave, Toronto, ON",  # Urban area
        #     "2855 W 20th Ave, Vancouver, BC",  # Another urban area
        # ]
        
        # Test locations with hardcoded coordinates
        self.test_locations = [
            {
                "name": "362_howland_ave_toronto_on",
                "latitude": 43.6762,
                "longitude": -79.4133
            },
            {
                "name": "2855_w_20th_ave_vancouver_bc",
                "latitude": 49.2548,
                "longitude": -123.1690
            }
        ]
    
    def test_address_to_satellite_workflow(self):
        """Test the workflow using hardcoded coordinates."""
        # Original geocoding workflow
        # for address in self.test_addresses:
        #     # 1. Geocode the address
        #     location = self.geocoder.geocode_address(address)
        #     
        #     # Verify geocoding results
        #     assert location.latitude is not None
        #     assert location.longitude is not None
        #     assert 'Canada' in location.formatted_address
        
        # New workflow with hardcoded coordinates
        for location in self.test_locations:
            print(f"\n=== Processing {location['name']} ===")
            print(f"Coordinates: {location['latitude']}, {location['longitude']}")
            
            # Fetch satellite image
            roof_image = self.satellite.get_roof_image(
                latitude=location['latitude'],
                longitude=location['longitude'],
                size_meters=50,
                max_cloud_coverage=20
            )
            
            # Debug information
            print(f"Image fetched successfully")
            print(f"Image size: {roof_image.image.size}")
            print(f"Image mode: {roof_image.image.mode}")
            print(f"Capture date: {roof_image.capture_date}")
            print(f"Resolution: {roof_image.resolution}m")
            print(f"Cloud coverage: {roof_image.cloud_coverage}%")
            
            # Verify satellite image
            assert isinstance(roof_image.image, Image.Image)
            assert roof_image.cloud_coverage <= 20
            print(f"Original image size: {roof_image.image.size}")
            # assert roof_image.latitude == location.latitude
            # assert roof_image.longitude == location.longitude
            
            # Preprocess the image
            processed = self.satellite.preprocess_image(roof_image)
            print(f"Processed image size: {processed.image.size}")
            
            # Verify preprocessing
            assert isinstance(processed.image, Image.Image)
            assert processed.image.size == (256, 256)  # Default size
            
            # Save images for manual inspection
            output_dir = "test_output"
            if not os.path.exists(output_dir):
                os.makedirs(output_dir)
            
            # Save both original and processed images
            # safe_address = address.replace(" ", "_").replace(",", "").lower()  # Old way
            roof_image.image.save(f"{output_dir}/{location['name']}_original.png")
            processed.image.save(f"{output_dir}/{location['name']}_processed.png")
            print(f"Images saved to {output_dir}/{location['name']}_*.png")
            
            # Save with timestamp for tracking
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            filename = f"{location['name']}_{timestamp}_gee.png"
            roof_image.image.save(f"{output_dir}/{filename}")
            print(f"Image saved to {output_dir}/{filename}")
    
    def test_error_handling(self):
        """Test error handling in the complete workflow."""
        # Test with invalid coordinates
        with pytest.raises(GEEError):
            self.satellite.get_roof_image(
                latitude=91,  # Invalid latitude
                longitude=0,
                max_cloud_coverage=20
            )
            
        # Test with invalid cloud coverage
        with pytest.raises(GEEError):
            self.satellite.get_roof_image(
                latitude=43.6762,
                longitude=-79.4133,
                max_cloud_coverage=101  # Invalid cloud coverage percentage
            )
            
        # Test with invalid date range
        with pytest.raises(GEEError):
            self.satellite.get_roof_image(
                latitude=43.6762,
                longitude=-79.4133,
                max_cloud_coverage=20,
                start_date="2025-01-01",  # Future date
                end_date="2024-01-01"  # Earlier end date
            ) 