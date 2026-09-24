# Rule: Phase Gating
- Implement exactly one phase from IMPLEMENTATION_PLAN.md at a time, in order (0→25), unless the human operator explicitly approves a different order.
- After finishing a phase: run its tests, start the relevant service, verify via curl/browser/logs, check off its ACCEPTANCE_CRITERIA.md items with evidence, commit, then STOP and report before continuing.
- Do not begin a later phase's code (e.g. frontend pages that assume an optimizer endpoint) before the phase that provides its dependency is verified complete.
- If a phase's acceptance criteria cannot be met, report exactly what's missing under "Requirements Not Completed" rather than proceeding past it.
