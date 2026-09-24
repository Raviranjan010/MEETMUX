"""
Cascade delay propagation engine per docs/CASCADE_ENGINE.md.
FR-13: Detect cascade delay propagation via actual flight/gate dependency chains.
"""
import logging
from typing import List, Dict, Any, Optional, Set
from collections import deque

from sqlalchemy.orm import Session

from app.models import (
    Flight, Gate, Runway, GateAssignment, OptimizationRun, SystemConfig,
    CascadeEvent, Scenario,
)
from app.models.enums import (
    GateStatus, RunwayStatus, RiskLevel, OptimizationStatus,
    AssignmentStatus,
)
from app.services.conflict import (
    compute_occupied_interval, intervals_overlap, get_turnaround_buffer,
)

logger = logging.getLogger(__name__)


def _get_current_gate_assignment_map(db: Session) -> Dict[str, str]:
    """Returns flight_id -> gate_id map for latest committed/baseline assignments."""
    latest_run = db.query(OptimizationRun).filter(
        OptimizationRun.status.in_([OptimizationStatus.OPTIMAL, OptimizationStatus.FEASIBLE]),
    ).order_by(OptimizationRun.created_at.desc()).first()
    
    if not latest_run:
        return {}
    
    result = {}
    for ga in latest_run.assignments:
        if ga.gate_id:
            result[str(ga.flight_id)] = str(ga.gate_id)
    return result


def analyze_cascade(
    db: Session,
    root_flight_id: Optional[str] = None,
    root_gate_id: Optional[str] = None,
    root_runway_id: Optional[str] = None,
    scenario_id: Optional[str] = None,
) -> Dict[str, Any]:
    """
    BFS cascade analysis per CASCADE_ENGINE.md algorithm.
    
    1. Start from root event (delay, closure, conflict)
    2. Traverse dependency edges up to cascade_max_depth
    3. Track propagation path and affected entities
    """
    config = db.query(SystemConfig).first()
    max_depth = int(config.cascade_max_depth) if config else 5
    buffer = get_turnaround_buffer(config)
    
    assignment_map = _get_current_gate_assignment_map(db)
    
    # Build gate -> flights lookup
    gate_flights: Dict[str, List[Flight]] = {}
    all_flights = db.query(Flight).order_by(Flight.scheduled_arrival.asc()).all()
    for f in all_flights:
        fid = str(f.id)
        gid = assignment_map.get(fid)
        if gid:
            gate_flights.setdefault(gid, []).append(f)
    
    propagation_path = []
    affected_flight_ids: Set[str] = set()
    queue = deque()  # (entity_type, entity_id, depth, effect, parent_id)
    visited = set()
    
    # Initialize root
    if root_flight_id:
        root_flight = db.query(Flight).filter(Flight.id == root_flight_id).first()
        if root_flight:
            queue.append(("flight", str(root_flight.id), 0, "ROOT_DELAY", None))
            propagation_path.append({
                "depth": 0,
                "type": "flight",
                "id": str(root_flight.id),
                "identifier": root_flight.flight_number,
                "effect": "ROOT_DELAY",
            })
    
    if root_gate_id:
        root_gate = db.query(Gate).filter(Gate.id == root_gate_id).first()
        if root_gate:
            queue.append(("gate", str(root_gate.id), 0, "GATE_CLOSURE", None))
            propagation_path.append({
                "depth": 0,
                "type": "gate",
                "id": str(root_gate.id),
                "identifier": root_gate.code,
                "effect": "GATE_CLOSURE",
            })
    
    if root_runway_id:
        root_runway = db.query(Runway).filter(Runway.id == root_runway_id).first()
        if root_runway:
            queue.append(("runway", str(root_runway.id), 0, "RUNWAY_CLOSURE", None))
            propagation_path.append({
                "depth": 0,
                "type": "runway",
                "id": str(root_runway.id),
                "identifier": root_runway.code,
                "effect": "RUNWAY_CLOSURE",
            })
            # Find all flights on this runway
            runway_flights = db.query(Flight).filter(Flight.runway_id == root_runway_id).all()
            for f in runway_flights:
                fid = str(f.id)
                if fid not in visited:
                    queue.append(("flight", fid, 1, "REASSIGNMENT_REQUIRED", str(root_runway.id)))
                    visited.add(fid)
    
    # BFS traversal
    while queue:
        entity_type, entity_id, depth, effect, parent_id = queue.popleft()
        
        if depth > max_depth:
            continue
        if entity_id in visited and entity_type == "flight":
            continue
        visited.add(entity_id)
        
        if entity_type == "flight" and depth > 0:
            flight = db.query(Flight).filter(Flight.id == entity_id).first()
            if not flight:
                continue
            
            affected_flight_ids.add(entity_id)
            propagation_path.append({
                "depth": depth,
                "type": "flight",
                "id": entity_id,
                "identifier": flight.flight_number,
                "effect": effect,
            })
            
            # Find the gate this flight is assigned to
            gate_id = assignment_map.get(entity_id)
            if gate_id and depth < max_depth:
                # Check other flights at the same gate for turnaround violations
                gate_flight_list = gate_flights.get(gate_id, [])
                for other_f in gate_flight_list:
                    ofid = str(other_f.id)
                    if ofid == entity_id or ofid in visited:
                        continue
                    # Check if delay causes overlap
                    s1, e1 = compute_occupied_interval(
                        flight.scheduled_arrival, flight.scheduled_departure, buffer
                    )
                    s2, e2 = compute_occupied_interval(
                        other_f.scheduled_arrival, other_f.scheduled_departure, buffer
                    )
                    if intervals_overlap(s1, e1, s2, e2):
                        queue.append(("flight", ofid, depth + 1, "TURNAROUND_VIOLATION", entity_id))
        
        elif entity_type == "gate":
            # Find all flights assigned to this gate
            gate_flight_list = gate_flights.get(entity_id, [])
            for f in gate_flight_list:
                fid = str(f.id)
                if fid not in visited:
                    queue.append(("flight", fid, depth + 1, "REASSIGNMENT_REQUIRED", entity_id))
    
    # Determine severity
    severity = RiskLevel.LOW
    if len(affected_flight_ids) >= 10:
        severity = RiskLevel.HIGH
    elif len(affected_flight_ids) >= 5:
        severity = RiskLevel.MEDIUM
    
    # Persist cascade event
    cascade_event = CascadeEvent(
        root_flight_id=root_flight_id,
        root_gate_id=root_gate_id,
        root_runway_id=root_runway_id,
        scenario_id=scenario_id,
        propagation_path=propagation_path,
        affected_flight_ids=list(affected_flight_ids),
        severity=severity,
    )
    db.add(cascade_event)
    db.commit()
    
    logger.info(
        f"Cascade analysis: {len(affected_flight_ids)} affected flights, "
        f"depth={len(propagation_path)}, severity={severity.value}"
    )
    
    return {
        "cascade_event_id": str(cascade_event.id),
        "root_flight_id": root_flight_id,
        "root_gate_id": root_gate_id,
        "root_runway_id": root_runway_id,
        "scenario_id": scenario_id,
        "propagation_path": propagation_path,
        "affected_flight_ids": list(affected_flight_ids),
        "affected_count": len(affected_flight_ids),
        "severity": severity.value,
        "max_depth_reached": max(p["depth"] for p in propagation_path) if propagation_path else 0,
    }
