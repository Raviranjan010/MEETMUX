# REOPTIMIZATION.md

`POST /api/reoptimize {scenario_id}` orchestrates, in this exact order, and stops immediately (returning what it has, with a clear status) if any step errors:

1. Identify affected flights (those referencing the closed/blocked/delayed resource, from the scenario's `state_changes`).
2. Re-run `ml/model.py` predictions for affected flights only (unaffected flights keep their last prediction — do not silently invalidate untouched data).
3. Re-run `services/conflict.py` over the full current committed+proposed assignment set (a closure can create conflicts among previously-unrelated flights via reassignment pressure).
4. Re-run `services/cascade.py` from the scenario's root event.
5. Build and solve a new MILP via `optimizer/milp.py`, seeded with the current committed assignments as `baseline_gate(i)` for the reassignment-penalty term.
6. Run `optimizer/validator.py`.
7. Persist a NEW `optimization_runs` row (`run_type=MILP`, `scenario_id` set) — never overwrite the prior run; `scenarios.resulting_optimization_run_id` is set to this new run's id.
8. Update `alerts` (resolve any that no longer apply, raise new ones) and leave `analytics`/`timeline`/`map` endpoints to recompute live from the new committed state on next GET.

This is a synchronous orchestration function but is invoked via `BackgroundTasks` at the API layer (same async pattern as `/api/optimizer/run`), returning `202 {optimization_run_id, status: RUNNING}` immediately, polled via `GET /api/optimizer/{id}`.
