"""
Geocoding module for converting Canadian addresses to latitude/longitude coordinates.
"""
import os
from typing import Optional, Tuple
from dataclasses import dataclass

import googlemaps
from dotenv import load_dotenv

@dataclass
class Location:
    """Represents a geographical location with address and coordinates."""
    address: str
    latitude: float
    longitude: float
    formatted_address: str

class GeocodingError(Exception):
    """Custom exception for geocoding-related errors."""
    pass

class GoogleMapsGeocoder:
    """Handles geocoding operations using Google Maps API."""
    
    def __init__(self, api_key: Optional[str] = None):
        """
        Initialize the geocoder with Google Maps API key.
        
        Args:
            api_key: Google Maps API key. If None, will try to load from environment.
        """
        if api_key is None:
            load_dotenv()
            api_key = os.getenv('GOOGLE_MAPS_API_KEY')
            
        if not api_key:
            raise GeocodingError("Google Maps API key not found. Please set GOOGLE_MAPS_API_KEY environment variable.")
            
        self.client = googlemaps.Client(key=api_key)
        
    def geocode_address(self, address: str) -> Location:
        """
        Convert a Canadian address to latitude and longitude coordinates.
        
        Args:
            address: A Canadian address string
            
        Returns:
            Location object containing the address and its coordinates
            
        Raises:
            GeocodingError: If address cannot be geocoded or is not in Canada
        """
        # Add 'Canada' to the address if not present
        if 'canada' not in address.lower():
            address = f"{address}, Canada"
            
        try:
            # Geocode the address
            result = self.client.geocode(address)
            
            if not result:
                raise GeocodingError(f"Could not geocode address: {address}")
                
            location = result[0]
            
            # Verify the address is in Canada
            if 'Canada' not in location['formatted_address']:
                raise GeocodingError(f"Address not found in Canada: {address}")
                
            return Location(
                address=address,
                latitude=location['geometry']['location']['lat'],
                longitude=location['geometry']['location']['lng'],
                formatted_address=location['formatted_address']
            )
            
        except Exception as e:
            raise GeocodingError(f"Error geocoding address: {str(e)}")
            
    def validate_coordinates(self, lat: float, lon: float) -> bool:
        """
        Validate if the given coordinates are within Canada's boundaries.
        
        Args:
            lat: Latitude
            lon: Longitude
            
        Returns:
            bool: True if coordinates are within Canada
        """
        # Approximate boundaries of Canada
        CANADA_BOUNDS = {
            'lat': {'min': 41.7, 'max': 83.0},
            'lon': {'min': -141.0, 'max': -52.6}
        }
        
        return (CANADA_BOUNDS['lat']['min'] <= lat <= CANADA_BOUNDS['lat']['max'] and
                CANADA_BOUNDS['lon']['min'] <= lon <= CANADA_BOUNDS['lon']['max']) 