# DECISION_LOG.md

Each entry: ID, decision, alternatives considered, rationale, consequences, status.

## D-001 — Modular monolith over microservices
**Decision:** Single FastAPI backend, modular by domain; single React SPA; single Postgres DB. **Alternatives:** microservices per domain, Kafka event bus. **Rationale:** 100/30/2 scale doesn't need distributed infra; monolith is faster to build/verify/debug in a phase-gated hackathon workflow and matches "avoid unnecessary microservices/Kafka" in REQUIREMENTS. **Consequences:** simpler ops, single point of scaling if this ever grows past hackathon scope (acceptable tradeoff). **Status:** Accepted.

## D-002 — Background tasks instead of Celery/Redis for async optimizer runs
**Decision:** FastAPI `BackgroundTasks` + polling `GET /api/optimizer/{id}`. **Alternatives:** Celery+Redis job queue. **Rationale:** single-operator, single-active-run assumption (enforced via 409 on concurrent run) makes a full job queue unnecessary overhead; avoids the "no unnecessary Redis" constraint. **Consequences:** would need revisiting for multi-user concurrent use; out of scope per REQUIREMENTS R4. **Status:** Accepted.

## D-003 — Gurobi requirement vs. no license in the dev/hackathon environment
**Problem:** Spec requires Gurobi as primary solver; the actual build/demo environment may have no Gurobi license. **Resolution:** OR-Tools CP-SAT is a first-class, fully-specified fallback (OPTIMIZATION.md), not an afterthought. The system always reports `solver_used` truthfully. The architecture is not weakened — Gurobi integration code is written and tested via mocking/import-guard even if never run against a real license locally; a real license, if obtained for the demo, simply activates the primary path. **Status:** Accepted.

## D-004 — Baseline definition
**Problem:** Spec says "first compatible available gate" but doesn't define tie-breaking or ordering. **Resolution:** REQUIREMENTS R8 fixes the exact algorithm: ascending scheduled_arrival processing order, ascending gate_id tie-break, single-pass greedy, unassigned-if-none-fit. **Status:** Accepted.

## D-005 — Objective double counting
**Problem:** Naive combination of "conflict cost" and "no-overlap hard constraint" could double-penalize the same infeasibility. **Resolution:** No-overlap is a hard constraint (OPTIMIZATION.md constraint 5); the objective's conflict-cost term is a slack-only safety net that is 0 under a normal feasible solve, documented explicitly so it isn't mistaken for a second independent penalty. **Status:** Accepted.

## D-006 — Scenario mutation semantics
**Problem:** Ambiguous whether running a scenario should auto-trigger re-optimization. **Resolution:** Split into two explicit calls — `POST /api/scenarios/run` (mutate state only) and `POST /api/reoptimize` (run the full recompute chain) — so each is independently observable/testable and the operator controls when re-optimization happens (human-in-the-loop principle). **Status:** Accepted.

## D-007 — Cascade causality must be graph-derived
**Problem:** Risk of an LLM-style narrative cascade explanation with no real backing. **Resolution:** Cascade engine is a deterministic BFS over a real dependency graph (CASCADE_ENGINE.md); `propagation_path` must reference real IDs; no free-text-only causes allowed. **Status:** Accepted.

## D-008 — Frontend vs backend state ownership
**Problem:** Spec both wants a rich, responsive UI and insists backend is source of truth. **Resolution:** Frontend may cache fetched data client-side for UX (React Query-style revalidation) but performs zero independent business-logic computation (no client-side conflict detection, no client-side optimization, no client-side risk classification). All such logic lives in one backend module each. **Status:** Accepted.

## D-009 — Performance expectations
**Problem:** No SLA was given, and inventing one risks becoming a fabricated promise. **Resolution:** PERFORMANCE.md states target scale and safety nets (timeout, pagination, indexes) but explicitly declines to assert a specific millisecond number until Phase 21 produces a real measurement, which then gets appended here. **Status:** Accepted, open follow-up: record real numbers post-Phase-21.

## D-010 — Deployment requirements vs. environment reality
**Problem:** Build environment may lack Docker/cloud access to actually deploy. **Resolution:** DEPLOYMENT.md is fully specified as a followable runbook; AC-P24 explicitly allows "documented but not executed" as an honest, passing state, distinct from a false claim of a live URL. **Status:** Accepted.

## D-011 — Authentication requirements
**Problem:** Spec doesn't mention auth, but a real ops system implies operator identity. **Resolution:** Single implicit "operator" actor for v1 (REQUIREMENTS R5); `audit_records.actor` defaults to `"operator"`. No login system built for the hackathon; nothing in the architecture blocks adding real auth later. **Status:** Accepted.

## D-012 — Synthetic data vs. real-world claims
**Problem:** Demo needs to look like a real airport ops tool without claiming real operational data. **Resolution:** `is_synthetic` boolean on `flights` (and equivalent flag on scenario-injected data), surfaced as a UI badge; DEMO.md script explicitly narrates this. **Status:** Accepted.

## D-013 — SVG airport map over a mapping library/canvas engine
**Decision:** Hand-built inline SVG driven by backend state, not a game engine or GIS library. **Rationale:** REQUIREMENTS explicitly lists SVG; avoids an unnecessary heavy dependency; easier to make deterministic/testable. **Status:** Accepted.

## D-014 — Configurable objective weights and risk thresholds
**Decision:** All weights/thresholds live in one `system_config` table/row, editable via `/settings` and `/api` (implied config endpoint), never hardcoded. **Rationale:** REQUIREMENTS R9 explicitly demands this; keeps optimizer and risk logic testable/tunable without code changes. **Status:** Accepted.

## D-015 — ML model selection method (recorded here once actually run)
**Decision (pending real run):** Selection is by lowest test-set RMSE among the four candidate regressors (ML.md). Actual metrics and chosen model to be appended to this entry once Phase 4 executes — this entry intentionally has no numbers yet to avoid fabrication. **Status:** Open — update at Phase 4 completion.
