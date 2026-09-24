# TROUBLESHOOTING.md

| Symptom | Likely cause | Fix |
|---|---|---|
| `/api/health` shows `database: false` | Postgres not up / wrong `DATABASE_URL` | Check compose service health, confirm env var |
| `/api/health` shows both solvers unavailable | Gurobi not licensed AND `ortools` not installed | `pip install ortools`; Gurobi is optional by design |
| `/api/predictions` returns 503 | No trained model file found by `ml/registry.py` | Run the training script (Phase 4) to produce a `models/*.joblib` |
| Optimizer stuck in RUNNING | Solve exceeded `optimizer_timeout_seconds` but status not yet persisted | Check backend logs for the background task exception; ensure timeout enforcement wraps the solver call |
| Frontend shows CORS error | Backend CORS allow-list doesn't include the frontend origin | Update backend CORS config env var |
| Alembic migration fails on fresh DB | Migration order/dependency issue | Check `alembic history`, ensure P2's initial migration runs first |
| Seed script duplicates rows on rerun | Seed script not idempotent | Ensure seed checks for existing rows (by a stable key) before inserting |
