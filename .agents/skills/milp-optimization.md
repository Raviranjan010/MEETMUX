# Skill: milp-optimization

**Purpose:** Solve the gate assignment MILP (Gurobi primary, OR-Tools fallback).
**When to use:** Phase 9, and every re-optimization in Phase 14.
**Inputs:** Flights, gates, conflict pairs (from gate-conflict-detection), system_config weights/timeout, optional scenario context.
**Outputs:** optimization_runs row + gate_assignments (assignment_status=PROPOSED) with solver_used/status/objective_value/solve_time_ms.
**Files involved:** backend/app/optimizer/milp.py; tests/optimizer/test_milp.py
**Validation requirements:** Formulation matches docs/OPTIMIZATION.md exactly; an intentionally infeasible test case returns INFEASIBLE with a reason.
**Failure handling:** Gurobi import/license failure → try OR-Tools; both fail → SOLVER_UNAVAILABLE; solver exception → ERROR, logged, never surfaced as a fake success.
**Prohibited shortcuts:** Never hardcode an assignment; never claim a solver ran that didn't; never skip the timeout wrapper.
