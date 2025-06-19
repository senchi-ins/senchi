import os
import requests
from dotenv import load_dotenv

# Load environment variables from .env file
load_dotenv()

def get_streetview_image(coord: str, heading: int, zoom: int = 21):
    API_KEY = os.getenv("GOOGLE_SV_API_KEY")
    
    if not API_KEY:
        raise ValueError("Google Street View API key not found in environment variables")
        
    size = "400x400"
    map_type = "satellite"
    fov = 80
    
    # Street view of houses
    sv_url = f"https://maps.googleapis.com/maps/api/streetview?size={size}&location={coord}&center={coord}&fov={fov}&heading={heading}&key={API_KEY}"
    
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
    }

if __name__ == "__main__":
    x = get_streetview_image("383 Wettlaufer Terrace, Milton, ON, L9T 7N4", 120)
    with open("mgen/images/sv_response.png", "wb") as f:
        f.write(x["sv_response"])
    with open("mgen/images/arial_response.png", "wb") as f:
        f.write(x["arial_response"])
