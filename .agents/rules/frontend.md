# Rule: Frontend
- No business logic (conflict/optimization/risk computation) in React — display and interaction only.
- Every page implements Loading/Success/Empty/Error (and Running/Polling where relevant) per docs/FRONTEND.md.
- Palette and design language from docs/UI_DESIGN.md are mandatory — no generic AI-dashboard styling.
- All data comes from the typed API client in `frontend/src/api/` — no inline fetch calls scattered in components.
