# Skill: ml-inference

**Purpose:** Serve predictions from the persisted model via the API.
**When to use:** Phase 4 (endpoint), and every later phase that needs a prediction (risk, cascade re-prediction).
**Inputs:** flight_id(s); loaded model from ml/registry.py.
**Outputs:** Prediction rows (predicted_taxi_minutes, predicted_delay_minutes, risk_level, feature_snapshot).
**Files involved:** backend/app/ml/model.py, registry.py; backend/app/api/routes/predictions.py
**Validation requirements:** Model version logged with every prediction; feature_snapshot stored for auditability.
**Failure handling:** No model loaded → 503 MODEL_UNAVAILABLE, never a fabricated number.
**Prohibited shortcuts:** Never fall back to a random or averaged 'placeholder' delay value.
