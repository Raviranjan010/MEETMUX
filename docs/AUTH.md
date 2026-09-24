# AUTH.md — Single-Operator Authentication

## Overview
A minimal, secure single-operator authentication system for RunwayOptX.
It ensures that the application cannot be accessed or manipulated by unauthenticated users who happen to know the URL, while avoiding the overhead of full multi-tenant RBAC, registration, or password reset flows (per DECISION_LOG D-016).

## Credentials
Configured via environment variables (with sensible local development defaults in `.env.example`):
- `OPERATOR_USERNAME`: default `operator`
- `OPERATOR_PASSWORD`: default `runwayoptx2026`
- `JWT_SECRET_KEY`: secret used to sign HS256 tokens (min 32 chars)
- `JWT_ACCESS_TOKEN_EXPIRE_MINUTES`: default `480` (8 hours)

## Backend Mechanics
- Token format: JWT signed with HS256 containing `{"sub": username, "exp": expiration_time}`.
- Unprotected routes:
  - `GET /api/health`
  - `POST /api/auth/login`
- Protected routes:
  All other endpoints under `/api/*` require an `Authorization: Bearer <token>` header. Missing or invalid token returns `401 Unauthorized` with the uniform error structure:
  ```json
  {
    "error": {
      "code": "UNAUTHORIZED",
      "message": "Invalid or expired authentication credentials",
      "details": {},
      "request_id": "<uuid>"
    }
  }
  ```
- Endpoint:
  - `POST /api/auth/login`
    - Request: `{"username": "...", "password": "..."}`
    - Success (200): `{"access_token": "...", "token_type": "bearer", "username": "operator"}`
    - Failure (401): `{"error": {"code": "INVALID_CREDENTIALS", "message": "Invalid username or password", ...}}`

## Frontend Mechanics
- Storage: JWT stored in `localStorage` or `sessionStorage` (key `runwayoptx_token`).
- Axios interceptor: automatically attaches `Authorization: Bearer <token>` to all outgoing API requests. Intercepts `401` errors and redirects to `/login`.
- Routes:
  - `/login`: Clean, command-center styled login form. Only shown when unauthenticated.
  - Route Guard (`ProtectedRoute`): Wraps all main routes (`/dashboard`, `/flights`, `/gates`, etc.). If no valid token exists, immediately redirects to `/login`.
  - Logout action in persistent sidebar/nav clears token and navigates to `/login`.
