"""
Conflict detection engine per docs/CONFLICT_ENGINE.md.
FR-6: Detect gate conflicts via true time-interval overlap.
"""
import logging
from datetime import datetime, timedelta
from typing import List, Dict, Any, Optional, Tuple
from decimal import Decimal

from sqlalchemy.orm import Session

from app.models import Flight, Gate, GateAssignment, OptimizationRun, SystemConfig
from app.models.enums import GateStatus, AssignmentStatus, OptimizationStatus

logger = logging.getLogger(__name__)


def get_turnaround_buffer(config: Optional[SystemConfig]) -> int:
    """Returns turnaround buffer minutes from system config."""
    if config:
        return int(config.turnaround_buffer_minutes)
    return 15


def compute_occupied_interval(
    arrival: datetime,
    departure: datetime,
    buffer_minutes: int,
) -> Tuple[datetime, datetime]:
    """
    Computes the occupied interval for a flight at a gate.
    Per CONFLICT_ENGINE.md: [arrival - buffer, departure + buffer]
    Buffer is already folded into interval bounds.
    """
    buf = timedelta(minutes=buffer_minutes)
    return (arrival - buf, departure + buf)


def intervals_overlap(
    start1: datetime, end1: datetime,
    start2: datetime, end2: datetime,
) -> bool:
    """
    Two intervals [a1,b1] and [a2,b2] conflict iff a1 < b2 AND a2 < b1.
    Strict inequality: touching endpoints (b1 == a2) is NOT a conflict.
    """
    return start1 < end2 and start2 < end1


def compute_overlap_minutes(
    start1: datetime, end1: datetime,
    start2: datetime, end2: datetime,
) -> float:
    """Computes overlap duration in minutes between two intervals."""
    overlap_start = max(start1, start2)
    overlap_end = min(end1, end2)
    if overlap_start >= overlap_end:
        return 0.0
    return (overlap_end - overlap_start).total_seconds() / 60.0


def detect_conflicts_for_assignments(
    assignments: List[Dict[str, Any]],
    config: Optional[SystemConfig] = None,
    detected_against: str = "BASELINE",
) -> List[Dict[str, Any]]:
    """
    Detects all conflicts across a set of gate assignments.
    
    Each assignment dict must have: flight_id, gate_id, gate_code, gate_status,
    arrival, departure.
    
    Returns list of conflict dicts per CONFLICT_ENGINE.md output shape.
    """
    buffer = get_turnaround_buffer(config)
    
    # Group assignments by gate
    gate_assignments: Dict[str, List[Dict]] = {}
    for a in assignments:
        gid = a.get("gate_id")
        if gid is None:
            continue
        gate_assignments.setdefault(str(gid), []).append(a)
    
    conflicts = []
    
    for gate_id, gate_flights in gate_assignments.items():
        gate_code = gate_flights[0].get("gate_code", "")
        gate_status = gate_flights[0].get("gate_status", "AVAILABLE")
        
        # Check BLOCKED gate conflicts
        if gate_status == "BLOCKED":
            for gf in gate_flights:
                conflicts.append({
                    "gate_id": gate_id,
                    "gate_code": gate_code,
                    "flight_ids": [gf["flight_id"]],
                    "conflict_type": "BLOCKED_GATE",
                    "overlap_minutes": 0.0,
                    "reason": f"Flight assigned to BLOCKED gate {gate_code}",
                    "detected_against": detected_against,
                })
            continue
        
        # Check pairwise time overlaps
        n = len(gate_flights)
        for i in range(n):
            fi = gate_flights[i]
            s1, e1 = compute_occupied_interval(fi["arrival"], fi["departure"], buffer)
            for j in range(i + 1, n):
                fj = gate_flights[j]
                s2, e2 = compute_occupied_interval(fj["arrival"], fj["departure"], buffer)
                if intervals_overlap(s1, e1, s2, e2):
                    overlap = compute_overlap_minutes(s1, e1, s2, e2)
                    conflicts.append({
                        "gate_id": gate_id,
                        "gate_code": gate_code,
                        "flight_ids": [fi["flight_id"], fj["flight_id"]],
                        "conflict_type": "TIME_OVERLAP",
                        "overlap_minutes": round(overlap, 1),
                        "reason": f"Time overlap of {overlap:.1f}min at gate {gate_code}",
                        "detected_against": detected_against,
                    })
    
    return conflicts


def detect_conflicts_from_db(
    db: Session,
    assignment_source: str = "BASELINE",
    optimization_run_id: Optional[str] = None,
) -> List[Dict[str, Any]]:
    """
    Detects conflicts from stored assignments in the database.
    assignment_source: "BASELINE", "COMMITTED", or an optimization_run_id UUID.
    """
    config = db.query(SystemConfig).first()
    
    # Build query for assignments
    query = db.query(GateAssignment).join(Flight).join(Gate, GateAssignment.gate_id == Gate.id, isouter=True)
    
    if assignment_source == "BASELINE":
        # Find latest BASELINE run
        run = db.query(OptimizationRun).filter(
            OptimizationRun.run_type == "BASELINE",
            OptimizationRun.status.in_(["OPTIMAL", "FEASIBLE"]),
        ).order_by(OptimizationRun.created_at.desc()).first()
        if run:
            query = query.filter(GateAssignment.optimization_run_id == run.id)
        else:
            return []
    elif assignment_source == "COMMITTED":
        query = query.filter(GateAssignment.assignment_status == AssignmentStatus.COMMITTED)
    else:
        # Treat as optimization_run_id
        query = query.filter(GateAssignment.optimization_run_id == assignment_source)
    
    results = query.all()
    
    # Build assignment dicts
    assignments = []
    for ga in results:
        if ga.gate_id is None:
            continue
        flight = ga.flight
        gate = ga.gate
        assignments.append({
            "flight_id": str(ga.flight_id),
            "gate_id": str(ga.gate_id),
            "gate_code": gate.code if gate else "",
            "gate_status": gate.status.value if gate else "AVAILABLE",
            "arrival": flight.scheduled_arrival,
            "departure": flight.scheduled_departure,
        })
    
    return detect_conflicts_for_assignments(
        assignments, config, detected_against=assignment_source
    )
