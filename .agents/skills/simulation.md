# Skill: simulation

**Purpose:** Apply a named disruption scenario, mutating real backend state.
**When to use:** Phase 12, whenever the operator runs a scenario from /scenarios.
**Inputs:** Scenario type + target_reference + params, per docs/SIMULATION.md table.
**Outputs:** A scenarios row + actual mutated flights/gates/runways rows + state_changes summary.
**Files involved:** backend/app/services/simulation.py; tests/services/test_simulation.py
**Validation requirements:** A subsequent GET on the mutated entity reflects the change (not just the POST response body).
**Failure handling:** Unknown scenario type or invalid target_reference (e.g., nonexistent gate) → 422, not a silent no-op.
**Prohibited shortcuts:** Never simulate a scenario by only changing a number returned to the frontend without touching the database.
