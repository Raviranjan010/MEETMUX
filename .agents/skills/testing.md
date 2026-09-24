# Skill: testing

**Purpose:** Write and execute the test suites required by docs/TESTING.md.
**When to use:** Every phase; also as its own dedicated pass in Phase 21.
**Inputs:** The code produced by the phase in question, plus the required edge-case list.
**Outputs:** Passing pytest/vitest runs with captured output for the phase report.
**Files involved:** backend/tests/**, frontend/src/**/*.test.tsx
**Validation requirements:** Actual exit code 0 from the test runner, not a code-review approximation.
**Failure handling:** A failing test blocks phase completion; report it under 'Requirements Not Completed', don't silently skip/xfail it to make the suite green.
**Prohibited shortcuts:** Never delete or weaken a test to make it pass; fix the underlying code or, if the requirement itself was wrong, update REQUIREMENTS.md via a DECISION_LOG entry first.
