import pytest
from datetime import datetime, timedelta
from fastapi.testclient import TestClient

from app.main import app
from app.database.database import SessionLocal, Base, engine


@pytest.fixture
def client():
    with TestClient(app) as test_client:
        yield test_client


def test_health_endpoint(client):
    response = client.get("/api/health")
    assert response.status_code == 200
    data = response.json()
    assert data["status"] in ["healthy", "degraded"]
    assert data["database"] == "connected"
    assert data["optimizer"] == "available"


def test_list_flights_endpoint(client):
    response = client.get("/api/flights?page=1&page_size=10")
    assert response.status_code == 200
    data = response.json()
    assert "items" in data
    assert "total" in data
    assert len(data["items"]) > 0
    assert "flight_number" in data["items"][0]


def test_list_gates_endpoint(client):
    response = client.get("/api/gates")
    assert response.status_code == 200
    data = response.json()
    assert "items" in data
    assert len(data["items"]) == 12


def test_predict_single_endpoint(client):
    payload = {
        "flight_number": "AI999",
        "airline": "Air India",
        "aircraft_type": "A320",
        "origin": "DEL",
        "destination": "BOM",
        "terminal": "T3",
        "scheduled_arrival": datetime.utcnow().isoformat(),
        "scheduled_departure": (datetime.utcnow() + timedelta(hours=2)).isoformat(),
        "temperature": 30.0,
        "wind_speed": 14.0,
        "visibility": 6.0,
        "precipitation": 0.0,
        "weather_condition": "Clear",
        "active_flights": 35
    }
    response = client.post("/api/predictions/predict", json=payload)
    assert response.status_code == 200
    data = response.json()
    assert data["flight_number"] == "AI999"
    assert "predicted_delay_minutes" in data
    assert "delay_category" in data


def test_feature_importance_endpoint(client):
    response = client.get("/api/predictions/feature-importance")
    assert response.status_code == 200
    data = response.json()
    assert "features" in data
    assert len(data["features"]) > 0


def test_run_optimization_endpoint(client):
    payload = {
        "solver": "ortools",
        "time_limit_seconds": 30,
        "weights": {
            "conflict": 1000.0,
            "walking_distance": 1.0,
            "delay_propagation": 10.0,
            "reassignment": 5.0,
            "unused_gate": 1.0
        }
    }
    response = client.post("/api/optimization/run", json=payload)
    assert response.status_code == 200
    data = response.json()
    assert data["status"] in ["optimal", "feasible"]
    assert "optimization_run_id" in data
    assert "assignments" in data
    assert len(data["assignments"]) > 0


def test_dashboard_summary_endpoint(client):
    response = client.get("/api/dashboard/summary")
    assert response.status_code == 200
    data = response.json()
    assert "kpis" in data
    assert data["kpis"]["total_flights"] > 0
    assert "delay_distribution" in data
    assert "delay_by_airline" in data
    assert "congestion_by_hour" in data
    assert "gate_occupancy" in data
