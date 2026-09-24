# SIMULATION.md

Every scenario type mutates real rows (never a frontend-only number change) and creates a `scenarios` row. `POST /api/scenarios/run {type, target_reference, params}`.

| Type | target_reference | params | State mutation |
|---|---|---|---|
| HEAVY_RAIN | airport code | `{visibility_m, wind_speed_kt}` | Insert `weather_records` row `condition=HEAVY_RAIN`; triggers re-prediction (worse taxi times) for flights scheduled in the affected window |
| RUNWAY_CLOSURE | runway code (e.g. `RWY-2`) | `{}` | `runways.status = CLOSED`; all flights with that `runway_id` need reassignment to remaining active runway(s) |
| GATE_CLOSURE | gate code | `{}` | `gates.status = BLOCKED`; any flight currently/planned there must be reassigned |
| TRAFFIC_SURGE | airport code | `{additional_flights: int}` | Inserts N synthetic flights (`is_synthetic=true`) into the relevant time window |
| FLIGHT_DELAY | flight_number | `{delay_minutes}` | Shifts that flight's `scheduled_arrival`/`scheduled_departure` by `delay_minutes`; may create downstream turnaround conflicts |
| GATE_CONFLICT | gate code | `{}` | Forces two existing flights onto the same gate with overlapping intervals (for demo purposes only, `is_synthetic=true` marked on the forcing action in audit) to demonstrate conflict detection |
| CASCADE_DELAY | flight_number | `{delay_minutes}` | Same mechanism as FLIGHT_DELAY but explicitly intended to trigger `services/cascade.py` on a flight with tight downstream turnarounds |

## Contract
`POST /api/scenarios/run` only mutates state and returns `{scenario_id, state_changes}`. It does **not** automatically re-run prediction/conflict/cascade/optimization — that is a separate, explicit call to `POST /api/reoptimize {scenario_id}` (REOPTIMIZATION.md), so the operator can see "what changed" before choosing to re-optimize. This separation also makes each step independently testable and auditable.
