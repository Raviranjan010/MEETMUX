# ALERTS.md

Alerts are raised (not polled/generated from thin air) at these trigger points, written by the module that detects the condition:
| Category | Raised by | Trigger |
|---|---|---|
| CONFLICT | `services/conflict.py` | new time-overlap or blocked-gate conflict detected on COMMITTED assignments |
| HIGH_RISK | `services/risk.py` | a flight's risk_level becomes HIGH |
| INFEASIBLE | `optimizer/milp.py` | optimization run status = INFEASIBLE |
| SOLVER_ISSUE | `optimizer/milp.py` | status = SOLVER_UNAVAILABLE, TIMEOUT, or ERROR |
| CASCADE | `services/cascade.py` | a cascade event with severity HIGH is produced |

Alerts are resolved (`resolved=true`) when the underlying condition is confirmed gone on the next relevant recompute (e.g. a conflict alert resolves once that conflict no longer appears in a fresh `conflicts/detect` call after re-optimization). `GET /api/alerts?resolved=false&severity=` for the UI's active alert list.
