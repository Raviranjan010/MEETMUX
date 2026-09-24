import numpy as np
from typing import Dict, Any, List
from sklearn.metrics import mean_absolute_error, mean_squared_error, r2_score


def calculate_regression_metrics(y_true: np.ndarray, y_pred: np.ndarray) -> Dict[str, float]:
    """
    Computes standard regression evaluation metrics:
    - MAE: Mean Absolute Error (average magnitude of errors in minutes)
    - RMSE: Root Mean Squared Error (penalizes larger errors more heavily)
    - R²: Coefficient of determination (proportion of variance explained by model)
    """
    mae = float(mean_absolute_error(y_true, y_pred))
    mse = float(mean_squared_error(y_true, y_pred))
    rmse = float(np.sqrt(mse))
    r2 = float(r2_score(y_true, y_pred))

    return {
        "mae": round(mae, 3),
        "rmse": round(rmse, 3),
        "r2": round(r2, 4)
    }


def calculate_optimization_kpis(
    total_flights: int,
    total_gates: int,
    assigned_count: int,
    conflicts_count: int,
    used_gate_ids: set,
    objective_val: float,
    runtime: float
) -> Dict[str, Any]:
    """
    Computes key performance indicators for an optimization run.
    """
    utilization_rate = round((len(used_gate_ids) / total_gates * 100.0), 1) if total_gates > 0 else 0.0
    assignment_rate = round((assigned_count / total_flights * 100.0), 1) if total_flights > 0 else 0.0

    return {
        "total_flights": total_flights,
        "assigned_flights": assigned_count,
        "unassigned_flights": total_flights - assigned_count,
        "assignment_rate_percentage": assignment_rate,
        "total_gates": total_gates,
        "gates_utilized": len(used_gate_ids),
        "gate_utilization_rate_percentage": utilization_rate,
        "conflicts_count": conflicts_count,
        "objective_value": round(objective_val, 2) if objective_val is not None else None,
        "execution_time_seconds": round(runtime, 3)
    }
