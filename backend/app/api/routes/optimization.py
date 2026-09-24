from typing import List
from fastapi import APIRouter, Depends, Query, status
from sqlalchemy.orm import Session

from app.api.dependencies import get_db
from app.services.optimization_service import OptimizationService
from app.schemas.optimization import (
    OptimizationRequest,
    OptimizationResponse,
    OptimizationRunSummary,
    GateAssignmentItem
)

router = APIRouter(prefix="/optimization", tags=["Optimization"])


@router.post("/run", response_model=OptimizationResponse, summary="Execute MILP Airport Gate Assignment Optimizer")
def run_gate_optimization(request: OptimizationRequest, db: Session = Depends(get_db)):
    return OptimizationService.run_optimization(db, request)


@router.get("/{run_id}", response_model=OptimizationRunSummary, summary="Get Optimization Run Summary by ID")
def get_run_summary(run_id: int, db: Session = Depends(get_db)):
    return OptimizationService.get_run_by_id(db, run_id)


@router.get("/{run_id}/assignments", response_model=List[GateAssignmentItem], summary="Get Gate Assignments for a Run")
def get_run_assignments(run_id: int, db: Session = Depends(get_db)):
    return OptimizationService.get_run_assignments(db, run_id)
