"""
MILP Gate Assignment Optimizer per docs/OPTIMIZATION.md.
FR-8: Optimize gate assignment via MILP (Gurobi primary, OR-Tools fallback).
"""
import logging
import time
from typing import Dict, Any, Optional, List, Tuple
from datetime import datetime

from sqlalchemy.orm import Session

from app.models import (
    Flight, Gate, SystemConfig, OptimizationRun, GateAssignment, AuditRecord, Prediction,
)
from app.models.enums import (
    RunType, SolverUsed, OptimizationStatus, AssignmentStatus,
    GateStatus, GateType, AuditAction,
)
from app.services.baseline import is_gate_compatible
from app.services.conflict import (
    compute_occupied_interval, intervals_overlap, get_turnaround_buffer,
)

logger = logging.getLogger(__name__)

BIG_M = 10000.0


def _check_gurobi() -> bool:
    try:
        import gurobipy
        return True
    except ImportError:
        return False


def _check_ortools() -> bool:
    try:
        from ortools.sat.python import cp_model
        return True
    except ImportError:
        return False


def _get_baseline_assignments(db: Session) -> Dict[str, str]:
    """Get the latest baseline run's flight->gate mapping."""
    baseline_run = db.query(OptimizationRun).filter(
        OptimizationRun.run_type == RunType.BASELINE,
        OptimizationRun.status.in_([OptimizationStatus.OPTIMAL, OptimizationStatus.FEASIBLE]),
    ).order_by(OptimizationRun.created_at.desc()).first()
    
    if not baseline_run:
        return {}
    
    result = {}
    for ga in baseline_run.assignments:
        if ga.gate_id:
            result[str(ga.flight_id)] = str(ga.gate_id)
    return result


def _get_prediction_delays(db: Session) -> Dict[str, float]:
    """Get latest prediction delay for each flight."""
    from sqlalchemy import func
    subq = db.query(
        Prediction.flight_id,
        func.max(Prediction.created_at).label("latest")
    ).group_by(Prediction.flight_id).subquery()
    
    preds = db.query(Prediction).join(
        subq,
        (Prediction.flight_id == subq.c.flight_id) & (Prediction.created_at == subq.c.latest)
    ).all()
    
    return {str(p.flight_id): float(p.predicted_delay_minutes) for p in preds}


def _build_conflict_pairs(
    flights: List[Flight],
    gates: List[Gate],
    buffer: int,
) -> List[Tuple[int, int, int]]:
    """Precompute conflicting (flight_i, flight_j, gate_k) triples."""
    pairs = []
    for k, gate in enumerate(gates):
        # Get flights compatible with this gate
        compat_flights = [(i, f) for i, f in enumerate(flights) if is_gate_compatible(f, gate)]
        for ci in range(len(compat_flights)):
            fi_idx, fi = compat_flights[ci]
            si, ei = compute_occupied_interval(fi.scheduled_arrival, fi.scheduled_departure, buffer)
            for cj in range(ci + 1, len(compat_flights)):
                fj_idx, fj = compat_flights[cj]
                sj, ej = compute_occupied_interval(fj.scheduled_arrival, fj.scheduled_departure, buffer)
                if intervals_overlap(si, ei, sj, ej):
                    pairs.append((fi_idx, fj_idx, k))
    return pairs


