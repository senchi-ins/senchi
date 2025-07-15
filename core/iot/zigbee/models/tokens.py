
import logging
from typing import Optional, Dict, Any

from pydantic import BaseModel

logger = logging.getLogger(__name__)


class TokenRequest(BaseModel):
    device_serial: str
    push_token: Optional[str] = None

class TokenResponse(BaseModel):
    jwt_token: str
    expires_at: str
    location_id: str

# TODO: Update default to medium once other sensors are added
class NotificationPayload(BaseModel):
    title: str
    body: str
    data: Dict[str, Any]
    priority: str = "high" # Starting with leaks, later we can add other priorities