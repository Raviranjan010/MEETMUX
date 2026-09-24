# DOCKER.md

`docker-compose.yml` services:
- `postgres`: official `postgres:16` image, env `POSTGRES_DB, POSTGRES_USER, POSTGRES_PASSWORD` from `.env`, volume for data persistence, healthcheck `pg_isready`.
- `backend`: builds from `backend/Dockerfile` (python:3.11-slim base), installs `requirements.txt`, runs `alembic upgrade head` then `uvicorn app.main:app --host 0.0.0.0 --port 8000` on container start, `depends_on: postgres` with `condition: service_healthy`, env from `.env`.
- `frontend`: builds from `frontend/Dockerfile` (node:20-slim build stage → static serve, or `vite preview`/nginx), env `VITE_API_BASE_URL=http://localhost:8000` (or the backend service name for internal compose networking, adjusted per actual browser-vs-container access needs), `depends_on: backend`.

## Startup order
postgres (healthy) → backend (runs migrations, then serves) → frontend. `docker compose up --build` must bring all three up with `/api/health` reachable at `http://localhost:8000/api/health` returning `database: true`.

## Environment variables (documented, not hardcoded into the compose file's `environment:` values beyond sane local defaults)
`DATABASE_URL`, `POSTGRES_DB/USER/PASSWORD`, `GUROBI_LICENSE_PATH` (optional, mount as a volume if present), `VITE_API_BASE_URL`.
