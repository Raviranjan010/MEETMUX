# RunwayOptX

**Predictive Air Traffic Delay & Airport Gate Scheduling Optimizer** — an airport operations decision-support system: `Predict → Detect → Optimize → Simulate → Explain`.

This repository currently contains the **complete specification package**, not the application itself. It exists so an implementation agent (e.g. Antigravity) can execute the 25-phase build in `IMPLEMENTATION_PLAN.md` without needing the product/architecture requirements re-explained.

## Start here
1. Read `AGENTS.md` for the mandatory read order and rules.
2. Read `REQUIREMENTS.md` and `ACCEPTANCE_CRITERIA.md` — these are the source of truth.
3. Read everything in `docs/`.
4. Read `.agents/rules/` and `.agents/skills/`.
5. Follow `IMPLEMENTATION_PLAN.md` phase by phase.
6. If you are Antigravity, your master instruction is `ANTIGRAVITY_PROMPT.md`.

## Stack
React + TypeScript + Tailwind (frontend) · FastAPI + SQLAlchemy + Alembic (backend) · PostgreSQL (data) · Scikit-Learn (ML) · Gurobi primary / OR-Tools fallback (MILP optimization) · Docker Compose (local) · GitHub Actions (CI).

## Non-negotiables
No fabricated metrics, solver results, or test results. Backend is the source of truth. Every optimizer result is independently validated before it is shown. See `NON_FABRICATION.md`.

## Status
Specification package complete. Application implementation has not started — Phase 0 (Specification Audit) is the next step.
