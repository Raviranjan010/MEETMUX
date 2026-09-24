from pathlib import Path
from typing import List, Union, Optional
from pydantic import field_validator
from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    APP_NAME: str = "Predictive Air Traffic Delay & Airport Gate Scheduling Optimizer"
    ENVIRONMENT: str = "development"
    LOG_LEVEL: str = "INFO"
    DATABASE_URL: str = "sqlite:///./airport.db"
    
    # ML Model Settings
    MODEL_PATH: str = "models/delay_model.joblib"
    PREPROCESSOR_PATH: str = "models/preprocessor.joblib"
    METADATA_PATH: str = "models/metadata.json"
    
    # Optimization Settings
    OPTIMIZER_BACKEND: str = "ortools"  # 'ortools' or 'gurobi'
    GUROBI_TIME_LIMIT: int = 60
    ORTOOLS_TIME_LIMIT: int = 60
    
    # Delay categorization thresholds (minutes)
    DELAY_THRESHOLD_ON_TIME: float = 5.0
    DELAY_THRESHOLD_LOW: float = 15.0
    DELAY_THRESHOLD_MODERATE: float = 30.0
    DELAY_THRESHOLD_HIGH: float = 60.0
    
    # Default optimization weights
    DEFAULT_WEIGHT_CONFLICT: float = 1000.0
    DEFAULT_WEIGHT_WALKING: float = 1.0
    DEFAULT_WEIGHT_DELAY_PROPAGATION: float = 10.0
    DEFAULT_WEIGHT_REASSIGNMENT: float = 5.0
    DEFAULT_WEIGHT_UNUSED_GATE: float = 1.0
    
    # External API Keys (optional — fallback to mock/synthetic data if not set)
    OPENWEATHER_API_KEY: Optional[str] = None   # https://openweathermap.org/api (free tier)
    AVIATIONSTACK_API_KEY: Optional[str] = None  # https://aviationstack.com/ (free tier)
    # OpenSky Network requires no key for anonymous access

    # Security / Networking
    CORS_ORIGINS: Union[List[str], str] = ["http://localhost:5173", "http://localhost:3000", "http://127.0.0.1:5173"]
    HOST: str = "0.0.0.0"
    PORT: int = 8000

    @field_validator("CORS_ORIGINS", mode="before")
    @classmethod
    def assemble_cors_origins(cls, v: Union[str, List[str]]) -> List[str]:
        if isinstance(v, str) and not v.startswith("["):
            return [i.strip() for i in v.split(",") if i.strip()]
        elif isinstance(v, (list, str)):
            return v
        raise ValueError(v)

    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
        extra="ignore"
    )


settings = Settings()
