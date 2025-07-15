"""
Module for calculating optimal Street View camera positions and headings.
"""
import math
from typing import Dict, Any, Tuple
import sys
from pathlib import Path

# Add core directory to Python path
core_dir = Path(__file__).resolve().parent.parent
if str(core_dir) not in sys.path:
    sys.path.append(str(core_dir))

from mgen.gmaps import get_streetview_metadata
from external.geoencoding import GoogleMapsGeocoder, GeocodingError

def calculate_bearing(lat1: float, lon1: float, lat2: float, lon2: float) -> float:
    """
    Calculate the bearing/heading angle between two geographical points.
    
    Args:
        lat1: Latitude of the first point (camera position)
        lon1: Longitude of the first point (camera position)
        lat2: Latitude of the second point (target building)
        lon2: Longitude of the second point (target building)
        
    Returns:
        float: Bearing angle in degrees (0-360)
    """
    def to_rad(deg: float) -> float:
        return deg * math.pi / 180
    
    def to_deg(rad: float) -> float:
        return rad * 180 / math.pi

    dLon = to_rad(lon2 - lon1)
    lat1 = to_rad(lat1)
    lat2 = to_rad(lat2)

    y = math.sin(dLon) * math.cos(lat2)
    x = math.cos(lat1) * math.sin(lat2) - \
        math.sin(lat1) * math.cos(lat2) * math.cos(dLon)
    bearing = math.atan2(y, x)
    return (to_deg(bearing) + 360) % 360

def get_optimal_streetview_position(address: str) -> Dict[str, Any]:
    """
    Get the optimal Street View camera position and heading for a given address.
    
    This function:
    1. Geocodes the address to get its exact coordinates
    2. Gets the nearest Street View camera position
    3. Calculates the optimal heading to point at the address
    
    Args:
        address: The target address to photograph
        
    Returns:
        Dict containing:
        - target_location: Dict with address coordinates and metadata
        - camera_position: Dict with Street View camera position
        - heading: Optimal camera heading in degrees
        
    Raises:
        GeocodingError: If address cannot be geocoded
        ValueError: If Street View metadata cannot be retrieved
    """
    # First get the exact coordinates of the address
    geocoder = GoogleMapsGeocoder()
    target_location = geocoder.geocode_address(address)
    
    # Get the nearest Street View camera position
    metadata = get_streetview_metadata(address)
    
    if metadata.get('status') != 'OK':
        raise ValueError(f"No Street View data available for address: {address}")
    
    # Calculate optimal heading from camera to target
    camera_lat = metadata['location']['lat']
    camera_lng = metadata['location']['lng']
    target_lat = target_location['latitude']
    target_lng = target_location['longitude']
    
    heading = calculate_bearing(
        camera_lat, camera_lng,
        target_lat, target_lng
    )
    
    return {
        "target_location": target_location,
        "camera_position": {
            "latitude": camera_lat,
            "longitude": camera_lng
        },
        "heading": heading
    }

if __name__ == "__main__":
    # Example usage
    test_address = "19 valleyway crescent, vaughan, on, L6A 1K6"
    try:
        result = get_optimal_streetview_position(test_address)
        print(f"Target Location: {result['target_location']}")
        print(f"Camera Position: {result['camera_position']}")
        print(f"Optimal Heading: {result['heading']:.2f}°")
    except (GeocodingError, ValueError) as e:
        print(f"Error: {str(e)}")
    except Exception as e:
        print(f"Unexpected error: {str(e)}") 