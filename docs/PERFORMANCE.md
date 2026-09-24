# PERFORMANCE.md

Target scale: 100 flights, 30 gates, 2 runways — deliberately modest, so no exotic performance work is required, but basics are still non-negotiable:
- Indexes per DATABASE.md on every FK and every column used in a list filter.
- Pagination on all list endpoints (default page_size 25, max 100) — never return unbounded result sets.
- MILP solve wrapped in `optimizer_timeout_seconds` (default 60s) — at this scale (≤100 binary-ish decision groups) both Gurobi and OR-Tools CP-SAT should solve well under this in practice, but the timeout is a hard safety net regardless of expected performance, not a promise of a specific solve time.
- Optimization and re-optimization run via FastAPI `BackgroundTasks` so the HTTP request thread is never blocked for the duration of a solve.
- Frontend: paginate/virtualize the flights list if rendering >50 rows at once; SVG map and Gantt render from already-fetched data, no polling faster than 2s intervals during a RUNNING optimization.
- No specific millisecond SLA is promised in this document — none has been measured yet. Once Phase 21 testing produces real timing numbers, record them in `docs/DECISION_LOG.md`, not as an a priori claim here.
