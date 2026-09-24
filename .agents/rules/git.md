# Rule: Git
- One phase = one or more small, reviewable commits referencing the phase number in the message (e.g. `[P7] gate conflict interval detection + tests`).
- Never squash the entire 25-phase build into one commit.
- Commit messages state what was added and what was verified (e.g. "tests: 12 passed").
- Do not commit `.env`, model artifacts larger than necessary for the demo, or generated `node_modules`/`__pycache__`.
