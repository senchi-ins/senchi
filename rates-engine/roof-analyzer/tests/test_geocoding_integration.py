"""
Integration tests for the geocoding module using real API calls.
"""
import os
import pytest
from dotenv import load_dotenv

from src.geocoding import GoogleMapsGeocoder, GeocodingError

# Load environment variables
load_dotenv()

# Skip these tests if no API key is available
requires_api_key = pytest.mark.skipif(
    not os.getenv('GOOGLE_MAPS_API_KEY'),
    reason="Google Maps API key not found in environment"
)

@requires_api_key
def test_real_toronto_address():
    """Test geocoding with a real Toronto address."""
    geocoder = GoogleMapsGeocoder()
    location = geocoder.geocode_address("483 Queen St W, Toronto, ON")
    
    assert location.latitude == pytest.approx(43.6488, abs=0.01)
    assert location.longitude == pytest.approx(-79.3978, abs=0.01)
    assert "Toronto" in location.formatted_address
    assert "Canada" in location.formatted_address

@requires_api_key
def test_real_vancouver_address():
    """Test geocoding with a real Vancouver address."""
    geocoder = GoogleMapsGeocoder()
    location = geocoder.geocode_address("800 Robson St, Vancouver, BC")
    
    assert location.latitude == pytest.approx(49.2827, abs=0.01)
    assert location.longitude == pytest.approx(-123.1207, abs=0.01)
    assert "Vancouver" in location.formatted_address
    assert "Canada" in location.formatted_address

@requires_api_key
def test_non_canadian_address():
    """Test that non-Canadian addresses are rejected."""
    geocoder = GoogleMapsGeocoder()
    with pytest.raises(GeocodingError, match="Address not found in Canada"):
        geocoder.geocode_address("350 5th Ave, New York, NY")

@requires_api_key
def test_invalid_address():
    """Test handling of invalid addresses."""
    geocoder = GoogleMapsGeocoder()
    with pytest.raises(GeocodingError):
        geocoder.geocode_address("This is not a real address, Toronto, ON") 