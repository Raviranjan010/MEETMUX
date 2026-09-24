# EXPLAINABILITY.md

`GET /api/explain/{gate_assignment_id}` returns a structured explanation built ONLY from facts already computed elsewhere in the system — never a free-generated sentence with invented content.

## Response shape
```json
{
  "flight_id": "...", "gate_id": "...", "optimization_run_id": "...",
  "reasons": [
    {"code": "COMPATIBLE_AIRCRAFT", "detail": "A320 (MEDIUM) fits gate max size MEDIUM"},
    {"code": "ROUTE_ELIGIBLE", "detail": "Flight is DOMESTIC; gate eligible_route_types=BOTH"},
    {"code": "NO_OVERLAP", "detail": "No conflicting interval found at this gate for this run"},
    {"code": "LOWER_OBJECTIVE_COST", "detail": "Objective contribution 12.4 vs next-best gate's 18.9"},
    {"code": "REDUCED_DOWNSTREAM_CONFLICT", "detail": "0 cascade-affected flights vs 2 for the alternative gate G22"}
  ],
  "alternatives_considered": [{"gate_id": "G22", "objective_contribution": 18.9, "rejected_reason": "higher taxi distance"}]
}
```
Each `reason.code` maps 1:1 to a real check already performed by `optimizer/validator.py`, `services/conflict.py`, or the objective breakdown stored in `gate_assignments.objective_contribution` / a per-term breakdown computed at explain-time from the same weights in `config_snapshot`. If a reason can't be backed by a real stored fact, it is omitted — never invented to fill out the list.
