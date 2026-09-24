# ARCHITECTURE.md

## Style
Clean **modular monolith**. One FastAPI backend process, organized into modules by domain (`ingestion`, `ml`, `gates`, `conflict`, `baseline`, `optimizer`, `cascade`, `simulation`, `analytics`, `alerts`, `audit`), one React SPA, one PostgreSQL database. No microservices, no message broker, no cache layer, no Kubernetes — see DECISION_LOG D-001.

## Backend module layout
```
backend/app/
  api/routes/        # FastAPI routers, one file per resource (flights.py, gates.py, predictions.py, optimizer.py, scenarios.py, analytics.py, alerts.py, health.py)
  models/            # SQLAlchemy ORM models (one file per entity)
  schemas/           # Pydantic request/response schemas
  services/          # business logic: risk.py, conflict.py, baseline.py, cascade.py, simulation.py, analytics.py, alerts.py, explain.py, reoptimize.py
  optimizer/         # milp.py (Gurobi+OR-Tools), validator.py
  ml/                # features.py, train.py, model.py, registry.py
  pipeline/          # ingestion.py, validation.py, cleaning.py
  core/              # config.py (reads system_config + env), db.py, logging.py, errors.py
  main.py
alembic/
tests/
```

## Frontend module layout
```
frontend/src/
  pages/             # one per route in docs/FRONTEND.md
  components/        # AirportMap, GateTimeline, RiskBadge, SolverStatusPill, ExplainPanel, ComparisonPanel, AlertList, ...
  api/                # axios client + typed request functions, one file per backend resource
  state/              # minimal global state (selected flight, active scenario) — NOT business logic
  routes.tsx
```

## Data flow (one request, e.g. "Run Optimizer")
`UI button click → axios POST /api/optimizer/run → FastAPI route → services/conflict.py (pre-check) → optimizer/milp.py (build+solve model) → optimizer/validator.py (independent check) → persist optimization_run + gate_assignment rows → response → UI updates AirportMap/Timeline/Analytics/Alerts from the response + a follow-up GET`.

## Background execution
Optimizer runs (and full re-optimization) execute via FastAPI `BackgroundTasks` (sufficient for hackathon scale — no Celery/Redis needed, see DECISION_LOG D-002). The client polls `GET /api/optimizer/{id}` for status until `status != RUNNING`.

## Why not microservices/Kafka/Redis/K8s
100 flights / 30 gates / 2 runways is small enough that a monolith with synchronous request/response plus background tasks meets every latency and reliability need in `docs/PERFORMANCE.md`. Adding infra here would cost implementation time without a measurable benefit and would violate the "avoid unnecessary cloud dependencies" requirement.

## Error boundary
All backend errors funnel through `core/errors.py` into a single JSON error shape (see `docs/API.md` §Error Format). The frontend has one shared error-rendering component so every page's Error state looks and behaves consistently.
