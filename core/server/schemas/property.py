from pydantic import BaseModel


class PropertyRequest(BaseModel):
    user_id: str

class PropertyResponse(BaseModel):
    id: str
    name: str
