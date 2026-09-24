"""
Scenario simulation engine per docs/SIMULATION.md.
FR-11: Run named disruption scenarios that mutate real backend state.
"""
import logging
from datetime import datetime, timedelta, timezone
from typing import Dict, Any, Optional, List
import random

from sqlalchemy.orm import Session
from fastapi import HTTPException

from app.models import (
    Flight, Gate, Runway, WeatherRecord, Scenario, AuditRecord,
    Airport, Aircraft, SystemConfig,
)
from app.models.enums import (
    ScenarioType, RunwayStatus, GateStatus, WeatherCondition,
    RouteType, AuditAction,
)

logger = logging.getLogger(__name__)


def run_scenario(
    db: Session,
    scenario_type: str,
    target_reference: str,
    params: Dict[str, Any],
) -> Dict[str, Any]:
    """
    Runs a disruption scenario that mutates real backend state.
    Creates a scenarios row and returns state changes.
    Does NOT automatically re-optimize (that's POST /api/reoptimize).
    """
    sc_type = ScenarioType(scenario_type)
    state_changes = {}
    
    if sc_type == ScenarioType.HEAVY_RAIN:
        state_changes = _apply_heavy_rain(db, target_reference, params)
    elif sc_type == ScenarioType.RUNWAY_CLOSURE:
        state_changes = _apply_runway_closure(db, target_reference, params)
    elif sc_type == ScenarioType.GATE_CLOSURE:
        state_changes = _apply_gate_closure(db, target_reference, params)
    elif sc_type == ScenarioType.TRAFFIC_SURGE:
        state_changes = _apply_traffic_surge(db, target_reference, params)
    elif sc_type == ScenarioType.FLIGHT_DELAY:
        state_changes = _apply_flight_delay(db, target_reference, params)
    elif sc_type == ScenarioType.GATE_CONFLICT:
        state_changes = _apply_gate_conflict(db, target_reference, params)
    elif sc_type == ScenarioType.CASCADE_DELAY:
        state_changes = _apply_flight_delay(db, target_reference, params)

    if "error" in state_changes:
        db.rollback()
        raise HTTPException(status_code=404, detail=state_changes["error"])
    
    # Create scenario record
    scenario = Scenario(
        type=sc_type,
        target_reference=target_reference,
        params={**params, "_state_changes": state_changes},
    )
    db.add(scenario)
    db.flush()
    
    # Audit record
    audit = AuditRecord(
        action=AuditAction.SCENARIO_RUN,
        actor="operator",
        reference_id=scenario.id,
        details={
            "scenario_type": sc_type.value,
            "target_reference": target_reference,
            "params": params,
            "state_changes": state_changes,
        },
    )
    db.add(audit)
    db.commit()
    
    logger.info(f"Scenario {sc_type.value} applied to {target_reference}")

    # Count active conflicts for frontend KPI
    from app.services.conflict import detect_conflicts_from_db
    conflicts = detect_conflicts_from_db(db, assignment_source="BASELINE")

    affected_count = state_changes.get("affected_flights", len(state_changes.get("affected_flight_ids", [])))
    if affected_count == 0 and "flight_id" in state_changes:
        affected_count = 1

    return {
        "scenario_id": str(scenario.id),
        "id": str(scenario.id),
        "type": sc_type.value,
        "scenario_name": sc_type.value.replace("_", " ").title(),
        "description": f"Simulation of {sc_type.value.replace('_', ' ').lower()} affecting {target_reference}",
        "target_reference": target_reference,
        "affected_flights_count": affected_count,
        "conflicts_detected": len(conflicts),
        "cascade_events_count": len(state_changes.get("created_flight_ids", [])) or (1 if affected_count > 0 else 0),
        "details": state_changes,
        "state_changes": state_changes,
    }


def _apply_heavy_rain(db: Session, airport_code: str, params: Dict) -> Dict:
    """Insert heavy rain weather record, affecting predictions."""
    airport = db.query(Airport).filter(Airport.code == airport_code).first()
    if not airport:
        return {"error": f"Airport {airport_code} not found"}
    
    recorded_at = datetime.now(timezone.utc)
    weather = WeatherRecord(
        airport_id=airport.id,
        recorded_at=recorded_at,
        condition=WeatherCondition.HEAVY_RAIN,
        wind_speed_kt=params.get("wind_speed_kt", 25.0),
        visibility_m=params.get("visibility_m", 2000.0),
    )
    db.add(weather)
    
    return {
        "weather_condition": "HEAVY_RAIN",
        "recorded_at": recorded_at.isoformat(),
        "airport_code": airport.code,
        "visibility_m": params.get("visibility_m", 2000.0),
        "wind_speed_kt": params.get("wind_speed_kt", 25.0),
        "effect": "Predictions will reflect worse taxi conditions",
    }


