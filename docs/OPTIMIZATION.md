# OPTIMIZATION.md — MILP Gate Assignment

## Decision variable
`x[i,j] ∈ {0,1}` — 1 if flight `i` is assigned to gate `j`. Domain: all flights in the current optimization scope × all non-BLOCKED gates.

## Hard constraints (every one must hold in any accepted solution)
1. **Exactly one gate per flight** (or explicit UNASSIGNED slack variable if infeasible for that flight — see §4): `Σ_j x[i,j] + u[i] = 1` for all i.
2. **Aircraft compatibility**: `x[i,j] = 0` if `aircraft.size_class(i) > gate.max_aircraft_size(j)`.
3. **Route eligibility**: `x[i,j] = 0` if `flight.route_type(i) not in gate.eligible_route_types(j)`.
4. **Gate availability / not BLOCKED**: `x[i,j] = 0` if `gate.status(j) == BLOCKED`.
5. **Turnaround feasibility & no overlap**: for any two flights i,k assigned to the same gate j, their occupied intervals (`arrival − buffer` to `departure + buffer`, `buffer = system_config.turnaround_buffer_minutes`) must not overlap. Modeled via standard disjunctive/big-M or interval-conflict pairwise constraints: for each conflicting pair (i,k) at gate j (precomputed from the conflict engine's interval logic), `x[i,j] + x[k,j] ≤ 1`.
6. **No double occupancy at a runway-constrained instant** (only if modeling runway as a resource in a given optimization scope — otherwise runway capacity is enforced upstream during scheduling, not in this MILP).

## Objective (configurable, weighted sum — see REQUIREMENTS R9 for weight config keys/defaults)
```
minimize:
  W_delay      * Σ_i predicted_delay_minutes(i) * (flight i assigned at all)
+ W_conflict   * Σ (unresolved conflicts, should be ~0 given constraint 5; this term is a safety net / slack penalty)
+ W_reassign   * Σ_i [x[i, baseline_gate(i)] == 0] * 1         # penalize moving off the baseline gate
+ W_taxi       * Σ_{i,j} x[i,j] * gate.taxi_distance_meters(j)
+ W_remote     * Σ_{i,j} x[i,j] * [gate.gate_type(j) == REMOTE]
+ BIG_M        * Σ_i u[i]                                       # heavily penalize unassigned flights
```
Each term is computed from a single, explicit source (no double counting — e.g. `W_conflict`'s term only fires if constraint 5's precomputed pairs are somehow violated by a slack formulation; under a pure hard-constraint formulation with no slack on constraint 5, this term is normally 0 and exists only for a soft-constraint variant if the solver would otherwise be infeasible for edge cases — see §4).

## Solver behavior
Primary: **Gurobi** (`gurobipy`), if `GUROBI_LICENSE` env/file is present and importable. Fallback: **OR-Tools** CP-SAT (`ortools.sat.python.cp_model`) with an equivalent model formulation. `optimizer/milp.py` tries Gurobi first, catches `ImportError`/license errors, falls back to OR-Tools, and if BOTH fail sets `solver_used = NONE`, `status = SOLVER_UNAVAILABLE` — never fabricates a result.

## Status handling
| Solver outcome | `status` stored |
|---|---|
| Optimal solution found | `OPTIMAL` |
| Feasible but not proven optimal (timeout hit) | `FEASIBLE` or `TIMEOUT` per solver's own signal |
| Proven infeasible | `INFEASIBLE` (response includes a human-readable reason: e.g. "3 international flights, 2 international-eligible gates available in this window") |
| Solver time exceeds `optimizer_timeout_seconds` | `TIMEOUT` |
| Neither Gurobi nor OR-Tools importable/licensed | `SOLVER_UNAVAILABLE` |
| Unhandled solver exception | `ERROR` (exception message logged, not shown raw to the user) |

## §4 Infeasibility handling
If a fully hard-constrained model is infeasible (e.g., more compatible flights than compatible gates in a window), the model includes a per-flight slack `u[i]` (constraint 1 above) so the solver always returns SOME solution, heavily penalized by `BIG_M`. The independent validator (§6) then reports "N flights unassigned" as a validation-visible fact, not a hidden failure. If the solver itself cannot even solve the slack-relaxed model within timeout, status is `TIMEOUT`; true structural infeasibility with slack variables present should not occur, but if it does, `status = INFEASIBLE` with the reason surfaced.

## §5 Exposed run fields (must be shown to the UI, never omitted)
`solver_used`, `solver_status` (raw string from the solver library), `status`, `objective_value`, `solve_time_ms`, `assignment_count`, `unassigned_count`, `validation_passed`.

## §6 Independent Validator (Phase 10 — mandatory, separate module from the solver)
`optimizer/validator.py` re-checks, using plain Python (no solver calls), every hard constraint 1–5 above against the solver's returned `x[i,j]` values. Any violation → `validation_passed = false`, `validation_report` lists every violated constraint with the specific flight/gate IDs involved, and the API/UI must present that run as **not usable as a committed schedule** (it can still be inspected for debugging, but Accept is disabled). This module must never be skipped, cached-skipped, or short-circuited "because the solver said optimal" — solver-reported optimality is not proof of constraint satisfaction against this validator's independent implementation, and any discrepancy is itself a bug to report, not to hide.
