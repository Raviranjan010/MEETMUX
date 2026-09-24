# Skill: gate-conflict-detection

**Purpose:** Detect time-interval conflicts between flights sharing a gate.
**When to use:** Phase 7, and every call site listed in docs/CONFLICT_ENGINE.md (MILP constraint building, live analytics, alerts).
**Inputs:** Set of gate assignments with arrival/departure times + turnaround_buffer_minutes config.
**Outputs:** List of conflicts: {gate_id, conflicting_flight_ids, conflict_type, overlap_minutes}.
**Files involved:** backend/app/services/conflict.py; tests/services/test_conflict.py
**Validation requirements:** All 6 required test cases in docs/CONFLICT_ENGINE.md pass.
**Failure handling:** If interval data is missing/null for a flight, exclude it from conflict checks and log a warning — do not crash the whole detection pass.
**Prohibited shortcuts:** Never reimplement this logic separately inside the MILP module — it must call this shared function.
