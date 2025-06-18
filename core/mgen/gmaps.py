import os
import requests

def get_streetview_image(coord: str, heading: int, zoom: int = 21):
    API_KEY = os.getenv("GOOGLE_SV_API_KEY")
    size = "400x400"
    map_type = "satellite"
    fov = 80
    
    # Street view of houses
    sv_url = f"https://maps.googleapis.com/maps/api/streetview?size={size}&location={coord}&center={coord}&fov={fov}&heading={heading}&key={API_KEY}"
    
    # Arial view of houses
    arial_url = f"https://maps.googleapis.com/maps/api/staticmap?center={coord}&zoom={zoom}&size={size}&maptype={map_type}&key={API_KEY}"
    sv_response = requests.get(sv_url)
    arial_response = requests.get(arial_url)

    return {
        "sv_response": sv_response.content,
        "arial_response": arial_response.content,
    }