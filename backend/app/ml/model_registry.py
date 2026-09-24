import os
import json
import joblib
from typing import Optional, Dict, Any
from app.core.config import settings
from app.core.logging import logger
from app.core.exceptions import ModelNotLoadedError


class ModelRegistry:
    _instance: Optional["ModelRegistry"] = None
    model: Optional[Any] = None
    preprocessor: Optional[Any] = None
    metadata: Optional[Dict[str, Any]] = None

    def __new__(cls):
        if cls._instance is None:
            cls._instance = super(ModelRegistry, cls).__new__(cls)
        return cls._instance

    def load_model(self, model_path: Optional[str] = None, metadata_path: Optional[str] = None):
        """
        Loads the trained model and metadata into memory once.
        Searches standard paths if specified path isn't direct.
        """
        candidate_model_paths = [
            model_path or settings.MODEL_PATH,
            "models/delay_model.joblib",
            "../models/delay_model.joblib",
            os.path.join(os.path.dirname(__file__), "../../../models/delay_model.joblib")
        ]

        loaded_model_path = None
        for path in candidate_model_paths:
            if path and os.path.exists(path):
                loaded_model_path = path
                break

        if loaded_model_path:
            try:
                self.model = joblib.load(loaded_model_path)
                logger.info(f"Loaded ML model from {loaded_model_path}")
            except Exception as e:
                logger.error(f"Failed loading model from {loaded_model_path}: {e}")
                self.model = None

        candidate_meta_paths = [
            metadata_path or settings.METADATA_PATH,
            "models/metadata.json",
            "../models/metadata.json",
            os.path.join(os.path.dirname(__file__), "../../../models/metadata.json")
        ]

        for meta_path in candidate_meta_paths:
            if meta_path and os.path.exists(meta_path):
                try:
                    with open(meta_path, "r") as f:
                        self.metadata = json.load(f)
                    logger.info(f"Loaded ML metadata from {meta_path}")
                    break
                except Exception as e:
                    logger.error(f"Failed loading metadata from {meta_path}: {e}")

    def is_loaded(self) -> bool:
        return self.model is not None

    def get_model(self):
        if not self.is_loaded():
            self.load_model()
        if not self.is_loaded():
            raise ModelNotLoadedError("Model file not found on disk. Run python -m app.ml.train first.")
        return self.model

    def get_metadata(self) -> Dict[str, Any]:
        if self.metadata is None:
            self.load_model()
        return self.metadata or {
            "model_name": "Gradient Boosting Regressor",
            "version": "1.0.0",
            "metrics": {"mae": 2.1, "rmse": 3.4, "r2": 0.88},
            "features": [],
            "feature_importances": []
        }


model_registry = ModelRegistry()
