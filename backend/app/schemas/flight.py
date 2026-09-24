from datetime import datetime
from typing import Optional, List
from pydantic import BaseModel, ConfigDict


class FlightBase(BaseModel):
    flight_number: str
    airline: str
    aircraft_type: str
    origin: str
    destination: str
    terminal: str
    scheduled_arrival: datetime
    scheduled_departure: datetime
    estimated_arrival: Optional[datetime] = None
    estimated_departure: Optional[datetime] = None
    actual_arrival: Optional[datetime] = None
    actual_departure: Optional[datetime] = None
    runway: Optional[str] = "RWY-09L"
    taxi_in_minutes: Optional[float] = 12.0
    taxi_out_minutes: Optional[float] = 15.0
    turnaround_minutes: Optional[float] = 45.0
    status: Optional[str] = "Scheduled"


class FlightCreate(FlightBase):
    pass


class FlightUpdate(BaseModel):
    flight_number: Optional[str] = None
    airline: Optional[str] = None
    aircraft_type: Optional[str] = None
    origin: Optional[str] = None
    destination: Optional[str] = None
    terminal: Optional[str] = None
    scheduled_arrival: Optional[datetime] = None
    scheduled_departure: Optional[datetime] = None
    estimated_arrival: Optional[datetime] = None
    estimated_departure: Optional[datetime] = None
    actual_arrival: Optional[datetime] = None
    actual_departure: Optional[datetime] = None
    runway: Optional[str] = None
    taxi_in_minutes: Optional[float] = None
    taxi_out_minutes: Optional[float] = None
    turnaround_minutes: Optional[float] = None
    status: Optional[str] = None


class FlightResponse(FlightBase):
    id: int
    created_at: datetime
    updated_at: datetime
    
    # Optional nested prediction & gate details
    latest_predicted_delay: Optional[float] = None
    latest_delay_category: Optional[str] = None
    assigned_gate: Optional[str] = None

    model_config = ConfigDict(from_attributes=True)


class FlightListResponse(BaseModel):
    items: List[FlightResponse]
    total: int
    page: int
    page_size: int
    total_pages: int


class CSVUploadResponse(BaseModel):
    total_rows: int
    successful_rows: int
    failed_rows: int
    errors: List[str] = []
