# AGENTS.md — RunwayOptX

This file is the entry point for any coding agent (Antigravity or otherwise) working in this repository.

## Read Order (mandatory, in this order)
1. `REQUIREMENTS.md` (source of truth #2, after the problem statement itself)
2. `ACCEPTANCE_CRITERIA.md` (source of truth #3)
3. `docs/ARCHITECTURE.md`
4. `docs/DOMAIN_MODEL.md`, `docs/DATABASE.md`
5. `docs/ML.md`, `docs/OPTIMIZATION.md`
6. Every other file in `docs/`
7. Every file in `.agents/rules/`
8. Every file in `.agents/skills/` relevant to the phase about to be implemented
9. `IMPLEMENTATION_PLAN.md` for the current phase's scope and exit criteria

## Source of Truth Priority (repeated from the master command, binding)
1. Problem Statement (this repo's stated goal: predictive delay + MILP gate optimizer)
2. `REQUIREMENTS.md`
3. `ACCEPTANCE_CRITERIA.md`
4. `docs/ARCHITECTURE.md`
5. Domain-specific docs (`docs/ML.md`, `docs/OPTIMIZATION.md`, `docs/GATE_SYSTEM.md`, etc.)
6. This file (`AGENTS.md`)
7. `.agents/rules/` and `.agents/skills/`
8. Your own implementation assumptions — lowest priority, must be logged in `docs/DECISION_LOG.md` if used

If two higher-priority documents conflict, STOP and report the conflict — do not resolve it yourself by guessing. (In this package, `docs/DECISION_LOG.md` D-series entries already resolve every contradiction found during authoring; if you find a NEW one, add a new decision entry and flag it to the human operator before proceeding.)

## Phase Gating (binding — see `.agents/rules/phase-gating.md`)
Implement exactly one phase from `IMPLEMENTATION_PLAN.md` at a time. After each phase, run the verification protocol in that rule file and confirm every AC item for that phase in `ACCEPTANCE_CRITERIA.md`. Do not start the next phase until the current one's ACs are demonstrated, not assumed.

## Non-Negotiable Rules (full detail in `.agents/rules/non-fabrication.md` and `NON_FABRICATION.md`)
- Never fabricate metrics, solver results, test results, or deployment status.
- Never replace the MILP with the baseline algorithm in production code paths.
- Never skip the independent optimization validator.
- Never leave `TODO`/`FIXME`/`pass`/`NotImplementedError` in a production code path.
- Backend is the sole source of truth; the frontend never re-implements business logic.

## Environment Reality
This build environment may lack a Docker daemon, a running Postgres, a Gurobi license, or GPU. This does NOT change the target architecture. Where a dependency is unavailable, the code must detect that and behave per the documented fallback (see `docs/OPTIMIZATION.md` for the Gurobi→OR-Tools fallback, `docs/DEPLOYMENT.md` for infra). Document what you could verify locally vs. what requires a fuller environment, in your phase reports — do not claim verification you could not actually perform.

## What "Done" Means
A phase is done only when: code exists, tests exist and pass, the relevant service was actually started and observed working (logs/console/curl), and the matching `ACCEPTANCE_CRITERIA.md` items are checked off with evidence quoted in your phase report.
