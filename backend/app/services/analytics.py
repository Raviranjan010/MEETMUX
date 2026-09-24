"""
Analytics service per docs/ANALYTICS.md.
FR-10: Compute baseline vs optimized comparison metrics from real data.
"""
import logging
from typing import Dict, Any, Optional, List

from sqlalchemy.orm import Session
from sqlalchemy import func

from app.models import (
    Flight, Gate, GateAssignment, OptimizationRun, Prediction, SystemConfig, Alert,
)
from app.models.enums import (
    RunType, OptimizationStatus, AssignmentStatus, GateType, GateStatus,
    RiskLevel, AlertSeverity,
)
from app.services.conflict import detect_conflicts_from_db

logger = logging.getLogger(__name__)


def get_live_analytics(db: Session) -> Dict[str, Any]:
    """
    Computes live analytics from current committed/latest state.
    GET /api/analytics response.
    """
    total_flights = db.query(Flight).count()
    
    # Risk distribution from latest predictions
    preds = db.query(Prediction.risk_level, func.count(Prediction.id)).group_by(
        Prediction.risk_level
    ).all()
    risk_dist = {"LOW": 0, "MEDIUM": 0, "HIGH": 0}
    for level, count in preds:
        risk_dist[level.value if hasattr(level, 'value') else str(level)] = count
    
    # Average predicted delay
    avg_delay = db.query(func.avg(Prediction.predicted_delay_minutes)).scalar()
    
    # Gate utilization
    total_gates = db.query(Gate).count()
    occupied_gates = db.query(Gate).filter(Gate.status == GateStatus.OCCUPIED).count()
    
    # Active conflicts from latest run
    active_conflicts = 0
    latest_run = db.query(OptimizationRun).filter(
        OptimizationRun.status.in_([OptimizationStatus.OPTIMAL, OptimizationStatus.FEASIBLE]),
    ).order_by(OptimizationRun.created_at.desc()).first()
    
    if latest_run:
        conflicts = detect_conflicts_from_db(db, assignment_source=str(latest_run.id))
        active_conflicts = len(conflicts)
    
    # Active alerts
    active_alerts = db.query(Alert).filter(Alert.resolved == False).count()
    
    return {
        "total_flights": total_flights,
        "fleet_utilization": round(occupied_gates / max(total_gates, 1) * 100, 1),
        "avg_predicted_delay": round(float(avg_delay or 0), 2),
        "risk_distribution": risk_dist,
        "active_conflicts": active_conflicts,
        "active_alerts": active_alerts,
        "total_gates": total_gates,
        "occupied_gates": occupied_gates,
    }


def get_comparison_analytics(
    db: Session,
    optimization_run_id: str,
) -> Dict[str, Any]:
    """
    Computes baseline vs optimized comparison from two stored assignment sets.
    GET /api/analytics/comparison response.
    """
    # Get the optimized run
    opt_run = db.query(OptimizationRun).filter(
        OptimizationRun.id == optimization_run_id,
    ).first()
    
    if not opt_run:
        return {"error": "Optimization run not found"}
    
    # Get the latest baseline run
    baseline_run = db.query(OptimizationRun).filter(
        OptimizationRun.run_type == RunType.BASELINE,
        OptimizationRun.status.in_([OptimizationStatus.OPTIMAL, OptimizationStatus.FEASIBLE]),
    ).order_by(OptimizationRun.created_at.desc()).first()
    
    if not baseline_run:
        return {"error": "No baseline run found for comparison"}
    
    # Compute metrics for baseline
    baseline_metrics = _compute_run_metrics(db, baseline_run)
    optimized_metrics = _compute_run_metrics(db, opt_run)
    
    # Compute deltas
    deltas = {}
    for key in baseline_metrics:
        if isinstance(baseline_metrics[key], (int, float)) and isinstance(optimized_metrics.get(key), (int, float)):
            deltas[key] = round(optimized_metrics[key] - baseline_metrics[key], 3)
    
    return {
        "baseline_run_id": str(baseline_run.id),
        "optimized_run_id": str(opt_run.id),
        "baseline": baseline_metrics,
        "optimized": optimized_metrics,
        "deltas": deltas,
    }


def _compute_run_metrics(db: Session, run: OptimizationRun) -> Dict[str, Any]:
    """Compute metrics for a single optimization run from its assignments."""
    assignments = db.query(GateAssignment).filter(
        GateAssignment.optimization_run_id == run.id,
    ).all()
    
    total = len(assignments)
    assigned = sum(1 for a in assignments if a.gate_id is not None)
    unassigned = total - assigned
    
    # Conflict count
    conflicts = detect_conflicts_from_db(db, assignment_source=str(run.id))
    conflict_count = len(conflicts)
    
    # Remote stand count and taxi distance
    remote_count = 0
    total_taxi_distance = 0.0
    gate_changes = 0
    
    for a in assignments:
        if a.gate:
            total_taxi_distance += float(a.gate.taxi_distance_meters or 0)
            if a.gate.gate_type == GateType.REMOTE:
                remote_count += 1
    
    # Objective value
    objective = float(run.objective_value or 0)
    
    return {
        "total_flights": total,
        "assigned_flights": assigned,
        "unassigned_flights": unassigned,
        "conflict_count": conflict_count,
        "remote_stand_count": remote_count,
        "total_taxi_distance": round(total_taxi_distance, 1),
        "avg_taxi_distance": round(total_taxi_distance / max(assigned, 1), 1),
        "objective_value": objective,
        "solve_time_ms": run.solve_time_ms or 0,
        "solver_used": run.solver_used.value if run.solver_used else "NONE",
        "validation_passed": run.validation_passed,
    }
