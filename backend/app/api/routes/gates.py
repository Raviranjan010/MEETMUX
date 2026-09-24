from typing import Optional
from fastapi import APIRouter, Depends, Query, status
from sqlalchemy.orm import Session

from app.api.dependencies import get_db
from app.services.gate_service import GateService
from app.schemas.gate import GateResponse, GateCreate, GateListResponse

router = APIRouter(prefix="/gates", tags=["Gates"])


@router.get("", response_model=GateListResponse, summary="List All Airport Gates")
def list_gates(
    terminal: Optional[str] = Query(None, description="Filter by terminal (e.g. T1, T2, T3)"),
    is_available: Optional[bool] = Query(None, description="Filter by availability status"),
    db: Session = Depends(get_db)
):
    return GateService.get_gates(db=db, terminal=terminal, is_available=is_available)


@router.get("/{gate_id}", response_model=GateResponse, summary="Get Gate by ID")
def get_gate(gate_id: int, db: Session = Depends(get_db)):
    return GateService.get_gate_by_id(db, gate_id)


@router.post("", response_model=GateResponse, status_code=status.HTTP_201_CREATED, summary="Create a New Gate")
def create_gate(gate_in: GateCreate, db: Session = Depends(get_db)):
    return GateService.create_gate(db, gate_in)
