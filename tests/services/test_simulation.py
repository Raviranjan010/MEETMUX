import pytest
from app.core.db import SessionLocal
from app.models import Runway, Gate, WeatherRecord, Flight
from app.models.enums import RunwayStatus, GateStatus, WeatherCondition
from app.services.simulation import run_scenario, reset_scenarios


@pytest.fixture
def db():
    session = SessionLocal()
    yield session
    session.close()


def test_scenario_runway_closure_mutates_state(db):
    res = run_scenario(db, "RUNWAY_CLOSURE", "RWY-2", {})
    assert res["target_reference"] == "RWY-2"
    assert res["state_changes"]["new_status"] == "CLOSED"

    # Verify real DB state changed
    rwy = db.query(Runway).filter(Runway.code == "RWY-2").first()
    assert rwy.status == RunwayStatus.CLOSED

    # Reset
    reset_scenarios(db)
    rwy = db.query(Runway).filter(Runway.code == "RWY-2").first()
    assert rwy.status == RunwayStatus.ACTIVE


def test_scenario_gate_closure_mutates_state(db):
    res = run_scenario(db, "GATE_CLOSURE", "A1", {})
    assert res["target_reference"] == "A1"
    assert res["state_changes"]["new_status"] == "BLOCKED"

    gate = db.query(Gate).filter(Gate.code == "A1").first()
    assert gate.status == GateStatus.BLOCKED

    # Reset
    reset_scenarios(db)
    gate = db.query(Gate).filter(Gate.code == "A1").first()
    assert gate.status == GateStatus.AVAILABLE


def test_scenario_heavy_rain(db):
    res = run_scenario(db, "HEAVY_RAIN", "DFW", {"wind_speed_kt": 30.0})
    weather = db.query(WeatherRecord).order_by(WeatherRecord.recorded_at.desc()).first()
    assert weather.condition == WeatherCondition.HEAVY_RAIN
    assert weather.wind_speed_kt == 30.0

    # Reset
    reset_scenarios(db)
    weather = db.query(WeatherRecord).order_by(WeatherRecord.recorded_at.desc()).first()
    assert weather.condition == WeatherCondition.CLEAR
