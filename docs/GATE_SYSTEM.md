# GATE_SYSTEM.md

## Gate fields
`code, gate_type (JETBRIDGE|REMOTE), max_aircraft_size (SMALL|MEDIUM|LARGE), eligible_route_types (DOMESTIC|INTERNATIONAL|BOTH), status (AVAILABLE|OCCUPIED|RESERVED|BLOCKED), taxi_distance_meters`.

## State machine (persistent `status` column)
| From | Event | To |
|---|---|---|
| AVAILABLE | assignment committed, flight now on-ground | OCCUPIED |
| OCCUPIED | flight departs (actual_departure set) | AVAILABLE |
| AVAILABLE | operator/scenario reserves gate | RESERVED |
| RESERVED | reservation expires or is cancelled | AVAILABLE |
| any | GATE_CLOSURE scenario applied | BLOCKED |
| BLOCKED | scenario reversed / operator clears | AVAILABLE |

`CONFLICT` is NOT a stored state — it is a derived, display-only flag computed live by the conflict engine when two committed/proposed assignments' intervals overlap at that gate. Storing it as persistent state would let it go stale; it must always be recomputed on read.

## Compatibility rule
A flight `i` may use gate `j` only if: `aircraft.size_class(i) ≤ gate.max_aircraft_size(j)` (SMALL < MEDIUM < LARGE ordering) AND `flight.route_type(i) ∈ gate.eligible_route_types(j)` (BOTH satisfies either) AND `gate.status(j) != BLOCKED`.

## Turnaround
Minimum ground time = `system_config.turnaround_buffer_minutes` (default 15) added after `scheduled_departure`/`actual_departure` before the gate is considered free for the next flight, and before `scheduled_arrival` as a pre-buffer. This buffer is what the conflict engine and the MILP both use — one shared implementation (`services/conflict.py::intervals_overlap`), never duplicated logic in the optimizer.
