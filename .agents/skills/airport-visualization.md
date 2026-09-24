# Skill: airport-visualization

**Purpose:** Build the interactive SVG airport map.
**When to use:** Phase 18.
**Inputs:** Live runway/gate/flight state from the backend.
**Outputs:** An SVG-rendered map with click/hover interactions and conflict highlighting, per docs/UI_DESIGN.md.
**Files involved:** frontend/src/components/AirportMap.tsx
**Validation requirements:** Map re-renders correctly after a state change (e.g. post-optimization) without a manual refresh.
**Failure handling:** If backend data is incomplete (e.g. a gate with no terminal), render it in a clearly marked 'unknown' state rather than omitting it silently.
**Prohibited shortcuts:** Never hardcode gate/runway positions or colors that ignore the actual status field.
