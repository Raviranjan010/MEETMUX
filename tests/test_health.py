from fastapi.testclient import TestClient
from unittest.mock import patch
from app.main import app

client = TestClient(app)


def test_root_endpoint():
    response = client.get("/")
    assert response.status_code == 200
    data = response.json()
    assert data["name"] == "RunwayOptX"
    assert data["status"] == "online"


def test_health_endpoint_structure():
    response = client.get("/api/health")
    assert response.status_code == 200
    data = response.json()

    # Assert required fields per ACCEPTANCE_CRITERIA.md AC-P1
    assert "status" in data
    assert "database" in data
    assert "ml_model_loaded" in data
    assert "optimizer" in data

    assert isinstance(data["database"], bool)
    assert isinstance(data["ml_model_loaded"], bool)
    assert isinstance(data["optimizer"]["gurobi_available"], bool)
    assert isinstance(data["optimizer"]["ortools_available"], bool)

    # In our environment, database is live, ortools is installed
    assert data["database"] is True
    assert data["optimizer"]["ortools_available"] is True
    # Initial startup has no trained model yet (honest reporting)
    assert data["ml_model_loaded"] is False
    assert data["status"] == "ok"


def test_health_endpoint_degraded_when_db_down():
    with patch("app.api.routes.health.check_db_health", return_value=False):
        response = client.get("/api/health")
        assert response.status_code == 200
        data = response.json()
        assert data["database"] is False
        assert data["status"] == "degraded"


def test_health_endpoint_degraded_when_no_solvers():
    with patch("app.api.routes.health.check_gurobi", return_value=False), \
         patch("app.api.routes.health.check_ortools", return_value=False):
        response = client.get("/api/health")
        assert response.status_code == 200
        data = response.json()
        assert data["optimizer"]["gurobi_available"] is False
        assert data["optimizer"]["ortools_available"] is False
        assert data["status"] == "degraded"


def test_error_shape_on_not_found():
    response = client.get("/api/non-existent-route")
    assert response.status_code == 404
    data = response.json()
    assert "error" in data
    assert data["error"]["code"] == "NOT_FOUND"
    assert "request_id" in data["error"]
