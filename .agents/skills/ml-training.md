# Skill: ml-training

**Purpose:** Train and evaluate the taxi-delay regression model.
**When to use:** Phase 4, and whenever the feature set or dataset changes meaningfully.
**Inputs:** Cleaned flights + weather + engineered features (docs/ML.md feature table).
**Outputs:** A persisted joblib model file with version string, and a metrics_<version>.json with real MAE/RMSE/R² from a held-out test split.
**Files involved:** backend/app/ml/features.py, train.py; tests/ml/test_training.py
**Validation requirements:** Metrics come from an actual held-out split, never estimated; feature list checked against the 'available at prediction time' column in docs/ML.md.
**Failure handling:** If training data is insufficient/degenerate, report that explicitly rather than reporting fabricated metrics.
**Prohibited shortcuts:** Never hardcode a target metric value; never train on a feature derived from the target.
