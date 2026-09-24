from abc import ABC, abstractmethod
from typing import List, Optional
from app.optimization.models import (
    FlightOptInput,
    GateOptInput,
    OptWeights,
    OptimizationOutput
)


class BaseOptimizer(ABC):
    """
    Abstract Base Class for MILP Gate Assignment Solvers.
    Decouples optimization algorithms (OR-Tools, Gurobi, CPLEX, etc.) from API handlers.
    """
    def __init__(self, name: str):
        self.name = name

    @abstractmethod
    def solve(
        self,
        flights: List[FlightOptInput],
        gates: List[GateOptInput],
        weights: OptWeights,
        time_limit_seconds: int = 60,
        buffer_minutes: float = 15.0
    ) -> OptimizationOutput:
        """
        Executes gate assignment optimization.
        """
        pass
