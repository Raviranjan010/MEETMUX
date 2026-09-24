import pytest
from app.core.db import SessionLocal
from app.models import Flight, Gate, SystemConfig
from app.models.enums import GateStatus, AircraftSizeClass, RouteType
from app.optimizer.validator import validate_solution


@pytest.fixture
def db():
    session = SessionLocal()
    yield session
    session.close()


def test_validator_rejects_missing_assignment(db):
    flights = db.query(Flight).limit(5).all()
    gates = db.query(Gate).limit(5).all()
    config = db.query(SystemConfig).first()

    # Only assign flights 0, 1, 2, leaving 3 and 4 missing completely (not even unassigned)
    assignments = [
        {"flight_index": 0, "gate_index": 0},
        {"flight_index": 1, "gate_index": 1},
        {"flight_index": 2, "gate_index": 2},
    ]

    report = validate_solution(flights, gates, assignments, config)
    assert report["passed"] is False
    assert any(v["constraint"] == "EXACTLY_ONE_GATE" for v in report["violations"])


def test_validator_detects_overlap(db):
    flights = db.query(Flight).limit(2).all()
    gates = db.query(Gate).limit(2).all()
    config = db.query(SystemConfig).first()

    # Force two flights with overlapping times to the same gate
    flights[0].scheduled_arrival = flights[1].scheduled_arrival
    flights[0].scheduled_departure = flights[1].scheduled_departure

    assignments = [
        {"flight_index": 0, "gate_index": 0},
        {"flight_index": 1, "gate_index": 0},
    ]

    report = validate_solution(flights, gates, assignments, config)
    assert report["passed"] is False
    assert any(v["constraint"] == "TURNAROUND_OVERLAP" for v in report["violations"])
