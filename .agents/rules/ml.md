# Rule: ML
- Target and features exactly as docs/ML.md defines — no feature that wouldn't be available at real prediction time.
- Train/test split and metrics (MAE/RMSE/R²) must come from an actual executed run; paste real numbers into the phase report, never estimated ones.
- Persist every trained model with a version string; never silently overwrite a prior model file without incrementing the version.
- If no model is loaded, the prediction endpoint returns 503 — never a random or hardcoded number.
