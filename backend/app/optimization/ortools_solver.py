import time
from typing import List, Dict, Tuple
from ortools.linear_solver import pywraplp

from app.optimization.solver import BaseOptimizer
from app.optimization.models import (
    FlightOptInput,
    GateOptInput,
    OptWeights,
    OptimizationOutput,
    GateAssignmentResult
)
from app.optimization.objective import compute_assignment_cost
from app.optimization.constraints import check_flight_gate_feasibility, identify_overlapping_pairs
from app.utils.validation import compute_walking_distance_score
from app.core.logging import logger


class ORToolsOptimizer(BaseOptimizer):
    def __init__(self):
        super().__init__(name="ortools")

    def solve(
        self,
        flights: List[FlightOptInput],
        gates: List[GateOptInput],
        weights: OptWeights,
        time_limit_seconds: int = 60,
        buffer_minutes: float = 15.0
    ) -> OptimizationOutput:
        start_time = time.time()
        logger.info(f"Starting OR-Tools optimization for {len(flights)} flights across {len(gates)} gates...")

        if not flights or not gates:
            return OptimizationOutput(
                status="INFEASIBLE",
                solver="ortools",
                objective_value=None,
                execution_time_seconds=round(time.time() - start_time, 3),
                total_flights=len(flights),
                total_gates=len(gates),
                assigned_flights=0,
                unassigned_flights=len(flights),
                gates_utilized=0,
                conflicts_count=0,
                message="Flight or gate list is empty."
            )

        # Create SCIP or CBC solver
        solver = pywraplp.Solver.CreateSolver("SCIP") or pywraplp.Solver.CreateSolver("CBC")
        if not solver:
            # Fallback to SAT or default MIP
            solver = pywraplp.Solver("AirportGateMILP", pywraplp.Solver.CBC_MIXED_INTEGER_PROGRAMMING)

        solver.set_time_limit(time_limit_seconds * 1000)

        # 1. Decision Variables
        # x[f_id, g_id] in {0, 1}
        x: Dict[Tuple[int, int], pywraplp.Variable] = {}
        # Slack variable u[f_id] in {0, 1} to handle oversubscribed/infeasible flight assignment with high penalty
        u: Dict[int, pywraplp.Variable] = {}

        for f in flights:
            u[f.id] = solver.BoolVar(f"unassigned_{f.id}")
            for g in gates:
                if check_flight_gate_feasibility(f, g):
                    x[(f.id, g.id)] = solver.BoolVar(f"x_{f.id}_{g.id}")

        # 2. Constraints
        # Constraint 1: Every flight assigned to exactly 1 gate OR marked unassigned via slack
        for f in flights:
            valid_gate_vars = [x[(f.id, g.id)] for g in gates if (f.id, g.id) in x]
            if valid_gate_vars:
                solver.Add(solver.Sum(valid_gate_vars) + u[f.id] == 1)
            else:
                # No compatible gate exists at all for flight f
                solver.Add(u[f.id] == 1)

        # Constraint 2: No overlapping flights at the same gate
        overlapping_pairs = identify_overlapping_pairs(flights, buffer_minutes=buffer_minutes)
        for (f1_id, f2_id) in overlapping_pairs:
            for g in gates:
                if (f1_id, g.id) in x and (f2_id, g.id) in x:
                    solver.Add(x[(f1_id, g.id)] + x[(f2_id, g.id)] <= 1)

        # 3. Objective Function
        objective = solver.Objective()
        objective.SetMinimization()

        # Assignment costs
        gate_map = {g.id: g for g in gates}
        for (f_id, g_id), var in x.items():
            flight_obj = next(f for f in flights if f.id == f_id)
            gate_obj = gate_map[g_id]
            cost = compute_assignment_cost(flight_obj, gate_obj, weights)
            objective.SetCoefficient(var, float(cost))

        # Unassigned flight penalty (heavily penalized by conflict weight)
        unassigned_penalty = weights.conflict * 2.0
        for f in flights:
            objective.SetCoefficient(u[f.id], float(unassigned_penalty))

        # 4. Solve
        solve_status = solver.Solve()
        runtime = round(time.time() - start_time, 3)

        status_mapping = {
            pywraplp.Solver.OPTIMAL: "OPTIMAL",
            pywraplp.Solver.FEASIBLE: "FEASIBLE",
            pywraplp.Solver.INFEASIBLE: "INFEASIBLE",
            pywraplp.Solver.UNBOUNDED: "UNBOUNDED",
            pywraplp.Solver.ABNORMAL: "ERROR",
            pywraplp.Solver.NOT_SOLVED: "TIMEOUT",
        }
        res_status = status_mapping.get(solve_status, "ERROR")

        if res_status in ["OPTIMAL", "FEASIBLE"]:
            assignments: List[GateAssignmentResult] = []
            used_gates = set()
            unassigned_count = 0

            flight_map = {f.id: f for f in flights}

            for f in flights:
                assigned = False
                for g in gates:
                    if (f.id, g.id) in x and x[(f.id, g.id)].solution_value() > 0.5:
                        used_gates.add(g.id)
                        walk_score = compute_walking_distance_score(g.gate_type, g.terminal, g.gate_number)
                        assignments.append(GateAssignmentResult(
                            flight_id=f.id,
                            flight_number=f.flight_number,
                            airline=f.airline,
                            aircraft_type=f.aircraft_type,
                            terminal=f.terminal,
                            gate_id=g.id,
                            gate_number=g.gate_number,
                            gate_terminal=g.terminal,
                            arrival_time=f.arrival_time,
                            departure_time=f.departure_time,
                            predicted_delay_minutes=f.predicted_delay_minutes,
                            delay_category=f.delay_category,
                            assignment_status="Assigned",
                            walking_distance_score=walk_score
                        ))
                        assigned = True
                        break
                if not assigned:
                    unassigned_count += 1

            return OptimizationOutput(
                status=res_status,
                solver="ortools",
                objective_value=round(solver.Objective().Value(), 2),
                execution_time_seconds=runtime,
                total_flights=len(flights),
                total_gates=len(gates),
                assigned_flights=len(assignments),
                unassigned_flights=unassigned_count,
                gates_utilized=len(used_gates),
                conflicts_count=0,
                assignments=assignments,
                message="Optimization successfully completed." if unassigned_count == 0 else f"{unassigned_count} flights could not be accommodated due to gate capacity/constraints."
            )
        else:
            return OptimizationOutput(
                status=res_status,
                solver="ortools",
                objective_value=None,
                execution_time_seconds=runtime,
                total_flights=len(flights),
                total_gates=len(gates),
                assigned_flights=0,
                unassigned_flights=len(flights),
                gates_utilized=0,
                conflicts_count=0,
                message=f"Solver returned status {res_status}."
            )
