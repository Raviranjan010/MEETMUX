# Skill: frontend-development

**Purpose:** Build React pages/components consuming the typed API client.
**When to use:** Phases 16–20.
**Inputs:** docs/FRONTEND.md route list, docs/UI_DESIGN.md palette/design language, backend API contract.
**Outputs:** Rendered pages with Loading/Success/Empty/Error states, wired to real endpoints.
**Files involved:** frontend/src/pages/*, components/*, api/*; *.test.tsx
**Validation requirements:** Each page has a test per state (loading/success/empty/error) where feasible.
**Failure handling:** A failed fetch renders the shared Error component with Retry — never a blank page or unhandled promise rejection.
**Prohibited shortcuts:** Never wire a page to mock/local fixture data in the shipped app; mocks are for isolated component dev only.
