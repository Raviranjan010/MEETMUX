import os
os.environ["OPENBLAS_NUM_THREADS"] = "1"
os.environ["MKL_NUM_THREADS"] = "1"
os.environ["OMP_NUM_THREADS"] = "1"

import json
import logging
from typing import Optional, Dict, Any
from datetime import datetime, timezone
import numpy as np
import pandas as pd
import joblib

from sklearn.model_selection import train_test_split
from sklearn.linear_model import LinearRegression
from sklearn.ensemble import RandomForestRegressor, GradientBoostingRegressor, HistGradientBoostingRegressor
from sklearn.metrics import mean_absolute_error, mean_squared_error, r2_score

from app.ml.features import (
    FEATURE_COLUMNS,
    compute_flight_features,
    AIRLINES_MAP,
    RUNWAYS_MAP,
    SIZE_CLASS_MAP,
    WEATHER_SEVERITY_MAP,
)

logger = logging.getLogger(__name__)


def generate_training_data(n_samples: int = 1500, random_state: int = 42) -> pd.DataFrame:
    """
    Generates deterministic historical flight dataset for training taxi-in delay models.
    Realistic domain relationships:
    - RWY-1 baseline = 12.0 min, RWY-2 baseline = 15.0 min
    - Traffic density increases taxi time by 0.8 min per extra flight
    - Heavy weather adds 3.0 to 10.0 min
    - Large aircraft take 2.5 min longer to taxi
    - Remote gates add 4.0 min
    - Day/hour peak curves
    """
    rng = np.random.RandomState(random_state)

    airlines = list(AIRLINES_MAP.keys())[:-1]  # AA, DL, UA, BA, LH, AF
    runways = ["RWY-1", "RWY-2"]
    size_classes = ["SMALL", "MEDIUM", "LARGE"]
    weather_conds = list(WEATHER_SEVERITY_MAP.keys())
    weather_weights = [0.60, 0.15, 0.10, 0.05, 0.03, 0.03, 0.02, 0.02]

    base_date = datetime(2026, 1, 1, 0, 0, tzinfo=timezone.utc)
    records = []

    for i in range(n_samples):
        # Sample timestamp throughout a month
        day_offset = rng.randint(0, 30)
        raw_p = np.array([1, 1, 1, 1, 2, 3, 5, 7, 8, 7, 6, 5, 5, 5, 6, 7, 8, 7, 5, 4, 3, 2, 1, 1], dtype=float)
        probs = raw_p / raw_p.sum()
        hour = rng.choice(np.arange(0, 24), p=probs)
        minute = rng.randint(0, 60)
        flight_dt = datetime(2026, 1, 1 + day_offset, hour, minute, tzinfo=timezone.utc)

        airline = rng.choice(airlines)
        is_intl = airline in ["BA", "LH", "AF"] or rng.rand() < 0.2
        route_type = "INTERNATIONAL" if is_intl else "DOMESTIC"
        size_class = rng.choice(size_classes, p=[0.25, 0.55, 0.20])
        runway = rng.choice(runways, p=[0.55, 0.45])
        weather = rng.choice(weather_conds, p=weather_weights)
        gate_type = "REMOTE" if rng.rand() < 0.15 else "JETBRIDGE"

        # Traffic density correlates with peak hours
        peak_factor = 1.8 if 8 <= hour <= 11 or 16 <= hour <= 19 else 0.8
        traffic_30m = int(max(0, rng.poisson(lam=4 * peak_factor)))

        features = compute_flight_features(
            scheduled_arrival=flight_dt,
            route_type=route_type,
            aircraft_size_class=size_class,
            airline=airline,
            runway_code=runway,
            weather_condition=weather,
            traffic_density_30m=traffic_30m,
            gate_type=gate_type,
        )

        # Ground truth actual taxi time (minutes)
        base_taxi = 12.0 if runway == "RWY-1" else 15.0
        weather_delay = WEATHER_SEVERITY_MAP[weather] * 1.5
        traffic_delay = traffic_30m * 0.75
        size_delay = (SIZE_CLASS_MAP[size_class] - 1) * 1.2
        remote_delay = 3.5 if gate_type == "REMOTE" else 0.0
        noise = rng.normal(0, 1.2)

        actual_taxi_minutes = max(
            5.0,
            base_taxi + weather_delay + traffic_delay + size_delay + remote_delay + noise
        )

        row = dict(features)
        row["actual_taxi_minutes"] = round(actual_taxi_minutes, 2)
        records.append(row)

    return pd.DataFrame(records)


def train_and_evaluate_models(
    df: Optional[pd.DataFrame] = None,
    output_dir: str = "backend/models",
    version: Optional[str] = None,
) -> Dict[str, Any]:
    """
    Trains 4 candidate regressors per docs/ML.md on 80/20 train/test split.
    Selects best model by lowest test RMSE.
    Saves model and metrics JSON.
    """
    if df is None:
        df = generate_training_data(n_samples=1500, random_state=42)

    if version is None:
        version = f"{datetime.now(timezone.utc).strftime('%Y%m%d')}_v1"

    X = df[FEATURE_COLUMNS]
    y = df["actual_taxi_minutes"]

    X_train, X_test, y_train, y_test = train_test_split(
        X, y, test_size=0.20, random_state=42
    )

    candidates = {
        "LinearRegression": LinearRegression(),
        "RandomForestRegressor": RandomForestRegressor(n_estimators=100, max_depth=12, random_state=42),
        "GradientBoostingRegressor": GradientBoostingRegressor(n_estimators=100, max_depth=4, random_state=42),
        "HistGradientBoostingRegressor": HistGradientBoostingRegressor(max_iter=100, random_state=42),
    }

    results = {}
    best_name = None
    best_rmse = float("inf")
    best_model = None

    for name, model in candidates.items():
        model.fit(X_train, y_train)
        preds = model.predict(X_test)

        mae = float(mean_absolute_error(y_test, preds))
        rmse = float(np.sqrt(mean_squared_error(y_test, preds)))
        r2 = float(r2_score(y_test, preds))

        results[name] = {
            "mae": round(mae, 4),
            "rmse": round(rmse, 4),
            "r2": round(r2, 4),
        }

        logger.info(f"Model {name} -> MAE: {mae:.4f}, RMSE: {rmse:.4f}, R2: {r2:.4f}")

        if rmse < best_rmse:
            best_rmse = rmse
            best_name = name
            best_model = model

    os.makedirs(output_dir, exist_ok=True)

    # Persist best model
    model_filename = f"taxi_delay_{version}.joblib"
    model_path = os.path.join(output_dir, model_filename)
    joblib.dump(best_model, model_path)

    # Persist metrics JSON
    metrics_payload = {
        "version": version,
        "selected_model": best_name,
        "selected_metrics": results[best_name],
        "all_candidates": results,
        "feature_columns": FEATURE_COLUMNS,
        "train_samples": len(X_train),
        "test_samples": len(X_test),
        "created_at": datetime.now(timezone.utc).isoformat(),
    }

    metrics_filename = f"metrics_{version}.json"
    metrics_path = os.path.join(output_dir, metrics_filename)
    with open(metrics_path, "w") as f:
        json.dump(metrics_payload, f, indent=2)

    logger.info(f"Best model '{best_name}' (RMSE={best_rmse:.4f}) persisted to {model_path}")
    logger.info(f"Metrics saved to {metrics_path}")

    return {
        "selected_model": best_name,
        "version": version,
        "model_path": model_path,
        "metrics_path": metrics_path,
        "metrics": metrics_payload,
    }


if __name__ == "__main__":
    logging.basicConfig(level=logging.INFO)
    train_and_evaluate_models()
