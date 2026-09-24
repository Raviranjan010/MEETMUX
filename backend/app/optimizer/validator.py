"""
Independent Validator per docs/OPTIMIZATION.md §6.
FR-9: Independently validate every optimizer solution against all hard constraints.
"""
import logging
from typing import List, Dict, Any, Optional

from app.models import Flight, Gate, SystemConfig
from app.models.enums import GateStatus
from app.services.baseline import is_gate_compatible, SIZE_ORDER
from app.services.conflict import compute_occupied_interval, intervals_overlap, get_turnaround_buffer

logger = logging.getLogger(__name__)


def validate_solution(
    flights: List[Flight],
    gates: List[Gate],
    assignments: List[Dict[str, Any]],
    config: Optional[SystemConfig] = None,
) -> Dict[str, Any]:
    """
    Re-checks every hard constraint from OPTIMIZATION.md §Hard constraints
    using plain Python (no solver calls).
    
    Hard constraints validated:
    1. Exactly one gate per flight (or explicit UNASSIGNED)
    2. Aircraft compatibility
    3. Route eligibility
    4. Gate availability / not BLOCKED
    5. Turnaround feasibility & no overlap
    
    Returns validation report.
    """
    violations = []
    buffer = get_turnaround_buffer(config)
    
    # Track assignments per gate for overlap checking
    gate_assignments: Dict[int, List[int]] = {}  # gate_index -> [flight_indices]
    assigned_flights = set()
    unassigned_flights = []
    
    for a in assignments:
        fi = a.get("flight_index")
        gi = a.get("gate_index")
        if not isinstance(fi, int) or fi < 0 or fi >= len(flights):
            violations.append({"constraint": "INDEX_OUT_OF_RANGE", "message": f"Invalid flight index {fi}"})
            continue
        
        if gi is not None:
            if fi in assigned_flights:
                violations.append({
                    "constraint": "EXACTLY_ONE_GATE",
                    "flight_id": str(flights[fi].id),
                    "flight_number": flights[fi].flight_number,
                    "message": f"Flight {flights[fi].flight_number} has multiple assignment rows",
                })
            assigned_flights.add(fi)
            if isinstance(gi, int):
                gate_assignments.setdefault(gi, []).append(fi)
        else:
            if fi in assigned_flights:
                violations.append({
                    "constraint": "EXACTLY_ONE_GATE",
                    "flight_id": str(flights[fi].id),
                    "flight_number": flights[fi].flight_number,
                    "message": f"Flight {flights[fi].flight_number} has multiple assignment rows",
                })
            unassigned_flights.append(fi)
            assigned_flights.add(fi)  # explicitly unassigned is acceptable
    
    # Constraint 1: Every flight accounted for
    for i in range(len(flights)):
        if i not in assigned_flights:
            violations.append({
                "constraint": "EXACTLY_ONE_GATE",
                "flight_id": str(flights[i].id),
                "flight_number": flights[i].flight_number,
                "message": f"Flight {flights[i].flight_number} has no assignment (not even UNASSIGNED)",
            })
    
    # Check each assigned flight
    for a in assignments:
        fi = a.get("flight_index")
        gi = a.get("gate_index")
        if not isinstance(fi, int) or fi < 0 or fi >= len(flights):
            continue
        
        if gi is None:
            continue  # Unassigned is valid (penalized)
        
        if not isinstance(gi, int) or gi < 0 or gi >= len(gates):
            violations.append({
                "constraint": "INDEX_OUT_OF_RANGE",
                "message": f"Invalid flight index {fi} or gate index {gi}",
            })
            continue
        
        flight = flights[fi]
        gate = gates[gi]
        
        # Constraint 2: Aircraft compatibility
        flight_size = SIZE_ORDER.get(flight.aircraft.size_class, 2)
        gate_max = SIZE_ORDER.get(gate.max_aircraft_size, 2)
        if flight_size > gate_max:
            violations.append({
                "constraint": "AIRCRAFT_COMPATIBILITY",
                "flight_id": str(flight.id),
                "flight_number": flight.flight_number,
                "gate_id": str(gate.id),
                "gate_code": gate.code,
                "message": f"Aircraft size {flight.aircraft.size_class.value} exceeds gate max {gate.max_aircraft_size.value}",
            })
        
        # Constraint 3: Route eligibility
        if not is_gate_compatible(flight, gate):
            # More specific check - this will also catch BLOCKED but let's be explicit
            from app.models.enums import GateEligibleRouteType, RouteType
            if gate.eligible_route_types != GateEligibleRouteType.BOTH:
                if flight.route_type == RouteType.DOMESTIC and gate.eligible_route_types != GateEligibleRouteType.DOMESTIC:
                    violations.append({
                        "constraint": "ROUTE_ELIGIBILITY",
                        "flight_id": str(flight.id),
                        "flight_number": flight.flight_number,
                        "gate_id": str(gate.id),
                        "gate_code": gate.code,
                        "message": f"Domestic flight at international-only gate {gate.code}",
                    })
                elif flight.route_type == RouteType.INTERNATIONAL and gate.eligible_route_types != GateEligibleRouteType.INTERNATIONAL:
                    violations.append({
                        "constraint": "ROUTE_ELIGIBILITY",
                        "flight_id": str(flight.id),
                        "flight_number": flight.flight_number,
                        "gate_id": str(gate.id),
                        "gate_code": gate.code,
                        "message": f"International flight at domestic-only gate {gate.code}",
                    })
        
        # Constraint 4: Not BLOCKED
        if gate.status == GateStatus.BLOCKED:
            violations.append({
                "constraint": "GATE_NOT_BLOCKED",
                "flight_id": str(flight.id),
                "flight_number": flight.flight_number,
                "gate_id": str(gate.id),
                "gate_code": gate.code,
                "message": f"Flight assigned to BLOCKED gate {gate.code}",
            })
    
    # Constraint 5: No overlap at same gate
    for gi, flight_indices in gate_assignments.items():
        if gi >= len(gates):
            continue
        gate = gates[gi]
        for i in range(len(flight_indices)):
            fi = flight_indices[i]
            if fi >= len(flights):
                continue
            si, ei = compute_occupied_interval(
                flights[fi].scheduled_arrival, flights[fi].scheduled_departure, buffer
            )
            for j in range(i + 1, len(flight_indices)):
                fj = flight_indices[j]
                if fj >= len(flights):
                    continue
                sj, ej = compute_occupied_interval(
                    flights[fj].scheduled_arrival, flights[fj].scheduled_departure, buffer
                )
                if intervals_overlap(si, ei, sj, ej):
                    violations.append({
                        "constraint": "TURNAROUND_OVERLAP",
                        "flight_ids": [str(flights[fi].id), str(flights[fj].id)],
                        "flight_numbers": [flights[fi].flight_number, flights[fj].flight_number],
                        "gate_id": str(gate.id),
                        "gate_code": gate.code,
                        "message": f"Overlap between {flights[fi].flight_number} and {flights[fj].flight_number} at gate {gate.code}",
                    })
    
    passed = len(violations) == 0
    
    report = {
        "passed": passed,
        "total_constraints_checked": 5,
        "total_flights": len(flights),
        "assigned_flights": len(assigned_flights) - len(unassigned_flights),
        "unassigned_flights": len(unassigned_flights),
        "violations": violations,
        "violation_count": len(violations),
    }
    
    if not passed:
        logger.warning(f"Validation FAILED: {len(violations)} violations found")
        for v in violations[:5]:
            logger.warning(f"  - [{v['constraint']}] {v['message']}")
    else:
        logger.info("Independent validation PASSED: all hard constraints satisfied")
    
    return report
