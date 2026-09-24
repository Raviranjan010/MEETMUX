import pytest
from fastapi import HTTPException
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


def test_reset_does_not_reopen_runways_without_a_closure_scenario(db):
    runway = db.query(Runway).filter(Runway.code == "RWY-1").first()
    runway.status = RunwayStatus.CLOSED
    db.commit()
    reset_scenarios(db)
    db.refresh(runway)
    assert runway.status == RunwayStatus.CLOSED
    runway.status = RunwayStatus.ACTIVE
    db.commit()


def test_scenario_gate_closure_mutates_state(db):
    gate_code = db.query(Gate).first().code
    res = run_scenario(db, "GATE_CLOSURE", gate_code, {})
    assert res["target_reference"] == gate_code
    assert res["state_changes"]["new_status"] == "BLOCKED"

    gate = db.query(Gate).filter(Gate.code == gate_code).first()
    assert gate.status == GateStatus.BLOCKED

    # Reset
    reset_scenarios(db)
    gate = db.query(Gate).filter(Gate.code == gate_code).first()
    assert gate.status == GateStatus.AVAILABLE


def test_scenario_heavy_rain(db):
    res = run_scenario(db, "HEAVY_RAIN", "DFW", {"wind_speed_kt": 30.0})
    from datetime import datetime
    recorded_at = datetime.fromisoformat(res["state_changes"]["recorded_at"])
    weather = db.query(WeatherRecord).filter(WeatherRecord.recorded_at == recorded_at).first()
    assert weather is not None
    assert weather.condition == WeatherCondition.HEAVY_RAIN
    assert weather.wind_speed_kt == 30.0

    # Reset
    reset_scenarios(db)
    assert db.query(WeatherRecord).filter(WeatherRecord.recorded_at == recorded_at).first() is None


def test_scenario_rejects_unknown_target_without_persisting(db):
    before = db.query(WeatherRecord).count()
    with pytest.raises(HTTPException) as error:
        run_scenario(db, "HEAVY_RAIN", "UNKNOWN", {})
    assert error.value.status_code == 404
    assert db.query(WeatherRecord).count() == before
