# ACCEPTANCE_CRITERIA.md — RunwayOptX

Status: SOURCE OF TRUTH, priority 3 (below REQUIREMENTS.md, above ARCHITECTURE.md). A phase is NOT complete until every AC listed under it is demonstrated true by an actual run (test output, curl response, screenshot/console log), never by static code reading alone.

## AC-P1 Foundation
- [x] `docker compose up` (or local uvicorn+vite) starts backend and frontend with zero import errors.
- [x] `GET /api/health` returns 200 with `{status, database: bool, ml_model_loaded: bool, optimizer: {gurobi_available: bool, ortools_available: bool}}` — all fields reflect real checks, not hardcoded `true`.
- [x] Alembic `upgrade head` runs cleanly against a fresh Postgres instance.
- [x] Frontend loads `/dashboard` with zero browser console errors.

## AC-P2 Database
- [x] All 14 entities in docs/DATABASE.md exist as tables with the documented columns, PK/FK, indexes, unique constraints.
- [x] Seed script inserts exactly 100 flights, 30 gates, 2 runways, and is idempotent (re-running doesn't duplicate rows).
- [x] A pytest suite asserts row counts and at least one FK integrity check per relationship.

## AC-P3 Data Pipeline
- [ ] Malformed CSV (bad timestamp, missing required column, duplicate flight_id) is rejected with a structured 422 error naming the row and field — never silently dropped or accepted.
- [ ] A duplicate-flight test and a malformed-timestamp test both pass.

## AC-P4 ML
- [ ] Training script produces a persisted model file (joblib) plus a metrics JSON containing real MAE/RMSE/R² computed on a held-out test split.
- [ ] Feature list is documented in docs/ML.md with an explicit "available at prediction time" column; no feature derived from post-flight actuals is used.
- [ ] `POST /api/predictions` returns a prediction whose value is traceable to the loaded model (log line with model version + input hash).
- [ ] If no model file exists, the endpoint returns a documented 503, never a random number.

## AC-P5 Risk
- [ ] Risk label is computed purely from `system_config` thresholds and the predicted value; changing the config changes the label without a code change.

## AC-P6 Gate System
- [ ] Gate compatibility/eligibility/state transitions match docs/GATE_SYSTEM.md exactly; unit tests cover every state transition table row.

## AC-P7 Conflict Engine
- [ ] Interval-overlap tests pass for: full overlap, partial overlap, touching intervals (boundary = no conflict unless buffer violated), turnaround-buffer violation, blocked-gate conflict, 3+ flight chain on one gate.

## AC-P8 Baseline
- [ ] Running the baseline on the seeded 100/30/2 dataset produces a deterministic, reproducible assignment (same output on repeat runs) and a metrics record with real conflict/utilization counts, not hardcoded numbers.

## AC-P9 MILP
- [ ] Solver actually runs (Gurobi if licensed in the deployment environment, else OR-Tools) and the response states which one, its native status string, objective value, and wall-clock solve time pulled from the solver, not fabricated.
- [ ] An intentionally infeasible scenario (e.g., more international flights than international-eligible gates) returns `status=INFEASIBLE` with a human-readable reason — not a fake assignment.

## AC-P10 Independent Validator
- [ ] A corrupted/forced-invalid solver output (used only in a test) is rejected by the validator with the specific violated constraint named; it is never forwarded to the API layer as valid.
- [ ] Every real optimizer run in the demo passes 100% of the hard-constraint checks in docs/OPTIMIZATION.md §5.

## AC-P11 Before/After Analytics
- [ ] Comparison numbers (conflict count delta, avg delay delta, gate changes, remote-stand count, taxi distance) are recomputed from the two stored assignment sets at request time — no cached "improvement %" constant anywhere in source.

## AC-P12 Simulation
- [ ] Each of the 7 scenarios in docs/SIMULATION.md actually mutates rows in `flights`/`gates`/`runways` and is reflected by a subsequent `GET`, not just returned in the POST response body.

## AC-P13 Cascade
- [ ] Cascade output lists a concrete propagation path of real flight/gate IDs pulled from the graph traversal in docs/CASCADE_ENGINE.md — never a templated sentence with no ID substitution.

## AC-P14 Re-optimization
- [ ] After Runway 2 closure, re-running the full pipeline (predict→conflict→cascade→optimize→validate) produces a new `optimization_run` row distinct from the pre-scenario one, and the timeline/map/analytics/alerts endpoints reflect the new state.

## AC-P15 FastAPI
- [ ] Every endpoint in docs/API.md has an automated test for at least one success and one documented error case.

## AC-P16 Frontend Foundation
- [ ] Every route renders Loading → data or documented Empty/Error state depending on backend response; verified by at least one Vitest test per state per route group.

## AC-P17 Command Center / AC-P18 Airport Map / AC-P19 Timeline / AC-P20 Analytics&Alerts&Explain
- [ ] Each of the 15 signature UI elements in REQUIREMENTS.md is present and backed by a real API call (verified via browser network tab or an integration test asserting the fetch call is made).

## AC-P21 Testing
- [ ] `pytest --cov` runs with 0 failing tests and a coverage report is produced (no minimum % gate required for hackathon, but the number must be reported honestly).
- [ ] `vitest run` runs with 0 failing tests.

## AC-P22 Docker
- [ ] `docker compose up --build` brings up all 3 services and `/api/health` returns 200 from inside the compose network.

## AC-P23 CI/CD
- [ ] GitHub Actions workflow completes install→lint→backend tests→frontend tests→build→docker validation on a clean push, and is configured to fail (non-zero exit) on any step failure.

## AC-P24 Deployment
- [ ] A documented, followable set of steps exists for deploying frontend/backend/DB; if not actually deployed during the hackathon, this is stated explicitly as "documented but not executed" — never claimed as live without a verifiable URL.

## AC-FINAL System Test (must all pass in one session, in order)
1. Seed 100 flights / 30 gates / 2 runways.
2. Validate → 0 rejected rows on the clean seed set.
3. Predict → risk-classify all 100 flights.
4. Detect conflicts on baseline.
5. Run cascade analysis.
6. Run MILP optimization; independent validator passes.
7. Baseline vs optimized comparison shows real (possibly zero or negative) deltas — not a hardcoded positive improvement.
8. Explain at least one gate recommendation with system-derived reasons.
9. Run "Runway Closure" scenario on Runway 2.
10. Re-run steps 3–8; new results differ from step 1–8's stored run and are all internally consistent (validator passes again).
11. Map, timeline, analytics, and alerts UI reflect the new state without a manual page-source edit.

If any numbered step fails, the final report must say so explicitly under "Requirements Not Completed" — it must not be marked done.
