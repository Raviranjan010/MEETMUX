# SYSTEM_DESIGN.md

## End-to-end pipeline
```
CSV/JSON upload
  → pipeline/validation.py (schema, types, required fields)
  → pipeline/cleaning.py (normalize timestamps to UTC, dedupe by flight_id+scheduled_arrival)
  → persist flights (+ weather_records, if included)
  → ml/features.py builds feature vectors
  → ml/model.py predicts actual_taxi_minutes → services/risk.py derives delay + LOW/MED/HIGH
  → services/conflict.py detects overlaps on current (baseline or committed) assignment
  → services/baseline.py OR optimizer/milp.py produces an assignment
  → optimizer/validator.py checks the assignment (always, even for baseline, per REQUIREMENTS R8)
  → services/analytics.py computes baseline-vs-optimized deltas
  → services/cascade.py traces downstream impact of any HIGH-risk or conflicted flight
  → services/alerts.py raises alerts from conflicts/HIGH risk/solver issues
  → services/explain.py answers "why this gate" for a specific flight+assignment
  → audit_records row written for every mutating action
```

## Request lifecycle for a scenario ("Runway Closure")
1. `POST /api/scenarios/run {type: RUNWAY_CLOSURE, target: "RWY-2"}`
2. `services/simulation.py` sets `runways.status = CLOSED` for RWY-2, persists a `scenarios` row.
3. Any flight whose planned runway was RWY-2 is reassigned to RWY-1 in-memory for downstream recompute, and this changes taxi-time features → re-predict for affected flights.
4. `services/conflict.py` + `services/cascade.py` re-run against the new state.
5. `services/reoptimize.py` orchestrates: predict → conflict → cascade → `optimizer/milp.py` → `optimizer/validator.py`.
6. New `optimization_run` row created (never overwrites the previous one — audit history is append-only).
7. Response includes the new run ID; UI re-fetches map/timeline/analytics/alerts.

## Concurrency
Single-writer assumption for the hackathon build: one operator, one active scenario/optimization at a time. `optimization_runs.status` prevents starting a second run while one is `RUNNING` (returns 409). No distributed locking needed (see DECISION_LOG D-002).

## State ownership
`gate_assignments` has a `status` column: `BASELINE`, `PROPOSED` (from an optimizer run not yet accepted), `COMMITTED` (operator accepted). Only `COMMITTED` assignments count as "the schedule" for conflict/cascade purposes going forward; `PROPOSED` is what the operator reviews via Accept/Reject.
