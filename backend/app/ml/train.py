import os
import json
import joblib
from datetime import datetime
import pandas as pd
import numpy as np
from sklearn.linear_model import LinearRegression
from sklearn.ensemble import RandomForestRegressor, GradientBoostingRegressor, HistGradientBoostingRegressor
from sklearn.pipeline import Pipeline

from app.ml.data_loader import generate_synthetic_airport_dataset, load_dataset
from app.ml.feature_engineering import extract_features
from app.ml.preprocessing import build_preprocessor, ALL_FEATURE_COLUMNS, NUMERICAL_FEATURES, CATEGORICAL_FEATURES
from app.ml.evaluate import evaluate_model
from app.core.config import settings
from app.core.logging import logger


def train_delay_model(
    csv_path: str = None,
    output_dir: str = "models",
    sample_dir: str = "data/sample"
) -> dict:
    """
    Complete ML pipeline:
    1. Loads dataset
    2. Extracts non-leaking features
    3. Chronological split (70% train / 15% val / 15% test)
    4. Trains multiple models (Linear Regression, Random Forest, Gradient Boosting)
    5. Evaluates and selects the champion model
    6. Persists artifacts and metadata
    """
    logger.info("Initializing ML training pipeline...")
    os.makedirs(output_dir, exist_ok=True)
    os.makedirs(sample_dir, exist_ok=True)

    # 1. Load or Generate Dataset
    if csv_path and os.path.exists(csv_path):
        df = pd.read_csv(csv_path)
    else:
        sample_flights_file = os.path.join(sample_dir, "flights.csv")
        sample_gates_file = os.path.join(sample_dir, "gates.csv")
        sample_weather_file = os.path.join(sample_dir, "weather.csv")
        
        df = generate_synthetic_airport_dataset(num_samples=5000)
        df.to_csv(sample_flights_file, index=False)
        logger.info(f"Saved sample flight dataset to {sample_flights_file}")

        # Also generate gates & weather sample files if not present
        if not os.path.exists(sample_gates_file):
            gates_df = pd.DataFrame([
                {"gate_number": "A01", "terminal": "T1", "gate_type": "Contact", "supported_aircraft_types": "A320,A321,B737", "is_international": False, "is_available": True},
                {"gate_number": "A02", "terminal": "T1", "gate_type": "Contact", "supported_aircraft_types": "A320,A321,B737", "is_international": False, "is_available": True},
                {"gate_number": "A03", "terminal": "T1", "gate_type": "Remote", "supported_aircraft_types": "A320,B737", "is_international": False, "is_available": True},
                {"gate_number": "B01", "terminal": "T2", "gate_type": "Contact", "supported_aircraft_types": "A320,A321,B737,B787", "is_international": False, "is_available": True},
                {"gate_number": "B02", "terminal": "T2", "gate_type": "Contact", "supported_aircraft_types": "A320,A321,B737,B787,B777", "is_international": False, "is_available": True},
                {"gate_number": "B03", "terminal": "T2", "gate_type": "Remote", "supported_aircraft_types": "A320,A321,B737", "is_international": False, "is_available": True},
                {"gate_number": "C01", "terminal": "T3", "gate_type": "Contact", "supported_aircraft_types": "A320,A321,B737,B787,B777,A350", "is_international": True, "is_available": True},
                {"gate_number": "C02", "terminal": "T3", "gate_type": "Contact", "supported_aircraft_types": "A320,A321,B737,B787,B777,A350", "is_international": True, "is_available": True},
                {"gate_number": "C03", "terminal": "T3", "gate_type": "Contact", "supported_aircraft_types": "A320,A321,B737,B787,B777,A350", "is_international": True, "is_available": True},
                {"gate_number": "C04", "terminal": "T3", "gate_type": "Remote", "supported_aircraft_types": "A320,A321,B737,B787,B777", "is_international": True, "is_available": True},
            ])
            gates_df.to_csv(sample_gates_file, index=False)

        if not os.path.exists(sample_weather_file):
            weather_df = pd.DataFrame([
                {"timestamp": datetime.utcnow().isoformat(), "temperature": 28.5, "wind_speed": 12.0, "visibility": 7.5, "precipitation": 0.0, "weather_condition": "Clear"},
                {"timestamp": (datetime.utcnow() - pd.Timedelta(hours=1)).isoformat(), "temperature": 27.8, "wind_speed": 14.5, "visibility": 6.0, "precipitation": 0.2, "weather_condition": "Rain"},
            ])
            weather_df.to_csv(sample_weather_file, index=False)

    total_rows = len(df)
    logger.info(f"Loaded dataset containing {total_rows} flight records.")

    # 2. Extract Features
    featured_df = extract_features(df)
    
    # Sort chronologically to respect temporal boundaries
    featured_df = featured_df.sort_values(by="scheduled_arrival").reset_index(drop=True)

    X = featured_df[ALL_FEATURE_COLUMNS]
    y = featured_df["taxi_delay_minutes"].values

    # 3. Chronological Train / Val / Test Split (70% / 15% / 15%)
    n_train = int(0.70 * total_rows)
    n_val = int(0.15 * total_rows)
    
    X_train, y_train = X.iloc[:n_train], y[:n_train]
    X_val, y_val = X.iloc[n_train:n_train + n_val], y[n_train:n_train + n_val]
    X_test, y_test = X.iloc[n_train + n_val:], y[n_train + n_val:]

    print("\n" + "="*60)
    print("  AIRPORT DELAY ML TRAINING PIPELINE")
    print("="*60)
    print(f"Dataset Total Rows: {total_rows}")
    print(f"Chronological Splits -> Train: {len(X_train)} | Val: {len(X_val)} | Test: {len(X_test)}")
    print("="*60 + "\n")

    # 4. Candidates to Train
    candidates = {
        "Linear Regression": LinearRegression(),
        "Random Forest Regressor": RandomForestRegressor(n_estimators=100, max_depth=12, random_state=42, n_jobs=-1),
        "Gradient Boosting Regressor": GradientBoostingRegressor(n_estimators=120, learning_rate=0.08, max_depth=5, random_state=42)
    }

    results = []
    trained_pipelines = {}

    for name, model in candidates.items():
        preprocessor = build_preprocessor()
        pipeline = Pipeline(steps=[
            ("preprocessor", preprocessor),
            ("regressor", model)
        ])
        
        pipeline.fit(X_train, y_train)
        
        val_metrics = evaluate_model(pipeline, X_val, y_val)
        test_metrics = evaluate_model(pipeline, X_test, y_test)
        
        print(f"[{name}]")
        print(f"  Validation -> MAE: {val_metrics['mae']:.2f} min | RMSE: {val_metrics['rmse']:.2f} min | R²: {val_metrics['r2']:.4f}")
        print(f"  Test       -> MAE: {test_metrics['mae']:.2f} min | RMSE: {test_metrics['rmse']:.2f} min | R²: {test_metrics['r2']:.4f}\n")
        
        results.append({
            "name": name,
            "val_metrics": val_metrics,
            "test_metrics": test_metrics
        })
        trained_pipelines[name] = pipeline

    # 5. Select Champion Model based on Validation MAE
    best_candidate = min(results, key=lambda r: r["val_metrics"]["mae"])
    champion_name = best_candidate["name"]
    champion_pipeline = trained_pipelines[champion_name]

    print("="*60)
    print(f" Selected Champion Model: {champion_name}")
    print(f" Best Test MAE: {best_candidate['test_metrics']['mae']:.2f} minutes (R² = {best_candidate['test_metrics']['r2']:.4f})")
    print("="*60 + "\n")

    # 6. Extract Feature Importance if available
    regressor = champion_pipeline.named_steps["regressor"]
    feature_importances = []
    
    if hasattr(regressor, "feature_importances_"):
        ohe = champion_pipeline.named_steps["preprocessor"].named_transformers_["cat"].named_steps["onehot"]
        cat_feature_names = list(ohe.get_feature_names_out(CATEGORICAL_FEATURES))
        all_feature_names = NUMERICAL_FEATURES + cat_feature_names
        
        importances = regressor.feature_importances_
        # Group back to high-level features for clarity
        grouped_importances = {feat: 0.0 for feat in ALL_FEATURE_COLUMNS}
        
        for name_idx, imp in enumerate(importances):
            name_str = all_feature_names[name_idx] if name_idx < len(all_feature_names) else "unknown"
            matched = False
            for parent_feat in ALL_FEATURE_COLUMNS:
                if name_str.startswith(parent_feat):
                    grouped_importances[parent_feat] += float(imp)
                    matched = True
                    break
            if not matched and name_idx < len(NUMERICAL_FEATURES):
                grouped_importances[NUMERICAL_FEATURES[name_idx]] += float(imp)

        # Normalize and sort
        total_imp = sum(grouped_importances.values()) or 1.0
        feature_importances = [
            {"name": k, "importance": round(v / total_imp, 4)}
            for k, v in sorted(grouped_importances.items(), key=lambda item: item[1], reverse=True)
            if v > 0.001
        ]

    # 7. Persist Artifacts
    model_file = os.path.join(output_dir, "delay_model.joblib")
    preprocessor_file = os.path.join(output_dir, "preprocessor.joblib")
    metadata_file = os.path.join(output_dir, "metadata.json")

    joblib.dump(champion_pipeline, model_file)
    joblib.dump(champion_pipeline.named_steps["preprocessor"], preprocessor_file)

    metadata = {
        "model_name": champion_name,
        "version": "1.0.0",
        "features": ALL_FEATURE_COLUMNS,
        "metrics": best_candidate["test_metrics"],
        "training_timestamp": datetime.utcnow().isoformat(),
        "total_samples": total_rows,
        "feature_importances": feature_importances,
        "model_comparisons": results
    }

    with open(metadata_file, "w") as f:
        json.dump(metadata, f, indent=2)

    logger.info(f"Model and artifacts successfully saved to {output_dir}")
    return metadata


if __name__ == "__main__":
    train_delay_model()
