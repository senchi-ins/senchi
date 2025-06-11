"""
Integration tests for the complete roof analyzer workflow.
"""
import os
import pytest
from datetime import datetime
from PIL import Image
from dotenv import load_dotenv

from src.geocoding import GoogleMapsGeocoder, GeocodingError
from src.satellite import Sentinel2Fetcher, SatelliteError

# Load environment variables
load_dotenv()

# Skip all tests if required credentials are not available
requires_credentials = pytest.mark.skipif(
    not (os.getenv('GOOGLE_MAPS_API_KEY') and 
         os.getenv('SENTINEL_INSTANCE_ID') and
         os.getenv('SENTINEL_CLIENT_ID') and
         os.getenv('SENTINEL_CLIENT_SECRET')),
    reason="Missing required API credentials"
)

@requires_credentials
class TestCompleteWorkflow:
    """Test the complete workflow from address to satellite image."""
    
    def setup_method(self):
        """Set up test instances."""
        self.geocoder = GoogleMapsGeocoder()
        self.satellite = Sentinel2Fetcher()
        
        # Test addresses - known locations with visible roofs
        self.test_addresses = [
            "483 Queen St W, Toronto, ON",  # Urban area
            "800 Robson St, Vancouver, BC",  # Another urban area
        ]
    
    def test_address_to_satellite_workflow(self):
        """Test the complete workflow from address to satellite image."""
        for address in self.test_addresses:
            # 1. Geocode the address
            location = self.geocoder.geocode_address(address)
            
            # Verify geocoding results
            assert location.latitude is not None
            assert location.longitude is not None
            assert 'Canada' in location.formatted_address
            
            # 2. Fetch satellite image
            roof_image = self.satellite.get_roof_image(
                latitude=location.latitude,
                longitude=location.longitude,
                max_cloud_coverage=30.0  # Slightly higher threshold for testing
            )
            
            # Verify satellite image
            assert isinstance(roof_image.image, Image.Image)
            assert roof_image.latitude == location.latitude
            assert roof_image.longitude == location.longitude
            
            # 3. Preprocess the image
            processed = self.satellite.preprocess_image(roof_image)
            
            # Verify preprocessing
            assert isinstance(processed.image, Image.Image)
            assert processed.image.size == (256, 256)  # Default size
            
            # Save images for manual inspection if needed
            output_dir = "test_output"
            if not os.path.exists(output_dir):
                os.makedirs(output_dir)
                
            # Save both original and processed images
            safe_address = address.replace(" ", "_").replace(",", "").lower()
            roof_image.image.save(f"{output_dir}/{safe_address}_original.png")
            processed.image.save(f"{output_dir}/{safe_address}_processed.png")
    
    def test_error_handling(self):
        """Test error handling in the complete workflow."""
        # Test with non-Canadian address (should raise GeocodingError)
        with pytest.raises(GeocodingError, match="Address not found in Canada"):
            self.geocoder.geocode_address("350 5th Ave, New York, NY")
        
        # # Test with invalid address format
        # with pytest.raises(GeocodingError):
        #     self.geocoder.geocode_address("!@#$%^&*()")
            
        # # Test with empty address
        # with pytest.raises(GeocodingError):
        #     self.geocoder.geocode_address("")
        
        # Test with valid coordinates but invalid cloud coverage
        location = self.geocoder.geocode_address(self.test_addresses[0])
        with pytest.raises(SatelliteError, match="Cloud coverage must be between 0 and 100 percent"):
            self.satellite.get_roof_image(
                latitude=location.latitude,
                longitude=location.longitude,
                max_cloud_coverage=101.0  # Invalid percentage
            ) 