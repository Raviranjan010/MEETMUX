# TESTING.md

Backend: Pytest + pytest-cov. Frontend: Vitest + React Testing Library. One test module per service/component minimum (see IMPLEMENTATION_PLAN.md §9 traceability matrix for exact paths).

## Required coverage areas (functional)
Validation, feature engineering, prediction, risk classification, gate compatibility, conflict detection, turnaround buffer logic, international/domestic eligibility, MILP optimization (constraint satisfaction), objective calculation (per-term breakdown sums correctly), baseline algorithm determinism, simulation state mutation, cascade propagation, re-optimization orchestration, every API endpoint (success + documented error), every frontend page's Loading/Success/Empty/Error states, at least one integration test that runs the full predict→conflict→optimize→validate chain against the seeded demo dataset, and one E2E-style test (Playwright or Vitest+RTL simulated flow) covering "run optimizer → accept a proposed assignment."

## Required edge cases (must each have a dedicated test)
No compatible gate for a flight (aircraft too large / wrong route type for every open gate) · all gates blocked · all international-eligible gates occupied · overlapping flights forced onto one gate · duplicate flight_id in upload · invalid/out-of-order timestamps · missing required fields · malformed CSV (wrong delimiter, missing header) · Gurobi unavailable (simulate `ImportError`) · OR-Tools unavailable · both solvers unavailable → `SOLVER_UNAVAILABLE` · solver returns provably-infeasible model → `INFEASIBLE` with reason · solver exceeds timeout → `TIMEOUT` · DB connection failure → `/api/health` reports `database: false`, dependent endpoints return 503 · backend unreachable from frontend → frontend Error state with Retry · empty dataset (0 flights) → analytics/optimizer endpoints return a documented empty result, not an exception.

## Definition of "tests pass"
`pytest` exit code 0 and `vitest run` exit code 0, with actual command output captured in the phase report — a phase is not "STOP-complete" on the basis of code review alone (see AGENTS.md).
