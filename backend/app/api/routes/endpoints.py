"""
Scenario, conflict, cascade, reoptimize, analytics, alerts, explain, config, assignment routes.
"""
import logging
from typing import Optional, Dict, Any
from fastapi import APIRouter, Depends, Query, status
from pydantic import BaseModel
from sqlalchemy.orm import Session

from app.core.db import get_db
from app.core.errors import AppError
from app.models import (
    Scenario, CascadeEvent, GateAssignment, Alert, AuditRecord,
    SystemConfig, OptimizationRun,
)
from app.models.enums import AuditAction, AssignmentStatus

logger = logging.getLogger(__name__)

# --- Conflicts ---
conflicts_router = APIRouter(prefix="/conflicts", tags=["Conflicts"])


class ConflictDetectRequest(BaseModel):
    assignment_source: str = "BASELINE"


@conflicts_router.post("/detect")
def detect_conflicts(body: ConflictDetectRequest, db: Session = Depends(get_db)):
    from app.services.conflict import detect_conflicts_from_db
    conflicts = detect_conflicts_from_db(db, assignment_source=body.assignment_source)
    return {"conflicts": conflicts, "total": len(conflicts)}


# --- Scenarios ---
scenarios_router = APIRouter(prefix="/scenarios", tags=["Scenarios"])


class ScenarioRunRequest(BaseModel):
    type: str
    target_reference: str
    params: Dict[str, Any] = {}


@scenarios_router.post("/run")
def run_scenario(body: ScenarioRunRequest, db: Session = Depends(get_db)):
    from app.services.simulation import run_scenario
    result = run_scenario(db, body.type, body.target_reference, body.params)
    return result


@scenarios_router.get("")
def get_scenarios(db: Session = Depends(get_db)):
    scenarios = db.query(Scenario).order_by(Scenario.applied_at.desc()).all()
    return {
        "items": [
            {
                "id": str(s.id),
                "type": s.type.value,
                "target_reference": s.target_reference,
                "params": s.params,
                "applied_at": s.applied_at.isoformat() if s.applied_at else None,
                "resulting_optimization_run_id": str(s.resulting_optimization_run_id) if s.resulting_optimization_run_id else None,
            }
            for s in scenarios
        ]
    }


# --- Reoptimize ---
reoptimize_router = APIRouter(tags=["Reoptimize"])


class ReoptimizeRequest(BaseModel):
    scenario_id: str


@reoptimize_router.post("/reoptimize", status_code=status.HTTP_202_ACCEPTED)
def reoptimize(body: ReoptimizeRequest, db: Session = Depends(get_db)):
    from app.services.reoptimize import reoptimize_after_scenario
    result = reoptimize_after_scenario(db, body.scenario_id)
    return result


# --- Analytics ---
analytics_router = APIRouter(prefix="/analytics", tags=["Analytics"])


@analytics_router.get("")
def get_analytics(db: Session = Depends(get_db)):
    from app.services.analytics import get_live_analytics
    return get_live_analytics(db)


@analytics_router.get("/comparison")
def get_comparison(
    optimization_run_id: str = Query(...),
    db: Session = Depends(get_db),
):
    from app.services.analytics import get_comparison_analytics
    return get_comparison_analytics(db, optimization_run_id)


# --- Alerts ---
alerts_router = APIRouter(prefix="/alerts", tags=["Alerts"])


@alerts_router.get("")
def get_alerts(
    resolved: Optional[bool] = None,
    severity: Optional[str] = None,
    db: Session = Depends(get_db),
):
    from app.services.alerts import get_alerts
    items = get_alerts(db, resolved=resolved, severity=severity)
    return {"items": items}


# --- Cascade ---
cascade_router = APIRouter(prefix="/cascade", tags=["Cascade"])


@cascade_router.get("/{scenario_id}")
def get_cascade_events(scenario_id: str, db: Session = Depends(get_db)):
    events = db.query(CascadeEvent).filter(
        CascadeEvent.scenario_id == scenario_id
    ).all()
    return {
        "items": [
            {
                "id": str(e.id),
                "root_flight_id": str(e.root_flight_id) if e.root_flight_id else None,
                "root_gate_id": str(e.root_gate_id) if e.root_gate_id else None,
                "root_runway_id": str(e.root_runway_id) if e.root_runway_id else None,
                "scenario_id": str(e.scenario_id) if e.scenario_id else None,
                "propagation_path": e.propagation_path,
                "affected_flight_ids": e.affected_flight_ids,
                "severity": e.severity.value,
                "created_at": e.created_at.isoformat() if e.created_at else None,
            }
            for e in events
        ]
    }


# --- Explain ---
explain_router = APIRouter(prefix="/explain", tags=["Explainability"])


