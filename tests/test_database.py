import pytest
import uuid
from datetime import datetime, timezone
from sqlalchemy import inspect
from sqlalchemy.exc import IntegrityError
from app.core.db import SessionLocal, engine
from app.models import (
    Airport,
    Terminal,
    Runway,
    Gate,
    Aircraft,
    Flight,
    WeatherRecord,
    Prediction,
    OptimizationRun,
    GateAssignment,
    Scenario,
    Alert,
    CascadeEvent,
    AuditRecord,
    SystemConfig,
    RunwayStatus,
    GateType,
    AircraftSizeClass,
    RouteType,
    GateEligibleRouteType,
    GateStatus,
    WeatherCondition,
    RiskLevel,
    RunType,
    SolverUsed,
    OptimizationStatus,
    AssignmentStatus,
    ScenarioType,
    AlertSeverity,
    AlertCategory,
    AuditAction,
)
from scripts.seed_demo import seed_demo_data


@pytest.fixture(scope="module")
def db_session():
    db = SessionLocal()
    yield db
    db.close()


def test_all_14_entity_tables_exist():
    inspector = inspect(engine)
    tables = inspector.get_table_names()

    required_tables = [
        "airports",
        "terminals",
        "runways",
        "gates",
        "aircraft",
        "flights",
        "weather_records",
        "predictions",
        "optimization_runs",
        "gate_assignments",
        "scenarios",
        "alerts",
        "cascade_events",
        "audit_records",
        "system_config",
    ]

    for table in required_tables:
        assert table in tables, f"Expected table '{table}' to exist in database"


def test_seeded_row_counts(db_session):
    # Verify exact counts per REQUIREMENTS NFR-1 and AC-P2
    flights_count = db_session.query(Flight).count()
    gates_count = db_session.query(Gate).count()
    runways_count = db_session.query(Runway).count()
    terminals_count = db_session.query(Terminal).count()
    airports_count = db_session.query(Airport).count()
    config_count = db_session.query(SystemConfig).count()

    assert flights_count == 100, f"Expected 100 flights, got {flights_count}"
    assert gates_count == 30, f"Expected 30 gates, got {gates_count}"
    assert runways_count == 2, f"Expected 2 runways, got {runways_count}"
    assert terminals_count == 3, f"Expected 3 terminals, got {terminals_count}"
    assert airports_count >= 1, "Expected at least 1 airport"
    assert config_count == 1, "Expected 1 system_config row"


def test_seed_idempotency(db_session):
    # Re-running seed script should not change counts
    seed_demo_data()
    assert db_session.query(Flight).count() == 100
    assert db_session.query(Gate).count() == 30
    assert db_session.query(Runway).count() == 2


def test_fk_integrity_terminal_to_airport(db_session):
    # Inserting terminal with invalid airport_id must raise IntegrityError
    invalid_terminal = Terminal(
        airport_id=uuid.uuid4(),
        code="T99",
        name="Invalid Terminal",
    )
    db_session.add(invalid_terminal)
    with pytest.raises(IntegrityError):
        db_session.commit()
    db_session.rollback()


def test_fk_integrity_gate_to_terminal(db_session):
    invalid_gate = Gate(
        terminal_id=uuid.uuid4(),
        code="G999",
        gate_type=GateType.JETBRIDGE,
        max_aircraft_size=AircraftSizeClass.MEDIUM,
        eligible_route_types=GateEligibleRouteType.DOMESTIC,
        status=GateStatus.AVAILABLE,
        taxi_distance_meters=300.0,
    )
    db_session.add(invalid_gate)
    with pytest.raises(IntegrityError):
        db_session.commit()
    db_session.rollback()


def test_fk_integrity_flight_to_aircraft(db_session):
    airport = db_session.query(Airport).first()
    runway = db_session.query(Runway).filter_by(airport_id=airport.id).first()

    invalid_flight = Flight(
        flight_number="XX999",
        airline="XX",
        aircraft_id=uuid.uuid4(),  # Non-existent aircraft
        route_type=RouteType.DOMESTIC,
        scheduled_arrival=datetime.now(timezone.utc),
        scheduled_departure=datetime.now(timezone.utc),
        runway_id=runway.id,
        is_synthetic=True,
    )
    db_session.add(invalid_flight)
    with pytest.raises(IntegrityError):
        db_session.commit()
    db_session.rollback()


