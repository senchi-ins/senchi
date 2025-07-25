from typing import Optional

from pydantic import BaseModel


class TokenRequest(BaseModel):
    device_serial: str
    push_token: Optional[str] = None
    email: Optional[str] = None
    full_name: Optional[str] = None

class TokenResponse(BaseModel):
    jwt_token: str
    expires_at: str
    location_id: Optional[str] = None

class LoginRequest(BaseModel):
    email: str
    password: str