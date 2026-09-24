# NON_FABRICATION.md — RunwayOptX

This is the single most important constraint on this project. A hackathon demo that fakes any of the following is a failed project, not a shortcut.

## Absolutely forbidden, no exceptions
| # | Forbidden | Why it matters here |
|---|---|---|
| 1 | Inventing ML metrics (MAE/RMSE/R²) instead of computing them on a held-out split | The whole pitch is "predictive"; fake metrics make every downstream number meaningless |
| 2 | Returning a fabricated solver status/objective/assignment when Gurobi/OR-Tools didn't actually run | Directly violates the MILP requirement; judges may ask "show me the solver log" |
| 3 | Hardcoding "baseline vs optimized" improvement percentages | The comparison must be computed from two real stored assignment sets |
| 4 | Inventing cascade causes not present in the actual flight/gate dependency graph | Cascade output must be a traceable graph path, not a narrative template |
| 5 | Generating "explanations" not derived from real constraint/objective facts about that specific assignment | Explainability must be inspectable and falsifiable |
| 6 | Claiming Gurobi ran when only OR-Tools ran, or vice versa | Solver identity is a first-class field in every optimization_run row and API response |
| 7 | Claiming tests passed without executing them | Every "STOP after Phase N" checkpoint requires actual run output |
| 8 | Claiming deployment succeeded without a verifiable live check (URL, health endpoint response) | See `docs/DEPLOYMENT.md` — undeployed is an acceptable, honestly-reported state |
| 9 | Marking a feature complete when only a mock/stub exists behind it | Frontend mock data is allowed ONLY in Storybook-style component dev, never wired to a real route in the shipped app |
| 10 | Silently swallowing an exception and returning a "success" response | See `docs/TESTING.md` edge cases — every failure must surface as a typed, visible error |

## Allowed and required
- **Deterministic synthetic demo data** — required for the 100/30/2 dataset. Must be labeled `is_synthetic: true`.
- **Documented fallback behavior** — e.g., OR-Tools running because Gurobi has no license in this environment IS honest, as long as the response says so.
- **"Not yet implemented" as an explicit, visible state** — a route that returns `501 Not Implemented` with a clear message is honest; a route that fakes a 200 with empty/fake data is not.
- **Reporting partial completion** — the final report format in `IMPLEMENTATION_PLAN.md` has a "Requirements Not Completed" section specifically so partial work is never hidden.

## Enforcement mechanism
- Phase 10 (Independent Validator) exists specifically to catch a fabricated/incorrect solver result before it reaches the API or UI layer — see `docs/OPTIMIZATION.md` §6.
- `docs/OBSERVABILITY.md` requires every optimization run, prediction, and scenario execution to be logged with enough detail (model version, solver name, timings) to audit after the fact.
- Code review checklist (see `.agents/rules/non-fabrication.md`) must be applied before any phase is marked STOP-complete.
