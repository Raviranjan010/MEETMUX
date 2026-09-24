# ANALYTICS.md

## Live analytics (`GET /api/analytics`)
Computed at request time from current committed state: `fleet_utilization` (occupied gates / total non-blocked gates), `avg_predicted_delay` (mean of latest predictions), `risk_distribution` (counts by LOW/MEDIUM/HIGH), `active_conflicts` (live call to conflict engine against COMMITTED assignments).

## Baseline vs optimized comparison (`GET /api/analytics/comparison?optimization_run_id=`)
Loads the sentinel baseline run's `gate_assignments` and the specified MILP run's `gate_assignments`, and for EACH set independently computes: conflict count (via conflict engine), total predicted delay minutes, unassigned flight count, remote-stand count, total taxi distance, gate-change count (assignments differing from baseline gate). Deltas = optimized − baseline for each metric, computed at request time — no cached/hardcoded percentage anywhere in source or config.
