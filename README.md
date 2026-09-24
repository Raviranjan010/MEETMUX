# RunwayOptX

**Predictive Air Traffic Delay & Airport Gate Scheduling Optimizer** — an airport operations decision-support system: `Predict → Detect → Optimize → Simulate → Explain`.

This repository contains the RunwayOptX specification and an in-progress application implementation. The implementation has backend domain modules, API routes, a React frontend, an ML artifact, optimizer integration, and tests, but several acceptance criteria remain incomplete. Consult `ACCEPTANCE_CRITERIA.md` and the latest report in `docs/phase-reports/` for verified status; source files alone do not indicate completion.

## Start here
1. Read `AGENTS.md` for the mandatory read order and rules.
2. Read `REQUIREMENTS.md` and `ACCEPTANCE_CRITERIA.md` — these are the source of truth.
3. Read everything in `docs/`.
4. Read `.agents/rules/` and `.agents/skills/`.
5. Follow `IMPLEMENTATION_PLAN.md` phase by phase.
6. Follow the phase gates and verification rules in `AGENTS.md` and `IMPLEMENTATION_PLAN.md`.

## Stack
React + TypeScript + Tailwind (frontend) · FastAPI + SQLAlchemy + Alembic (backend) · PostgreSQL (data) · Scikit-Learn (ML) · Gurobi primary / OR-Tools fallback (MILP optimization) · Docker Compose (local) · GitHub Actions (CI).

## Non-negotiables
No fabricated metrics, solver results, or test results. Backend is the source of truth. Every optimizer result is independently validated before it is shown. See `NON_FABRICATION.md`.

## Status
Application implementation is in progress. Local verification currently uses the checked-in `.env` SQLite URL, which conflicts with accepted decision D-017 (PostgreSQL-only runtime). Docker/PostgreSQL deployment has not been verified in this environment.
