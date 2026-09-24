import pytest
from app.core.db import SessionLocal
from app.models import Flight, Gate, Runway, CascadeEvent
from app.services.cascade import analyze_cascade


@pytest.fixture
def db():
    session = SessionLocal()
    yield session
    session.close()


def test_cascade_analysis_runway(db):
    rwy = db.query(Runway).first()
    assert rwy is not None

    res = analyze_cascade(db, root_runway_id=str(rwy.id))
    assert "cascade_event_id" in res
    assert "propagation_path" in res
    assert "affected_flight_ids" in res
    assert res["max_depth_reached"] <= 5
    assert res["severity"] in ["LOW", "MEDIUM", "HIGH"]

    # Verify event stored in DB
    event = db.query(CascadeEvent).filter(CascadeEvent.id == res["cascade_event_id"]).first()
    assert event is not None
    assert str(event.root_runway_id) == str(rwy.id)


def test_cascade_analysis_flight(db):
    flight = db.query(Flight).first()
    assert flight is not None

    res = analyze_cascade(db, root_flight_id=str(flight.id))
    assert "propagation_path" in res
    assert len(res["propagation_path"]) >= 1
    assert res["propagation_path"][0]["identifier"] == flight.flight_number
