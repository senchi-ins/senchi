from typing import Optional, List

from pydantic import BaseModel


class TokenRequest(BaseModel):
    device_serial: str
    push_token: Optional[str] = None
    email: Optional[str] = None
    full_name: Optional[str] = None

class LoginRequest(BaseModel):
    email: str
    password: str

class UserInfoResponse(BaseModel):
    user_id: str
    location_id: Optional[str] = None
    device_serial: Optional[str] = None
    full_name: Optional[str] = None
    iat: Optional[float] = None
    exp: float
    created_at: Optional[str] = None

class TokenResponse(BaseModel):
    jwt_token: str
    expires_at: str
    user_info: UserInfoResponse