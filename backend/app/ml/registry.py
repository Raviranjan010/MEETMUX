import os
import glob
import logging
from typing import Any, Optional
import joblib

logger = logging.getLogger(__name__)


class ModelRegistry:
    """Manages loading and querying the persisted taxi delay model."""

    def __init__(self, model_dir: str = "backend/models"):
        self.model_dir = model_dir
        self.current_model: Optional[Any] = None
        self.current_version: Optional[str] = None

    def is_loaded(self) -> bool:
        return self.current_model is not None

    def load_latest(self) -> bool:
        """Finds and loads the latest joblib model from candidate model dirs."""
        search_dirs = [
            self.model_dir,
            "models",
            "backend/models",
            os.path.join(os.path.dirname(__file__), "../../../models"),
            os.path.join(os.path.dirname(__file__), "../../models"),
        ]

        files = []
        for d in search_dirs:
            if os.path.exists(d):
                pattern = os.path.join(d, "taxi_delay_*.joblib")
                found = glob.glob(pattern)
                files.extend(found)

        if not files:
            return False

        # Sort by modification time or version
        files.sort(key=os.path.getmtime, reverse=True)
        latest_file = files[0]

        try:
            self.current_model = joblib.load(latest_file)
            self.current_version = os.path.splitext(os.path.basename(latest_file))[0].replace("taxi_delay_", "")
            logger.info(f"Loaded ML model version {self.current_version} from {latest_file}")
            return True
        except Exception as e:
            logger.error(f"Failed loading ML model from {latest_file}: {e}")
            self.current_model = None
            self.current_version = None
            return False


registry = ModelRegistry()
