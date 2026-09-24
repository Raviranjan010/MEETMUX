# API.md — FastAPI contract

Base path `/api`. All responses JSON. Error format (uniform):
```json
{ "error": { "code": "VALIDATION_ERROR", "message": "human readable", "details": {...}, "request_id": "uuid" } }
```
HTTP status conventions: 200 success, 201 created, 202 accepted (async op started), 400 bad request, 404 not found, 409 conflict (e.g. run already in progress), 422 validation error, 503 dependency unavailable (model/solver/db).

## GET /api/health
200: `{status: "ok"|"degraded", database: bool, ml_model_loaded: bool, optimizer: {gurobi_available: bool, ortools_available: bool}}`. `status` is `degraded` if database is false OR both solvers unavailable.

## GET /api/flights?page&page_size&route_type&risk_level
200: `{items: [Flight], total: int, page: int, page_size: int}`. `page_size` default 25, max 100.

## POST /api/flights
Body: flight fields (see DATA_DICTIONARY.md). 201 with created flight, or 422 with field-level errors (duplicate flight_number+scheduled_arrival, invalid timestamp order, unknown aircraft type).

## GET /api/flights/{id}
200 Flight (with latest prediction + current gate assignment embedded), 404 if missing.

## POST /api/predictions
Body: `{flight_id}` or `{flight_ids: [...]}` for batch. 201: `[Prediction]`. 503 if no model loaded.

## GET /api/predictions/{flight_id}
200: latest Prediction for that flight, 404 if none exists yet.

## GET /api/gates?status&terminal&gate_type
200: `{items: [Gate]}` (paginated same as flights).

## GET /api/gates/{id}
200 Gate with current occupancy window, 404 if missing.

## POST /api/conflicts/detect
Body: `{assignment_source: "BASELINE"|"COMMITTED"|optimization_run_id}`. 200: `{conflicts: [{gate_id, flight_ids: [...], overlap_minutes, reason}]}`.

## POST /api/optimizer/run
Body: `{run_type: "BASELINE"|"MILP", scenario_id?: uuid, objective_weights?: {...override defaults...}}`. 202: `{optimization_run_id, status: "RUNNING"}`. 409 if another run is already RUNNING.

## GET /api/optimizer/{id}
200: full `OptimizationRun` (solver_used, solver_status, status, objective_value, solve_time_ms, validation_passed, validation_report, assignments: [GateAssignment]).

## POST /api/scenarios/run
Body: `{type, target_reference, params}` (see SIMULATION.md for per-type params). 200: `{scenario_id, state_changes: {...}}` — synchronous state mutation; does NOT automatically re-optimize (see `/api/reoptimize`).

## GET /api/scenarios
200: `{items: [Scenario]}`.

## POST /api/reoptimize
Body: `{scenario_id}`. 202: `{optimization_run_id, status: "RUNNING"}`. Internally runs predict→conflict→cascade→MILP→validate for all affected flights, per REOPTIMIZATION.md.

## GET /api/analytics
200: `{fleet_utilization, avg_predicted_delay, risk_distribution: {LOW,MEDIUM,HIGH}, active_conflicts}` — all computed live from current committed state.

## GET /api/analytics/comparison?optimization_run_id
200: `{baseline: {...metrics}, optimized: {...metrics}, deltas: {...}}` — computed from the two stored assignment sets referenced (baseline sentinel run vs the given run).

## GET /api/alerts?resolved&severity
200: `{items: [Alert]}`.

## Additional supporting endpoints (implied by UI, must exist)
`GET /api/cascade/{scenario_id}` → CascadeEvent(s). `GET /api/explain/{gate_assignment_id}` → structured explanation (see EXPLAINABILITY.md). `POST /api/assignments/{id}/accept`, `POST /api/assignments/{id}/reject` → 200, writes audit_records. `POST /api/data/upload` (CSV/JSON) → 202 with per-row validation report.

## Pagination & filtering conventions
All list endpoints: `page` (1-indexed), `page_size`, and documented filter query params only — no free-form filter DSL.
