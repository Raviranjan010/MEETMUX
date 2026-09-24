# Rule: Optimization
- Implement the exact MILP formulation in docs/OPTIMIZATION.md — decision variables, hard constraints, objective terms, weights.
- Gurobi first, OR-Tools fallback, `SOLVER_UNAVAILABLE` if neither works — always report which one actually ran.
- The Independent Validator (Phase 10) is a separate, from-scratch re-check of every hard constraint — it must not import or call the solver's own feasibility claim as its check.
- Never substitute the baseline algorithm for the MILP in a production code path, even temporarily "to unblock the UI."
- Never fabricate `objective_value`, `solve_time_ms`, or `solver_status` — these come only from the solver library's actual return values.
