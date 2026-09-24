# UI_DESIGN.md

## Design language: Airport Operations Command Center
NOT a generic AI SaaS dashboard. No blue/purple gradients, no glassmorphism, no cyberpunk/neon, no robot imagery.

## Palette (exact hex, from REQUIREMENTS)
Background `#07100E` · Surface `#0E1916` · Amber (attention/medium risk) `#F5A623` · Green (nominal/optimal) `#39C878` · Red (critical/high risk/infeasible) `#EF5350` · Warm white (primary text) `#F4F1E8` · Muted (secondary text/borders) `#87938D`.

## Typography & feel
Monospace or semi-condensed sans for data-dense panels (flight lists, IDs, timestamps) evoking radar/ops-room readouts; regular sans for prose (explain panel, alerts). Sharp corners or minimal radius (2–4px), thin 1px borders in Muted, no heavy drop shadows — flat, high-contrast, information-dense.

## Airport SVG Map (`/airport`, Phase 18)
Rendered as inline SVG (not a canvas game engine) driven by live backend state: runways as long rectangles (color = ACTIVE green / CLOSED red), taxiway lines connecting terminals to runways, terminal shapes with gates as small numbered rectangles colored by state (AVAILABLE green outline, OCCUPIED amber fill, BLOCKED red fill, CONFLICT red pulsing outline), aircraft as small icons at occupied gates. Interactions: click a gate → side panel with gate detail + explain link; click a flight/aircraft icon → flight detail; hover → tooltip; conflicts visually highlighted (red outline + connecting line between the conflicting flights' gates).

## Gate Timeline / Gantt (`/timeline`, Phase 19)
Rows = gates, columns = time. Each flight's occupied interval (arrival−buffer to departure+buffer) drawn as a bar; conflicts shown as overlapping bars with a red hatch pattern; reassignments (post-optimization) shown as a dashed "ghost" bar at the old position with an arrow to the new one.

## Explainability panel
Renders the `reasons[]` list from EXPLAINABILITY.md as a checklist with icons (lucide-react), plus a small "alternatives considered" comparison table.

## Before/After comparison panel
Two-column layout (Baseline | Optimized) with the metrics from ANALYTICS.md, deltas shown with up/down indicators colored green (improvement) or red (regression) — never assumed to always be green.
