# Skill: optimization-validation

**Purpose:** Independently re-check a solver's output against every hard constraint.
**When to use:** Phase 10, run automatically after every MILP solve before a result can be marked usable.
**Inputs:** The solver's returned x[i,j] assignment plus the same flights/gates/config used to build the model.
**Outputs:** validation_passed boolean + validation_report listing any violated constraint with specific IDs.
**Files involved:** backend/app/optimizer/validator.py; tests/optimizer/test_validator.py
**Validation requirements:** A corrupted/forced-invalid assignment (test fixture) is caught and rejected; every real demo run passes 100%.
**Failure handling:** On a validation failure, the run is retained for debugging but marked not-committable; Accept is disabled in the API/UI for that run.
**Prohibited shortcuts:** Never call this 'redundant because the solver said optimal' and skip it; never let it import solver internals to 'trust' the result instead of independently recomputing.
