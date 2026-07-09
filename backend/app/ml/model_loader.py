"""
Model Loader
============

Responsible for dynamically loading trained ML models from the filesystem.
Supports multiple framework backends:
- scikit-learn (.pkl / .joblib)
- xgboost (.json / .model)
- tensorflow (.h5 / SavedModel)

Handles versioning by looking up the latest model version from the
specified models directory if an explicit version is not provided.
"""

import os
from pathlib import Path
from typing import Any, Tuple

from app.config import get_settings
from app.utils.logger import logger


class ModelLoader:
    """
    Dynamically loads and manages machine learning models.
    """

    def __init__(self, models_dir: str | None = None):
        """
        Initialize the loader.

        Args:
            models_dir: Base directory where models are stored.
                        Defaults to the directory containing ML_MODEL_PATH.
        """
        settings = get_settings()
        if models_dir:
            self.models_dir = Path(models_dir)
        else:
            # Fallback to the parent directory of ML_MODEL_PATH
            self.models_dir = Path(settings.ML_MODEL_PATH).parent

    def load_latest_model(self) -> Tuple[Any | None, str | None, str]:
        """
        Scan the models directory for the latest model version and load it.

        Returns:
            Tuple containing:
            - The loaded model instance (or None if failed/not found)
            - The framework type (e.g., 'scikit-learn', 'xgboost', 'tensorflow')
            - The version string (e.g., 'v1', 'fallback')
        """
        # For this phase, we'll try to load exactly what's in ML_MODEL_PATH
        # A full versioning system would scan self.models_dir for v1, v2 folders.
        settings = get_settings()
        model_path = Path(settings.ML_MODEL_PATH)
        
        if not model_path.exists():
            logger.warning(f"No model found at {model_path}. Using fallback.")
            return None, None, "fallback"
            
        extension = model_path.suffix.lower()
        
        try:
            if extension in [".pkl", ".joblib"]:
                import joblib
                model = joblib.load(model_path)
                logger.info(f"Loaded scikit-learn model from {model_path}")
                return model, "scikit-learn", "latest"
                
            elif extension in [".json", ".model"]:
                import xgboost as xgb
                model = xgb.Booster()
                model.load_model(str(model_path))
                logger.info(f"Loaded XGBoost model from {model_path}")
                return model, "xgboost", "latest"
                
            elif extension in [".h5", ".keras"] or model_path.is_dir():
                import tensorflow as tf
                model = tf.keras.models.load_model(str(model_path))
                logger.info(f"Loaded TensorFlow model from {model_path}")
                return model, "tensorflow", "latest"
                
            else:
                logger.error(f"Unsupported model extension: {extension}")
                return None, None, "fallback"
                
        except Exception as e:
            logger.error(f"Failed to load model from {model_path}: {e}")
            return None, None, "fallback"
