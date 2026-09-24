# SECURITY.md

- Secrets via `.env` (local) / platform env vars (deployed), never committed. `.env.example` lists every required key with placeholder values: `DATABASE_URL`, `GUROBI_LICENSE_PATH` (optional), `VITE_API_BASE_URL`, `MODEL_VERSION_OVERRIDE` (optional).
- No Gurobi credentials, DB passwords, or tokens in source, logs, or error messages.
- Upload validation (`/api/data/upload`): max file size 5 MB, only `.csv`/`.json`, schema-validated before any DB write, rejected rows reported per-row rather than aborting the whole batch silently.
- CORS: explicit allow-list of the frontend origin(s) from env config, not `*`, even in the demo.
- All DB access via SQLAlchemy parameterized queries/ORM — no raw string-interpolated SQL.
- Error responses never include stack traces or raw exception text to the client; full detail goes to server-side logs only (`docs/OBSERVABILITY.md`).
- Single implicit "operator" role for v1 (REQUIREMENTS R5) — no auth system required for the hackathon; this must not block adding auth later without touching business logic.
