# CICD.md

GitHub Actions workflow `.github/workflows/ci.yml`, single workflow, steps in order (fail-fast, each step's non-zero exit fails the job):
1. **Install** — `pip install -r backend/requirements.txt`, `npm ci` in `frontend/`.
2. **Lint** — `ruff check backend/` (or flake8), `eslint frontend/src`.
3. **Backend tests** — `pytest --cov=backend/app backend/tests`.
4. **Frontend tests** — `vitest run` in `frontend/`.
5. **Frontend build** — `npm run build` in `frontend/` (catches TS/build errors even if unit tests pass).
6. **Docker validation** — `docker compose build` (build-only, no full up/health-check in CI unless a Postgres service container is also configured in the workflow for an integration step).

Triggers: on push and pull_request to `main`. No deployment step in this workflow (deployment is manual/documented per DEPLOYMENT.md, not auto-deployed by CI, to avoid claiming an unverified live deployment).
