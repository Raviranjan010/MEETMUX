# PROJECT_RULES.md — RunwayOptX

Binding rules for all contributors (human or agent). Detailed per-domain versions live in `.agents/rules/`; this file is the short index + the rules that don't fit a single domain.

1. **One phase at a time.** No skipping ahead, no building Phase 17 UI against Phase 9 stubs.
2. **Backend owns state.** Any number, status, or assignment shown in the UI must come from a backend response in this request/session — no client-side recomputation of business logic (formatting/derived display strings are fine).
3. **No fabrication, ever** — see `NON_FABRICATION.md`. This overrides "make the demo look good."
4. **Solver honesty.** The UI must always be able to answer "which solver actually produced this, and what did it report?" truthfully.
5. **Configuration over hardcoding.** Every threshold/weight in `REQUIREMENTS.md` §R9 must be read from `system_config`, never inlined as a magic number in optimizer or risk-classification code.
6. **Tests are part of the feature.** A phase without passing tests is not complete, regardless of how the UI looks.
7. **Errors are visible, not swallowed.** Every failure mode in `docs/TESTING.md`'s edge-case list must produce a clear, typed error — never a silent fallback or a blank screen.
8. **Synthetic data is labeled.** Any demo/synthetic record carries `is_synthetic: true` in its API representation and the UI shows a "Demo Data" badge where such data is displayed.
9. **Git hygiene** — see `.agents/rules/git.md`: one phase = one or more small commits, never one giant commit for the whole system.
10. **Documentation is a deliverable.** If implementation diverges from a doc, update the doc in the same PR/commit, and log the change in `docs/DECISION_LOG.md` if it affects an architectural decision.
