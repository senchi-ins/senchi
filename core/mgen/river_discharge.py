import openmeteo_requests
import requests_cache
from retry_requests import retry
import pandas as pd
from typing import Dict, Any, Tuple
import plotly.graph_objects as go
from dotenv import load_dotenv
import os
from pathlib import Path

# Load environment variables from .env file
load_dotenv()

# Setup the Open-Meteo API client with cache and retry on error
CACHE_DIR = Path(__file__).parent / '.cache'
cache_session = requests_cache.CachedSession(str(CACHE_DIR), expire_after=3600)  # Cache for 1 hour
retry_session = retry(cache_session, retries=5, backoff_factor=0.2)
openmeteo = openmeteo_requests.Client(session=retry_session)

def get_river_discharge_data(latitude: float, longitude: float) -> Tuple[pd.DataFrame, Dict[str, Any]]:
    """Get river discharge data from Open-Meteo API.
    
    Args:
        latitude (float): Geographical WGS84 latitude
        longitude (float): Geographical WGS84 longitude
    
    Returns:
        Tuple[pd.DataFrame, Dict[str, Any]]: 
            - DataFrame with discharge data
            - Dictionary with metadata (coordinates, elevation, timezone)
        
    Raises:
        ValueError: If coordinates are invalid
        requests.exceptions.RequestException: If API request fails
    """
    # Validate input parameters
    if not (-90 <= latitude <= 90):
        raise ValueError("Latitude must be between -90 and 90 degrees")
    if not (-180 <= longitude <= 180):
        raise ValueError("Longitude must be between -180 and 180 degrees")

    # Get API key from environment
    api_key = os.getenv('OPEN_METEO_API')
    
    # API endpoint and parameters
    url = "https://flood-api.open-meteo.com/v1/flood"
    params = {
        "latitude": latitude,
        "longitude": longitude,
        "forecast_days": 14,  # 14 days forecast
        "past_days": 30,     # 30 days historical
        "daily": [
            "river_discharge",
            "river_discharge_mean",
            "river_discharge_median",
            "river_discharge_max",
            "river_discharge_min",
            "river_discharge_p25",
            "river_discharge_p75"
        ]
    }
    
    # Add API key if provided
    if api_key:
        params["apikey"] = api_key

    # Make API request with retry and caching
    responses = openmeteo.weather_api(url, params=params)
    response = responses[0]  # Process first location

    # Extract metadata
    metadata = {
        "latitude": response.Latitude(),
        "longitude": response.Longitude(),
        "elevation": response.Elevation(),
        "timezone": response.Timezone(),
        "timezone_abbreviation": response.TimezoneAbbreviation(),
        "utc_offset_seconds": response.UtcOffsetSeconds()
    }

    # Process daily data
    daily = response.Daily()
    
    # Create date range
    daily_data = {
        "date": pd.date_range(
            start=pd.to_datetime(daily.Time(), unit="s", utc=True),
            end=pd.to_datetime(daily.TimeEnd(), unit="s", utc=True),
            freq=pd.Timedelta(seconds=daily.Interval()),
            inclusive="left"
        )
    }

    # Extract all variables
    var_names = [
        "river_discharge",
        "river_discharge_mean",
        "river_discharge_median",
        "river_discharge_max",
        "river_discharge_min",
        "river_discharge_p25",
        "river_discharge_p75"
    ]
    
    for i, var_name in enumerate(var_names):
        daily_data[var_name] = daily.Variables(i).ValuesAsNumpy()

    return pd.DataFrame(data=daily_data), metadata

def create_discharge_plot(latitude: float, longitude: float) -> go.Figure:
    """Create an interactive plotly plot of river discharge data.
    
    Args:
        latitude (float): Geographical WGS84 latitude
        longitude (float): Geographical WGS84 longitude
    
    Returns:
        go.Figure: Interactive plotly figure showing river discharge data
        
    Raises:
        ValueError: If coordinates are invalid or API key is missing
        requests.exceptions.RequestException: If API request fails
    """
    # Get the data
    df, metadata = get_river_discharge_data(latitude, longitude)
    
    # Create figure with secondary y-axis
    fig = go.Figure()
    
    # Add main discharge line (blue with dots)
    fig.add_trace(
        go.Scatter(
            x=df['date'],
            y=df['river_discharge'],
            name='River discharge (actual and forcast)',
            mode='lines+markers',
            line=dict(color='rgb(33, 150, 243)', width=2),
            marker=dict(
                size=6,
                color='rgb(33, 150, 243)',
                symbol='circle'
            ),
            hovertemplate="<b>%{x|%a %-d %b %Y}</b><br>" +
                         "river_discharge: %{y:.2f} m³/s<extra></extra>"
        )
    )
    
    # Add median line (purple with dots)
    fig.add_trace(
        go.Scatter(
            x=df['date'],
            y=df['river_discharge_median'],
            name='Historical river discharge median',
            mode='lines+markers',
            line=dict(color='rgb(156, 39, 176)', width=2),
            marker=dict(
                size=6,
                color='rgb(156, 39, 176)',
                symbol='diamond'
            ),
            hovertemplate="<b>%{x|%a %-d %b %Y}</b><br>" +
                         "river_discharge_median: %{y:.2f} m³/s<extra></extra>"
        )
    )

    # Update layout
    fig.update_layout(
        # Title
        title=dict(
            text=f"{metadata['latitude']:.2f}°N {metadata['longitude']:.2f}°E",
            font=dict(size=16),
            y=0.98,
            x=0.5,
            xanchor='center',
            yanchor='top'
        ),
        # Plot area
        plot_bgcolor='white',
        paper_bgcolor='white',
        margin=dict(t=60, b=50),
        
        # X-axis
        xaxis=dict(
            showgrid=True,
            gridwidth=1,
            gridcolor='rgba(0, 0, 0, 0.1)',
            zeroline=False,
            tickformat='%d %b',
            tickmode='auto',
            dtick='M1',
            tickfont=dict(size=10),
            showline=True,
            linewidth=1,
            linecolor='rgba(0, 0, 0, 0.2)'
        ),
        
        # Y-axis
        yaxis=dict(
            title='m³/s',
            showgrid=True,
            gridwidth=1,
            gridcolor='rgba(0, 0, 0, 0.1)',
            zeroline=False,
            tickfont=dict(size=10),
            showline=True,
            linewidth=1,
            linecolor='rgba(0, 0, 0, 0.2)',
            rangemode='nonnegative'  # Prevent negative values
        ),
        
        # Legend
        showlegend=True,
        legend=dict(
            orientation="h",
            yanchor="bottom",
            y=1.02,
            xanchor="right",
            x=1,
            font=dict(size=12)
        ),
        
        # Hover
        hovermode='x unified',
        hoverlabel=dict(
            bgcolor="white",
            font_size=12,
            font_family="Arial"
        )
    )

    # Add today line
    today = pd.Timestamp.now(tz='UTC').normalize()  # Get today's date at midnight UTC
    fig.add_vline(
        x=today,
        line=dict(
            color='red',
            width=1,
            dash='dash'
        )
    )

    return fig

def get_discharge_graph(latitude: float, longitude: float) -> go.Figure:
    """Main function to get an interactive river discharge graph for given coordinates.
    
    Args:
        latitude (float): Geographical WGS84 latitude
        longitude (float): Geographical WGS84 longitude
    
    Returns:
        go.Figure: Interactive plotly figure showing river discharge data
        
    Example:
        >>> fig = get_discharge_graph(latitude=59.9139, longitude=10.7522)
        >>> fig.show()  # Display the interactive plot in browser
    """
    return create_discharge_plot(latitude, longitude)
