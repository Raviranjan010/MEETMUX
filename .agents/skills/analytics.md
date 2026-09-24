# Skill: analytics

**Purpose:** Compute live analytics and baseline-vs-optimized comparisons.
**When to use:** Phase 11 (backend) and Phase 20 (UI).
**Inputs:** Committed state (live analytics) or two stored assignment sets (comparison).
**Outputs:** Analytics payload per docs/ANALYTICS.md, computed at request time.
**Files involved:** backend/app/services/analytics.py; tests/services/test_analytics.py
**Validation requirements:** Deltas recomputed live match a manual recomputation from the same two datasets in a test.
**Failure handling:** Missing data (e.g. no baseline run yet) → documented empty/ fields, not a crash or a fabricated placeholder number.
**Prohibited shortcuts:** Never cache a computed improvement percentage as a constant anywhere in code or config.
