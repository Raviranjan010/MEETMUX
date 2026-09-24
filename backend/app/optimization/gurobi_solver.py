import time
from typing import List, Dict, Tuple

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

try:
    import gurobipy as gp
    from gurobipy import GRB
    GUROBI_AVAILABLE = True
except ImportError:
    GUROBI_AVAILABLE = False


class GurobiOptimizer(BaseOptimizer):
    def __init__(self):
        super().__init__(name="gurobi")

    def solve(
        self,
        flights: List[FlightOptInput],
        gates: List[GateOptInput],
        weights: OptWeights,
        time_limit_seconds: int = 60,
        buffer_minutes: float = 15.0
    ) -> OptimizationOutput:
        start_time = time.time()
        
        if not GUROBI_AVAILABLE:
            logger.warning("Gurobi is not installed or available in this Python environment.")
            return OptimizationOutput(
                status="ERROR",
                solver="gurobi",
                objective_value=None,
                execution_time_seconds=round(time.time() - start_time, 3),
                total_flights=len(flights),
                total_gates=len(gates),
                assigned_flights=0,
                unassigned_flights=len(flights),
                gates_utilized=0,
                conflicts_count=0,
                message="Gurobi solver is not installed or license is missing. Please select OR-Tools solver backend."
            )

        try:
            logger.info(f"Initializing Gurobi MILP model for {len(flights)} flights...")
            env = gp.Env(empty=True)
            env.setParam("OutputFlag", 0)
            env.start()

            model = gp.Model("AirportGateMILP", env=env)
            model.setParam(GRB.Param.TimeLimit, time_limit_seconds)

            # 1. Variables
            x: Dict[Tuple[int, int], Any] = {}
            u: Dict[int, Any] = {}

            for f in flights:
                u[f.id] = model.addVar(vtype=GRB.BINARY, name=f"u_{f.id}")
                for g in gates:
                    if check_flight_gate_feasibility(f, g):
                        x[(f.id, g.id)] = model.addVar(vtype=GRB.BINARY, name=f"x_{f.id}_{g.id}")

            # 2. Assignment Constraints
            for f in flights:
                valid_vars = [x[(f.id, g.id)] for g in gates if (f.id, g.id) in x]
                if valid_vars:
                    model.addConstr(gp.quicksum(valid_vars) + u[f.id] == 1, name=f"assign_{f.id}")
                else:
                    model.addConstr(u[f.id] == 1, name=f"unassigned_{f.id}")

            # 3. Non-overlapping Constraints
            overlapping_pairs = identify_overlapping_pairs(flights, buffer_minutes=buffer_minutes)
            for (f1_id, f2_id) in overlapping_pairs:
                for g in gates:
                    if (f1_id, g.id) in x and (f2_id, g.id) in x:
                        model.addConstr(x[(f1_id, g.id)] + x[(f2_id, g.id)] <= 1, name=f"conflict_{f1_id}_{f2_id}_{g.id}")

            # 4. Objective Function
            obj_expr = gp.LinExpr()
            gate_map = {g.id: g for g in gates}

            for (f_id, g_id), var in x.items():
                f_obj = next(f for f in flights if f.id == f_id)
                g_obj = gate_map[g_id]
                cost = compute_assignment_cost(f_obj, g_obj, weights)
                obj_expr += cost * var

            unassigned_penalty = weights.conflict * 2.0
            for f in flights:
                obj_expr += unassigned_penalty * u[f.id]

            model.setObjective(obj_expr, GRB.MINIMIZE)
            model.optimize()

            runtime = round(time.time() - start_time, 3)

            if model.Status in [GRB.OPTIMAL, GRB.SUBOPTIMAL]:
                assignments: List[GateAssignmentResult] = []
                used_gates = set()
                unassigned_count = 0

                for f in flights:
                    assigned = False
                    for g in gates:
                        if (f.id, g.id) in x and x[(f.id, g.id)].X > 0.5:
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

                res_status = "OPTIMAL" if model.Status == GRB.OPTIMAL else "FEASIBLE"
                return OptimizationOutput(
                    status=res_status,
                    solver="gurobi",
                    objective_value=round(model.ObjVal, 2),
                    execution_time_seconds=runtime,
                    total_flights=len(flights),
                    total_gates=len(gates),
                    assigned_flights=len(assignments),
                    unassigned_flights=unassigned_count,
                    gates_utilized=len(used_gates),
                    conflicts_count=0,
                    assignments=assignments,
                    message="Gurobi optimization completed successfully."
                )
            elif model.Status == GRB.INFEASIBLE:
                return OptimizationOutput(
                    status="INFEASIBLE",
                    solver="gurobi",
                    objective_value=None,
                    execution_time_seconds=runtime,
                    total_flights=len(flights),
                    total_gates=len(gates),
                    assigned_flights=0,
                    unassigned_flights=len(flights),
                    gates_utilized=0,
                    conflicts_count=0,
                    message="Gurobi model proven infeasible."
                )
            else:
                return OptimizationOutput(
                    status="ERROR",
                    solver="gurobi",
                    objective_value=None,
                    execution_time_seconds=runtime,
                    total_flights=len(flights),
                    total_gates=len(gates),
                    assigned_flights=0,
                    unassigned_flights=len(flights),
                    gates_utilized=0,
                    conflicts_count=0,
                    message=f"Gurobi solver ended with status {model.Status}."
                )

        except Exception as e:
            logger.error(f"Gurobi optimization error: {e}")
            return OptimizationOutput(
                status="ERROR",
                solver="gurobi",
                objective_value=None,
                execution_time_seconds=round(time.time() - start_time, 3),
                total_flights=len(flights),
                total_gates=len(gates),
                assigned_flights=0,
                unassigned_flights=len(flights),
                gates_utilized=0,
                conflicts_count=0,
                message=f"Gurobi execution failed: {str(e)}"
            )
