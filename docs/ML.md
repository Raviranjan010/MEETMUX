# ML.md

## Pipeline
`Raw Data → Validation → Cleaning → Feature Engineering → Train/Test Split → Preprocessing → Model Training → Evaluation → Model Persistence (joblib) → Inference (FastAPI)`.

## Target definition (no leakage)
Target: `actual_taxi_minutes` = `actual_arrival_at_gate − actual_runway_touchdown` (arrivals) or the departure equivalent. Prediction happens **before** actuals exist, i.e. at schedule-publish time or at a triggered re-prediction after a scenario. `predicted_delay_minutes = predicted_taxi_minutes − runway.taxi_base_minutes` (REQUIREMENTS R7).

## Features (available at prediction time only)
| Feature | Available at prediction time? | Notes |
|---|---|---|
| scheduled_arrival hour-of-day, day-of-week | Yes | cyclical encoding |
| route_type (domestic/international) | Yes | |
| aircraft size_class, type_code | Yes | |
| airline | Yes | one-hot or target-encoded |
| runway assigned | Yes | |
| current weather condition at scheduled time | Yes | forecast-time value, not actual-time |
| traffic_level (flights scheduled in same 30-min window) | Yes | computed from schedule, not actuals |
| gate_type of currently assigned gate (if any) | Yes | |

Explicitly EXCLUDED (would leak): `actual_arrival`, `actual_departure`, any post-hoc weather reading taken after the flight landed, any field derived from the target itself.

## Models
Candidates: `LinearRegression` (baseline), `RandomForestRegressor`, `GradientBoostingRegressor`, `HistGradientBoostingRegressor`. Selection: train all four on the same train split, evaluate on the same held-out test split (80/20, `random_state` fixed for reproducibility), select by lowest test RMSE (report MAE/R² alongside regardless of which wins). Record the choice + metrics in `docs/DECISION_LOG.md` once run.

## Evaluation (required, must be real numbers from a real run)
MAE, RMSE, R² on the held-out test set. Metrics persisted alongside the model as `metrics_<version>.json`. No hardcoded/assumed metrics anywhere in code or docs going forward — this doc intentionally does NOT state target numbers because none exist until the model is actually trained.

## Persistence & versioning
`joblib.dump(model, f"models/taxi_delay_{version}.joblib")`, version = ISO date + short git hash. `ml/registry.py` loads the latest version at API startup; `/api/health.ml_model_loaded` reflects whether that load succeeded.

## Risk classification (Phase 5)
Pure function of `predicted_delay_minutes` and `system_config.risk_low_max_minutes` / `risk_medium_max_minutes` (REQUIREMENTS R9). `delay ≤ risk_low_max → LOW`; `risk_low_max < delay ≤ risk_medium_max → MEDIUM`; `delay > risk_medium_max → HIGH`. Never hardcoded in frontend — frontend only renders the `risk_level` string the backend returns.

## Failure handling
No model file present → `/api/predictions` returns 503 `{error: {code: "MODEL_UNAVAILABLE", ...}}`, never a fabricated number.
