# Roof Analyzer

A tool to analyze roof quality, age, shape, and material using satellite imagery for Canadian properties.

## Setup

1. Install dependencies:
```bash
pip install -r requirements.txt
```

2. Configure Google Maps API:
   - Obtain a Google Maps API key from the [Google Cloud Console](https://console.cloud.google.com/)
   - Create a `.env` file in the project root
   - Add your API key:
     ```
     GOOGLE_MAPS_API_KEY=your_api_key_here
     ```

## Usage

### Geocoding Module

```python
from src.geocoding import GoogleMapsGeocoder

# Initialize the geocoder
geocoder = GoogleMapsGeocoder()  # Will use API key from .env file
# Or provide API key directly:
# geocoder = GoogleMapsGeocoder(api_key="your_api_key")

# Geocode a Canadian address
try:
    location = geocoder.geocode_address("123 Example St, Toronto, ON")
    print(f"Latitude: {location.latitude}")
    print(f"Longitude: {location.longitude}")
    print(f"Formatted Address: {location.formatted_address}")
except GeocodingError as e:
    print(f"Error: {e}")
```

## Testing

Run tests using pytest:
```bash
pytest tests/
```

## Project Structure

```
roof-analyzer/
├── src/
│   ├── __init__.py
│   └── geocoding.py
├── tests/
│   ├── __init__.py
│   └── test_geocoding.py
├── requirements.txt
├── .env.example
└── README.md
``` 