from dataclasses import Field
from typing import Optional, Dict, List, Any
from datetime import datetime
from enum import Enum

from pydantic import BaseModel

# Currently supported device types
class DeviceType(str, Enum):
    LEAK_SENSOR = "leak_sensor"
    SHUTOFF_VALVE = "shutoff_valve"

class NotificationResponse(BaseModel):
    device_id: str
    event: str
    timestamp: datetime
    battery_low: bool
    link_quality: int

class LeakSensorResponse(NotificationResponse):
    water_leak: bool

class DeviceType(str, Enum):
    COORDINATOR = "Coordinator"
    END_DEVICE = "EndDevice"
    ROUTER = "Router"

class InterviewState(str, Enum):
    SUCCESSFUL = "SUCCESSFUL"
    FAILED = "FAILED"
    IN_PROGRESS = "IN_PROGRESS"

class PowerSource(str, Enum):
    BATTERY = "Battery"
    MAINS = "Mains"
    UNKNOWN = "Unknown"

class DeviceDefinition(BaseModel):
    description: Optional[str] = None
    model: Optional[str] = None
    vendor: Optional[str] = None
    supports_ota: Optional[bool] = None
    exposes: Optional[List[Dict[str, Any]]] = None
    options: Optional[List[Dict[str, Any]]] = None

class DeviceEndpoint(BaseModel):
    bindings: List[Any]
    clusters: Dict[str, List[str]]
    configured_reportings: List[Any]
    scenes: List[Any]

class Device(BaseModel):
    ieee_address: str
    name: str = ""
    battery: Optional[int] = None
    last_seen: Optional[datetime] = None
    status: Optional[Any] = None
    
    # Extended fields from Zigbee data
    friendly_name: Optional[str] = None
    network_address: Optional[int] = None
    type: Optional[DeviceType] = None
    manufacturer: Optional[str] = None
    model_id: Optional[str] = None
    power_source: Optional[PowerSource] = None
    software_build_id: Optional[str] = None
    date_code: Optional[str] = None
    
    # Interview and status
    interview_completed: Optional[bool] = None
    interview_state: Optional[InterviewState] = None
    interviewing: Optional[bool] = None
    supported: Optional[bool] = None
    disabled: Optional[bool] = None
    
    # Device definition and endpoints
    definition: Optional[DeviceDefinition] = None
    endpoints: Optional[Dict[str, DeviceEndpoint]] = None
    
    # Additional sensor data (commonly available)
    voltage: Optional[int] = None  # Battery voltage in mV
    device_temperature: Optional[float] = None  # Device temperature in °C
    battery_low: Optional[bool] = None
    linkquality: Optional[int] = None  # Link quality (0-255)
    power_outage_count: Optional[int] = None
    trigger_count: Optional[int] = None
    
    # Device-specific properties (will vary by device type)
    water_leak: Optional[bool] = None  # For water leak sensors
    # Add more device-specific fields as needed
    
    class Config:
        # Allow extra fields for device-specific properties
        extra = "allow"
        # Use enum values in serialization
        use_enum_values = True

class LandlordNotification(BaseModel):
    target_id: str
    notification_type: str
    priority: str
    message: str
    sent_at: datetime
    sent_status: str


# TODO: Refine, integrate
class NotificationConfig(BaseModel):
    pushover_token: Optional[str] = None
    pushover_user: Optional[str] = None
    sms_email: Optional[str] = None
    email_username: Optional[str] = None
    email_password: Optional[str] = None
    enabled: bool = True

# Exports for server.py, add new notification types here
# This will automatically update the database columns
NOTIFICATION_TYPES = [
    NotificationResponse,
    LeakSensorResponse,
]