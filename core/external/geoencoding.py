"""
Geocoding module for converting USA and Canadian addresses to latitude/longitude coordinates.
"""
import os
from typing import Optional
from dataclasses import dataclass, asdict

import googlemaps
from dotenv import load_dotenv
import requests
import re

@dataclass
class Location:
    """Represents a geographical location with address and coordinates."""
    address: str
    latitude: float
    longitude: float
    formatted_address: str
    country: str

class GeocodingError(Exception):
    """Custom exception for geocoding-related errors."""
    pass

class GoogleMapsGeocoder:
    """Handles geocoding operations using Google Maps API for USA and Canada."""
    
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
        
    @staticmethod
    def _get_county_from_fcc(lat: float, lon: float) -> Optional[str]:
        """Fetch county name from FCC census API given latitude and longitude."""
        try:
            url = f"https://geo.fcc.gov/api/census/area?lat={lat}&lon={lon}&format=json"
            resp = requests.get(url, timeout=5)
            if resp.status_code == 200:
                data = resp.json()
                if data.get('results'):
                    return data['results'][0].get('county_name')
        except Exception:
            pass  # Swallow any exception and return None if FCC API fails
        return None

    @staticmethod
    def _clean_county_name(name: str) -> str:
        """Remove common suffixes like 'County', 'Municipality', etc. from county name."""
        return re.sub(r"\s+(County|City and County|City|Municipality|Parish|Borough|Census Area)$", "", name, flags=re.IGNORECASE)
        
    def geocode_address(self, address: str) -> dict:
        """
        Convert a USA or Canadian address to latitude and longitude coordinates and return as a dictionary.
        For USA addresses, also include 'County' and 'State' abbreviation.
        For Canadian addresses, include 'Province' abbreviation and 'Region' (administrative area level 2).
        """
        try:
            result = self.client.geocode(address)
            
            if not result:
                raise GeocodingError(f"No results found for address: {address}")
                
            location = result[0]
            address_components = location.get('address_components', [])
            
            # Extract all address components
            street_number = ""
            route = ""
            city = ""
            state_abbr = None
            postal_code = ""
            country = None
            county = None # For USA administrative_area_level_2
            region = None  # For Canadian administrative_area_level_2
            
            candidate_admin2 = None  # store administrative_area_level_2 regardless of country
            for component in address_components:
                types = component['types']
                if 'street_number' in types:
                    street_number = component['long_name']
                elif 'route' in types:
                    route = component['long_name']
                elif 'locality' in types:
                    city = component['long_name']
                elif 'administrative_area_level_1' in types:
                    state_abbr = component['short_name']
                elif 'postal_code' in types:
                    postal_code = component['long_name']
                elif 'country' in types:
                    country_code = component['short_name']
                    country = 'USA' if country_code == 'US' else ('Canada' if country_code == 'CA' else None)
                elif 'administrative_area_level_2' in types:
                    candidate_admin2 = component['long_name']
            
            # Decide on county/region based on collected administrative_area_level_2
            if country == 'USA':
                if not county and candidate_admin2:
                    county = self._clean_county_name(candidate_admin2)
                # If still missing, fallback to FCC API
                if not county:
                    fcc_county = self._get_county_from_fcc(location['geometry']['location']['lat'],
                                                           location['geometry']['location']['lng'])
                    if fcc_county:
                        county = self._clean_county_name(fcc_county)
            elif country == 'Canada':
                if not region and candidate_admin2:
                    region = candidate_admin2
            
            if not country or country not in ['USA', 'Canada']:
                raise GeocodingError(f"Address not found in USA/Canada: {address}")
            
            # Construct clean formatted address
            formatted_parts = []
            if street_number and route:
                formatted_parts.append(f"{street_number} {route}")
            elif route:
                formatted_parts.append(route)
                
            if city:
                formatted_parts.append(city)
            if state_abbr:
                formatted_parts.append(state_abbr)
            if postal_code:
                formatted_parts.append(postal_code)
            formatted_parts.append(country)
            
            formatted_address = ", ".join(formatted_parts)
            
            loc_obj = Location(
                address=address,
                latitude=location['geometry']['location']['lat'],
                longitude=location['geometry']['location']['lng'],
                formatted_address=formatted_address,
                country=country
            )
            
            output = asdict(loc_obj)
            if country == 'USA':
                if county:
                    output['county'] = county
                if state_abbr:
                    output['state'] = state_abbr
            elif country == 'Canada':
                if state_abbr:
                    output['province'] = state_abbr
                if region:
                    output['region'] = region
                    
            return output
                
        except Exception as e:
            raise GeocodingError(f"Error geocoding address: {str(e)}") 