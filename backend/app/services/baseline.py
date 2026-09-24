"""
Baseline gate assignment algorithm per REQUIREMENTS.md R8.
FR-7: Generate a deterministic baseline gate assignment (first-fit).
"""
import logging
import time
from typing import List, Dict, Any, Optional, Tuple
from datetime import datetime

from sqlalchemy.orm import Session

from app.models import (
    Flight, Gate, SystemConfig, OptimizationRun, GateAssignment, AuditRecord,
)
from app.models.enums import (
    RunType, SolverUsed, OptimizationStatus, AssignmentStatus,
    GateStatus, AircraftSizeClass, GateEligibleRouteType, RouteType, AuditAction,
)
from app.services.conflict import compute_occupied_interval, intervals_overlap, get_turnaround_buffer

logger = logging.getLogger(__name__)

SIZE_ORDER = {AircraftSizeClass.SMALL: 1, AircraftSizeClass.MEDIUM: 2, AircraftSizeClass.LARGE: 3}


def is_gate_compatible(flight: Flight, gate: Gate) -> bool:
    """
    Checks gate compatibility per GATE_SYSTEM.md:
    - aircraft.size_class <= gate.max_aircraft_size
    - flight.route_type ∈ gate.eligible_route_types (BOTH satisfies either)
    - gate.status != BLOCKED
    """
    if gate.status == GateStatus.BLOCKED:
        return False

    # Size compatibility
    flight_size = SIZE_ORDER.get(flight.aircraft.size_class, 2)
    gate_max = SIZE_ORDER.get(gate.max_aircraft_size, 2)
    if flight_size > gate_max:
        return False

    # Route eligibility
    if gate.eligible_route_types == GateEligibleRouteType.BOTH:
        return True
    if flight.route_type == RouteType.DOMESTIC and gate.eligible_route_types == GateEligibleRouteType.DOMESTIC:
        return True
    if flight.route_type == RouteType.INTERNATIONAL and gate.eligible_route_types == GateEligibleRouteType.INTERNATIONAL:
        return True

    return False


def run_baseline(
    db: Session,
    scenario_id: Optional[str] = None,
) -> Dict[str, Any]:
    """
    Runs the baseline greedy gate assignment algorithm per R8.
    
    For each flight in ascending scheduled_arrival_time order:
    assign the first gate (ordered by gate_id ascending) that is:
    (a) compatible with aircraft type
    (b) satisfies domestic/international eligibility
    (c) not BLOCKED
    (d) has no time-interval overlap with any existing assignment
    
    Single-pass, deterministic, reproducible.
    """
    start_time = time.time()
    config = db.query(SystemConfig).first()
    buffer = get_turnaround_buffer(config)

    # Get all flights ordered by scheduled_arrival ascending
    flights = db.query(Flight).order_by(Flight.scheduled_arrival.asc()).all()
    # Get all gates ordered by id ascending (code ascending as proxy)
    gates = db.query(Gate).order_by(Gate.code.asc()).all()

    if not flights:
        return {"error": "No flights found in database"}
    if not gates:
        return {"error": "No gates found in database"}

    # Config snapshot for the run
    config_snapshot = {}
    if config:
        config_snapshot = {
            "turnaround_buffer_minutes": int(config.turnaround_buffer_minutes),
            "optimizer_weight_delay_cost": float(config.optimizer_weight_delay_cost),
            "optimizer_weight_conflict_cost": float(config.optimizer_weight_conflict_cost),
            "optimizer_weight_reassignment_cost": float(config.optimizer_weight_reassignment_cost),
            "optimizer_weight_taxi_distance": float(config.optimizer_weight_taxi_distance),
            "optimizer_weight_remote_stand": float(config.optimizer_weight_remote_stand),
        }

    # Create optimization run record
    opt_run = OptimizationRun(
        run_type=RunType.BASELINE,
        scenario_id=scenario_id,
        solver_used=SolverUsed.NONE,
        solver_status="GREEDY_FIRST_FIT",
        status=OptimizationStatus.RUNNING,
        config_snapshot=config_snapshot,
    )
    db.add(opt_run)
    db.flush()

    # Track occupied intervals per gate: gate_id -> list of (start, end)
    gate_intervals: Dict[str, List[Tuple[datetime, datetime]]] = {str(g.id): [] for g in gates}
    
    assignments = []
    unassigned_count = 0
    conflict_count = 0

    for flight in flights:
        assigned = False
        for gate in gates:
            if not is_gate_compatible(flight, gate):
                continue

            # Check no overlap with existing assignments at this gate
            s, e = compute_occupied_interval(
                flight.scheduled_arrival, flight.scheduled_departure, buffer
            )
            gate_key = str(gate.id)
            has_overlap = False
            for existing_s, existing_e in gate_intervals[gate_key]:
                if intervals_overlap(s, e, existing_s, existing_e):
                    has_overlap = True
                    break

            if not has_overlap:
                # Assign this flight to this gate
                ga = GateAssignment(
                    optimization_run_id=opt_run.id,
                    flight_id=flight.id,
                    gate_id=gate.id,
                    assignment_status=AssignmentStatus.BASELINE,
                    objective_contribution=float(gate.taxi_distance_meters) * 0.1,
                )
                db.add(ga)
                gate_intervals[gate_key].append((s, e))
                assignments.append({
                    "flight_id": str(flight.id),
                    "flight_number": flight.flight_number,
                    "gate_id": str(gate.id),
                    "gate_code": gate.code,
                })
                assigned = True
                break

        if not assigned:
            # UNASSIGNED - no compatible gate available
            ga = GateAssignment(
                optimization_run_id=opt_run.id,
                flight_id=flight.id,
                gate_id=None,
                assignment_status=AssignmentStatus.BASELINE,
                objective_contribution=None,
            )
            db.add(ga)
            unassigned_count += 1
            assignments.append({
                "flight_id": str(flight.id),
                "flight_number": flight.flight_number,
                "gate_id": None,
                "gate_code": "UNASSIGNED",
            })

    solve_time_ms = int((time.time() - start_time) * 1000)

    # Update run status
    opt_run.status = OptimizationStatus.OPTIMAL
    opt_run.solve_time_ms = solve_time_ms
    opt_run.objective_value = 0  # Baseline has no objective
    opt_run.validation_passed = True
    opt_run.validation_report = {
        "total_flights": len(flights),
        "assigned": len(flights) - unassigned_count,
        "unassigned": unassigned_count,
    }

    # Audit record
    audit = AuditRecord(
        action=AuditAction.OPTIMIZATION_RUN,
        actor="operator",
        reference_id=opt_run.id,
        details={
            "run_type": "BASELINE",
            "total_flights": len(flights),
            "assigned": len(flights) - unassigned_count,
            "unassigned": unassigned_count,
            "solve_time_ms": solve_time_ms,
        },
    )
    db.add(audit)
    db.commit()

    logger.info(
        f"Baseline complete: {len(flights)} flights, {len(flights) - unassigned_count} assigned, "
        f"{unassigned_count} unassigned, {solve_time_ms}ms"
    )

    return {
        "optimization_run_id": str(opt_run.id),
        "status": opt_run.status.value,
        "run_type": "BASELINE",
        "solver_used": "NONE",
        "solver_status": "GREEDY_FIRST_FIT",
        "total_flights": len(flights),
        "assigned": len(flights) - unassigned_count,
        "unassigned": unassigned_count,
        "solve_time_ms": solve_time_ms,
        "assignments": assignments,
    }
