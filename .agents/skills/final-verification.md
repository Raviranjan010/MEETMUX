# Skill: final-verification

**Purpose:** Execute the full AC-FINAL system test end-to-end.
**When to use:** Phase 25, only after all prior phases report complete.
**Inputs:** The fully implemented system (seeded dataset, trained model, working optimizer, full UI).
**Outputs:** A completed final report per IMPLEMENTATION_PLAN.md §10 template, with every section honestly filled.
**Files involved:** N/A (verification activity, not a code module)
**Validation requirements:** Every numbered step in ACCEPTANCE_CRITERIA.md §AC-FINAL executed in order and its actual outcome recorded.
**Failure handling:** Any step that fails is listed under 'Requirements Not Completed' / 'Remaining Issues' — the report is never marked fully complete if a step failed.
**Prohibited shortcuts:** Never mark AC-FINAL passed based on a subset of steps or on code inspection instead of an actual run.
