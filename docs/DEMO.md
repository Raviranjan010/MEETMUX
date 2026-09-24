# DEMO.md

Deterministic 3–5 minute walkthrough (matches ACCEPTANCE_CRITERIA.md §AC-FINAL, this is the presentation script version):
1. Show `/dashboard` with the seeded 100 flights / 30 gates / 2 runways loaded (point out the "Demo Data" badge — `is_synthetic=true`).
2. `/predictions` — run batch prediction, show real MAE/RMSE/R² from the trained model card.
3. `/flights` — filter to HIGH risk, open one flight's detail, show its risk badge derived from config thresholds.
4. `/airport` — point out a conflict highlighted on the SVG map.
5. `/cascade` — show the propagation path for that conflict.
6. `/optimizer` — run MILP, show solver-used pill (Gurobi or OR-Tools, whichever actually ran), objective value, solve time, validator PASS.
7. `/analytics` — show baseline vs optimized comparison, real deltas.
8. `/flights/:id` → Explain panel for one reassigned flight.
9. `/scenarios` — trigger Runway Closure on RWY-2.
10. `/reoptimize` (via `/optimizer` or `/scenarios` action) — show new run, new solver status.
11. `/airport`, `/timeline`, `/analytics`, `/alerts` — show all four reflect the new state without a page reload trick.

Script explicitly narrates when OR-Tools is used instead of Gurobi (if no license in the demo environment) rather than hiding it.