def solve_with_ortools(
    flights: List[Flight],
    gates: List[Gate],
    config: SystemConfig,
    baseline_map: Dict[str, str],
    delay_map: Dict[str, float],
    timeout_seconds: int,
) -> Dict[str, Any]:
    """Solve the MILP gate assignment using OR-Tools CP-SAT solver."""
    from ortools.sat.python import cp_model

    buffer = get_turnaround_buffer(config)
    n_flights = len(flights)
    n_gates = len(gates)

    model = cp_model.CpModel()

    # Decision variables: x[i][j] = 1 if flight i assigned to gate j
    x = {}
    for i in range(n_flights):
        for j in range(n_gates):
            if is_gate_compatible(flights[i], gates[j]):
                x[i, j] = model.NewBoolVar(f"x_{i}_{j}")

    # Slack variables: u[i] = 1 if flight i is unassigned
    u = {}
    for i in range(n_flights):
        u[i] = model.NewBoolVar(f"u_{i}")

    # Constraint 1: Exactly one gate per flight (or unassigned)
    for i in range(n_flights):
        assigned_vars = [x[i, j] for j in range(n_gates) if (i, j) in x]
        model.Add(sum(assigned_vars) + u[i] == 1)

    # Constraint 5: No overlap - for conflicting pairs at same gate
    conflict_pairs = _build_conflict_pairs(flights, gates, buffer)
    for fi, fj, gk in conflict_pairs:
        if (fi, gk) in x and (fj, gk) in x:
            model.Add(x[fi, gk] + x[fj, gk] <= 1)

    # Objective function
    w_delay = float(config.optimizer_weight_delay_cost) if config else 1.0
    w_conflict = float(config.optimizer_weight_conflict_cost) if config else 50.0
    w_reassign = float(config.optimizer_weight_reassignment_cost) if config else 5.0
    w_taxi = float(config.optimizer_weight_taxi_distance) if config else 0.1
    w_remote = float(config.optimizer_weight_remote_stand) if config else 10.0

    # Scale for integer arithmetic (CP-SAT uses integers)
    SCALE = 1000
    
    objective_terms = []
    
    for i in range(n_flights):
        fid = str(flights[i].id)
        delay = delay_map.get(fid, 0.0)
        
        for j in range(n_gates):
            if (i, j) not in x:
                continue
            
            cost = 0
            # Delay cost
            cost += int(w_delay * delay * SCALE)
            # Taxi distance cost
            cost += int(w_taxi * float(gates[j].taxi_distance_meters) * SCALE)
            # Remote stand penalty
            if gates[j].gate_type == GateType.REMOTE:
                cost += int(w_remote * SCALE)
            # Reassignment penalty
            baseline_gate = baseline_map.get(fid)
            if baseline_gate and baseline_gate != str(gates[j].id):
                cost += int(w_reassign * SCALE)
            
            if cost != 0:
                objective_terms.append(cost * x[i, j])
        
        # Heavy penalty for unassigned
        objective_terms.append(int(BIG_M * SCALE) * u[i])
    
    model.Minimize(sum(objective_terms))

    solver = cp_model.CpSolver()
    solver.parameters.max_time_in_seconds = timeout_seconds

    start = time.time()
    status = solver.Solve(model)
    solve_time = time.time() - start

    status_map = {
        cp_model.OPTIMAL: ("OPTIMAL", OptimizationStatus.OPTIMAL),
        cp_model.FEASIBLE: ("FEASIBLE", OptimizationStatus.FEASIBLE),
        cp_model.INFEASIBLE: ("INFEASIBLE", OptimizationStatus.INFEASIBLE),
        cp_model.MODEL_INVALID: ("ERROR", OptimizationStatus.ERROR),
    }
    
    solver_status_str, opt_status = status_map.get(
        status, ("UNKNOWN", OptimizationStatus.ERROR)
    )
    
    if status == cp_model.UNKNOWN:
        solver_status_str = "TIMEOUT"
        opt_status = OptimizationStatus.TIMEOUT

    assignments = []
    objective_value = 0.0
    
    if status in (cp_model.OPTIMAL, cp_model.FEASIBLE):
        objective_value = solver.ObjectiveValue() / SCALE
        for i in range(n_flights):
            assigned_gate = None
            obj_contrib = None
            for j in range(n_gates):
                if (i, j) in x and solver.Value(x[i, j]) == 1:
                    assigned_gate = j
                    # Compute objective contribution
                    fid = str(flights[i].id)
                    delay = delay_map.get(fid, 0.0)
                    cost = w_delay * delay
                    cost += w_taxi * float(gates[j].taxi_distance_meters)
                    if gates[j].gate_type == GateType.REMOTE:
                        cost += w_remote
                    baseline_gate = baseline_map.get(fid)
                    if baseline_gate and baseline_gate != str(gates[j].id):
                        cost += w_reassign
                    obj_contrib = round(cost, 3)
                    break
            
            assignments.append({
                "flight_index": i,
                "gate_index": assigned_gate,
                "objective_contribution": obj_contrib,
                "unassigned": assigned_gate is None,
            })

    return {
        "solver": "ORTOOLS",
        "solver_status": solver_status_str,
        "opt_status": opt_status,
        "objective_value": round(objective_value, 3),
        "solve_time_ms": int(solve_time * 1000),
        "assignments": assignments,
    }


