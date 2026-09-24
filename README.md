# AeroOptima: Predictive Air Traffic Delay & Airport Gate Scheduling Optimizer

A production-grade, full-stack decision-support system integrating **Machine Learning Delay Prediction** with **Mixed Integer Linear Programming (MILP) Airport Gate Optimization**.

---

## 🛫 System Overview

Airport operations frequently suffer from flight cascading bottlenecks due to unpredictable runway delays and rigid gate assignments. **AeroOptima** addresses this with a two-phase architecture:
1. **Predictive AI Engine**: Trains tree-based gradient boosted regressors on historical flight telemetry, airport congestion indices, and meteorological conditions to predict incoming taxi/runway delay in minutes without lookahead data leakage.
2. **Operations Research (MILP) Engine**: Employs Google OR-Tools (CBC/SCIP) and Gurobi solvers to assign flights to compatible airport gates, minimizing passenger walking distance, delay propagation, and gate reassignments while eliminating simultaneous gate overlaps.

---

## 🏗️ High-Level Architecture

```text
                        ┌─────────────────────────┐
                        │      React 18 + Vite     │
                        │    Glassmorphism UI     │
                        └────────────┬────────────┘
                                     │
                                     │ REST API / JSON
                                     ▼
                        ┌─────────────────────────┐
                        │       FastAPI API       │
                        │   Request Validation    │
                        │   Pydantic Schemas      │
                        └────────────┬────────────┘
                                     │
                ┌────────────────────┼────────────────────┐
                │                    │                    │
                ▼                    ▼                    ▼
       ┌────────────────┐   ┌────────────────┐   ┌────────────────┐
       │ Prediction     │   │ Optimization   │   │ Flight / Gate  │
       │ Service        │   │ Service        │   │ Service        │
       └───────┬────────┘   └───────┬────────┘   └───────┬────────┘
               │                    │                    │
               ▼                    ▼                    ▼
       ┌───────────────┐    ┌───────────────┐    ┌───────────────┐
       │ Scikit-Learn  │    │ Google OR-Tools│   │ SQLite /      │
       │ ML Regressor  │    │ / Gurobi MILP │    │ PostgreSQL    │
       └───────────────┘    └───────────────┘    └───────────────┘
```

---

## 🛠️ Technology Stack

| Layer | Technologies |
| :--- | :--- |
| **Backend API** | Python 3.11+, FastAPI, Pydantic v2, SQLAlchemy 2.0, Uvicorn |
| **Machine Learning** | Scikit-Learn (`GradientBoostingRegressor`, `RandomForestRegressor`, `ColumnTransformer`), Joblib, NumPy, Pandas |
| **Optimization Engine** | Google OR-Tools (`pywraplp` SCIP/CBC), Gurobi integration (`gurobipy` with auto fallback) |
| **Frontend UI** | React 18, Vite, React Router v6, Axios, Recharts, Lucide Icons, Custom Design System |
| **Database** | SQLite (development/demo), PostgreSQL ready |
| **DevOps & Containers**| Docker, Docker Compose, Nginx |
| **Testing** | Pytest, Pytest-Asyncio, HTTPX TestClient |

---

## 🚀 Quick Start Guide

### Prerequisites
* Python 3.11+
* Node.js 18+ and npm
* (Optional) Docker & Docker Compose

---

### Step 1: Clone and Set Up Backend

```bash
cd backend

# Create and activate virtual environment
python -m venv .venv

# Windows:
.venv\Scripts\activate
# Linux/macOS:
# source .venv/bin/activate

# Install dependencies
pip install -r requirements.txt
```

### Step 2: Train Machine Learning Delay Model
Executes chronological 70/15/15 validation, trains multi-model tournament (Linear Regression, Random Forest, Gradient Boosting), and saves the champion model:

```bash
python -m app.ml.train
```

### Step 3: Seed Database
Seeds 12 realistic airport gates, 30 scheduled flights across Terminals 1, 2, and 3, runs batch ML inference, and generates baseline gate assignments:

