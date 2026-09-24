import pandas as pd
import numpy as np
from typing import Dict, Any, List, Union
from app.ml.model_registry import model_registry
from app.ml.feature_engineering import extract_features
from app.ml.preprocessing import ALL_FEATURE_COLUMNS
from app.utils.time_utils import categorize_delay


def predict_delay(input_data: Union[Dict[str, Any], pd.DataFrame]) -> List[Dict[str, Any]]:
    """
    Executes fast inference on single or batch records using the in-memory pipeline.
    Returns predicted delay in minutes and the associated operational delay category.
    """
    if isinstance(input_data, dict):
        df = pd.DataFrame([input_data])
    else:
        df = input_data.copy()

    # Engineer features without leakage
    featured_df = extract_features(df)
    X = featured_df[ALL_FEATURE_COLUMNS]

    model = model_registry.get_model()
    metadata = model_registry.get_metadata()

    # Predict
    raw_predictions = model.predict(X)
    # Clip to non-negative delays
    cleaned_predictions = np.clip(raw_predictions, a_min=0.0, a_max=None)

    results = []
    for i, pred_val in enumerate(cleaned_predictions):
        delay_min = round(float(pred_val), 1)
        cat = categorize_delay(delay_min)
        flight_num = df.iloc[i].get("flight_number", f"FLIGHT-{i+1}")
        flight_id = df.iloc[i].get("id", None)
        
        results.append({
            "flight_number": flight_num,
            "flight_id": flight_id,
            "predicted_delay_minutes": delay_min,
            "delay_category": cat,
            "confidence_score": 0.90 if delay_min < 15 else (0.85 if delay_min < 45 else 0.80),
            "model_name": metadata.get("model_name", "Gradient Boosting"),
            "model_version": metadata.get("version", "1.0.0")
        })

    return results
