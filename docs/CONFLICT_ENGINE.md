# CONFLICT_ENGINE.md

## Interval model
Each flight-at-gate occupies `[arrival_time − buffer, departure_time + buffer]` where `buffer = system_config.turnaround_buffer_minutes`. Two intervals `[a1,b1]` and `[a2,b2]` conflict iff `a1 < b2 AND a2 < b1` (strict inequality — touching endpoints, `b1 == a2`, is NOT a conflict, matching real turnaround scheduling where back-to-back is allowed once the buffer is already included in the interval bounds).

## Required test cases (must all exist and pass, Phase 7)
1. Full overlap (one interval contains another) → conflict.
2. Partial overlap → conflict.
3. Touching intervals with buffer already satisfied (`b1 == a2`) → no conflict.
4. Turnaround-buffer violation (intervals don't nominally overlap but gap < buffer) → conflict, because buffer is already folded into the interval bounds above.
5. Two flights at a BLOCKED gate → conflict category `BLOCKED_GATE`, separate from `TIME_OVERLAP`.
6. Three or more flights chained at one gate → engine must report every pairwise conflicting pair, not just the first found.

## Output shape
`{gate_id, conflicting_flight_ids: [...], conflict_type: "TIME_OVERLAP"|"BLOCKED_GATE", overlap_minutes, detected_against: "BASELINE"|"COMMITTED"|optimization_run_id}`. Used by both `/api/conflicts/detect` and internally by the MILP's constraint-5 pair list (OPTIMIZATION.md §Hard constraints item 5) — one implementation, two callers.
