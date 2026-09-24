# Skill: cascade-analysis

**Purpose:** Trace downstream propagation of a delay/closure/conflict through the real flight/gate/runway dependency graph.
**When to use:** Phase 13, and re-run as part of reoptimization (Phase 14).
**Inputs:** Root event (flight/gate/runway), current assignment state, cascade_max_depth config.
**Outputs:** cascade_events row with propagation_path (real IDs) and affected_flight_ids.
**Files involved:** backend/app/services/cascade.py; tests/services/test_cascade.py
**Validation requirements:** Every ID in propagation_path corresponds to a real row; depth never exceeds cascade_max_depth.
**Failure handling:** If no downstream effects are found, return an empty/low-severity result — never invent an effect to make the output look non-trivial.
**Prohibited shortcuts:** Never write a templated causal sentence not backed by an actual graph edge traversed in this run.
