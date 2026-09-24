# Skill: api-development

**Purpose:** Implement/extend FastAPI endpoints per docs/API.md.
**When to use:** Phase 15, and incrementally in earlier phases as each service becomes available.
**Inputs:** docs/API.md contract for the endpoint being built.
**Outputs:** A working route with Pydantic request/response schemas and the uniform error shape.
**Files involved:** backend/app/api/routes/*.py, backend/app/schemas/*.py; tests/api/
**Validation requirements:** At least one success-path and one documented error-path test per endpoint.
**Failure handling:** Uncaught exceptions funnel through core/errors.py into the standard error JSON — never a raw 500 with a Python traceback body.
**Prohibited shortcuts:** Never return a hardcoded/mock response body for an endpoint that's supposed to be wired to a real service.
