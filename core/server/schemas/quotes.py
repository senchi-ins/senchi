from enum import Enum
from pydantic import BaseModel, Field
from typing import Optional, Dict, Any
from datetime import datetime
from uuid import UUID, uuid4

class QuoteType(str, Enum):
    HOME = "home"
    AUTO = "auto"
    RENTER = "renter"

class Quote(BaseModel):
    quote_id: UUID = Field(default_factory=uuid4)
    quote_type: QuoteType = Field(..., min_length=1, max_length=50)
    quote_parameters: Optional[Dict[str, Any]] = Field(default_factory=dict)
