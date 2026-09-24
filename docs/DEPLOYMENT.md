# DEPLOYMENT.md

## Target topology
Frontend → Vercel (or Netlify). Backend → Render/Railway/Fly/AWS/GCP (any platform that runs a long-lived Python process + supports background tasks and env vars). Database → managed PostgreSQL (Neon/Supabase/RDS/Railway Postgres — any).

## Required steps (documented here even if not executed in this environment — see AGENTS.md "Environment Reality")
1. Provision managed Postgres; set `DATABASE_URL`.
2. Run `alembic upgrade head` against it (as a one-off job or release step).
3. Run `scripts/seed_demo.py` once for the 100/30/2 dataset (idempotent).
4. Deploy backend with env vars from `.env.example`; Gurobi license is OPTIONAL — if absent, `/api/health.optimizer.gurobi_available=false` and the app runs on OR-Tools, which must be stated in the deployed app's UI (solver status pill), not hidden.
5. Deploy frontend with `VITE_API_BASE_URL` pointing at the deployed backend.
6. Verify: hit the deployed `/api/health`, confirm `status: ok` (or `degraded` with an honest reason), load the deployed frontend `/dashboard`.

## Honesty requirement
If deployment is not actually carried out during the hackathon, the final report must say "documented but not executed," with no live URL claimed. A live URL is only reported if `GET {url}/api/health` was actually hit and its response recorded.

## External API optionality
No external API (weather feed, real flight data feed) is required for the app to function — all such data is synthetic/seeded per REQUIREMENTS NFR-2.
