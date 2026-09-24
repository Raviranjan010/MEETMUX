# Skill: docker

**Purpose:** Containerize and locally orchestrate frontend/backend/postgres.
**When to use:** Phase 22.
**Inputs:** docs/DOCKER.md service definitions.
**Outputs:** A working docker-compose.yml + Dockerfiles bringing up all 3 services with a passing health check.
**Files involved:** docker-compose.yml, backend/Dockerfile, frontend/Dockerfile
**Validation requirements:** "docker compose up --build" succeeds and GET /api/health returns 200 from within the compose network.
**Failure handling:** If the local environment has no Docker daemon, document that verification could not be performed here rather than claiming it was.
**Prohibited shortcuts:** Never mark this phase done from a Dockerfile that has never actually been built.
