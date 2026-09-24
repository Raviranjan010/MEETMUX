# API Documentation

The AeroOptima REST API is hosted on port `8000`. Interactive Swagger UI is available at `http://localhost:8000/docs`.

## Key Endpoints

### 1. Flights
* `GET /api/flights`: Paginated list of flights with filtering by airline, terminal, delay category, and search query.
* `GET /api/flights/{id}`: Detailed flight telemetry.
* `POST /api/flights`: Create a new scheduled flight.
* `POST /api/flights/upload`: Ingest flight batch via CSV upload.

### 2. Predictions
* `POST /api/predictions/predict`: Single flight ML delay prediction.
* `POST /api/predictions/batch`: Batch delay prediction across all or selected flights.
* `GET /api/predictions/feature-importance`: Exposes relative tree feature importances.
* `GET /api/predictions/metrics`: ML model tournament benchmarks (MAE, RMSE, R²).

### 3. Optimization
* `POST /api/optimization/run`: Solves MILP airport gate assignment with configurable objective weights.
* `GET /api/optimization/{run_id}`: Optimization run metadata.
* `GET /api/optimization/{run_id}/assignments`: Flight-to-gate assignment listings.

### 4. Dashboard & Health
* `GET /api/dashboard/summary`: Aggregated operational KPIs, hourly congestion, and timeline data.
* `GET /api/health`: System health and solver availability check.
