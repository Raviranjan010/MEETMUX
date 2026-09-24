from datetime import datetime
from typing import Optional, List, Dict, Any
from pydantic import BaseModel, ConfigDict, Field


class OptimizationWeights(BaseModel):
    conflict: float = Field(1000.0, description="Penalty for gate conflict / simultaneous overlap")
    walking_distance: float = Field(1.0, description="Penalty for remote or high passenger walking distance")
    delay_propagation: float = Field(10.0, description="Penalty for tight buffers on delayed incoming flights")
    reassignment: float = Field(5.0, description="Penalty for altering previously planned gate")
    unused_gate: float = Field(1.0, description="Penalty for uneven gate distribution / unused gates")


class OptimizationRequest(BaseModel):
    flight_ids: Optional[List[int]] = None
    gate_ids: Optional[List[int]] = None
    solver: Optional[str] = Field("ortools", description="Solver backend: 'ortools' or 'gurobi'")
    time_limit_seconds: Optional[int] = Field(60, description="Maximum solver runtime limit in seconds")
    weights: Optional[OptimizationWeights] = Field(default_factory=OptimizationWeights)
    buffer_minutes: Optional[float] = Field(15.0, description="Operational buffer between consecutive aircraft on same gate")


class GateAssignmentItem(BaseModel):
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
    predicted_delay_minutes: float = 0.0
    delay_category: str = "On Time"
    assignment_status: str = "Assigned"
    walking_distance_score: float = 1.0


class OptimizationDiagnostics(BaseModel):
    is_valid: bool
    errors: List[str] = []
    warnings: List[str] = []
    conflict_count: int = 0
    incompatibilities_count: int = 0


class OptimizationResponse(BaseModel):
    optimization_run_id: int
    status: str  # optimal, feasible, infeasible, timeout, error
    solver: str
    objective_value: Optional[float] = None
    execution_time_seconds: float
    total_flights: int
    total_gates: int
    assigned_flights: int
    unassigned_flights: int
    gates_utilized: int
    conflicts: int
    assignments: List[GateAssignmentItem]
    diagnostics: Optional[OptimizationDiagnostics] = None
    message: Optional[str] = None

    model_config = ConfigDict(from_attributes=True)


class OptimizationRunSummary(BaseModel):
    id: int
    status: str
    solver: str
    objective_value: Optional[float]
    execution_time: float
    total_flights: int
    total_gates: int
    assigned_flights: int
    unassigned_flights: int
    conflicts_count: int
    created_at: datetime

    model_config = ConfigDict(from_attributes=True)
