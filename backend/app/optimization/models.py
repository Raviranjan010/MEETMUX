from dataclasses import dataclass, field
from datetime import datetime
from typing import List, Dict, Any, Optional


@dataclass
class FlightOptInput:
    id: int
    flight_number: str
    airline: str
    aircraft_type: str
    terminal: str
    arrival_time: datetime
    departure_time: datetime
    turnaround_minutes: float = 45.0
    predicted_delay_minutes: float = 0.0
    delay_category: str = "On Time"
    preferred_gate_id: Optional[int] = None


@dataclass
class GateOptInput:
    id: int
    gate_number: str
    terminal: str
    gate_type: str = "Contact"
    supported_aircraft_types: str = "*"
    is_international: bool = False
    is_available: bool = True
    latitude: Optional[float] = None
    longitude: Optional[float] = None


@dataclass
class OptWeights:
    conflict: float = 1000.0
    walking_distance: float = 1.0
    delay_propagation: float = 10.0
    reassignment: float = 5.0
    unused_gate: float = 1.0


@dataclass
class GateAssignmentResult:
    flight_id: int
    flight_number: str
    airline: str
    aircraft_type: str
    terminal: str
    gate_id: int
    gate_number: str
    gate_terminal: str
    arrival_time: datetime
    departure_time: datetime
    predicted_delay_minutes: float
    delay_category: str
    assignment_status: str
    walking_distance_score: float


@dataclass
class OptimizationOutput:
    status: str  # OPTIMAL, FEASIBLE, INFEASIBLE, TIMEOUT, ERROR
    solver: str
    objective_value: Optional[float]
    execution_time_seconds: float
    total_flights: int
    total_gates: int
    assigned_flights: int
    unassigned_flights: int
    gates_utilized: int
    conflicts_count: int
    assignments: List[GateAssignmentResult] = field(default_factory=list)
    validation_errors: List[str] = field(default_factory=list)
    diagnostics: Dict[str, Any] = field(default_factory=dict)
    message: Optional[str] = None