def _apply_runway_closure(db: Session, runway_code: str, params: Dict) -> Dict:
    """Close a runway - all flights on it need reassignment."""
    runway = db.query(Runway).filter(Runway.code == runway_code).first()
    if not runway:
        return {"error": f"Runway {runway_code} not found"}
    
    runway.status = RunwayStatus.CLOSED
    original_status = RunwayStatus.ACTIVE.value
    
    affected_flights = db.query(Flight).filter(Flight.runway_id == runway.id).all()
    affected_ids = [str(f.id) for f in affected_flights]
    
    # Reassign affected flights to remaining active runways
    active_runways = db.query(Runway).filter(
        Runway.status == RunwayStatus.ACTIVE,
        Runway.id != runway.id,
    ).all()
    
    reassigned = 0
    if active_runways:
        for i, f in enumerate(affected_flights):
            f.runway_id = active_runways[i % len(active_runways)].id
            reassigned += 1
    
    return {
        "runway_code": runway_code,
        "previous_status": original_status,
        "new_status": "CLOSED",
        "affected_flights": len(affected_ids),
        "affected_flight_ids": affected_ids[:20],
        "reassigned_to_active_runways": reassigned,
    }


def _apply_gate_closure(db: Session, gate_code: str, params: Dict) -> Dict:
    """Block a gate - flights assigned there need reassignment."""
    gate = db.query(Gate).filter(Gate.code == gate_code).first()
    if not gate:
        return {"error": f"Gate {gate_code} not found"}
    
    gate.status = GateStatus.BLOCKED
    
    return {
        "gate_code": gate_code,
        "new_status": "BLOCKED",
        "effect": "Flights assigned to this gate require reassignment via re-optimization",
    }


def _apply_traffic_surge(db: Session, airport_code: str, params: Dict) -> Dict:
    """Insert additional synthetic flights."""
    additional = params.get("additional_flights", 10)
    if not isinstance(additional, int) or additional < 1 or additional > 100:
        return {"error": "additional_flights must be an integer between 1 and 100"}
    airport = db.query(Airport).filter(Airport.code == airport_code).first()
    if not airport:
        return {"error": f"Airport {airport_code} not found"}
    
    runways = db.query(Runway).filter(Runway.status == RunwayStatus.ACTIVE).all()
    aircraft_list = db.query(Aircraft).all()
    
    if not runways or not aircraft_list:
        return {"error": "No active runways or aircraft available"}
    
    rng = random.Random(99)
    base_time = datetime.now(timezone.utc).replace(hour=12, minute=0, second=0, microsecond=0)
    created_ids = []
    
    airlines = ["AA", "DL", "UA", "BA"]
    for i in range(additional):
        airline = airlines[i % len(airlines)]
        ac = aircraft_list[i % len(aircraft_list)]
        arr = base_time + timedelta(minutes=rng.randint(0, 360))
        dep = arr + timedelta(minutes=rng.choice([45, 60, 75, 90]))
        
        flight = Flight(
            flight_number=f"SG{900 + i}",
            airline=airline,
            aircraft_id=ac.id,
            route_type=RouteType.DOMESTIC if i % 3 != 0 else RouteType.INTERNATIONAL,
            origin="DFW",
            destination="ORD",
            runway_id=runways[i % len(runways)].id,
            scheduled_arrival=arr,
            scheduled_departure=dep,
            is_synthetic=True,
        )
        db.add(flight)
        db.flush()
        created_ids.append(str(flight.id))
    
    return {
        "additional_flights": additional,
        "created_flight_ids": created_ids,
        "is_synthetic": True,
    }


