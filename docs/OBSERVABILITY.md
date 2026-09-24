# OBSERVABILITY.md

Structured logging (JSON lines, Python `logging` + a simple formatter) for:
- Every prediction request: `flight_id, model_version, predicted_taxi_minutes, latency_ms`.
- Every optimization run: `optimization_run_id, run_type, solver_used, solver_status, status, objective_value, solve_time_ms`.
- Every scenario execution: `scenario_id, type, target_reference, affected_flight_count`.
- Every error: `request_id, endpoint, error_code, message` (no stack trace or secret values in the log line itself beyond what's needed to debug — full traceback may go to a server-only debug log, never to the API response).

Never log: `.env` values, DB connection strings with credentials, Gurobi license content. Log level `INFO` for the above, `ERROR` for failures, `DEBUG` gated behind an env flag for verbose solver output.
