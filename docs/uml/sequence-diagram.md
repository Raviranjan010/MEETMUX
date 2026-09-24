# UML Sequence Diagram

```mermaid
sequenceDiagram
    autonumber
    actor User as Airport Dispatcher
    participant UI as React Frontend
    participant API as FastAPI Router
    participant ML as PredictionService
    participant Reg as ModelRegistry (In-Memory)
    participant Opt as OptimizationService
    participant Solver as ORTools / Gurobi Solver
    participant DB as SQLite / PostgreSQL

    User->>UI: Trigger "Run Optimization"
    UI->>API: POST /api/optimization/run (weights, solver)
    API->>Opt: run_optimization(request)
    Opt->>DB: Query scheduled flights & available gates
    DB-->>Opt: Flight & Gate entities
    Opt->>ML: Query latest delay predictions
    ML->>Reg: predict(features)
    Reg-->>ML: Expected taxi delay minutes
    ML-->>Opt: Enriched delay vectors
    Opt->>Solver: solve(MILP Model Formulation)
    Note over Solver: Minimizes walking distance & delay propagation
    Solver-->>Opt: Optimal Binary Assignment Matrix x[f,g]
    Opt->>Opt: Validate zero overlap & compatibility
    Opt->>DB: Persist OptimizationRun & GateAssignments
    DB-->>Opt: Persisted record ID
    Opt-->>API: OptimizationResponse (KPIs + Assignments)
    API-->>UI: JSON Response
    UI-->>User: Render Gantt Timeline & Assignment Table
```
