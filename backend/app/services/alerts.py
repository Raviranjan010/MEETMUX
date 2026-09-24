"""
Alert generation service per docs/ALERTS.md.
FR-15: Surface operational alerts derived from real state.
"""
import logging
from typing import List, Dict, Any

from sqlalchemy.orm import Session

from app.models import Alert, Flight, Gate, Prediction, OptimizationRun
from app.models.enums import (
    AlertSeverity, AlertCategory, RiskLevel, GateStatus, 
    OptimizationStatus, RunwayStatus,
)

logger = logging.getLogger(__name__)


def generate_alerts_from_state(db: Session) -> List[Dict[str, Any]]:
    """
    Scans current state and generates real alerts.
    Resolves stale alerts that no longer apply.
    """
    new_alerts = []
    
    # 1. High risk flights
    high_risk_preds = db.query(Prediction).filter(
        Prediction.risk_level == RiskLevel.HIGH,
    ).all()
    for p in high_risk_preds:
        flight = p.flight
        existing = db.query(Alert).filter(
            Alert.flight_id == flight.id,
            Alert.category == AlertCategory.HIGH_RISK,
            Alert.resolved == False,
        ).first()
        if not existing:
            alert = Alert(
                severity=AlertSeverity.WARNING,
                category=AlertCategory.HIGH_RISK,
                flight_id=flight.id,
                message=f"Flight {flight.flight_number} classified as HIGH risk (delay: {p.predicted_delay_minutes}min)",
            )
            db.add(alert)
            new_alerts.append({
                "type": "HIGH_RISK",
                "flight": flight.flight_number,
                "delay": float(p.predicted_delay_minutes),
            })
    
    # 2. Blocked gates
    blocked_gates = db.query(Gate).filter(Gate.status == GateStatus.BLOCKED).all()
    for gate in blocked_gates:
        existing = db.query(Alert).filter(
            Alert.gate_id == gate.id,
            Alert.category == AlertCategory.CONFLICT,
            Alert.resolved == False,
            Alert.message.contains("BLOCKED"),
        ).first()
        if not existing:
            alert = Alert(
                severity=AlertSeverity.CRITICAL,
                category=AlertCategory.CONFLICT,
                gate_id=gate.id,
                message=f"Gate {gate.code} is BLOCKED - flights require reassignment",
            )
            db.add(alert)
            new_alerts.append({"type": "GATE_BLOCKED", "gate": gate.code})
    
    # 3. Failed/infeasible optimization runs
    failed_runs = db.query(OptimizationRun).filter(
        OptimizationRun.status.in_([
            OptimizationStatus.INFEASIBLE,
            OptimizationStatus.ERROR,
            OptimizationStatus.SOLVER_UNAVAILABLE,
        ]),
    ).order_by(OptimizationRun.created_at.desc()).limit(5).all()
    
    for run in failed_runs:
        existing = db.query(Alert).filter(
            Alert.category == AlertCategory.SOLVER_ISSUE,
            Alert.resolved == False,
            Alert.message.contains(str(run.id)[:8]),
        ).first()
        if not existing:
            alert = Alert(
                severity=AlertSeverity.CRITICAL if run.status == OptimizationStatus.INFEASIBLE else AlertSeverity.WARNING,
                category=AlertCategory.INFEASIBLE if run.status == OptimizationStatus.INFEASIBLE else AlertCategory.SOLVER_ISSUE,
                message=f"Optimization run {str(run.id)[:8]} status: {run.status.value}",
            )
            db.add(alert)
            new_alerts.append({"type": run.status.value, "run_id": str(run.id)[:8]})
    
    if new_alerts:
        db.commit()
    
    logger.info(f"Generated {len(new_alerts)} new alerts from state scan")
    return new_alerts


def get_alerts(
    db: Session,
    resolved: bool = None,
    severity: str = None,
) -> List[Dict[str, Any]]:
    """Returns alerts with optional filtering."""
    query = db.query(Alert).order_by(Alert.created_at.desc())
    
    if resolved is not None:
        query = query.filter(Alert.resolved == resolved)
    if severity:
        query = query.filter(Alert.severity == AlertSeverity(severity))
    
    alerts = query.limit(100).all()
    
    return [
        {
            "id": str(a.id),
            "severity": a.severity.value,
            "category": a.category.value,
            "flight_id": str(a.flight_id) if a.flight_id else None,
            "gate_id": str(a.gate_id) if a.gate_id else None,
            "message": a.message,
            "resolved": a.resolved,
            "created_at": a.created_at.isoformat() if a.created_at else None,
        }
        for a in alerts
    ]
