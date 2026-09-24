import pytest
from datetime import datetime, timedelta

from app.optimization.models import FlightOptInput, GateOptInput, OptWeights
from app.optimization.ortools_solver import ORToolsOptimizer
from app.optimization.optimizer import OptimizerFactory, OptimizationValidator


def test_deterministic_feasible_assignment():
    """
    Test Case 1: 2 non-overlapping flights, 2 gates -> both assigned successfully.
    """
    now = datetime(2026, 9, 24, 10, 0)
    flights = [
        FlightOptInput(
            id=1, flight_number="AI101", airline="Air India", aircraft_type="A320",
            terminal="T1", arrival_time=now, departure_time=now + timedelta(minutes=60)
        ),
        FlightOptInput(
            id=2, flight_number="6E202", airline="IndiGo", aircraft_type="A320",
            terminal="T1", arrival_time=now + timedelta(minutes=90), departure_time=now + timedelta(minutes=150)
        )
    ]

    gates = [
        GateOptInput(id=1, gate_number="A01", terminal="T1", supported_aircraft_types="A320,B737"),
        GateOptInput(id=2, gate_number="A02", terminal="T1", supported_aircraft_types="A320,B737")
    ]

    optimizer = ORToolsOptimizer()
    output = optimizer.solve(flights, gates, OptWeights())

    assert output.status in ["OPTIMAL", "FEASIBLE"]
    assert output.assigned_flights == 2
    assert output.unassigned_flights == 0
    assert len(output.assignments) == 2


def test_overlapping_flights_single_gate():
    """
    Test Case 2: 2 simultaneously overlapping flights, 1 gate -> 1 flight assigned, 1 flight unassigned/slack flagged.
    """
    now = datetime(2026, 9, 24, 10, 0)
    flights = [
        FlightOptInput(
            id=1, flight_number="AI101", airline="Air India", aircraft_type="A320",
            terminal="T1", arrival_time=now, departure_time=now + timedelta(minutes=60)
        ),
        FlightOptInput(
            id=2, flight_number="6E202", airline="IndiGo", aircraft_type="A320",
            terminal="T1", arrival_time=now + timedelta(minutes=10), departure_time=now + timedelta(minutes=70)
        )
    ]

    gates = [
        GateOptInput(id=1, gate_number="A01", terminal="T1", supported_aircraft_types="A320")
    ]

    optimizer = ORToolsOptimizer()
    output = optimizer.solve(flights, gates, OptWeights(), buffer_minutes=15.0)

    # Since only 1 gate is available for 2 overlapping flights, exactly 1 is assigned and 1 is unassigned
    assert output.assigned_flights == 1
    assert output.unassigned_flights == 1


def test_incompatible_aircraft_handling():
    """
    Test Case 3: Widebody aircraft (B777) on gate supporting only narrowbody (A320) -> should not assign.
    """
    now = datetime(2026, 9, 24, 10, 0)
    flights = [
        FlightOptInput(
            id=1, flight_number="EK511", airline="Emirates", aircraft_type="B777",
            terminal="T3", arrival_time=now, departure_time=now + timedelta(minutes=90)
        )
    ]

    gates = [
        GateOptInput(id=1, gate_number="A01", terminal="T1", supported_aircraft_types="A320")
    ]

    optimizer = ORToolsOptimizer()
    output = optimizer.solve(flights, gates, OptWeights())

    assert output.assigned_flights == 0
    assert output.unassigned_flights == 1


def test_optimizer_factory_fallback():
    opt = OptimizerFactory.get_optimizer("non_existent_solver")
    assert isinstance(opt, ORToolsOptimizer)
