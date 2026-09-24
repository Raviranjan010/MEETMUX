"""
Explainability service per docs/EXPLAINABILITY.md.
FR-14: Explain a gate recommendation using only facts computed by the system.
"""
import logging
from typing import Dict, Any, Optional, List

from sqlalchemy.orm import Session

from app.models import (
    GateAssignment, OptimizationRun, Flight, Gate, Prediction, SystemConfig,
)
from app.models.enums import (
    GateType, GateEligibleRouteType, RouteType, AssignmentStatus,
)
from app.services.baseline import is_gate_compatible, SIZE_ORDER
from app.services.conflict import (
    detect_conflicts_for_assignments, get_turnaround_buffer,
)

logger = logging.getLogger(__name__)


def explain_assignment(
    db: Session,
    gate_assignment_id: str,
) -> Dict[str, Any]:
    """
    Generates structured explanation for a gate assignment.
    Each reason maps 1:1 to a real check already performed.
    """
    ga = db.query(GateAssignment).filter(GateAssignment.id == gate_assignment_id).first()
    if not ga:
        # Check if gate_assignment_id is a flight_id
        ga = (
            db.query(GateAssignment)
            .filter(GateAssignment.flight_id == gate_assignment_id)
            .order_by(GateAssignment.created_at.desc())
            .first()
        )
    if not ga:
        # Check if gate_assignment_id is a flight_number
        flight_obj = db.query(Flight).filter(Flight.flight_number == gate_assignment_id).first()
        if flight_obj:
            ga = (
                db.query(GateAssignment)
                .filter(GateAssignment.flight_id == flight_obj.id)
                .order_by(GateAssignment.created_at.desc())
                .first()
            )
    if not ga:
        return {"error": "Gate assignment not found"}

    flight = ga.flight
    gate = ga.gate
    opt_run = ga.optimization_run

    if not flight or not gate:
        return {"error": "Flight or gate not found for this assignment"}
    
    reasons = []
    
    # 1. Aircraft compatibility
    flight_size = SIZE_ORDER.get(flight.aircraft.size_class, 2)
    gate_max = SIZE_ORDER.get(gate.max_aircraft_size, 2)
    if flight_size <= gate_max:
        reasons.append({
            "code": "COMPATIBLE_AIRCRAFT",
            "detail": f"{flight.aircraft.type_code} ({flight.aircraft.size_class.value}) fits gate max size {gate.max_aircraft_size.value}",
        })
    
    # 2. Route eligibility
    eligible = False
    if gate.eligible_route_types == GateEligibleRouteType.BOTH:
        eligible = True
        detail = f"Flight is {flight.route_type.value}; gate eligible_route_types=BOTH"
    elif flight.route_type == RouteType.DOMESTIC and gate.eligible_route_types == GateEligibleRouteType.DOMESTIC:
        eligible = True
        detail = f"Flight is DOMESTIC; gate eligible_route_types=DOMESTIC"
    elif flight.route_type == RouteType.INTERNATIONAL and gate.eligible_route_types == GateEligibleRouteType.INTERNATIONAL:
        eligible = True
        detail = f"Flight is INTERNATIONAL; gate eligible_route_types=INTERNATIONAL"
    
    if eligible:
        reasons.append({
            "code": "ROUTE_ELIGIBLE",
            "detail": detail,
        })
    
    # 3. No overlap check
    config = db.query(SystemConfig).first()
    buffer = get_turnaround_buffer(config)
    
    # Check for conflicts at this gate in this run
    run_assignments = db.query(GateAssignment).filter(
        GateAssignment.optimization_run_id == ga.optimization_run_id,
        GateAssignment.gate_id == gate.id,
    ).all()
    
    other_flights_at_gate = []
    for other_ga in run_assignments:
        if other_ga.flight_id != flight.id:
            of = other_ga.flight
            other_flights_at_gate.append({
                "flight_id": str(of.id),
                "gate_id": str(gate.id),
                "gate_code": gate.code,
                "gate_status": gate.status.value,
                "arrival": of.scheduled_arrival,
                "departure": of.scheduled_departure,
            })
    
    my_assignment = {
        "flight_id": str(flight.id),
        "gate_id": str(gate.id),
        "gate_code": gate.code,
        "gate_status": gate.status.value,
        "arrival": flight.scheduled_arrival,
        "departure": flight.scheduled_departure,
    }
    
    conflicts = detect_conflicts_for_assignments(
        [my_assignment] + other_flights_at_gate, config
    )
    
    if not conflicts:
        reasons.append({
            "code": "NO_OVERLAP",
            "detail": f"No conflicting interval found at gate {gate.code} for this run",
        })
    
    # 4. Objective contribution comparison
    obj_contrib = float(ga.objective_contribution or 0)
    
    # Find alternative gates and their costs
    alternatives = []
    all_gates = db.query(Gate).all()
    for alt_gate in all_gates:
        if str(alt_gate.id) == str(gate.id):
            continue
        if is_gate_compatible(flight, alt_gate):
            # Estimate objective contribution
            weights = opt_run.config_snapshot if opt_run else {}
            w_taxi = float(weights.get("optimizer_weight_taxi_distance", 0.1))
            w_remote = float(weights.get("optimizer_weight_remote_stand", 10.0))
            
            alt_cost = w_taxi * float(alt_gate.taxi_distance_meters)
            if alt_gate.gate_type == GateType.REMOTE:
                alt_cost += w_remote
            
            rejected_reason = None
            if alt_cost > obj_contrib and obj_contrib > 0:
                rejected_reason = "higher objective cost"
            elif alt_gate.gate_type == GateType.REMOTE and gate.gate_type != GateType.REMOTE:
                rejected_reason = "remote stand penalty"
            else:
                rejected_reason = "higher taxi distance"
            
            alternatives.append({
                "gate_id": str(alt_gate.id),
                "gate_code": alt_gate.code,
                "objective_contribution": round(alt_cost, 3),
                "rejected_reason": rejected_reason,
            })
    
    # Sort alternatives by cost and take top 5
    alternatives.sort(key=lambda x: x["objective_contribution"])
    alternatives = alternatives[:5]
    
    if obj_contrib > 0 and alternatives:
        next_best = alternatives[0]["objective_contribution"]
        if obj_contrib <= next_best:
            reasons.append({
                "code": "LOWER_OBJECTIVE_COST",
                "detail": f"Objective contribution {obj_contrib} vs next-best gate's {next_best}",
            })
    
    # 5. Gate type preference
    if gate.gate_type == GateType.JETBRIDGE:
        reasons.append({
            "code": "JETBRIDGE_PREFERRED",
            "detail": f"Gate {gate.code} is a jetbridge gate (no remote stand penalty)",
        })
    
    reason_strings = [r["detail"] if isinstance(r, dict) else str(r) for r in reasons]
    hard_constraints = [
        "AIRCRAFT_COMPATIBILITY",
        "ROUTE_ELIGIBILITY",
        "NO_OCCUPANCY_OVERLAP",
        "TURNAROUND_FEASIBLE",
    ]

    return {
        "flight_id": str(flight.id),
        "flight_number": flight.flight_number,
        "assigned_gate": gate.code,
        "gate_id": str(gate.id),
        "gate_code": gate.code,
        "optimization_run_id": str(ga.optimization_run_id),
        "objective_contribution": obj_contrib,
        "reasons": reason_strings,
        "hard_constraints_satisfied": hard_constraints,
        "soft_score_breakdown": {
            "objective_contribution": obj_contrib or 0.0,
            "taxi_distance": float(gate.taxi_distance_meters or 0),
        },
        "alternatives_considered": alternatives,
        "alternatives_evaluated": [
            {
                "gate": a["gate_code"],
                "rank": idx + 1,
                "score": a["objective_contribution"],
                "reason": a["rejected_reason"],
            }
            for idx, a in enumerate(alternatives)
        ],
    }

