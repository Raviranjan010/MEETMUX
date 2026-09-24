"""
Flight routes per docs/API.md.
"""
import logging
from typing import Optional
from fastapi import APIRouter, Depends, Query, status
from sqlalchemy.orm import Session, joinedload

from app.core.db import get_db
from app.core.errors import AppError
from app.models import Flight, Prediction, GateAssignment
from app.models.enums import RouteType, RiskLevel

router = APIRouter(prefix="/flights", tags=["Flights"])
logger = logging.getLogger(__name__)


@router.get("")
def get_flights(
    page: int = Query(1, ge=1),
    page_size: int = Query(25, ge=1, le=100),
    route_type: Optional[str] = None,
    risk_level: Optional[str] = None,
    airline: Optional[str] = None,
    db: Session = Depends(get_db),
):
    """GET /api/flights with pagination and filtering."""
    query = db.query(Flight).options(
        joinedload(Flight.aircraft),
        joinedload(Flight.runway),
    ).order_by(Flight.scheduled_arrival.asc())

    if route_type:
        query = query.filter(Flight.route_type == RouteType(route_type))
    if airline:
        query = query.filter(Flight.airline == airline.upper())

    # Risk level filter requires join with predictions
    if risk_level:
        query = query.join(Prediction, Flight.id == Prediction.flight_id).filter(
            Prediction.risk_level == RiskLevel(risk_level)
        )

    total = query.count()
    offset = (page - 1) * page_size
    flights = query.offset(offset).limit(page_size).all()

    items = []
    for f in flights:
        # Get latest prediction
        pred = db.query(Prediction).filter(
            Prediction.flight_id == f.id
        ).order_by(Prediction.created_at.desc()).first()

        # Get latest assignment
        assignment = db.query(GateAssignment).filter(
            GateAssignment.flight_id == f.id,
            GateAssignment.gate_id.isnot(None),
        ).order_by(GateAssignment.created_at.desc()).first()

        items.append({
            "id": str(f.id),
            "flight_number": f.flight_number,
            "airline": f.airline,
            "aircraft_type": f.aircraft.type_code if f.aircraft else None,
            "aircraft_size": f.aircraft.size_class.value if f.aircraft else None,
            "route_type": f.route_type.value,
            "origin": f.origin,
            "destination": f.destination,
            "runway_code": f.runway.code if f.runway else None,
            "scheduled_arrival": f.scheduled_arrival.isoformat() if f.scheduled_arrival else None,
            "scheduled_departure": f.scheduled_departure.isoformat() if f.scheduled_departure else None,
            "actual_arrival": f.actual_arrival.isoformat() if f.actual_arrival else None,
            "actual_departure": f.actual_departure.isoformat() if f.actual_departure else None,
            "is_synthetic": f.is_synthetic,
            "predicted_delay": float(pred.predicted_delay_minutes) if pred else None,
            "predicted_taxi": float(pred.predicted_taxi_minutes) if pred else None,
            "risk_level": pred.risk_level.value if pred else None,
            "gate_code": assignment.gate.code if assignment and assignment.gate else None,
            "gate_id": str(assignment.gate_id) if assignment else None,
        })

    return {
        "items": items,
        "total": total,
        "page": page,
        "page_size": page_size,
    }


@router.post("", status_code=status.HTTP_201_CREATED)
def create_flight(
    body: dict,
    db: Session = Depends(get_db),
):
    """POST /api/flights - create a single flight."""
    from app.pipeline.validation import validate_flight_batch
    from app.pipeline.cleaning import clean_and_normalize_flights

    accepted, errors = validate_flight_batch([body], db)
    if errors:
        e = errors[0]
        raise AppError(
            code="VALIDATION_ERROR",
            message=e.message,
            status_code=422,
            details={"field": e.field, "error_code": e.error_code},
        )

    cleaned = clean_and_normalize_flights(accepted, db)
    flight = Flight(**cleaned[0])
    db.add(flight)
    db.commit()
    db.refresh(flight)

    return {
        "id": str(flight.id),
        "flight_number": flight.flight_number,
        "airline": flight.airline,
        "route_type": flight.route_type.value,
        "scheduled_arrival": flight.scheduled_arrival.isoformat(),
        "scheduled_departure": flight.scheduled_departure.isoformat(),
    }


@router.get("/{flight_id}")
def get_flight_detail(
    flight_id: str,
    db: Session = Depends(get_db),
):
    """GET /api/flights/{id} with prediction and assignment."""
    flight = db.query(Flight).options(
        joinedload(Flight.aircraft),
        joinedload(Flight.runway),
    ).filter(Flight.id == flight_id).first()

    if not flight:
        raise AppError(code="NOT_FOUND", message="Flight not found", status_code=404)

    pred = db.query(Prediction).filter(
        Prediction.flight_id == flight.id
    ).order_by(Prediction.created_at.desc()).first()

    assignment = db.query(GateAssignment).filter(
        GateAssignment.flight_id == flight.id,
        GateAssignment.gate_id.isnot(None),
    ).order_by(GateAssignment.created_at.desc()).first()

    return {
        "id": str(flight.id),
        "flight_number": flight.flight_number,
        "airline": flight.airline,
        "aircraft": {
            "registration": flight.aircraft.registration if flight.aircraft else None,
            "type_code": flight.aircraft.type_code if flight.aircraft else None,
            "size_class": flight.aircraft.size_class.value if flight.aircraft else None,
        },
        "route_type": flight.route_type.value,
        "origin": flight.origin,
        "destination": flight.destination,
        "runway": {
            "code": flight.runway.code if flight.runway else None,
            "status": flight.runway.status.value if flight.runway else None,
            "taxi_base_minutes": float(flight.runway.taxi_base_minutes) if flight.runway else None,
        },
        "scheduled_arrival": flight.scheduled_arrival.isoformat() if flight.scheduled_arrival else None,
        "scheduled_departure": flight.scheduled_departure.isoformat() if flight.scheduled_departure else None,
        "actual_arrival": flight.actual_arrival.isoformat() if flight.actual_arrival else None,
        "actual_departure": flight.actual_departure.isoformat() if flight.actual_departure else None,
        "is_synthetic": flight.is_synthetic,
        "prediction": {
            "id": str(pred.id),
            "predicted_taxi_minutes": float(pred.predicted_taxi_minutes),
            "predicted_delay_minutes": float(pred.predicted_delay_minutes),
            "risk_level": pred.risk_level.value,
            "model_version": pred.model_version,
            "feature_snapshot": pred.feature_snapshot,
        } if pred else None,
        "assignment": {
            "id": str(assignment.id),
            "gate_id": str(assignment.gate_id),
            "gate_code": assignment.gate.code if assignment and assignment.gate else None,
            "assignment_status": assignment.assignment_status.value,
            "objective_contribution": float(assignment.objective_contribution) if assignment and assignment.objective_contribution else None,
        } if assignment else None,
    }
