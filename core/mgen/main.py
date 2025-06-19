import asyncio
import os
from dotenv import load_dotenv
import requests

from utils import get_tile_coordinates

load_dotenv()

HIGHSIGHT_API_KEY = os.getenv("HIGHSIGHT_API_KEY")

if not HIGHSIGHT_API_KEY:
    raise ValueError("HIGHSIGHT_API_KEY is not set")

coordinates = get_tile_coordinates(8, 43.51030762363075, -79.88669995721484)

coord = "383 Wettlaufer Terrace, Milton, ON L9T 7N4"

# date = "2025/01/04/0710"

# headers = {
#     "Authorization": f"Bearer {HIGHSIGHT_API_KEY}"
# }

# response = requests.get(f"https://api.highsight.dev/v1/tiles/{coordinates[0]}/{coordinates[1]}/{coordinates[2]}?date={date}", headers=headers)

# if response.status_code != 200:
#     print(f"Error: {response.status_code}")
#     print(response.text)
#     exit(1)

# filename = f"images/tile_z{coordinates[0]}_x{coordinates[1]}_y{coordinates[2]}_{date.replace('/', '_')}.png"
# with open(filename, 'wb') as f:
#     f.write(response.content)

# print(f"Image saved to {filename}")


if __name__ == "__main__":

    from utils import sign_url

    # from addrconv import GoogleMapsGeocoder

    # geocoder = GoogleMapsGeocoder()

    # location = geocoder.geocode_address("383 Wettlaufer Terrace, Milton, ON L9T 7N4")
    # print(location)

    # SECRET = os.getenv("GOOGLE_STREETVIEW_SECRET")
    # API_KEY = os.getenv("GOOGLE_SV_API_KEY")
    # size = "400x400"
    # map_type = "satellite"
    # fov = 80
    
    # heading = 120
    # # Street view of houses
    # url = f"https://maps.googleapis.com/maps/api/streetview?size={size}&location={coord}&center={coord}&fov={fov}&heading={heading}&key={API_KEY}"
    
    # # Arial view of houses
    # # url = f"https://maps.googleapis.com/maps/api/staticmap?center={coord}&zoom={zoom}&size={size}&maptype={map_type}&key={API_KEY}"
    # # stripped_url = f"/maps/api/streetview?location={coord}&size=400x400&key={API_KEY}"
    # # signed_url = sign_url(url, SECRET)
    # response = requests.get(url)
    # print(signed_url)
    # print(response.text)

    from gmaps import get_streetview_image
    response = get_streetview_image(coord, 120)
    filename = f"images/google_streetview_personal_{coord}.png"
    with open(filename, "wb") as f:
        f.write(response["sv_response"])

    # success = asyncio.run(upload_file(response.content, "png"))
    # print(success)













