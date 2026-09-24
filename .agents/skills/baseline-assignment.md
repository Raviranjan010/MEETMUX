# Skill: baseline-assignment

**Purpose:** Produce the deterministic first-fit baseline gate assignment.
**When to use:** Phase 8, and as the reassignment-penalty reference (baseline_gate) in every MILP run.
**Inputs:** Flights ordered by scheduled_arrival; gates with compatibility/eligibility/status.
**Outputs:** gate_assignments rows with assignment_status=BASELINE, plus unassigned flights flagged.
**Files involved:** backend/app/services/baseline.py; tests/services/test_baseline.py
**Validation requirements:** Re-running on identical input produces an identical output (determinism test).
**Failure handling:** A flight with no compatible gate is left UNASSIGNED and reported, not force-assigned to an incompatible gate.
**Prohibited shortcuts:** Never use this algorithm as the production optimizer; it is a comparison baseline only.
