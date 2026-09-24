"""
Prediction routes per docs/API.md.
"""
import logging
from typing import Optional, List
from fastapi import APIRouter, Depends, status
from pydantic import BaseModel
from sqlalchemy.orm import Session

from app.core.db import get_db
from app.core.errors import AppError
from app.models import Flight, Prediction
from app.ml.predict import predict_for_flight, predict_batch

router = APIRouter(prefix="/predictions", tags=["Predictions"])
logger = logging.getLogger(__name__)


class PredictionRequest(BaseModel):
    flight_id: Optional[str] = None
    flight_ids: Optional[List[str]] = None


@router.post("", status_code=status.HTTP_201_CREATED)
def run_predictions(
    body: PredictionRequest,
    db: Session = Depends(get_db),
):
    """POST /api/predictions - run prediction(s)."""
    if body.flight_ids:
        results = predict_batch(body.flight_ids, db)
        return results
    
    if body.flight_id:
        flight = db.query(Flight).filter(Flight.id == body.flight_id).first()
        if not flight:
            raise AppError(code="NOT_FOUND", message="Flight not found", status_code=404)
        result = predict_for_flight(flight, db, persist=True)
        return [result]
    
    # Predict for all flights
    flights = db.query(Flight).all()
    results = predict_batch([str(f.id) for f in flights], db)
    return results


@router.get("/{flight_id}")
def get_prediction(
    flight_id: str,
    db: Session = Depends(get_db),
):
    """GET /api/predictions/{flight_id}."""
    pred = db.query(Prediction).filter(
        Prediction.flight_id == flight_id,
    ).order_by(Prediction.created_at.desc()).first()

    if not pred:
        raise AppError(code="NOT_FOUND", message="No prediction found for this flight", status_code=404)

    return {
        "id": str(pred.id),
        "flight_id": str(pred.flight_id),
        "model_version": pred.model_version,
        "predicted_taxi_minutes": float(pred.predicted_taxi_minutes),
        "predicted_delay_minutes": float(pred.predicted_delay_minutes),
        "risk_level": pred.risk_level.value,
        "feature_snapshot": pred.feature_snapshot,
        "created_at": pred.created_at.isoformat() if pred.created_at else None,
    }
