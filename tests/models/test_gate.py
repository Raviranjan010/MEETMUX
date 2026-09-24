import pytest
from app.core.db import SessionLocal
from app.models import Gate, Flight, Aircraft
from app.models.enums import (
    GateStatus, GateType, GateEligibleRouteType, AircraftSizeClass, RouteType,
)
from app.services.baseline import is_gate_compatible


@pytest.fixture
def db():
    session = SessionLocal()
    yield session
    session.close()


def test_gate_model_attributes(db):
    gates = db.query(Gate).all()
    assert len(gates) == 30

    for g in gates:
        assert g.code is not None
        assert g.terminal is not None
        assert g.gate_type in [GateType.JETBRIDGE, GateType.REMOTE]
        assert g.status in [
            GateStatus.AVAILABLE,
            GateStatus.OCCUPIED,
            GateStatus.RESERVED,
            GateStatus.BLOCKED,
            GateStatus.CONFLICT,
        ]
        assert g.eligible_route_types in [
            GateEligibleRouteType.DOMESTIC,
            GateEligibleRouteType.INTERNATIONAL,
            GateEligibleRouteType.BOTH,
        ]
        assert g.max_aircraft_size in [
            AircraftSizeClass.SMALL,
            AircraftSizeClass.MEDIUM,
            AircraftSizeClass.LARGE,
        ]


def test_gate_compatibility_aircraft_size():
    large_gate = Gate(
        code="G01",
        status=GateStatus.AVAILABLE,
        eligible_route_types=GateEligibleRouteType.BOTH,
        max_aircraft_size=AircraftSizeClass.LARGE,
    )
    small_gate = Gate(
        code="G02",
        status=GateStatus.AVAILABLE,
        eligible_route_types=GateEligibleRouteType.BOTH,
        max_aircraft_size=AircraftSizeClass.SMALL,
    )

    large_aircraft = Aircraft(type_code="B77W", size_class=AircraftSizeClass.LARGE)
    small_aircraft = Aircraft(type_code="CRJ9", size_class=AircraftSizeClass.SMALL)

    f_large = Flight(aircraft=large_aircraft, route_type=RouteType.DOMESTIC)
    f_small = Flight(aircraft=small_aircraft, route_type=RouteType.DOMESTIC)

    assert is_gate_compatible(f_large, large_gate) is True
    assert is_gate_compatible(f_large, small_gate) is False
    assert is_gate_compatible(f_small, small_gate) is True


def test_gate_compatibility_route_types():
    intl_gate = Gate(
        code="G03",
        status=GateStatus.AVAILABLE,
        eligible_route_types=GateEligibleRouteType.INTERNATIONAL,
        max_aircraft_size=AircraftSizeClass.LARGE,
    )
    dom_gate = Gate(
        code="G04",
        status=GateStatus.AVAILABLE,
        eligible_route_types=GateEligibleRouteType.DOMESTIC,
        max_aircraft_size=AircraftSizeClass.LARGE,
    )

    aircraft = Aircraft(type_code="A320", size_class=AircraftSizeClass.MEDIUM)
    f_dom = Flight(aircraft=aircraft, route_type=RouteType.DOMESTIC)
    f_intl = Flight(aircraft=aircraft, route_type=RouteType.INTERNATIONAL)

    assert is_gate_compatible(f_dom, intl_gate) is False
    assert is_gate_compatible(f_intl, intl_gate) is True
    assert is_gate_compatible(f_dom, dom_gate) is True
    assert is_gate_compatible(f_intl, dom_gate) is False


def test_blocked_gate_rejected():
    gate = Gate(
        code="G05",
        status=GateStatus.BLOCKED,
        eligible_route_types=GateEligibleRouteType.BOTH,
        max_aircraft_size=AircraftSizeClass.LARGE,
    )
    aircraft = Aircraft(type_code="A320", size_class=AircraftSizeClass.MEDIUM)
    flight = Flight(aircraft=aircraft, route_type=RouteType.DOMESTIC)

    assert is_gate_compatible(flight, gate) is False
