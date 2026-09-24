# Skill: reoptimization

**Purpose:** Orchestrate predict→conflict→cascade→optimize→validate after a scenario.
**When to use:** Phase 14, triggered by POST /api/reoptimize.
**Inputs:** scenario_id, current committed state.
**Outputs:** A new optimization_runs row (never overwriting the prior one) + updated alerts.
**Files involved:** backend/app/services/reoptimize.py; tests/services/test_reoptimize.py
**Validation requirements:** New run is validated (optimization-validation skill) before being exposed as usable; old run remains queryable for before/after comparison.
**Failure handling:** Any step failure halts the chain with a clear status on the run record (e.g. status=ERROR with a message) rather than presenting a partially-completed chain as done.
**Prohibited shortcuts:** Never skip re-running conflict/cascade 'because only one flight changed' — reassignment pressure can affect unrelated flights.
