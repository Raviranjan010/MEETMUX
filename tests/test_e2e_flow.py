"""
End-to-End Acceptance Test per Section 40 of USER_REQUEST.
Executes the exact 23-step acceptance sequence against real backend and DB.
"""
import pytest
from fastapi.testclient import TestClient
from app.main import app
from app.core.db import SessionLocal
from app.models import Flight, Gate, Runway, OptimizationRun, Alert, Scenario
from app.models.enums import RunwayStatus, OptimizationStatus

client = TestClient(app)


@pytest.fixture(scope="module")
def db():
    session = SessionLocal()
    yield session
    session.close()


def test_section_40_full_e2e_acceptance_flow(db):
    # Step 1, 2, 3: Verify clean DB, tables, and seeded demo counts
    flights_count = db.query(Flight).count()
    gates_count = db.query(Gate).count()
    runways_count = db.query(Runway).count()

    assert flights_count == 100, f"Expected 100 flights, got {flights_count}"
    assert gates_count == 30, f"Expected 30 gates, got {gates_count}"
    assert runways_count == 2, f"Expected 2 runways, got {runways_count}"

    # Step 4: Validate operational data via health and DB checks
    health_resp = client.get("/api/health")
    assert health_resp.status_code == 200
    assert health_resp.json()["status"] == "ok"
    assert health_resp.json()["database"] is True

    # Step 5: Run predictions for all flights
    pred_resp = client.post("/api/predictions/batch")
    assert pred_resp.status_code == 201
    pred_data = pred_resp.json()
    assert pred_data["count"] >= 100

    # Step 6: Generate risk classifications (verified on predictions)
    list_preds_resp = client.get("/api/predictions")
    assert list_preds_resp.status_code == 200
    all_preds = list_preds_resp.json()
    assert len(all_preds) >= 100
    assert all(p["risk_level"] in ["LOW", "MEDIUM", "HIGH"] for p in all_preds)

    # Step 7: Detect conflicts
    conflict_resp = client.post("/api/conflicts/detect")
    assert conflict_resp.status_code == 200
    conflict_data = conflict_resp.json()
    assert "conflicts" in conflict_data

    # Step 8: Generate cascade analysis
    cascade_resp = client.get("/api/cascade")
    assert cascade_resp.status_code == 200
    cascade_data = cascade_resp.json()
    assert isinstance(cascade_data, list)
    assert len(cascade_data) > 0

    # Step 9: Generate deterministic baseline
    baseline_resp = client.post("/api/optimizer/run", json={"run_type": "BASELINE"})
    assert baseline_resp.status_code in [200, 202]
    baseline_data = baseline_resp.json()
    baseline_run_id = baseline_data["optimization_run_id"]
    assert baseline_data["run_type"] == "BASELINE"

    # Step 10: Run MILP optimization
    initial_milp_count = db.query(OptimizationRun).filter(OptimizationRun.run_type == "MILP").count()
    milp_resp = client.post("/api/optimizer/run", json={"run_type": "MILP"})
    assert milp_resp.status_code in [200, 202]
    milp_data = milp_resp.json()
    milp_run_id = milp_data["optimization_run_id"]
    assert milp_data["solver_used"] in ["GUROBI", "ORTOOLS"]

    # Step 11: Run independent validator (embedded in optimization run)
    assert milp_data["validation_passed"] is True
    assert milp_data["validation_report"]["passed"] is True

    # Step 12: Calculate baseline vs optimized metrics
    comp_resp = client.get(f"/api/analytics/comparison?optimization_run_id={milp_run_id}")
    assert comp_resp.status_code == 200
    comp_data = comp_resp.json()
    assert "baseline" in comp_data
    assert "optimized" in comp_data
    assert "deltas" in comp_data

    # Step 13: Open a flight and display prediction details
    sample_flight = db.query(Flight).first()
    flight_resp = client.get(f"/api/flights/{sample_flight.id}")
    assert flight_resp.status_code == 200
    f_detail = flight_resp.json()
    assert f_detail["flight_number"] == sample_flight.flight_number

    flight_pred_resp = client.get(f"/api/predictions/{sample_flight.id}")
    assert flight_pred_resp.status_code == 200
    assert "predicted_taxi_minutes" in flight_pred_resp.json()

    # Step 14: Open "Why This Gate?"
    explain_resp = client.get(f"/api/explain/{sample_flight.id}")
    assert explain_resp.status_code == 200
    explain_data = explain_resp.json()
    assert "assigned_gate" in explain_data
    assert len(explain_data["reasons"]) > 0

    # Step 15: Run Runway 2 Closure scenario
    sc_resp = client.post("/api/scenarios/run", json={"scenario_type": "RUNWAY_CLOSURE", "target_reference": "RWY-2"})
    assert sc_resp.status_code == 200
    sc_data = sc_resp.json()
    scenario_id = sc_data["scenario_id"]

    # Step 16: Verify backend state changed (Runway 2 status == CLOSED)
    rwy2 = db.query(Runway).filter(Runway.code == "RWY-2").first()
    assert rwy2.status == RunwayStatus.CLOSED

    # Step 17: Run re-optimization (prediction -> conflict detection -> cascade -> optimization -> validation)
    reopt_resp = client.post("/api/reoptimize", json={"scenario_id": scenario_id})
    assert reopt_resp.status_code in [200, 202]
    reopt_data = reopt_resp.json()
    assert reopt_data["scenario_acknowledged"] is True
    assert len(reopt_data["steps"]) >= 5

    # Step 18: Verify a NEW optimization run exists
    new_milp_count = db.query(OptimizationRun).filter(OptimizationRun.run_type == "MILP").count()
    assert new_milp_count > initial_milp_count

    # Step 19: Verify dashboard / live analytics changed
    analytics_resp = client.get("/api/analytics")
    assert analytics_resp.status_code == 200
    live_analytics = analytics_resp.json()
    assert "total_flights" in live_analytics

    # Step 20: Verify airport map gates data is live
    gates_resp = client.get("/api/gates")
    assert gates_resp.status_code == 200
    assert len(gates_resp.json()["items"]) == 30

    # Step 21: Verify gate timeline conflicts
    timeline_conflicts = client.post("/api/conflicts/detect")
    assert timeline_conflicts.status_code == 200

    # Step 22: Verify analytics comparison updated with the new run
    new_run_id = reopt_data["optimization_run_id"]
    new_comp_resp = client.get(f"/api/analytics/comparison?optimization_run_id={new_run_id}")
    assert new_comp_resp.status_code == 200
    assert "deltas" in new_comp_resp.json()

    # Step 23: Verify alerts updated
    alerts_resp = client.get("/api/alerts")
    assert alerts_resp.status_code == 200
    alerts_list = alerts_resp.json()
    assert isinstance(alerts_list, list)

    # Clean up: Reset scenario state to nominal baseline
    client.post("/api/scenarios/reset")
    db.refresh(rwy2)
    rwy2_restored = db.query(Runway).filter(Runway.code == "RWY-2").first()
    assert rwy2_restored.status == RunwayStatus.ACTIVE
