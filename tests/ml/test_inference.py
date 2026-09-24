import pytest
from app.core.db import SessionLocal
from app.models import Flight, SystemConfig, WeatherRecord
from app.ml.registry import registry
from app.ml.predict import predict_for_flight, predict_batch
from fastapi.testclient import TestClient
from app.main import app

client = TestClient(app)


@pytest.fixture
def db():
    session = SessionLocal()
    yield session
    session.close()


def test_registry_loads_model():
    loaded = registry.load_latest()
    assert loaded is True
    assert registry.is_loaded() is True
    assert registry.current_version is not None


def test_predict_for_single_flight(db):
    flight = db.query(Flight).first()
    assert flight is not None

    result = predict_for_flight(flight, db, persist=False)

    assert "predicted_taxi_minutes" in result
    assert "predicted_delay_minutes" in result
    assert "risk_level" in result
    assert result["predicted_taxi_minutes"] >= 5.0
    assert result["predicted_delay_minutes"] >= 0.0
    assert result["risk_level"] in ["LOW", "MEDIUM", "HIGH"]
    assert result["model_version"] == registry.current_version


def test_predictions_api_metrics():
    response = client.get("/api/predictions/metrics")
    assert response.status_code == 200
    data = response.json()
    assert "mae" in data
    assert "rmse" in data
    assert "r2" in data
    assert data["mae"] > 0
    assert data["r2"] > 0.8


def test_predictions_api_batch():
    response = client.post("/api/predictions/batch")
    assert response.status_code == 201
    data = response.json()
    assert data["count"] >= 100
    assert len(data["predictions"]) >= 100
