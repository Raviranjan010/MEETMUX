from typing import Dict, Any, List
import numpy as np
from app.utils.metrics import calculate_regression_metrics


def evaluate_model(model, X_test, y_test) -> Dict[str, float]:
    """
    Evaluates a trained model against test features and target.
    """
    y_pred = model.predict(X_test)
    # Target delay cannot be negative in physical operations
    y_pred = np.clip(y_pred, a_min=0.0, a_max=None)
    metrics = calculate_regression_metrics(y_test, y_pred)
    return metrics
