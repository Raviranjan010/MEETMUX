# Rule: Backend
- FastAPI + Pydantic schemas for every request/response — no raw dict responses.
- SQLAlchemy models match docs/DATABASE.md exactly; any deviation requires a DECISION_LOG entry.
- All config values in REQUIREMENTS.md §R9 are read from `system_config`, never hardcoded.
- Long-running work (optimizer, reoptimize) uses BackgroundTasks; the HTTP handler returns immediately with a run ID.
- Every endpoint has an error path following the shape in docs/API.md — no bare 500s without a caught, logged, typed error.
