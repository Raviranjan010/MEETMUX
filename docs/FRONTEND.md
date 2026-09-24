# FRONTEND.md

## Routes (all required, React Router)
`/dashboard` (overview: risk distribution, active alerts, quick links) · `/flights` (paginated/filterable list) · `/flights/:id` (detail: prediction, current assignment, explain link) · `/gates` (grid/list with state) · `/airport` (interactive SVG map, see UI_DESIGN.md) · `/predictions` (batch prediction runner + results table) · `/optimizer` (run controls, solver status, objective breakdown) · `/scenarios` (scenario runner, one card per type from SIMULATION.md) · `/cascade` (cascade visualization for a selected scenario/event) · `/timeline` (Gantt, see UI_DESIGN.md) · `/analytics` (before/after comparison, live analytics) · `/alerts` (active/resolved alert list) · `/settings` (system_config editor — read/update the values in REQUIREMENTS.md §R9).

## Page states (every route)
Loading (skeleton, not spinner-only-for->2s), Success, Empty (e.g. no flights uploaded yet — with a call-to-action to load demo data), Error (shared error component, shows `error.message` from the API's error shape, plus Retry), and for long-running ops (optimizer run) a Running/Polling state distinct from Loading.

## API client
`frontend/src/api/client.ts` — one axios instance, base URL from `VITE_API_BASE_URL`. One typed function per endpoint in API.md, e.g. `getFlights(params)`, `runOptimizer(body)`, `pollOptimizationRun(id)`. No business logic in these files beyond request/response shaping.

## State
Minimal global state (React context or lightweight store) for: selected flight/gate (map/timeline interaction), active optimization_run_id being polled, active scenario. Everything else is fetched per-page via React Query or equivalent fetch/caching pattern — server is the source of truth, client caches for UX only and revalidates after any mutating action.
