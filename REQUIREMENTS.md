# REQUIREMENTS.md — RunwayOptX

Status: SOURCE OF TRUTH (priority 2, after Problem Statement). Supersedes AGENTS.md and all docs/ on conflict. Superseded only by ACCEPTANCE_CRITERIA.md.

## R0. Problem Statement (fixed, do not reinterpret)
Predictive Air Traffic Delay & Airport Gate Scheduling Optimizer. Stack: React + FastAPI + Gurobi/OR-Tools + Scikit-Learn. Predict runway/taxi delay; solve gate assignment as a MILP.

## R1. Product Flow
`Predict → Detect → Optimize → Simulate → Explain`, human-in-the-loop, backend is source of truth. This is a decision-support tool, not autonomous control — every optimizer output requires an Accept/Reject/Re-optimize action from a human operator role before it changes the "committed" schedule (see R14).

## R2. Functional Requirements

| ID | Requirement |
|---|---|
| FR-1 | Ingest flight data from CSV/JSON, validate, clean, normalize |
| FR-2 | Engineer ML features from validated flight/weather/traffic data |
| FR-3 | Predict runway taxi delay (minutes) per flight |
| FR-4 | Classify predicted delay into LOW/MEDIUM/HIGH risk using configurable thresholds |
| FR-5 | Model gates: identity, terminal, type, compatibility, eligibility, state, availability window |
| FR-6 | Detect gate conflicts via true time-interval overlap (arrival→turnaround→departure + buffer) |
| FR-7 | Generate a deterministic baseline gate assignment (first-fit, defined in R8) |
| FR-8 | Optimize gate assignment via MILP (Gurobi primary, OR-Tools fallback) |
| FR-9 | Independently validate every optimizer solution against all hard constraints before it can be shown or committed |
| FR-10 | Compute baseline vs optimized comparison metrics from real computed data only |
| FR-11 | Run named disruption scenarios that mutate real backend state |
| FR-12 | Re-run prediction, conflict detection, cascade analysis, and optimization after a scenario |
| FR-13 | Detect cascade delay propagation via actual flight/gate dependency chains |
| FR-14 | Explain a gate recommendation using only facts computed by the system |
| FR-15 | Surface operational alerts derived from real state (conflicts, high risk, infeasible runs, solver issues) |
| FR-16 | Provide an audit trail of every optimization run and every operator action |
| FR-17 | Provide a command-center UI covering all routes in docs/FRONTEND.md |
| FR-18 | Support Accept / Reject / View Alternatives / Re-optimize actions on any assignment |

## R3. Non-Functional Requirements

| ID | Requirement |
|---|---|
| NFR-1 | Demo scale: 100 flights, 30 gates, 2 runways, multiple airlines/aircraft types, deterministic seed |
| NFR-2 | No external API dependency required for the app to run; synthetic data must be labeled `is_synthetic=true` everywhere it is surfaced |
| NFR-3 | Never fabricate: ML metrics, solver output, optimization assignments, improvement %, cascade causes, explanations, test results, deployment status |
| NFR-4 | No placeholders (`TODO`, `FIXME`, bare `pass`, `NotImplementedError`) in production code paths |
| NFR-5 | Backend is sole source of truth; frontend holds no independent copy of operational business logic |
| NFR-6 | Optimizer must run as a background task (not block the request thread) with a configurable timeout |
| NFR-7 | Every optimizer result must state which solver actually ran and its raw status |

## R4. Out of Scope (explicitly, to prevent scope drift)
Authentication/authorization beyond a single implicit operator role, multi-tenant/multi-airport support, real-time external flight-data feeds, mobile app, Kafka/Redis/Kubernetes/microservices, any LLM/chatbot feature, payment/billing, multi-language i18n.

## R5. Roles
Single role for v1: **Operator**. No login system required for the hackathon build; if auth is added later it must not change any of the above business logic. This resolves the "authentication requirements" contradiction (see DECISION_LOG D-011).

## R6. Data Ownership
All entities in docs/DATABASE.md live in PostgreSQL. Frontend fetches via the API in docs/API.md and renders; it performs no independent conflict/optimization/cascade computation.

## R7. Delay Definition (prevents ML/domain ambiguity)
"Runway/taxi delay" = `predicted_taxi_minutes - scheduled_taxi_minutes`, where `scheduled_taxi_minutes` is a static reference value per airport/runway config (`docs/DATA_DICTIONARY.md#scheduled_taxi_minutes`). The model predicts `actual_taxi_minutes`; delay is derived, not predicted directly. This keeps the regression target concrete and testable.

## R8. Baseline Algorithm (exact, non-negotiable definition)
For each flight in ascending `scheduled_arrival_time` order: assign the first gate (ordered by `gate_id` ascending) that is (a) compatible with aircraft type, (b) satisfies domestic/international eligibility, (c) not BLOCKED, (d) has no time-interval overlap (including turnaround buffer) with any gate assignment already made in this baseline run. If no gate qualifies, the flight is left UNASSIGNED and flagged. This is a greedy, single-pass, deterministic algorithm — it is the ONLY approved baseline algorithm; it must never be swapped in as the production optimizer.

## R9. Configurable Values (all defaults; see docs/DATABASE.md `system_config` table)

| Config Key | Default | Range | Purpose |
|---|---|---|---|
| `risk_low_max_minutes` | 5 | 0–30 | upper bound of LOW risk band |
| `risk_medium_max_minutes` | 15 | risk_low_max < x ≤ 60 | upper bound of MEDIUM risk band (above = HIGH) |
| `turnaround_buffer_minutes` | 15 | 5–60 | mandatory buffer between departure of one flight and arrival of next at same gate |
| `optimizer_timeout_seconds` | 60 | 10–300 | hard wall-clock cap per solver run |
| `optimizer_weight_delay_cost` | 1.0 | 0–100 | objective weight, predicted delay minutes |
| `optimizer_weight_conflict_cost` | 50.0 | 0–1000 | objective weight, penalty per unresolved conflict (should be ~infeasible-avoidance weight) |
| `optimizer_weight_reassignment_cost` | 5.0 | 0–100 | objective weight, penalty for moving a flight off its baseline gate |
| `optimizer_weight_taxi_distance` | 0.1 | 0–10 | objective weight, per meter of gate-to-runway taxi distance |
| `optimizer_weight_remote_stand` | 10.0 | 0–100 | objective weight, flat penalty for assigning a remote (non-jetbridge) stand |
| `cascade_max_depth` | 5 | 1–20 | max propagation hops the cascade engine will traverse |

These live in one `system_config` row (or `.env`-seeded table) and are read at request time — never hardcoded in UI or optimizer code.

## R10. Traceability
See docs/DECISION_LOG.md and the Requirements Traceability Matrix in IMPLEMENTATION_PLAN.md §9 for ID→phase→file→test mapping.

## R11. Change Control
Any change to this file after Phase 0 sign-off requires a new entry in `docs/DECISION_LOG.md` referencing the requirement ID changed.
