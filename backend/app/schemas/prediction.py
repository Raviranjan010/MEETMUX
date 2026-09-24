from datetime import datetime
from typing import Optional, List, Dict, Any
from pydantic import BaseModel, ConfigDict, Field


class PredictionRequest(BaseModel):
    flight_number: str = Field(..., example="AI101")
    airline: str = Field(..., example="Air India")
    aircraft_type: str = Field(..., example="A320")
    origin: str = Field(..., example="DEL")
    destination: str = Field(..., example="BOM")
    terminal: str = Field(..., example="T3")
    runway: Optional[str] = Field("RWY-09L", example="RWY-09L")
    scheduled_arrival: datetime = Field(..., example="2026-09-24T14:30:00")
    scheduled_departure: datetime = Field(..., example="2026-09-24T16:00:00")
    temperature: Optional[float] = Field(28.5, example=28.5)
    wind_speed: Optional[float] = Field(12.0, example=12.0)
    visibility: Optional[float] = Field(5.2, example=5.2)
    precipitation: Optional[float] = Field(0.0, example=0.0)
    weather_condition: Optional[str] = Field("Clear", example="Clear")
    active_flights: Optional[int] = Field(42, example=42)
    turnaround_minutes: Optional[float] = Field(45.0, example=45.0)


class BatchPredictionRequest(BaseModel):
    flight_ids: Optional[List[int]] = None
    flights: Optional[List[PredictionRequest]] = None


class PredictionResponse(BaseModel):
    flight_number: str
    flight_id: Optional[int] = None
    predicted_delay_minutes: float
    delay_category: str
    confidence_score: Optional[float] = 0.88
    model_version: str
    model_name: str
    contributing_features: Optional[Dict[str, float]] = None
    timestamp: datetime = Field(default_factory=datetime.utcnow)

    model_config = ConfigDict(from_attributes=True)


class BatchPredictionResponse(BaseModel):
    predictions: List[PredictionResponse]
    total_processed: int
    average_delay_minutes: float


class FeatureImportanceItem(BaseModel):
    name: str
    importance: float


class FeatureImportanceResponse(BaseModel):
    features: List[FeatureImportanceItem]
    model_name: str
    disclaimer: str = "Feature importance reflects relative tree split/weight contributions, not causal guarantees."


class ModelMetricsResponse(BaseModel):
    model_name: str
    version: str
    training_timestamp: str
    features: List[str]
    metrics: Dict[str, Any]
    model_comparisons: List[Dict[str, Any]]