def _apply_flight_delay(db: Session, flight_number: str, params: Dict) -> Dict:
    """Delay a flight by shifting arrival/departure times."""
    delay_minutes = params.get("delay_minutes", 30)
    
    flight = db.query(Flight).filter(Flight.flight_number == flight_number).first()
    if not flight:
        return {"error": f"Flight {flight_number} not found"}
    
    delta = timedelta(minutes=delay_minutes)
    original_arrival = flight.scheduled_arrival
    original_departure = flight.scheduled_departure
    
    flight.scheduled_arrival = original_arrival + delta
    flight.scheduled_departure = original_departure + delta
    
    return {
        "flight_number": flight.flight_number,
        "flight_id": str(flight.id),
        "delay_minutes": delay_minutes,
        "original_arrival": original_arrival.isoformat(),
        "new_arrival": flight.scheduled_arrival.isoformat(),
        "original_departure": original_departure.isoformat(),
        "new_departure": flight.scheduled_departure.isoformat(),
    }


def _apply_gate_conflict(db: Session, gate_code: str, params: Dict) -> Dict:
    """Force overlapping flights at a gate to demonstrate conflict detection."""
    gate = db.query(Gate).filter(Gate.code == gate_code).first()
    if not gate:
        return {"error": f"Gate {gate_code} not found"}
    
    candidates = (
        db.query(Flight)
        .filter(Flight.scheduled_arrival.isnot(None), Flight.scheduled_departure.isnot(None))
        .order_by(Flight.scheduled_arrival.asc())
        .limit(2)
        .all()
    )
    if len(candidates) < 2:
        return {"error": "At least two flights with scheduled intervals are required"}

    from app.models import GateAssignment, OptimizationRun
    from app.models.enums import RunType, SolverUsed, OptimizationStatus, AssignmentStatus
    run = OptimizationRun(
        run_type=RunType.BASELINE,
        solver_used=SolverUsed.NONE,
        solver_status="SCENARIO_FORCED_CONFLICT",
        status=OptimizationStatus.FEASIBLE,
        config_snapshot={"scenario_forced": True},
    )
    db.add(run)
    db.flush()
    for flight in candidates:
        db.add(GateAssignment(
            optimization_run_id=run.id,
            flight_id=flight.id,
            gate_id=gate.id,
            assignment_status=AssignmentStatus.BASELINE,
        ))
    return {
        "gate_code": gate_code,
        "optimization_run_id": str(run.id),
        "flight_ids": [str(f.id) for f in candidates],
        "effect": "Two scheduled flights were assigned to this gate for conflict detection",
        "is_synthetic": True,
    }


def reset_scenarios(db: Session) -> Dict[str, Any]:
    """
    Resets airport state back to nominal baseline:
    - Restores closed runways to ACTIVE
    - Restores blocked gates to AVAILABLE
    - Removes surge flights
    - Restores baseline weather
    """
    # 1. Restore runways
    runways = db.query(Runway).all()
    runway_scenarios = db.query(Scenario).filter(Scenario.type == ScenarioType.RUNWAY_CLOSURE).all()
    for scenario in runway_scenarios:
        previous_status = scenario.params.get("_state_changes", {}).get("previous_status")
        runway = db.query(Runway).filter(Runway.code == scenario.target_reference).first()
        if runway:
            runway.status = RunwayStatus(previous_status or RunwayStatus.ACTIVE.value)

    # 2. Restore gates
    gates = db.query(Gate).all()
    for g in gates:
        g.status = GateStatus.AVAILABLE

    # 3. Restore clear weather
    scenario_rows = db.query(Scenario).filter(Scenario.type == ScenarioType.HEAVY_RAIN).all()
    for scenario in scenario_rows:
        recorded_at = scenario.params.get("_state_changes", {}).get("recorded_at")
        if recorded_at:
            weather = db.query(WeatherRecord).filter(
                WeatherRecord.recorded_at == datetime.fromisoformat(recorded_at)
            ).first()
            if weather:
                db.delete(weather)

    # 4. Remove surge flights
    surge_flights = db.query(Flight).filter(Flight.flight_number.like("SG9%")).all()
    surge_count = len(surge_flights)
    for sf in surge_flights:
        db.delete(sf)

    # 5. Audit record
    audit = AuditRecord(
        action=AuditAction.SCENARIO_RUN,
        actor="operator",
        details={"action": "RESET_AIRPORT_STATE", "surge_flights_removed": surge_count},
    )
    db.add(audit)
    db.commit()

    logger.info("Airport operational state reset to nominal baseline")

    return {
        "status": "reset",
        "message": "Airport operational state restored to nominal baseline",
        "runways_active": len(runways),
        "gates_available": len(gates),
        "surge_flights_removed": surge_count,
    }
