"""
Tests for the geocoding module.
"""
import pytest
from unittest.mock import Mock, patch

from src.geocoding import GoogleMapsGeocoder, GeocodingError, Location

def test_validate_coordinates_within_canada():
    """Test coordinate validation for points within Canada."""
    # Create a mock client that won't be used
    mock_client = Mock()
    geocoder = GoogleMapsGeocoder.__new__(GoogleMapsGeocoder)
    geocoder.client = mock_client
    
    # Test valid Canadian coordinates (Toronto)
    assert geocoder.validate_coordinates(43.6532, -79.3832) == True
    
    # Test valid Canadian coordinates (Vancouver)
    assert geocoder.validate_coordinates(49.2827, -123.1207) == True

def test_validate_coordinates_outside_canada():
    """Test coordinate validation for points outside Canada."""
    # Create a mock client that won't be used
    mock_client = Mock()
    geocoder = GoogleMapsGeocoder.__new__(GoogleMapsGeocoder)
    geocoder.client = mock_client
    
    # Test New York coordinates
    assert geocoder.validate_coordinates(40.7128, -74.0060) == False
    
    # Test London coordinates
    assert geocoder.validate_coordinates(51.5074, -0.1278) == False

@patch('googlemaps.Client')
def test_geocode_address_success(mock_client):
    """Test successful address geocoding."""
    # Mock the Google Maps client response
    mock_response = [{
        'formatted_address': '123 Example St, Toronto, ON, Canada',
        'geometry': {
            'location': {
                'lat': 43.6532,
                'lng': -79.3832
            }
        }
    }]
    mock_client.return_value.geocode.return_value = mock_response
    
    geocoder = GoogleMapsGeocoder(api_key="dummy_key")
    result = geocoder.geocode_address("123 Example St, Toronto")
    
    assert isinstance(result, Location)
    assert result.latitude == 43.6532
    assert result.longitude == -79.3832
    assert "Canada" in result.formatted_address

@patch('googlemaps.Client')
def test_geocode_address_not_in_canada(mock_client):
    """Test geocoding address outside Canada."""
    # Mock response for non-Canadian address
    mock_response = [{
        'formatted_address': '123 Example St, New York, NY, USA',
        'geometry': {
            'location': {
                'lat': 40.7128,
                'lng': -74.0060
            }
        }
    }]
    mock_client.return_value.geocode.return_value = mock_response
    
    geocoder = GoogleMapsGeocoder(api_key="dummy_key")
    with pytest.raises(GeocodingError, match="Address not found in Canada"):
        geocoder.geocode_address("123 Example St, New York") 