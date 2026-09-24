from typing import Optional, List
from fastapi import APIRouter, Depends, Query, status
from sqlalchemy.orm import Session
from sqlalchemy import desc

from app.api.dependencies import get_db
from app.services.prediction_service import PredictionService
from app.models.prediction import DelayPrediction
from app.schemas.prediction import (
    PredictionRequest,
    PredictionResponse,
    BatchPredictionRequest,
    BatchPredictionResponse,
    FeatureImportanceResponse,
    ModelMetricsResponse
)

router = APIRouter(prefix="/predictions", tags=["Predictions"])


@router.post("/predict", response_model=PredictionResponse, summary="Predict Delay for a Single Flight")
def predict_single(request: PredictionRequest, db: Session = Depends(get_db)):
    return PredictionService.predict_single(db, request)


@router.post("/batch", response_model=BatchPredictionResponse, summary="Batch Delay Prediction for Multiple Flights")
def predict_batch(request: BatchPredictionRequest, db: Session = Depends(get_db)):
    return PredictionService.predict_batch_flights(db, request.flight_ids)


@router.get("/feature-importance", response_model=FeatureImportanceResponse, summary="Get Model Feature Importance")
def get_feature_importance():
    return PredictionService.get_feature_importance()


@router.get("/metrics", response_model=ModelMetricsResponse, summary="Get Model Performance and Evaluation Metrics")
def get_model_metrics():
    return PredictionService.get_model_metrics()


@router.get("/{flight_id}", response_model=PredictionResponse, summary="Get Delay Prediction for a specific Flight ID")
def get_flight_prediction(flight_id: int, db: Session = Depends(get_db)):
    pred = (
        db.query(DelayPrediction)
        .filter(DelayPrediction.flight_id == flight_id)
        .order_by(desc(DelayPrediction.prediction_timestamp))
        .first()
    )
    if not pred:
        # Generate on the fly
        res = PredictionService.predict_batch_flights(db, [flight_id])
        if res.predictions:
            return res.predictions[0]
        # Return fallback
        return PredictionResponse(
            flight_number=f"FLIGHT-{flight_id}",
            flight_id=flight_id,
            predicted_delay_minutes=0.0,
            delay_category="On Time",
            confidence_score=0.85,
            model_version="1.0.0",
            model_name="Gradient Boosting"
        )

    return PredictionResponse(
        flight_number=pred.flight_number or f"FLIGHT-{flight_id}",
        flight_id=pred.flight_id,
        predicted_delay_minutes=pred.predicted_delay_minutes,
        delay_category=pred.delay_category,
        confidence_score=pred.confidence_score or 0.88,
        model_version=pred.model_version or "1.0.0",
        model_name="Gradient Boosting Regressor",
        timestamp=pred.prediction_timestamp
    )
