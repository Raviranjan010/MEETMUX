import os
from typing import List
from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    # App
    PROJECT_NAME: str = "RunwayOptX"
    API_V1_STR: str = "/api"
    ENVIRONMENT: str = "development"
    PORT: int = 8000
    HOST: str = "0.0.0.0"

    # Database
    DATABASE_URL: str = "sqlite:///./runwayoptx.db"

    # CORS
    CORS_ORIGINS: str = "http://localhost:5173,http://localhost:3000,http://127.0.0.1:5173"

    @property
    def cors_origins_list(self) -> List[str]:
        return [origin.strip() for origin in self.CORS_ORIGINS.split(",") if origin.strip()]

    # Auth (docs/AUTH.md)
    OPERATOR_USERNAME: str = "operator"
    OPERATOR_PASSWORD: str = "runwayoptx2026"
    JWT_SECRET_KEY: str = "runwayoptx-super-secret-key-at-least-32-chars-long-2026"
    JWT_ALGORITHM: str = "HS256"
    JWT_ACCESS_TOKEN_EXPIRE_MINUTES: int = 480

    # Solvers & ML
    GUROBI_LICENSE_PATH: str = ""
    OPTIMIZER_TIMEOUT_SECONDS: int = 60
    MODEL_DIR: str = "backend/models"

    # Default configurable parameters (REQUIREMENTS.md §R9)
    RISK_LOW_MAX_MINUTES: float = 5.0
    RISK_MEDIUM_MAX_MINUTES: float = 15.0
    TURNAROUND_BUFFER_MINUTES: int = 15
    OPTIMIZER_WEIGHT_DELAY_COST: float = 1.0
    OPTIMIZER_WEIGHT_CONFLICT_COST: float = 50.0
    OPTIMIZER_WEIGHT_REASSIGNMENT_COST: float = 5.0
    OPTIMIZER_WEIGHT_TAXI_DISTANCE: float = 0.1
    OPTIMIZER_WEIGHT_REMOTE_STAND: float = 10.0
    CASCADE_MAX_DEPTH: int = 5

    model_config = SettingsConfigDict(
        env_file=(".env", "../.env"),
        env_file_encoding="utf-8",
        extra="ignore",
    )


settings = Settings()
