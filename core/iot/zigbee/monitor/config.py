import os
from typing import List

from pydantic_settings import BaseSettings

class Settings(BaseSettings):
    """
    Configuration for the Zigbee2MQTT API.
    """
    PROJECT_NAME: str = "Senchi Zigbee API"

    # API Version. This directly impacts the file path
    # used when looking for endpoints. E.g. v1 is api/v1/endpoints/
    VERSION: str = "v1"
    DESCRIPTION: str = "FastAPI server to handle Zigbee2MQTT API."
    
    # Prefixes any url paths. E.g. /api/zigbee/v1/...
    API_PREFIX: str = "/api/zigbee/v1"
    
    # CORS Configuration
    ALLOWED_ORIGINS: List[str] = [
        "http://localhost:3000", 
        "https://localhost:3000", 
        "http://localhost:8000", 
        "https://localhost:8000",
        "https://api.senchi.ca",
        "http://api.senchi.ca",
        "https://www.senchi.ca",
        "http://www.senchi.ca",
        "http://localhost:5500"
    ]
    ALLOWED_CREDENTIALS: bool = True
    ALLOWED_HEADERS: List[str] = ["*"]
    ALLOWED_METHODS: List[str] = ["*"]
    
    # Security
    SECRET_KEY: str = os.environ.get("API_SECRET_KEY", "")
    ACCESS_TOKEN_EXPIRE_MINUTES: int = 60 * 24 * 8  # 8 days
    
    # Central API Configuration
    CENTRAL_API_BASE: str = os.environ.get("CENTRAL_API_BASE", "https://api.senchi.ca")
        
    ZIGBEE2MQTT_DEVICE: str = os.environ.get("ZIGBEE2MQTT_DEVICE", "")
    ZIGBEE_CHANNEL: int = int(os.environ.get("ZIGBEE_CHANNEL", 11))

    # MQTT Configuration
    MQTT_BROKER: str = os.environ.get("MQTT_BROKER", "localhost")
    MQTT_PORT: int = int(os.environ.get("MQTT_PORT", 1883))
    MQTT_USERNAME: str = os.environ.get("MQTT_USERNAME", "")
    MQTT_PASSWORD: str = os.environ.get("MQTT_PASSWORD", "")
    EXTERNAL_MQTT: bool = os.environ.get("EXTERNAL_MQTT_BROKER", "true") == "true"

    
    class Config:
        env_file = ".env"
        env_file_encoding = "utf-8"

settings = Settings()