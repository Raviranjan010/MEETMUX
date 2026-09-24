# IMPLEMENTATION_PLAN.md — RunwayOptX

25 phases, each phase = scope + exit criteria (pointer into ACCEPTANCE_CRITERIA.md) + required verification. Antigravity implements exactly one phase per work session unless the human operator explicitly approves batching small phases (e.g., P4+P5).

## §1 Phase List (scope only — full AC in ACCEPTANCE_CRITERIA.md)
| Phase | Name | Primary docs |
|---|---|---|
| 0 | Specification Audit | this file, REQUIREMENTS.md |
| 1 | Foundation (repo, Docker, health) | docs/ARCHITECTURE.md, docs/DOCKER.md |
| 2 | Database | docs/DATABASE.md |
| 3 | Data Pipeline | docs/DATABASE.md, docs/DATA_DICTIONARY.md |
| 4 | ML | docs/ML.md |
| 5 | Risk Engine | docs/ML.md §Risk |
| 6 | Gate System | docs/GATE_SYSTEM.md |
| 7 | Conflict Engine | docs/CONFLICT_ENGINE.md |
| 8 | Baseline | REQUIREMENTS.md §R8 |
| 9 | MILP Optimization | docs/OPTIMIZATION.md |
| 10 | Independent Validator | docs/OPTIMIZATION.md §6 |
| 11 | Before/After Analytics | docs/ANALYTICS.md |
| 12 | Simulation | docs/SIMULATION.md |
| 13 | Cascade Engine | docs/CASCADE_ENGINE.md |
| 14 | Re-optimization | docs/REOPTIMIZATION.md |
| 15 | FastAPI (complete) | docs/API.md |
| 16 | Frontend Foundation | docs/FRONTEND.md |
| 17 | Command Center pages | docs/FRONTEND.md, docs/UI_DESIGN.md |
| 18 | Airport Visualization (SVG) | docs/UI_DESIGN.md §SVG Map |
| 19 | Gate Timeline (Gantt) | docs/UI_DESIGN.md §Timeline |
| 20 | Analytics/Alerts/Explainability UI | docs/ANALYTICS.md, docs/ALERTS.md, docs/EXPLAINABILITY.md |
| 21 | Testing | docs/TESTING.md |
| 22 | Docker | docs/DOCKER.md |
| 23 | CI/CD | docs/CICD.md |
| 24 | Deployment | docs/DEPLOYMENT.md |
| 25 | Final System Test | ACCEPTANCE_CRITERIA.md §AC-FINAL |

## §2 Phase 0 Deliverable (Antigravity must produce this before any code)
1. Architecture summary (confirm/restate docs/ARCHITECTURE.md in its own words)
2. Module dependency graph
3. Requirements traceability matrix (§9 below, filled in / confirmed)
4. Database, ML, optimization, API, frontend dependency analyses
5. Deployment architecture
6. Any NEW contradictions found (existing ones are pre-resolved in docs/DECISION_LOG.md)
7. Technical risks
8. Missing information — if genuinely blocking, list it and stop; otherwise proceed with the documented default and note the assumption

## §3–§8 Per-Phase Exit Protocol (applies to every phase 1–25)
1. Implement only what's in scope for this phase.
2. Write/execute tests for this phase's code.
3. Start the relevant service(s) locally.
4. Hit the relevant endpoint(s) / render the relevant page(s).
5. Inspect logs, browser console, and network tab as applicable.
6. Fix anything broken; re-verify.
7. Check off the phase's items in ACCEPTANCE_CRITERIA.md with the actual evidence (paste command + output) in the phase report.
8. Commit with a message referencing the phase number.
9. STOP and report before starting the next phase.

## §9 Requirements Traceability Matrix (initial — extend as needed, never delete rows)
| Req ID | Requirement | Phase | File/Module | Test | AC ID |
|---|---|---|---|---|---|
| FR-1 | Ingest/validate/clean | 3 | `backend/app/pipeline/` | `tests/pipeline/test_validation.py` | AC-P3 |
| FR-2 | Feature engineering | 4 | `backend/app/ml/features.py` | `tests/ml/test_features.py` | AC-P4 |
| FR-3 | Predict taxi delay | 4 | `backend/app/ml/model.py`, `POST /api/predictions` | `tests/ml/test_inference.py` | AC-P4 |
| FR-4 | Risk classification | 5 | `backend/app/services/risk.py` | `tests/services/test_risk.py` | AC-P5 |
| FR-5 | Gate model | 6 | `backend/app/models/gate.py` | `tests/models/test_gate.py` | AC-P6 |
| FR-6 | Conflict detection | 7 | `backend/app/services/conflict.py` | `tests/services/test_conflict.py` | AC-P7 |
| FR-7 | Baseline assignment | 8 | `backend/app/services/baseline.py` | `tests/services/test_baseline.py` | AC-P8 |
| FR-8 | MILP optimization | 9 | `backend/app/optimizer/milp.py` | `tests/optimizer/test_milp.py` | AC-P9 |
| FR-9 | Independent validation | 10 | `backend/app/optimizer/validator.py` | `tests/optimizer/test_validator.py` | AC-P10 |
| FR-10 | Baseline/optimized comparison | 11 | `backend/app/services/analytics.py` | `tests/services/test_analytics.py` | AC-P11 |
| FR-11 | Scenario simulation | 12 | `backend/app/services/simulation.py` | `tests/services/test_simulation.py` | AC-P12 |
| FR-12 | Re-run pipeline post-scenario | 14 | `backend/app/services/reoptimize.py` | `tests/services/test_reoptimize.py` | AC-P14 |
| FR-13 | Cascade detection | 13 | `backend/app/services/cascade.py` | `tests/services/test_cascade.py` | AC-P13 |
| FR-14 | Explainability | 20 | `backend/app/services/explain.py`, frontend panel | `tests/services/test_explain.py` | AC-P20 |
| FR-15 | Alerts | 20 | `backend/app/services/alerts.py` | `tests/services/test_alerts.py` | AC-P20 |
| FR-16 | Audit trail | 9–14 (write), 20 (view) | `backend/app/models/audit.py` | `tests/models/test_audit.py` | AC-P9–P14 |
| FR-17 | Command-center UI | 16–20 | `frontend/src/pages/*` | `frontend/src/**/*.test.tsx` | AC-P17–P20 |
| FR-18 | Accept/Reject/Alternatives/Re-optimize actions | 20 | `backend/app/api/routes/assignments.py` | `tests/api/test_assignments.py` | AC-P20 |

## §10 Final Report Template (use verbatim structure at the end of Phase 25)
`## Implementation Summary`, `## Files Created`, `## Files Modified`, `## Requirements Completed`, `## Requirements Not Completed`, `## Tests Executed`, `## Test Results`, `## Browser Verification`, `## API Verification`, `## Database Verification`, `## ML Verification`, `## Optimization Verification`, `## Solver Used`, `## Optimization Objective`, `## Constraint Validation`, `## Docker Verification`, `## Deployment Verification`, `## Known Risks`, `## Remaining Issues`.