def solve_with_gurobi(
    flights: List[Flight],
    gates: List[Gate],
    config: SystemConfig,
    baseline_map: Dict[str, str],
    delay_map: Dict[str, float],
    timeout_seconds: int,
) -> Dict[str, Any]:
    """Solve the MILP gate assignment using Gurobi solver."""
    import gurobipy as gp
    from gurobipy import GRB

    buffer = get_turnaround_buffer(config)
    n_flights = len(flights)
    n_gates = len(gates)

    env = gp.Env(empty=True)
    env.setParam("OutputFlag", 0)
    env.start()
    model = gp.Model("gate_assignment", env=env)
    model.setParam("TimeLimit", timeout_seconds)

    # Decision variables
    x = {}
    for i in range(n_flights):
        for j in range(n_gates):
            if is_gate_compatible(flights[i], gates[j]):
                x[i, j] = model.addVar(vtype=GRB.BINARY, name=f"x_{i}_{j}")

    u = {}
    for i in range(n_flights):
        u[i] = model.addVar(vtype=GRB.BINARY, name=f"u_{i}")

    model.update()

    # Constraint 1: Exactly one gate per flight
    for i in range(n_flights):
        assigned_vars = [x[i, j] for j in range(n_gates) if (i, j) in x]
        model.addConstr(gp.quicksum(assigned_vars) + u[i] == 1, name=f"assign_{i}")

    # Constraint 5: No overlap
    conflict_pairs = _build_conflict_pairs(flights, gates, buffer)
    for fi, fj, gk in conflict_pairs:
        if (fi, gk) in x and (fj, gk) in x:
            model.addConstr(x[fi, gk] + x[fj, gk] <= 1, name=f"nooverlap_{fi}_{fj}_{gk}")

    # Objective
    w_delay = float(config.optimizer_weight_delay_cost) if config else 1.0
    w_reassign = float(config.optimizer_weight_reassignment_cost) if config else 5.0
    w_taxi = float(config.optimizer_weight_taxi_distance) if config else 0.1
    w_remote = float(config.optimizer_weight_remote_stand) if config else 10.0

    obj = gp.LinExpr()
    for i in range(n_flights):
        fid = str(flights[i].id)
        delay = delay_map.get(fid, 0.0)
        for j in range(n_gates):
            if (i, j) not in x:
                continue
            cost = w_delay * delay
            cost += w_taxi * float(gates[j].taxi_distance_meters)
            if gates[j].gate_type == GateType.REMOTE:
                cost += w_remote
            baseline_gate = baseline_map.get(fid)
            if baseline_gate and baseline_gate != str(gates[j].id):
                cost += w_reassign
            obj += cost * x[i, j]
        obj += BIG_M * u[i]

    model.setObjective(obj, GRB.MINIMIZE)

    start = time.time()
    model.optimize()
    solve_time = time.time() - start

    status_map = {
        GRB.OPTIMAL: ("OPTIMAL", OptimizationStatus.OPTIMAL),
        GRB.SUBOPTIMAL: ("FEASIBLE", OptimizationStatus.FEASIBLE),
        GRB.INFEASIBLE: ("INFEASIBLE", OptimizationStatus.INFEASIBLE),
        GRB.TIME_LIMIT: ("TIMEOUT", OptimizationStatus.TIMEOUT),
    }
    solver_status_str, opt_status = status_map.get(
        model.Status, ("ERROR", OptimizationStatus.ERROR)
    )
    if model.Status == GRB.TIME_LIMIT and model.SolCount > 0:
        solver_status_str = "FEASIBLE"
        opt_status = OptimizationStatus.FEASIBLE

    assignments = []
    objective_value = 0.0

    if model.SolCount > 0:
        objective_value = model.ObjVal
        for i in range(n_flights):
            assigned_gate = None
            obj_contrib = None
            for j in range(n_gates):
                if (i, j) in x and x[i, j].X > 0.5:
                    assigned_gate = j
                    fid = str(flights[i].id)
                    delay = delay_map.get(fid, 0.0)
                    cost = w_delay * delay
                    cost += w_taxi * float(gates[j].taxi_distance_meters)
                    if gates[j].gate_type == GateType.REMOTE:
                        cost += w_remote
                    baseline_gate = baseline_map.get(fid)
                    if baseline_gate and baseline_gate != str(gates[j].id):
                        cost += w_reassign
                    obj_contrib = round(cost, 3)
                    break
            assignments.append({
                "flight_index": i,
                "gate_index": assigned_gate,
                "objective_contribution": obj_contrib,
                "unassigned": assigned_gate is None,
            })

    model.dispose()
    env.dispose()

    return {
        "solver": "GUROBI",
        "solver_status": solver_status_str,
        "opt_status": opt_status,
        "objective_value": round(objective_value, 3),
        "solve_time_ms": int(solve_time * 1000),
        "assignments": assignments,
    }


