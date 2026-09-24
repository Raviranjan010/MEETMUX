from typing import Optional
from fastapi import APIRouter, Depends, UploadFile, File, Query, status
from sqlalchemy.orm import Session

from app.api.dependencies import get_db
from app.services.flight_service import FlightService
from app.schemas.flight import (
    FlightResponse,
    FlightCreate,
    FlightListResponse,
    CSVUploadResponse
)

router = APIRouter(prefix="/flights", tags=["Flights"])


@router.get("", response_model=FlightListResponse, summary="List Flights with Filtering and Pagination")
def list_flights(
    page: int = Query(1, ge=1, description="Page number"),
    page_size: int = Query(20, ge=1, le=100, description="Items per page"),
    search: Optional[str] = Query(None, description="Search term for flight number, airline, origin, dest"),
    airline: Optional[str] = Query(None, description="Filter by airline"),
    terminal: Optional[str] = Query(None, description="Filter by terminal"),
    delay_category: Optional[str] = Query(None, description="Filter by delay category"),
    status: Optional[str] = Query(None, description="Filter by flight status"),
    db: Session = Depends(get_db)
):
    return FlightService.get_flights(
        db=db,
        page=page,
        page_size=page_size,
        search=search,
        airline=airline,
        terminal=terminal,
        delay_category=delay_category,
        status=status
    )


@router.get("/{flight_id}", response_model=FlightResponse, summary="Get Flight Details by ID")
def get_flight(flight_id: int, db: Session = Depends(get_db)):
    f = FlightService.get_flight_by_id(db, flight_id)
    return FlightResponse.model_validate(f)


@router.post("", response_model=FlightResponse, status_code=status.HTTP_201_CREATED, summary="Create a New Flight Record")
def create_flight(flight_in: FlightCreate, db: Session = Depends(get_db)):
    f = FlightService.create_flight(db, flight_in)
    return FlightResponse.model_validate(f)


@router.post("/upload", response_model=CSVUploadResponse, summary="Import Flight Data via CSV Upload")
async def upload_flight_csv(file: UploadFile = File(...), db: Session = Depends(get_db)):
    contents = await file.read()
    return FlightService.import_csv(db, contents)
