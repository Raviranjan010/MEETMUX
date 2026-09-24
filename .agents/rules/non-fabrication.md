# Rule: Non-Fabrication (see NON_FABRICATION.md for full detail)
Before marking any phase STOP-complete, verify:
1. Every metric/result reported in the phase report came from an actual command you ran, quoted verbatim or closely paraphrased with real numbers.
2. No `TODO`/`FIXME`/bare `pass`/`NotImplementedError` remains in the code paths touched this phase.
3. Any claim of "tests pass" is backed by an actual test-run exit code.
4. Any claim about which solver ran is backed by the solver library's own return value, not an assumption.
5. If something couldn't be verified in this environment (e.g., no Docker daemon), the phase report says so explicitly rather than claiming it was verified.