def run_milp_optimization(
    db: Session,
    scenario_id: Optional[str] = None,
    objective_weights: Optional[Dict[str, float]] = None,
) -> Dict[str, Any]:
    """
    Runs the MILP gate assignment optimizer.
    Tries Gurobi first, falls back to OR-Tools.
    """
    config = db.query(SystemConfig).first()
    
    # Apply weight overrides if provided
    if objective_weights and config:
        if "delay_cost" in objective_weights:
            config.optimizer_weight_delay_cost = objective_weights["delay_cost"]
        if "conflict_cost" in objective_weights:
            config.optimizer_weight_conflict_cost = objective_weights["conflict_cost"]
        if "reassignment_cost" in objective_weights:
            config.optimizer_weight_reassignment_cost = objective_weights["reassignment_cost"]
        if "taxi_distance" in objective_weights:
            config.optimizer_weight_taxi_distance = objective_weights["taxi_distance"]
        if "remote_stand" in objective_weights:
            config.optimizer_weight_remote_stand = objective_weights["remote_stand"]

    timeout = int(config.optimizer_timeout_seconds) if config else 60

    flights = db.query(Flight).order_by(Flight.scheduled_arrival.asc()).all()
    gates = db.query(Gate).filter(Gate.status != GateStatus.BLOCKED).order_by(Gate.code.asc()).all()

    if not flights:
        return {"error": "No flights in database"}
    if not gates:
        return {"error": "No available gates"}

    baseline_map = _get_baseline_assignments(db)
    delay_map = _get_prediction_delays(db)

    config_snapshot = {}
    if config:
        config_snapshot = {
            "turnaround_buffer_minutes": int(config.turnaround_buffer_minutes),
            "optimizer_timeout_seconds": timeout,
            "optimizer_weight_delay_cost": float(config.optimizer_weight_delay_cost),
            "optimizer_weight_conflict_cost": float(config.optimizer_weight_conflict_cost),
            "optimizer_weight_reassignment_cost": float(config.optimizer_weight_reassignment_cost),
            "optimizer_weight_taxi_distance": float(config.optimizer_weight_taxi_distance),
            "optimizer_weight_remote_stand": float(config.optimizer_weight_remote_stand),
        }

    # Try solvers in order
    solver_result = None
    solver_used = SolverUsed.NONE

    gurobi_available = _check_gurobi()
    ortools_available = _check_ortools()

    if gurobi_available:
        try:
            solver_result = solve_with_gurobi(flights, gates, config, baseline_map, delay_map, timeout)
            solver_used = SolverUsed.GUROBI
            logger.info("MILP solved with Gurobi")
        except Exception as e:
            logger.warning(f"Gurobi failed: {e}, falling back to OR-Tools")
            solver_result = None

    if solver_result is None and ortools_available:
        try:
            solver_result = solve_with_ortools(flights, gates, config, baseline_map, delay_map, timeout)
            solver_used = SolverUsed.ORTOOLS
            logger.info("MILP solved with OR-Tools")
        except Exception as e:
            logger.error(f"OR-Tools failed: {e}")
            solver_result = None

    if solver_result is None:
        # Neither solver available
        opt_run = OptimizationRun(
            run_type=RunType.MILP,
            scenario_id=scenario_id,
            solver_used=SolverUsed.NONE,
            solver_status="NONE_AVAILABLE",
            status=OptimizationStatus.SOLVER_UNAVAILABLE,
            config_snapshot=config_snapshot,
        )
        db.add(opt_run)
        db.commit()
        return {
            "optimization_run_id": str(opt_run.id),
            "status": "SOLVER_UNAVAILABLE",
            "solver_used": "NONE",
            "message": "Neither Gurobi nor OR-Tools is available",
        }

    # Create optimization run record
    opt_run = OptimizationRun(
        run_type=RunType.MILP,
        scenario_id=scenario_id,
        solver_used=solver_used,
        solver_status=solver_result["solver_status"],
        status=solver_result["opt_status"],
        objective_value=solver_result["objective_value"],
        solve_time_ms=solver_result["solve_time_ms"],
        config_snapshot=config_snapshot,
    )
    db.add(opt_run)
    db.flush()

    # Persist assignments
    assignment_records = []
    unassigned_count = 0
    for a in solver_result["assignments"]:
        fi = a["flight_index"]
        gi = a["gate_index"]
        ga = GateAssignment(
            optimization_run_id=opt_run.id,
            flight_id=flights[fi].id,
            gate_id=gates[gi].id if gi is not None else None,
            assignment_status=AssignmentStatus.PROPOSED,
            objective_contribution=a.get("objective_contribution"),
        )
        db.add(ga)
        assignment_records.append({
            "flight_id": str(flights[fi].id),
            "flight_number": flights[fi].flight_number,
            "gate_id": str(gates[gi].id) if gi is not None else None,
            "gate_code": gates[gi].code if gi is not None else "UNASSIGNED",
            "objective_contribution": a.get("objective_contribution"),
        })
        if gi is None:
            unassigned_count += 1

    # Run independent validator
    from app.optimizer.validator import validate_solution
    validation = validate_solution(flights, gates, solver_result["assignments"], config)
    opt_run.validation_passed = validation["passed"]
    opt_run.validation_report = validation

    # Audit record
    audit = AuditRecord(
        action=AuditAction.OPTIMIZATION_RUN,
        actor="operator",
        reference_id=opt_run.id,
        details={
            "run_type": "MILP",
            "solver_used": solver_used.value,
            "solver_status": solver_result["solver_status"],
            "objective_value": solver_result["objective_value"],
            "solve_time_ms": solver_result["solve_time_ms"],
            "total_flights": len(flights),
            "assigned": len(flights) - unassigned_count,
            "unassigned": unassigned_count,
            "validation_passed": validation["passed"],
        },
    )
    db.add(audit)
    db.commit()

    logger.info(
        f"MILP complete: solver={solver_used.value}, status={solver_result['solver_status']}, "
        f"obj={solver_result['objective_value']}, time={solver_result['solve_time_ms']}ms, "
        f"validation={'PASS' if validation['passed'] else 'FAIL'}"
    )

    return {
        "optimization_run_id": str(opt_run.id),
        "status": solver_result["opt_status"].value,
        "run_type": "MILP",
        "solver_used": solver_used.value,
        "solver_status": solver_result["solver_status"],
        "objective_value": solver_result["objective_value"],
        "solve_time_ms": solver_result["solve_time_ms"],
        "total_flights": len(flights),
        "assigned": len(flights) - unassigned_count,
        "unassigned": unassigned_count,
        "validation_passed": validation["passed"],
        "validation_report": validation,
        "assignments": assignment_records,
    }
