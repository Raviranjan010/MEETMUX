# DATABASE.md — PostgreSQL schema (SQLAlchemy + Alembic)

All tables: `id UUID PK default gen_random_uuid()`, `created_at TIMESTAMPTZ default now()`, `updated_at TIMESTAMPTZ default now()` unless noted. All FKs `ON DELETE RESTRICT` unless noted.

## airports
`code VARCHAR(4) UNIQUE NOT NULL`, `name TEXT NOT NULL`, `timezone TEXT NOT NULL`.

## terminals
`airport_id FK→airports`, `code VARCHAR(8) NOT NULL`, `name TEXT`. Unique `(airport_id, code)`.

## runways
`airport_id FK→airports`, `code VARCHAR(8) NOT NULL` (e.g. `RWY-1`), `status ENUM(ACTIVE,CLOSED) NOT NULL DEFAULT ACTIVE`, `taxi_base_minutes NUMERIC(5,2) NOT NULL` (scheduled_taxi_minutes reference, see REQUIREMENTS R7). Unique `(airport_id, code)`. Index on `status`.

## gates
`terminal_id FK→terminals`, `code VARCHAR(8) NOT NULL`, `gate_type ENUM(JETBRIDGE,REMOTE) NOT NULL`, `max_aircraft_size ENUM(SMALL,MEDIUM,LARGE) NOT NULL`, `eligible_route_types ENUM(DOMESTIC,INTERNATIONAL,BOTH) NOT NULL`, `status ENUM(AVAILABLE,OCCUPIED,RESERVED,BLOCKED) NOT NULL DEFAULT AVAILABLE` (CONFLICT is derived, not stored), `taxi_distance_meters NUMERIC(6,1) NOT NULL`. Unique `(terminal_id, code)`. Index on `status`, `gate_type`.

## aircraft
`registration VARCHAR(16) UNIQUE NOT NULL`, `type_code VARCHAR(8) NOT NULL` (e.g. `A320`), `size_class ENUM(SMALL,MEDIUM,LARGE) NOT NULL`.

## flights
`flight_number VARCHAR(8) NOT NULL`, `airline VARCHAR(4) NOT NULL`, `aircraft_id FK→aircraft`, `route_type ENUM(DOMESTIC,INTERNATIONAL) NOT NULL`, `origin VARCHAR(4)`, `destination VARCHAR(4)`, `runway_id FK→runways NULLABLE`, `scheduled_arrival TIMESTAMPTZ`, `scheduled_departure TIMESTAMPTZ`, `actual_arrival TIMESTAMPTZ NULLABLE`, `actual_departure TIMESTAMPTZ NULLABLE`, `is_synthetic BOOLEAN NOT NULL DEFAULT true`. Unique `(flight_number, scheduled_arrival)`. Index on `scheduled_arrival`, `route_type`, `runway_id`.

## weather_records
`airport_id FK→airports`, `recorded_at TIMESTAMPTZ NOT NULL`, `condition ENUM(CLEAR,RAIN,HEAVY_RAIN,FOG,SNOW) NOT NULL`, `wind_speed_kt NUMERIC(5,1)`, `visibility_m NUMERIC(6,1)`. Index on `(airport_id, recorded_at)`.

## predictions
`flight_id FK→flights`, `model_version VARCHAR(32) NOT NULL`, `predicted_taxi_minutes NUMERIC(6,2) NOT NULL`, `predicted_delay_minutes NUMERIC(6,2) NOT NULL` (derived = predicted_taxi_minutes − runway.taxi_base_minutes), `risk_level ENUM(LOW,MEDIUM,HIGH) NOT NULL`, `feature_snapshot JSONB NOT NULL` (exact inputs used, for auditability). Index on `flight_id`.

## optimization_runs
`run_type ENUM(BASELINE,MILP) NOT NULL`, `scenario_id FK→scenarios NULLABLE`, `solver_used ENUM(GUROBI,ORTOOLS,NONE) NOT NULL`, `solver_status VARCHAR(32) NOT NULL` (raw solver status string), `status ENUM(RUNNING,OPTIMAL,FEASIBLE,INFEASIBLE,TIMEOUT,SOLVER_UNAVAILABLE,ERROR) NOT NULL`, `objective_value NUMERIC(12,3) NULLABLE`, `solve_time_ms INTEGER NULLABLE`, `validation_passed BOOLEAN NULLABLE`, `validation_report JSONB NULLABLE`, `config_snapshot JSONB NOT NULL` (weights/thresholds used). Index on `status`, `created_at`.

## gate_assignments
`optimization_run_id FK→optimization_runs`, `flight_id FK→flights`, `gate_id FK→gates NULLABLE` (null = UNASSIGNED), `assignment_status ENUM(BASELINE,PROPOSED,COMMITTED,REJECTED) NOT NULL`, `objective_contribution NUMERIC(10,3) NULLABLE`. Unique `(optimization_run_id, flight_id)`. Index on `gate_id`, `assignment_status`.

## scenarios
`type ENUM(HEAVY_RAIN,RUNWAY_CLOSURE,GATE_CLOSURE,TRAFFIC_SURGE,FLIGHT_DELAY,GATE_CONFLICT,CASCADE_DELAY) NOT NULL`, `target_reference TEXT NOT NULL` (e.g. gate code / runway code / flight_number), `params JSONB NOT NULL`, `applied_at TIMESTAMPTZ NOT NULL DEFAULT now()`, `resulting_optimization_run_id FK→optimization_runs NULLABLE`.

## alerts
`severity ENUM(INFO,WARNING,CRITICAL) NOT NULL`, `category ENUM(CONFLICT,HIGH_RISK,INFEASIBLE,SOLVER_ISSUE,CASCADE) NOT NULL`, `flight_id FK→flights NULLABLE`, `gate_id FK→gates NULLABLE`, `message TEXT NOT NULL`, `resolved BOOLEAN NOT NULL DEFAULT false`. Index on `resolved`, `severity`.

## cascade_events
`root_flight_id FK→flights NULLABLE`, `root_gate_id FK→gates NULLABLE`, `root_runway_id FK→runways NULLABLE`, `scenario_id FK→scenarios NULLABLE`, `propagation_path JSONB NOT NULL` (ordered list of `{type, id, effect}`), `affected_flight_ids JSONB NOT NULL` (array of UUIDs), `severity ENUM(LOW,MEDIUM,HIGH) NOT NULL`.

## audit_records
`action ENUM(PREDICTION_RUN,OPTIMIZATION_RUN,SCENARIO_RUN,ASSIGNMENT_ACCEPT,ASSIGNMENT_REJECT,DATA_UPLOAD) NOT NULL`, `actor TEXT NOT NULL DEFAULT 'operator'`, `reference_id UUID NULLABLE` (points at the relevant run/scenario/assignment), `details JSONB NOT NULL`. Index on `action`, `created_at`.

## system_config
Single-row (or key/value) table holding every value in REQUIREMENTS.md §R9: `risk_low_max_minutes`, `risk_medium_max_minutes`, `turnaround_buffer_minutes`, `optimizer_timeout_seconds`, `optimizer_weight_delay_cost`, `optimizer_weight_conflict_cost`, `optimizer_weight_reassignment_cost`, `optimizer_weight_taxi_distance`, `optimizer_weight_remote_stand`, `cascade_max_depth`. All NUMERIC/INTEGER with the defaults given there.

## Alembic
One migration per phase that touches schema (P2 creates all tables; later phases only alter if a genuinely new column is needed, logged in DECISION_LOG). Seed data lives in a separate `scripts/seed_demo.py`, not in a migration.
