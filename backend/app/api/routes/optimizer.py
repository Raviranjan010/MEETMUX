"""
Optimizer routes per docs/API.md.
"""
import logging
from typing import Optional, Dict, Any
from fastapi import APIRouter, Depends, BackgroundTasks, status
from pydantic import BaseModel
from sqlalchemy.orm import Session

from app.core.db import get_db, SessionLocal
from app.core.errors import AppError
from app.models import OptimizationRun, GateAssignment
from app.models.enums import OptimizationStatus, RunType

router = APIRouter(prefix="/optimizer", tags=["Optimizer"])
logger = logging.getLogger(__name__)


class OptimizerRunRequest(BaseModel):
    run_type: str = "MILP"
    scenario_id: Optional[str] = None
    objective_weights: Optional[Dict[str, float]] = None


def _run_optimization_task(run_type: str, scenario_id: Optional[str], weights: Optional[Dict]):
    """Background task for running optimizer."""
    db = SessionLocal()
    try:
        if run_type == "BASELINE":
            from app.services.baseline import run_baseline
            run_baseline(db, scenario_id=scenario_id)
        else:
            from app.optimizer.milp import run_milp_optimization
            run_milp_optimization(db, scenario_id=scenario_id, objective_weights=weights)
    except Exception as e:
        logger.error(f"Optimization task failed: {e}")
    finally:
        db.close()


@router.post("/run", status_code=status.HTTP_202_ACCEPTED)
def run_optimizer(
    body: OptimizerRunRequest,
    background_tasks: BackgroundTasks,
    db: Session = Depends(get_db),
):
    """POST /api/optimizer/run - start optimization."""
    # Check for already running
    running = db.query(OptimizationRun).filter(
        OptimizationRun.status == OptimizationStatus.RUNNING,
    ).first()
    if running:
        raise AppError(
            code="CONFLICT",
            message="Another optimization run is already in progress",
            status_code=409,
        )

    # For baseline, run synchronously (fast)
    if body.run_type == "BASELINE":
        from app.services.baseline import run_baseline
        result = run_baseline(db, scenario_id=body.scenario_id)
        return result

    # For MILP, create placeholder and run in background
    from app.optimizer.milp import run_milp_optimization
    result = run_milp_optimization(
        db, scenario_id=body.scenario_id, objective_weights=body.objective_weights
    )
    return result


@router.get("/{run_id}")
def get_optimization_run(
    run_id: str,
    db: Session = Depends(get_db),
):
    """GET /api/optimizer/{id} - poll optimization status."""
    run = db.query(OptimizationRun).filter(OptimizationRun.id == run_id).first()
    if not run:
        raise AppError(code="NOT_FOUND", message="Optimization run not found", status_code=404)

    assignments = []
    for ga in run.assignments:
        assignments.append({
            "id": str(ga.id),
            "flight_id": str(ga.flight_id),
            "flight_number": ga.flight.flight_number if ga.flight else None,
            "gate_id": str(ga.gate_id) if ga.gate_id else None,
            "gate_code": ga.gate.code if ga.gate else "UNASSIGNED",
            "assignment_status": ga.assignment_status.value,
            "objective_contribution": float(ga.objective_contribution) if ga.objective_contribution else None,
        })

    return {
        "id": str(run.id),
        "run_type": run.run_type.value,
        "solver_used": run.solver_used.value,
        "solver_status": run.solver_status,
        "status": run.status.value,
        "objective_value": float(run.objective_value) if run.objective_value else None,
        "solve_time_ms": run.solve_time_ms,
        "validation_passed": run.validation_passed,
        "validation_report": run.validation_report,
        "config_snapshot": run.config_snapshot,
        "assignment_count": len([a for a in assignments if a["gate_id"]]),
        "unassigned_count": len([a for a in assignments if not a["gate_id"]]),
        "assignments": assignments,
        "created_at": run.created_at.isoformat() if run.created_at else None,
    }
