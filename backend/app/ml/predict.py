import logging
from typing import Dict, Any, Optional, List
from datetime import datetime, timezone
import pandas as pd
from sqlalchemy.orm import Session

from app.models import Flight, Runway, WeatherRecord, Gate, SystemConfig, Prediction
from app.models.enums import RiskLevel, WeatherCondition
from app.ml.registry import registry
from app.ml.features import (
    FEATURE_COLUMNS,
    compute_flight_features,
    compute_input_hash,
)
from app.ml.risk import classify_flight_risk
from app.core.errors import AppError

logger = logging.getLogger(__name__)


def predict_for_flight(
    flight: Flight,
    db: Session,
    weather: Optional[WeatherRecord] = None,
    config: Optional[SystemConfig] = None,
    persist: bool = True,
) -> Dict[str, Any]:
    """
    Runs delay prediction for a single flight using the loaded ML model.
    Throws AppError(503, MODEL_UNAVAILABLE) if model is not loaded.
    """
    if not registry.is_loaded():
        # Attempt to load
        loaded = registry.load_latest()
        if not loaded:
            raise AppError(
                code="MODEL_UNAVAILABLE",
                message="ML prediction model is not available. Please train or deploy a model first.",
                status_code=503,
            )

    # 1. Resolve runway base taxi time
    runway = flight.runway
    runway_code = runway.code if runway else "RWY-1"
    taxi_base_minutes = runway.taxi_base_minutes if runway else 12.0

    # 2. Resolve weather
    if weather is None:
        weather = db.query(WeatherRecord).order_by(WeatherRecord.recorded_at.desc()).first()
    weather_cond = weather.condition.value if weather else "CLEAR"

    # 3. Resolve aircraft size class
    size_class = flight.aircraft.size_class.value if flight.aircraft else "MEDIUM"

    # 4. Resolve gate type if assigned
    gate_type = None
    if flight.assigned_gate:
        gate_type = flight.assigned_gate.gate_type.value

    # 5. Traffic density in 30-min window (schedule-based, non-leaking)
    start_win = flight.scheduled_arrival
    from datetime import timedelta
    win_start = start_win - timedelta(minutes=15)
    win_end = start_win + timedelta(minutes=15)
    traffic_density = (
        db.query(Flight)
        .filter(
            Flight.scheduled_arrival >= win_start,
            Flight.scheduled_arrival <= win_end,
            Flight.id != flight.id,
        )
        .count()
    )

    # 6. Extract features
    features = compute_flight_features(
        scheduled_arrival=flight.scheduled_arrival,
        route_type=flight.route_type.value,
        aircraft_size_class=size_class,
        airline=flight.airline,
        runway_code=runway_code,
        weather_condition=weather_cond,
        traffic_density_30m=traffic_density,
        gate_type=gate_type,
    )
    input_hash = compute_input_hash(features)

    # 7. Model inference
    df_feat = pd.DataFrame([features])[FEATURE_COLUMNS]
    predicted_taxi = float(registry.current_model.predict(df_feat)[0])
    predicted_taxi = max(5.0, round(predicted_taxi, 2))

    # Delay is derived: predicted_taxi - scheduled_base
    predicted_delay = max(0.0, round(predicted_taxi - taxi_base_minutes, 2))

    # 8. Risk classification
    if config is None:
        config = db.query(SystemConfig).first()
    risk_level = classify_flight_risk(predicted_delay, config)

    # Provenance log per AC-P4
    logger.info(
        f"Prediction [flight={flight.flight_number}, model_ver={registry.current_version}, "
        f"hash={input_hash}]: taxi={predicted_taxi}m, delay={predicted_delay}m, risk={risk_level.value}"
    )

    # Prediction explanation factors
    factors = {
        "base_taxi_minutes": taxi_base_minutes,
        "runway": runway_code,
        "traffic_density_30m": traffic_density,
        "weather_condition": weather_cond,
        "aircraft_size_class": size_class,
        "input_hash": input_hash,
    }

    result = {
        "flight_id": str(flight.id),
        "flight_number": flight.flight_number,
        "model_version": registry.current_version,
        "input_hash": input_hash,
        "predicted_taxi_minutes": predicted_taxi,
        "predicted_delay_minutes": predicted_delay,
        "risk_level": risk_level.value,
        "confidence_score": 0.88,  # Based on model test R2
        "factors": factors,
    }

    if persist:
        # Create or update prediction record in DB
        pred_record = Prediction(
            flight_id=flight.id,
            model_version=registry.current_version or "v1",
            predicted_taxi_minutes=predicted_taxi,
            predicted_delay_minutes=predicted_delay,
            risk_level=risk_level,
            confidence_score=0.88,
            factors=factors,
        )
        db.add(pred_record)
        db.commit()
        result["prediction_id"] = str(pred_record.id)

    return result
