import os
from typing import List
from pydantic_settings import BaseSettings
from pydantic import AnyHttpUrl
from dotenv import load_dotenv

load_dotenv()


class Settings(BaseSettings):
    """
    Configuration for the API.
    """
    PROJECT_NAME: str = "Senchi API"

    # API Version. This directly impacts the file path
    # used when looking for endpoints. E.g. v1 is api/v1/endpoints/
    VERSION: str = "v1"
    DESCRIPTION: str = "FastAPI server to handle quoting and claims engines."
    
    # Prefixes any url paths. E.g. /api/v1/quote/
    API_PREFIX: str = "/api/v1"
    
    # CORS Configuration
    ALLOWED_ORIGINS: List[str] = [
        "http://localhost:3000", 
        "https://localhost:3000", 
        "http://localhost:8000", 
        "https://localhost:8000",
        "https://api.senchi.ca",
        "http://api.senchi.ca",
        "https://www.senchi.ca",
        "http://www.senchi.ca"
    ]
    ALLOWED_CREDENTIALS: bool = True
    ALLOWED_HEADERS: List[str] = ["*"]
    ALLOWED_METHODS: List[str] = ["*"]
    
    # Security
    SECRET_KEY: str = os.environ.get("API_SECRET_KEY", "")
    ACCESS_TOKEN_EXPIRE_MINUTES: int = 60 * 24 * 8  # 8 days
    
    # TODO: Move this to a separate file
    DATABASE_URL: str = os.environ.get("DATABASE_URL", "")

    HIGHSIGHT_API_KEY: str = os.environ.get("HIGHSIGHT_API_KEY", "")
    GOOGLE_SV_API_KEY: str = os.environ.get("GOOGLE_SV_API_KEY", "")
    GOOGLE_STREETVIEW_SECRET: str = os.environ.get("GOOGLE_STREETVIEW_SECRET", "")
    GOOGLE_MAPS_API_KEY: str = os.environ.get("GOOGLE_MAPS_API_KEY", "")
    TRIPPO_API_KEY: str = os.environ.get("TRIPPO_API_KEY", "")
    OPENAI_API_KEY: str = os.environ.get("OPENAI_API_KEY", "")
    AWS_ACCESS_KEY_ID: str = os.environ.get("AWS_ACCESS_KEY_ID", "")
    AWS_SECRET_ACCESS_KEY: str = os.environ.get("AWS_SECRET_ACCESS_KEY", "")
    AWS_REGION: str = os.environ.get("AWS_REGION", "")
    AWS_S3_SIGNATURE_VERSION: str = os.environ.get("AWS_S3_SIGNATURE_VERSION", "s3v4")
    AWS_S3_REGION_NAME: str = os.environ.get("AWS_S3_REGION_NAME", 'us-east-2')
    
    class Config:
        env_file = ".env"
        env_file_encoding = "utf-8"

settings = Settings()
