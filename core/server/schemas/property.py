from pydantic import BaseModel
from typing import Optional


class PropertyRequest(BaseModel):
    user_id: str
    property_name: Optional[str] = None

class PropertyResponse(BaseModel):
    id: str
    name: str
    address: Optional[str] = None
    property_type: Optional[str] = None
    description: Optional[str] = None
