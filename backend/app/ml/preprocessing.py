from typing import List, Tuple
from sklearn.compose import ColumnTransformer
from sklearn.pipeline import Pipeline
from sklearn.preprocessing import StandardScaler, OneHotEncoder
from sklearn.impute import SimpleImputer

# Define canonical features
NUMERICAL_FEATURES: List[str] = [
    "hour",
    "day_of_week",
    "month",
    "is_weekend",
    "is_peak_hour",
    "scheduled_duration_minutes",
    "turnaround_minutes",
    "active_flights",
    "flights_per_hour",
    "arrivals_per_hour",
    "departures_per_hour",
    "temperature",
    "wind_speed",
    "visibility",
    "precipitation"
]

CATEGORICAL_FEATURES: List[str] = [
    "airline",
    "aircraft_type",
    "origin",
    "destination",
    "terminal",
    "runway",
    "weather_condition"
]

ALL_FEATURE_COLUMNS = NUMERICAL_FEATURES + CATEGORICAL_FEATURES


def build_preprocessor() -> ColumnTransformer:
    """
    Builds a robust scikit-learn ColumnTransformer for numerical and categorical features.
    Handles missing values and unseen categories gracefully with handle_unknown='ignore'.
    """
    numeric_transformer = Pipeline(steps=[
        ("imputer", SimpleImputer(strategy="median")),
        ("scaler", StandardScaler())
    ])

    categorical_transformer = Pipeline(steps=[
        ("imputer", SimpleImputer(strategy="constant", fill_value="Unknown")),
        ("onehot", OneHotEncoder(handle_unknown="ignore", sparse_output=False))
    ])

    preprocessor = ColumnTransformer(
        transformers=[
            ("num", numeric_transformer, NUMERICAL_FEATURES),
            ("cat", categorical_transformer, CATEGORICAL_FEATURES)
        ],
        remainder="drop"
    )

    return preprocessor
