from enum import Enum
from pydantic import BaseModel
from typing import Optional


class PropertyRequest(BaseModel):
    user_id: str
    property_name: Optional[str] = None

class PropertyScores(BaseModel):
    overall: Optional[float] = None
    internal: Optional[float] = None
    external: Optional[float] = None

class PropertyDevices(BaseModel):
    connected: Optional[int] = None
    total: Optional[int] = None

class AlertSeverity(Enum):
    LOW = "low"
    MEDIUM = "medium"
    HIGH = "high"

class PropertyAlerts(BaseModel):
    alert_type: Optional[str] = None
    message: Optional[str] = None
    severity: Optional[AlertSeverity] = None

class PropertyResponse(BaseModel):
    id: str
    name: str
    address: Optional[str] = None
    property_type: Optional[str] = None
    description: Optional[str] = None
    scores: Optional[PropertyScores] = None
    devices: Optional[PropertyDevices] = None
    total_savings: Optional[float] = None
    alerts: Optional[PropertyAlerts] = None

class AddManagerPhoneNumberRequest(BaseModel):
    user_id: str
    property_id: str
    phone_number: str
    role: Optional[str] = 'Manager'

class AddManagerPhoneNumberResponse(BaseModel):
    success: bool
    response: str
