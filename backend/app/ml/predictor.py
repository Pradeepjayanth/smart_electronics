"""
ML Predictor Wrapper
======================

Provides a unified interface for making predictions.
Attempts to load a trained scikit-learn model from disk.
If the model is not found or fails to load, gracefully falls back
to the rule-based MockPredictor.
"""

from app.config import get_settings
from app.ml.mock_model import MockPredictor
from app.ml.model_loader import ModelLoader
from app.utils.logger import logger


class Predictor:
    """
    Wrapper for ML predictions with a built-in fallback.
    """

    def __init__(self):
        self.settings = get_settings()
        self.loader = ModelLoader()
        self.mock_predictor = MockPredictor()
        self.model, self.framework, self.version = self.loader.load_latest_model()

    def _load_model(self) -> None:
        """Reload model using ModelLoader."""
        self.model, self.framework, self.version = self.loader.load_latest_model()

    def predict(self, sensor_data: dict) -> dict:
        """
        Make a prediction based on sensor data.

        If a trained ML model is loaded, it formats the data and uses it.
        Otherwise, routes the request to the MockPredictor.

        Args:
            sensor_data: Dict with temperature, humidity, voltage, current, vibration.

        Returns:
            Dict containing prediction results.
        """
        if self.model:
            return self._predict_with_model(sensor_data)
        else:
            return self.mock_predictor.predict(sensor_data)

    def _predict_with_model(self, sensor_data: dict) -> dict:
        """
        Execute prediction using the loaded scikit-learn model.

        Note: This is a stub implementation. Once an actual model is trained,
        this method must be updated to match the model's expected feature
        vector format and output parsing.
        """
        try:
            # Example feature extraction (depends on actual model training)
            # features = [[
            #     sensor_data.get("temperature", 0),
            #     sensor_data.get("humidity", 0),
            #     sensor_data.get("voltage", 0),
            #     sensor_data.get("current", 0),
            #     sensor_data.get("vibration", 0)
            # ]]
            #
            # prob = self.model.predict_proba(features)[0][1]
            # ... process results ...

            logger.warning("Actual ML model inference logic not fully implemented. Using mock.")
            return self.mock_predictor.predict(sensor_data)

        except Exception as e:
            logger.error(f"ML model prediction failed: {e}. Using mock fallback.")
            return self.mock_predictor.predict(sensor_data)

# Singleton instance
predictor = Predictor()
