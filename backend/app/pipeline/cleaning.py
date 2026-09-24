from typing import List, Dict, Any, Optional
from sqlalchemy.orm import Session
from app.models import Aircraft, Runway
from app.models.enums import RunwayStatus


def clean_and_normalize_flights(
    validated_rows: List[Dict[str, Any]],
    db: Session,
) -> List[Dict[str, Any]]:
    """
    Cleans, enriches, and resolves references (aircraft_id, runway_id)
    for validated flight rows prior to persistence.
    """
    cleaned: List[Dict[str, Any]] = []

    # Get active runways for round-robin assignment
    active_runways = db.query(Runway).filter(Runway.status == RunwayStatus.ACTIVE).order_by(Runway.code).all()
    if not active_runways:
        raise ValueError("No active runways available in database to assign to flights.")

    # Cache airframes by type_code
    aircraft_by_type: Dict[str, List[Aircraft]] = {}
    all_aircraft = db.query(Aircraft).all()
    for ac in all_aircraft:
        aircraft_by_type.setdefault(ac.type_code, []).append(ac)

    runway_lookup = {r.code: r for r in active_runways}
    rr_index = 0

    for idx, row in enumerate(validated_rows):
        ac_type = row["aircraft_type_code"]
        candidates = aircraft_by_type.get(ac_type, [])
        if not candidates:
            raise ValueError(f"No aircraft available with type code '{ac_type}'")

        # Pick airframe round-robin or first available
        chosen_aircraft = candidates[idx % len(candidates)]

        # Resolve runway
        target_runway_code = row.get("runway_code")
        if target_runway_code and target_runway_code in runway_lookup:
            assigned_runway = runway_lookup[target_runway_code]
        else:
            assigned_runway = active_runways[rr_index % len(active_runways)]
            rr_index += 1

        cleaned_item = {
            "flight_number": row["flight_number"],
            "airline": row["airline"],
            "aircraft_id": chosen_aircraft.id,
            "route_type": row["route_type"],
            "origin": row["origin"],
            "destination": row["destination"],
            "runway_id": assigned_runway.id,
            "scheduled_arrival": row["scheduled_arrival"],
            "scheduled_departure": row["scheduled_departure"],
            "actual_arrival": row.get("actual_arrival"),
            "actual_departure": row.get("actual_departure"),
            "is_synthetic": True,
        }
        cleaned.append(cleaned_item)

    return cleaned
