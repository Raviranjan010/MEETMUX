"""
Gate routes per docs/API.md.
"""
import logging
from typing import Optional
from fastapi import APIRouter, Depends, Query
from sqlalchemy.orm import Session, joinedload

from app.core.db import get_db
from app.core.errors import AppError
from app.models import Gate, GateAssignment, Flight
from app.models.enums import GateStatus, GateType

router = APIRouter(prefix="/gates", tags=["Gates"])
logger = logging.getLogger(__name__)


@router.get("")
def get_gates(
    status_filter: Optional[str] = Query(None, alias="status"),
    terminal: Optional[str] = None,
    gate_type: Optional[str] = None,
    db: Session = Depends(get_db),
):
    """GET /api/gates with filtering."""
    query = db.query(Gate).options(joinedload(Gate.terminal)).order_by(Gate.code.asc())

    if status_filter:
        query = query.filter(Gate.status == GateStatus(status_filter))
    if gate_type:
        query = query.filter(Gate.gate_type == GateType(gate_type))
    if terminal:
        from app.models import Terminal
        query = query.join(Terminal).filter(Terminal.code == terminal)

    gates = query.all()

    items = []
    for g in gates:
        # Get current/next flight at this gate
        current_assignment = db.query(GateAssignment).filter(
            GateAssignment.gate_id == g.id,
            GateAssignment.gate_id.isnot(None),
        ).order_by(GateAssignment.created_at.desc()).first()

        items.append({
            "id": str(g.id),
            "code": g.code,
            "terminal_code": g.terminal.code if g.terminal else None,
            "gate_type": g.gate_type.value,
            "max_aircraft_size": g.max_aircraft_size.value,
            "eligible_route_types": g.eligible_route_types.value,
            "status": g.status.value,
            "taxi_distance_meters": float(g.taxi_distance_meters),
            "current_flight": current_assignment.flight.flight_number if current_assignment and current_assignment.flight else None,
        })

    return {"items": items, "total": len(items)}


@router.get("/{gate_id}")
def get_gate_detail(
    gate_id: str,
    db: Session = Depends(get_db),
):
    """GET /api/gates/{id}."""
    gate = db.query(Gate).options(joinedload(Gate.terminal)).filter(Gate.id == gate_id).first()
    if not gate:
        raise AppError(code="NOT_FOUND", message="Gate not found", status_code=404)

    # Get all assignments at this gate
    assignments = db.query(GateAssignment).filter(
        GateAssignment.gate_id == gate.id,
    ).order_by(GateAssignment.created_at.desc()).limit(20).all()

    flight_list = []
    for a in assignments:
        if a.flight:
            flight_list.append({
                "flight_id": str(a.flight_id),
                "flight_number": a.flight.flight_number,
                "arrival": a.flight.scheduled_arrival.isoformat() if a.flight.scheduled_arrival else None,
                "departure": a.flight.scheduled_departure.isoformat() if a.flight.scheduled_departure else None,
                "assignment_status": a.assignment_status.value,
            })

    return {
        "id": str(gate.id),
        "code": gate.code,
        "terminal_code": gate.terminal.code if gate.terminal else None,
        "gate_type": gate.gate_type.value,
        "max_aircraft_size": gate.max_aircraft_size.value,
        "eligible_route_types": gate.eligible_route_types.value,
        "status": gate.status.value,
        "taxi_distance_meters": float(gate.taxi_distance_meters),
        "flights": flight_list,
    }
