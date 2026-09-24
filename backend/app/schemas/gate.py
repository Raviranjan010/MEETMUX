from datetime import datetime
from typing import Optional, List
from pydantic import BaseModel, ConfigDict


class GateBase(BaseModel):
    gate_number: str
    terminal: str
    gate_type: Optional[str] = "Contact"
    supported_aircraft_types: str
    is_international: Optional[bool] = False
    is_available: Optional[bool] = True
    latitude: Optional[float] = None
    longitude: Optional[float] = None


class GateCreate(GateBase):
    pass


class GateResponse(GateBase):
    id: int
    created_at: datetime
    current_occupancy: Optional[str] = None

    model_config = ConfigDict(from_attributes=True)


class GateListResponse(BaseModel):
    items: List[GateResponse]
    total: int
