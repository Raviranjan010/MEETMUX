# Rule: Testing
- Every phase ships with its own tests before being marked complete — see docs/TESTING.md for required coverage and edge cases.
- Tests must actually be executed (`pytest`, `vitest run`) with output captured in the phase report — code review alone never substitutes for a run.
- New edge cases discovered during implementation get added to docs/TESTING.md, not just fixed silently.
