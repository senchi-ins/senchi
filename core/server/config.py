import os
from typing import List
from pydantic_settings import BaseSettings
from pydantic import AnyHttpUrl


class Settings(BaseSettings):
    """
    Configuration for the API.
    """
    PROJECT_NAME: str = "Senchi API"

    # API Version. This directly impacts the file path
    # used when looking for endpoints. E.g. v1 is api/v1/endpoints/
    VERSION: str = "v1"
    DESCRIPTION: str = "FastAPI server to handle quoting and claims engines"
    
    # Prefixes any url paths. E.g. /api/v1/quote/
    API_PREFIX: str = "/api/v1"
    
    # CORS Configuration
    ALLOWED_ORIGINS: List[AnyHttpUrl] = [
        AnyHttpUrl(os.environ.get("ALLOWED_ORIGINS", "http://localhost:3000")),
    ]
    ALLOWED_CREDENTIALS: bool = os.environ.get("ALLOWED_CREDENTIALS", "true") == "true"
    ALLOWED_HEADERS: List[str] = ["*"]
    ALLOWED_METHODS: List[str] = ["*"]
    
    # API Keys
    openai_api_key: str = ""
    google_sv_api_key: str = ""
    trippo_api_key: str = ""
    api_secret_key: str = ""
    
    # Security
    SECRET_KEY: str = os.environ.get("API_SECRET_KEY", "")
    ACCESS_TOKEN_EXPIRE_MINUTES: int = 60 * 24 * 8  # 8 days
    
    # TODO: Move this to a separate file
    DATABASE_URL: str = os.environ.get("DATABASE_URL", "")
    
    class Config:
        env_file = ".env"
        env_file_encoding = "utf-8"

settings = Settings() 