@explain_router.get("/{gate_assignment_id}")
def explain_assignment(gate_assignment_id: str, db: Session = Depends(get_db)):
    from app.services.explain import explain_assignment as do_explain
    result = do_explain(db, gate_assignment_id)
    if "error" in result:
        raise AppError(code="NOT_FOUND", message=result["error"], status_code=404)
    return result


# --- Assignments ---
assignments_router = APIRouter(prefix="/assignments", tags=["Assignments"])


@assignments_router.post("/{assignment_id}/accept")
def accept_assignment(assignment_id: str, db: Session = Depends(get_db)):
    ga = db.query(GateAssignment).filter(GateAssignment.id == assignment_id).first()
    if not ga:
        raise AppError(code="NOT_FOUND", message="Assignment not found", status_code=404)
    
    # Check validation passed
    run = ga.optimization_run
    if run and run.validation_passed is False:
        raise AppError(
            code="VALIDATION_FAILED",
            message="Cannot accept assignment from a run that failed validation",
            status_code=400,
        )
    
    ga.assignment_status = AssignmentStatus.COMMITTED
    audit = AuditRecord(
        action=AuditAction.ASSIGNMENT_ACCEPT,
        actor="operator",
        reference_id=ga.id,
        details={"gate_id": str(ga.gate_id), "flight_id": str(ga.flight_id)},
    )
    db.add(audit)
    db.commit()
    return {"status": "accepted", "assignment_id": str(ga.id)}


@assignments_router.post("/{assignment_id}/reject")
def reject_assignment(assignment_id: str, db: Session = Depends(get_db)):
    ga = db.query(GateAssignment).filter(GateAssignment.id == assignment_id).first()
    if not ga:
        raise AppError(code="NOT_FOUND", message="Assignment not found", status_code=404)
    
    ga.assignment_status = AssignmentStatus.REJECTED
    audit = AuditRecord(
        action=AuditAction.ASSIGNMENT_REJECT,
        actor="operator",
        reference_id=ga.id,
        details={"gate_id": str(ga.gate_id), "flight_id": str(ga.flight_id)},
    )
    db.add(audit)
    db.commit()
    return {"status": "rejected", "assignment_id": str(ga.id)}


# --- Config ---
config_router = APIRouter(prefix="/config", tags=["Config"])


@config_router.get("")
def get_config(db: Session = Depends(get_db)):
    config = db.query(SystemConfig).first()
    if not config:
        return {"error": "No system config found"}
    return {
        "id": str(config.id),
        "risk_low_max_minutes": float(config.risk_low_max_minutes),
        "risk_medium_max_minutes": float(config.risk_medium_max_minutes),
        "turnaround_buffer_minutes": int(config.turnaround_buffer_minutes),
        "optimizer_timeout_seconds": int(config.optimizer_timeout_seconds),
        "optimizer_weight_delay_cost": float(config.optimizer_weight_delay_cost),
        "optimizer_weight_conflict_cost": float(config.optimizer_weight_conflict_cost),
        "optimizer_weight_reassignment_cost": float(config.optimizer_weight_reassignment_cost),
        "optimizer_weight_taxi_distance": float(config.optimizer_weight_taxi_distance),
        "optimizer_weight_remote_stand": float(config.optimizer_weight_remote_stand),
        "cascade_max_depth": int(config.cascade_max_depth),
    }


class ConfigUpdateRequest(BaseModel):
    risk_low_max_minutes: Optional[float] = None
    risk_medium_max_minutes: Optional[float] = None
    turnaround_buffer_minutes: Optional[int] = None
    optimizer_timeout_seconds: Optional[int] = None
    optimizer_weight_delay_cost: Optional[float] = None
    optimizer_weight_conflict_cost: Optional[float] = None
    optimizer_weight_reassignment_cost: Optional[float] = None
    optimizer_weight_taxi_distance: Optional[float] = None
    optimizer_weight_remote_stand: Optional[float] = None
    cascade_max_depth: Optional[int] = None


@config_router.put("")
def update_config(body: ConfigUpdateRequest, db: Session = Depends(get_db)):
    config = db.query(SystemConfig).first()
    if not config:
        raise AppError(code="NOT_FOUND", message="No system config found", status_code=404)
    
    for field, value in body.model_dump(exclude_none=True).items():
        setattr(config, field, value)
    
    db.commit()
    return get_config(db)


# --- Runways ---
runways_router = APIRouter(prefix="/runways", tags=["Runways"])


@runways_router.get("")
def get_runways(db: Session = Depends(get_db)):
    from app.models import Runway
    runways = db.query(Runway).all()
    return {
        "items": [
            {
                "id": str(r.id),
                "code": r.code,
                "status": r.status.value,
                "taxi_base_minutes": float(r.taxi_base_minutes),
            }
            for r in runways
        ]
    }
