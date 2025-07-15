import os
import requests
from dotenv import load_dotenv
from typing import Dict, Any

# Load environment variables from .env file
load_dotenv()

def get_streetview_metadata(coord: str) -> Dict[str, Any]:
    """
    Get metadata about the Street View image location.
    
    Args:
        coord (str): The location coordinates or address
        
    Returns:
        Dict[str, Any]: Dictionary containing metadata about the Street View location
    """
    API_KEY = os.getenv("GOOGLE_SV_API_KEY")
    if not API_KEY:
        raise ValueError("Google Street View API key not found in environment variables")
    if not API_KEY.startswith('"'):
        API_KEY = API_KEY.strip('"')
    
    metadata_url = f"https://maps.googleapis.com/maps/api/streetview/metadata?location={coord}&key={API_KEY}"
    
    response = requests.get(metadata_url)
    if not response.ok:
        raise ValueError(f"Street View Metadata API request failed: {response.status_code}")
    
    metadata = response.json()
    if metadata.get('status') != 'OK':
        raise ValueError(f"Street View Metadata API error: {metadata.get('status')}")
        
    return metadata

def get_streetview_image(coord: str, heading: int, zoom: int = 21):
    """
    Get Street View and aerial images for a location.
    
    Args:
        coord (str): The location coordinates or address
        heading (int): The camera heading in degrees
        zoom (int, optional): Zoom level for aerial view. Defaults to 21.
        
    Returns:
        Dict[str, Any]: Dictionary containing image data and camera location
    """
    API_KEY = os.getenv("GOOGLE_SV_API_KEY")
    if not API_KEY:
        raise ValueError("Google Street View API key not found in environment variables")
    if not API_KEY.startswith('"'):
        API_KEY = API_KEY.strip('"')
    
    # Get Street View metadata first
    metadata = get_streetview_metadata(coord)
    
    size = "400x400"
    map_type = "satellite"
    fov = 80
    
    # Use the exact camera location from metadata for the Street View image
    camera_lat = metadata['location']['lat']
    camera_lng = metadata['location']['lng']
    camera_location = f"{camera_lat},{camera_lng}"
    
    # Street view of houses
    sv_url = f"https://maps.googleapis.com/maps/api/streetview?size={size}&location={camera_location}&fov={fov}&heading={heading}&key={API_KEY}"
    
    # Arial view of houses
    arial_url = f"https://maps.googleapis.com/maps/api/staticmap?center={coord}&zoom={zoom}&size={size}&maptype={map_type}&key={API_KEY}"
    
    # Get Street View image
    sv_response = requests.get(sv_url)
    if not sv_response.ok:
        raise ValueError(f"Street View API request failed: {sv_response.status_code}")
    if not sv_response.headers.get('content-type', '').startswith('image'):
        raise ValueError(f"Invalid response from Street View API: Not an image")
        
    # Get Arial view image
    arial_response = requests.get(arial_url)
    if not arial_response.ok:
        raise ValueError(f"Static Maps API request failed: {arial_response.status_code}")
    if not arial_response.headers.get('content-type', '').startswith('image'):
        raise ValueError(f"Invalid response from Static Maps API: Not an image")

    return {
        "sv_response": sv_response.content,
        "arial_response": arial_response.content,
        "camera_location": {
            "latitude": camera_lat,
            "longitude": camera_lng,
            "heading": heading
        }
    }

if __name__ == "__main__":
    x = get_streetview_image("383 Wettlaufer Terrace, Milton, ON, L9T 7N4", 120)
    print(f"Camera Location: {x['camera_location']}")
    with open("mgen/images/sv_response.png", "wb") as f:
        f.write(x["sv_response"])
    with open("mgen/images/arial_response.png", "wb") as f:
        f.write(x["arial_response"])
