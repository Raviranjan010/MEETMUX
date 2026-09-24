# CASCADE_ENGINE.md

## Graph model
Nodes: flights, gates, runways. Edges: `flight → gate` (occupies), `flight → runway` (uses), `gate → next flight at same gate` (turnaround dependency), `runway → flights scheduled on it` (capacity dependency). Cascade = breadth-first traversal from a root event (delay, closure, conflict) up to `system_config.cascade_max_depth` hops (default 5), following only edges that represent a *real, computed* dependency — e.g. "flight B is delayed because it shares gate G14 with flight A, whose departure slipped, violating B's turnaround buffer."

## Algorithm (Phase 13)
1. Root event: a flight's `predicted_delay_minutes` increases past a threshold, OR a gate/runway is closed/blocked.
2. For a delayed flight, find every OTHER flight at its assigned gate whose arrival interval now overlaps (conflict engine) due to the shift → these become depth-1 affected nodes with `effect: "TURNAROUND_VIOLATION"`.
3. For a closed runway/gate, find every flight whose `runway_id`/`gate_id` matches → depth-1 affected nodes with `effect: "REASSIGNMENT_REQUIRED"`.
4. Recurse: each depth-1 affected flight's own gate/turnaround situation is re-evaluated for depth-2 effects, and so on, until no new affected flights are found or `cascade_max_depth` is reached.
5. Output `propagation_path`: ordered list of `{depth, type: "flight"|"gate"|"runway", id, effect}`. `affected_flight_ids`: deduplicated set. `severity`: HIGH if any affected flight becomes HIGH risk or unassignable, else MEDIUM/LOW by count of affected flights (`≥5 → MEDIUM`, `≥10 or any HIGH risk → HIGH`, else LOW — thresholds documented here since they are display/severity heuristics, not a system_config item; make configurable only if judges/testing reveal a need, logged in DECISION_LOG if changed).

## Prohibition
Never write a cascade explanation string that names a flight/gate not actually present in `propagation_path`; never invent a causal link the BFS above didn't actually traverse.
