# Rule: Architecture
- Modular monolith only (see docs/ARCHITECTURE.md). No new services, brokers, or caches without a DECISION_LOG entry approved by the human operator.
- One business-logic implementation per concern (conflict detection, risk classification, etc.) — never duplicate logic between backend modules or between backend and frontend.
- Every new module must map to an existing phase in IMPLEMENTATION_PLAN.md; if it doesn't, stop and ask rather than inventing scope.