def test_fk_integrity_prediction_to_flight(db_session):
    invalid_prediction = Prediction(
        flight_id=uuid.uuid4(),
        model_version="v1.0",
        predicted_taxi_minutes=15.0,
        predicted_delay_minutes=3.0,
        risk_level=RiskLevel.LOW,
        feature_snapshot={"test": 1},
    )
    db_session.add(invalid_prediction)
    with pytest.raises(IntegrityError):
        db_session.commit()
    db_session.rollback()


def test_fk_integrity_runway_to_airport(db_session):
    invalid_runway = Runway(
        airport_id=uuid.uuid4(),
        code="RWY-99",
        status=RunwayStatus.ACTIVE,
        taxi_base_minutes=12.0,
    )
    db_session.add(invalid_runway)
    with pytest.raises(IntegrityError):
        db_session.commit()
    db_session.rollback()


def test_fk_integrity_weather_to_airport(db_session):
    invalid_weather = WeatherRecord(
        airport_id=uuid.uuid4(),
        recorded_at=datetime.now(timezone.utc),
        condition=WeatherCondition.CLEAR,
    )
    db_session.add(invalid_weather)
    with pytest.raises(IntegrityError):
        db_session.commit()
    db_session.rollback()


def test_fk_integrity_flight_to_runway(db_session):
    aircraft = db_session.query(Aircraft).first()
    invalid_flight = Flight(
        flight_number="RWYFAIL",
        airline="AA",
        aircraft_id=aircraft.id,
        route_type=RouteType.DOMESTIC,
        scheduled_arrival=datetime.now(timezone.utc),
        scheduled_departure=datetime.now(timezone.utc),
        runway_id=uuid.uuid4(),
        is_synthetic=True,
    )
    db_session.add(invalid_flight)
    with pytest.raises(IntegrityError):
        db_session.commit()
    db_session.rollback()


def test_fk_integrity_gate_assignment_to_run_and_flight_and_gate(db_session):
    flight = db_session.query(Flight).first()
    gate = db_session.query(Gate).first()

    # 1. Invalid optimization_run_id
    invalid_assignment_1 = GateAssignment(
        optimization_run_id=uuid.uuid4(),
        flight_id=flight.id,
        gate_id=gate.id,
        assignment_status=AssignmentStatus.PROPOSED,
    )
    db_session.add(invalid_assignment_1)
    with pytest.raises(IntegrityError):
        db_session.commit()
    db_session.rollback()

    # Create a valid run to test flight and gate FKs
    valid_run = OptimizationRun(
        run_type=RunType.MILP,
        solver_used=SolverUsed.ORTOOLS,
        solver_status="OPTIMAL",
        status=OptimizationStatus.OPTIMAL,
        config_snapshot={},
    )
    db_session.add(valid_run)
    db_session.commit()

    try:
        # 2. Invalid flight_id
        invalid_assignment_2 = GateAssignment(
            optimization_run_id=valid_run.id,
            flight_id=uuid.uuid4(),
            gate_id=gate.id,
            assignment_status=AssignmentStatus.PROPOSED,
        )
        db_session.add(invalid_assignment_2)
        with pytest.raises(IntegrityError):
            db_session.commit()
        db_session.rollback()

        # 3. Invalid gate_id
        invalid_assignment_3 = GateAssignment(
            optimization_run_id=valid_run.id,
            flight_id=flight.id,
            gate_id=uuid.uuid4(),
            assignment_status=AssignmentStatus.PROPOSED,
        )
        db_session.add(invalid_assignment_3)
        with pytest.raises(IntegrityError):
            db_session.commit()
        db_session.rollback()
    finally:
        db_session.delete(valid_run)
        db_session.commit()


def test_fk_integrity_optimization_run_to_scenario(db_session):
    invalid_run = OptimizationRun(
        run_type=RunType.MILP,
        scenario_id=uuid.uuid4(),
        solver_used=SolverUsed.ORTOOLS,
        solver_status="OPTIMAL",
        status=OptimizationStatus.OPTIMAL,
        config_snapshot={},
    )
    db_session.add(invalid_run)
    with pytest.raises(IntegrityError):
        db_session.commit()
    db_session.rollback()


def test_fk_integrity_scenario_to_optimization_run(db_session):
    invalid_scenario = Scenario(
        type=ScenarioType.RUNWAY_CLOSURE,
        target_reference="RWY-1",
        params={},
        resulting_optimization_run_id=uuid.uuid4(),
    )
    db_session.add(invalid_scenario)
    with pytest.raises(IntegrityError):
        db_session.commit()
    db_session.rollback()


