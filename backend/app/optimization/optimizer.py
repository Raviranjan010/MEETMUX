from typing import List, Dict, Any, Tuple
from app.optimization.solver import BaseOptimizer
from app.optimization.ortools_solver import ORToolsOptimizer
from app.optimization.gurobi_solver import GurobiOptimizer, GUROBI_AVAILABLE
from app.optimization.models import (
    FlightOptInput,
    GateOptInput,
    OptWeights,
    OptimizationOutput,
    GateAssignmentResult
)
from app.utils.time_utils import check_time_overlap, get_occupancy_interval
from app.utils.validation import is_flight_gate_compatible
from app.core.logging import logger


class OptimizerFactory:
    """
    Factory creating optimizer instances according to requested backend.
    Defaults to OR-Tools if Gurobi is requested but unavailable.
    """
    @staticmethod
    def get_optimizer(solver_name: str = "ortools") -> BaseOptimizer:
        clean_name = (solver_name or "ortools").lower().strip()
        if clean_name == "gurobi":
            if GUROBI_AVAILABLE:
                return GurobiOptimizer()
            else:
                logger.warning("Requested 'gurobi' solver but gurobipy is not installed/licensed. Gracefully falling back to OR-Tools.")
                return ORToolsOptimizer()
        return ORToolsOptimizer()


class OptimizationValidator:
    """
    Validates solver results post-execution:
    1. Every assigned flight is compatible with its gate
    2. No two flights on the same gate have overlapping occupancy intervals
    3. Terminal and aircraft type constraints hold
    """
    @staticmethod
    def validate_assignments(
        assignments: List[GateAssignmentResult],
        flights_map: Dict[int, FlightOptInput],
        gates_map: Dict[int, GateOptInput],
        buffer_minutes: float = 15.0
    ) -> Tuple[bool, List[str], List[str]]:
        errors: List[str] = []
        warnings: List[str] = []

        # 1. Check compatibility for each assignment
        for a in assignments:
            flight = flights_map.get(a.flight_id)
            gate = gates_map.get(a.gate_id)
            if not flight or not gate:
                errors.append(f"Assignment references invalid flight ID {a.flight_id} or gate ID {a.gate_id}")
                continue

            if not gate.is_available:
                errors.append(f"Flight {flight.flight_number} assigned to out-of-service gate {gate.gate_number}")

            if flight.terminal != gate.terminal:
                warnings.append(f"Flight {flight.flight_number} (terminal {flight.terminal}) assigned to gate in terminal {gate.terminal}")

            if gate.supported_aircraft_types != "*" and flight.aircraft_type not in [t.strip() for t in gate.supported_aircraft_types.split(",")]:
                errors.append(f"Aircraft {flight.aircraft_type} on flight {flight.flight_number} not supported by gate {gate.gate_number}")

        # 2. Check for simultaneous overlapping assignments on the same gate
        gate_buckets: Dict[int, List[GateAssignmentResult]] = {}
        for a in assignments:
            gate_buckets.setdefault(a.gate_id, []).append(a)

        for gate_id, gate_assigns in gate_buckets.items():
            gate_obj = gates_map.get(gate_id)
            gate_label = gate_obj.gate_number if gate_obj else f"ID {gate_id}"
            n = len(gate_assigns)
            for i in range(n):
                for j in range(i + 1, n):
                    a1 = gate_assigns[i]
                    a2 = gate_assigns[j]
                    f1 = flights_map.get(a1.flight_id)
                    f2 = flights_map.get(a2.flight_id)
                    if f1 and f2:
                        s1, e1 = get_occupancy_interval(f1.arrival_time, f1.departure_time, f1.predicted_delay_minutes, f1.turnaround_minutes)
                        s2, e2 = get_occupancy_interval(f2.arrival_time, f2.departure_time, f2.predicted_delay_minutes, f2.turnaround_minutes)
                        if check_time_overlap(s1, e1, s2, e2, buffer_minutes=buffer_minutes):
                            errors.append(
                                f"Gate Conflict on {gate_label}: Flight {f1.flight_number} and Flight {f2.flight_number} have overlapping intervals with buffer."
                            )

        is_valid = len(errors) == 0
        return is_valid, errors, warnings