```bash
python -m app.database.seed
```

### Step 4: Run Backend Server
```bash
uvicorn app.main:app --reload --port 8000
```
* **Swagger API Docs**: `http://localhost:8000/docs`
* **Health Check**: `http://localhost:8000/api/health`

---

### Step 5: Start Frontend Application

In a separate terminal:

```bash
cd frontend
npm install
npm run dev
```
Open **`http://localhost:5173`** in your browser.

---

## 🐳 Running with Docker Compose

```bash
docker compose up --build
```
* Frontend: `http://localhost:5173`
* Backend API: `http://localhost:8000`
* Swagger UI: `http://localhost:8000/docs`

---

## 🧪 Running Automated Tests

```bash
cd backend
python -m pytest ../tests -v
```
Runs:
- **ML pipeline tests**: Feature extraction, no-leakage verification, inference, metrics calculation.
- **MILP Optimization tests**: 2-flight deterministic feasible case, single-gate overlapping capacity case, aircraft type incompatibilities, validator logic.
- **Backend API integration tests**: Health, flights pagination, single prediction, batch prediction, MILP solver execution, dashboard aggregation.

---

## 📐 Mixed Integer Linear Programming (MILP) Formulation

### Sets
* $\mathcal{F}$: Set of flights to schedule.
* $\mathcal{G}$: Set of available airport gates.
* $\mathcal{C}$: Set of overlapping flight pairs $(f_1, f_2)$ considering predicted delay and operational buffer.
* $\mathcal{K}_f$: Set of compatible gates for flight $f$ (matching terminal and aircraft type).

### Decision Variable
$$x_{f,g} \in \{0, 1\} \quad \text{where } x_{f,g} = 1 \text{ if flight } f \text{ is assigned to gate } g$$

### Objective Function
$$\min \sum_{f \in \mathcal{F}} \sum_{g \in \mathcal{K}_f} \left[ w_2 \cdot \text{WalkScore}(g) + w_3 \cdot \left(\frac{\delta_f}{10}\right) + w_4 \cdot \text{Reassign}(f,g) \right] x_{f,g} + \sum_{f \in \mathcal{F}} (2 w_1) \cdot u_f$$

### Constraints
1. **Assignment Constraint**: $\sum_{g \in \mathcal{K}_f} x_{f,g} + u_f = 1, \quad \forall f \in \mathcal{F}$
2. **Compatibility Constraint**: $x_{f,g} = 0, \quad \forall g \notin \mathcal{K}_f$
3. **Non-Overlap Constraint**: $x_{f_1,g} + x_{f_2,g} \le 1, \quad \forall (f_1, f_2) \in \mathcal{C}, \; \forall g \in \mathcal{K}_{f_1} \cap \mathcal{K}_{f_2}$
4. **Turnaround & Delay Dynamics**: Effective occupancy $= [t^{arr}_f + \max(0, \delta_f), \max(t^{dep}_f, t^{arr}_f + \delta_f + \text{Turnaround}_f)]$

---

## 🖥️ Application Modules

1. **Operations Dashboard (`/`)**: Real-time KPIs, delay category breakdown, hourly congestion trends, airline performance, and interactive Gantt-style gate timeline.
2. **Flight Management (`/flights`)**: Search, filter by airline/terminal/delay tier, pagination, flight inspection modal, and CSV batch ingestion.
3. **ML Delay Predictor (`/predictions`)**: Interactive single-flight inference, fleet-wide batch prediction, and feature importance analysis.
4. **MILP Gate Optimizer (`/optimization`)**: Configurable penalty weights ($w_1 \dots w_5$), solver engine selection (OR-Tools / Gurobi), execution timer, and CSV assignment export.
5. **Analytics & Models (`/analytics`)**: Multi-model tournament benchmarks (MAE, RMSE, $R^2$), weather-to-delay correlation, and mathematical formulations.

---

## 📜 License
MIT License. Created for portfolio and academic decision-support demonstration.