def test_fk_integrity_alerts_to_flight_and_gate(db_session):
    invalid_alert_flight = Alert(
        severity=AlertSeverity.WARNING,
        category=AlertCategory.HIGH_RISK,
        flight_id=uuid.uuid4(),
        message="Invalid flight alert",
    )
    db_session.add(invalid_alert_flight)
    with pytest.raises(IntegrityError):
        db_session.commit()
    db_session.rollback()

    invalid_alert_gate = Alert(
        severity=AlertSeverity.CRITICAL,
        category=AlertCategory.CONFLICT,
        gate_id=uuid.uuid4(),
        message="Invalid gate alert",
    )
    db_session.add(invalid_alert_gate)
    with pytest.raises(IntegrityError):
        db_session.commit()
    db_session.rollback()


def test_fk_integrity_cascade_event_relationships(db_session):
    # Invalid root_flight_id
    c1 = CascadeEvent(
        root_flight_id=uuid.uuid4(),
        propagation_path=[],
        affected_flight_ids=[],
        severity=RiskLevel.HIGH,
    )
    db_session.add(c1)
    with pytest.raises(IntegrityError):
        db_session.commit()
    db_session.rollback()

    # Invalid root_gate_id
    c2 = CascadeEvent(
        root_gate_id=uuid.uuid4(),
        propagation_path=[],
        affected_flight_ids=[],
        severity=RiskLevel.MEDIUM,
    )
    db_session.add(c2)
    with pytest.raises(IntegrityError):
        db_session.commit()
    db_session.rollback()

    # Invalid root_runway_id
    c3 = CascadeEvent(
        root_runway_id=uuid.uuid4(),
        propagation_path=[],
        affected_flight_ids=[],
        severity=RiskLevel.LOW,
    )
    db_session.add(c3)
    with pytest.raises(IntegrityError):
        db_session.commit()
    db_session.rollback()

    # Invalid scenario_id
    c4 = CascadeEvent(
        scenario_id=uuid.uuid4(),
        propagation_path=[],
        affected_flight_ids=[],
        severity=RiskLevel.LOW,
    )
    db_session.add(c4)
    with pytest.raises(IntegrityError):
        db_session.commit()
    db_session.rollback()


def test_unique_constraint_flight_arrival(db_session):
    flight = db_session.query(Flight).first()
    assert flight is not None

    duplicate = Flight(
        flight_number=flight.flight_number,
        airline=flight.airline,
        aircraft_id=flight.aircraft_id,
        route_type=flight.route_type,
        scheduled_arrival=flight.scheduled_arrival,  # Duplicate combination
        scheduled_departure=flight.scheduled_departure,
        runway_id=flight.runway_id,
        is_synthetic=True,
    )
    db_session.add(duplicate)
    with pytest.raises(IntegrityError):
        db_session.commit()
    db_session.rollback()


def test_unique_constraint_gate_code_per_terminal(db_session):
    gate = db_session.query(Gate).first()
    assert gate is not None

    duplicate = Gate(
        terminal_id=gate.terminal_id,
        code=gate.code,  # Duplicate code in same terminal
        gate_type=GateType.JETBRIDGE,
        max_aircraft_size=AircraftSizeClass.LARGE,
        eligible_route_types=GateEligibleRouteType.BOTH,
        status=GateStatus.AVAILABLE,
        taxi_distance_meters=500.0,
    )
    db_session.add(duplicate)
    with pytest.raises(IntegrityError):
        db_session.commit()
    db_session.rollback()


def test_system_config_defaults(db_session):
    config = db_session.query(SystemConfig).first()
    assert config is not None
    assert float(config.risk_low_max_minutes) == 5.0
    assert float(config.risk_medium_max_minutes) == 15.0
    assert config.turnaround_buffer_minutes == 15
    assert config.optimizer_timeout_seconds == 60
    assert float(config.optimizer_weight_delay_cost) == 1.0
    assert float(config.optimizer_weight_conflict_cost) == 50.0
    assert float(config.optimizer_weight_reassignment_cost) == 5.0
    assert float(config.optimizer_weight_taxi_distance) == 0.1
    assert float(config.optimizer_weight_remote_stand) == 10.0
    assert config.cascade_max_depth == 5
