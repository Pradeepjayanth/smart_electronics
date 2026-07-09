"""
Mock ML Model
==============

Rule-based failure predictor used as a fallback when no trained
ML model (model.pkl) is available. Provides deterministic predictions
based on sensor thresholds, enabling the platform to work immediately
without requiring training data.

This module is also useful for testing and development.
"""

import random


class MockPredictor:
    """
    Rule-based predictor that simulates ML model behavior.

    Analyzes sensor data against predefined thresholds to produce
    failure probability, health score, risk level, and recommendations.
    """

    # Thresholds for each sensor (warning, critical)
    THRESHOLDS = {
        "temperature": {"warning": 70.0, "critical": 100.0, "weight": 0.30},
        "humidity": {"warning": 80.0, "critical": 95.0, "weight": 0.10},
        "voltage": {"warning_low": 3.0, "warning_high": 400.0, "critical_high": 480.0, "weight": 0.20},
        "current": {"warning": 50.0, "critical": 80.0, "weight": 0.15},
        "vibration": {"warning": 5.0, "critical": 15.0, "weight": 0.25},
    }

    # Root cause mappings
    ROOT_CAUSES = {
        "temperature": "Overheating — thermal management failure",
        "humidity": "Moisture ingress — seal degradation",
        "voltage": "Power supply instability — voltage regulator failure",
        "current": "Excessive current draw — short circuit risk",
        "vibration": "Mechanical stress — bearing or mount degradation",
    }

    # Recommendations by risk level
    RECOMMENDATIONS = {
        "low": "Continue normal monitoring. Next scheduled maintenance in 30 days.",
        "medium": "Increase monitoring frequency. Schedule preventive maintenance within 14 days.",
        "high": "Immediate inspection required. Schedule maintenance within 48 hours.",
        "critical": "URGENT: Shut down device immediately. Dispatch technician for emergency repair.",
    }

    def predict(self, sensor_data: dict) -> dict:
        """
        Generate a prediction based on sensor data using threshold rules.

        Args:
            sensor_data: Dict containing temperature, humidity, voltage,
                        current, and vibration readings.

        Returns:
            Dict with failure_probability, health_score, risk_level,
            confidence_score, remaining_useful_life, root_cause,
            and recommendation.
        """
        # Calculate per-sensor risk scores
        risk_scores = {}
        worst_sensor = None
        worst_score = 0.0

        # Temperature risk
        temp = sensor_data.get("temperature", 25.0)
        temp_risk = self._calculate_risk(
            temp, self.THRESHOLDS["temperature"]["warning"],
            self.THRESHOLDS["temperature"]["critical"],
        )
        risk_scores["temperature"] = temp_risk

        # Humidity risk
        humid = sensor_data.get("humidity", 50.0)
        humid_risk = self._calculate_risk(
            humid, self.THRESHOLDS["humidity"]["warning"],
            self.THRESHOLDS["humidity"]["critical"],
        )
        risk_scores["humidity"] = humid_risk

        # Voltage risk (both low and high are problematic)
        volt = sensor_data.get("voltage", 12.0)
        if volt < self.THRESHOLDS["voltage"]["warning_low"]:
            volt_risk = min(1.0, (self.THRESHOLDS["voltage"]["warning_low"] - volt) / 3.0)
        else:
            volt_risk = self._calculate_risk(
                volt, self.THRESHOLDS["voltage"]["warning_high"],
                self.THRESHOLDS["voltage"]["critical_high"],
            )
        risk_scores["voltage"] = volt_risk

        # Current risk
        curr = sensor_data.get("current", 2.0)
        curr_risk = self._calculate_risk(
            curr, self.THRESHOLDS["current"]["warning"],
            self.THRESHOLDS["current"]["critical"],
        )
        risk_scores["current"] = curr_risk

        # Vibration risk
        vib = sensor_data.get("vibration", 0.5)
        vib_risk = self._calculate_risk(
            vib, self.THRESHOLDS["vibration"]["warning"],
            self.THRESHOLDS["vibration"]["critical"],
        )
        risk_scores["vibration"] = vib_risk

        # Find the worst sensor
        for sensor, score in risk_scores.items():
            if score > worst_score:
                worst_score = score
                worst_sensor = sensor

        # Calculate weighted failure probability
        failure_probability = sum(
            risk_scores[s] * self.THRESHOLDS[s]["weight"]
            for s in risk_scores
        )
        failure_probability = min(1.0, max(0.0, failure_probability))

        # Health score (inverse of failure probability)
        health_score = round((1.0 - failure_probability) * 100, 1)

        # Risk level classification
        risk_level = self._classify_risk(failure_probability)

        # Confidence score (mock: higher for extreme values)
        confidence = min(0.95, 0.70 + failure_probability * 0.25)
        confidence += random.uniform(-0.02, 0.02)  # Add small noise
        confidence = round(min(0.99, max(0.60, confidence)), 2)

        # Remaining Useful Life (hours) — inversely proportional to risk
        if failure_probability > 0.9:
            rul = random.uniform(1, 24)
        elif failure_probability > 0.7:
            rul = random.uniform(24, 168)
        elif failure_probability > 0.4:
            rul = random.uniform(168, 720)
        else:
            rul = random.uniform(720, 8760)
        rul = round(rul, 1)

        # Root cause and recommendation
        root_cause = (
            self.ROOT_CAUSES.get(worst_sensor, "No anomalies detected")
            if worst_score > 0.3
            else "No significant anomalies detected"
        )
        recommendation = self.RECOMMENDATIONS[risk_level]

        return {
            "failure_probability": round(failure_probability, 4),
            "health_score": health_score,
            "risk_level": risk_level,
            "confidence_score": confidence,
            "remaining_useful_life": rul,
            "root_cause": root_cause,
            "recommendation": recommendation,
        }

    @staticmethod
    def _calculate_risk(value: float, warning: float, critical: float) -> float:
        """
        Calculate a 0-1 risk score based on warning and critical thresholds.

        Args:
            value: The sensor reading.
            warning: The warning threshold.
            critical: The critical threshold.

        Returns:
            Risk score between 0.0 and 1.0.
        """
        if value <= warning:
            return 0.0
        elif value >= critical:
            return 1.0
        else:
            return (value - warning) / (critical - warning)

    @staticmethod
    def _classify_risk(failure_probability: float) -> str:
        """Classify risk level based on failure probability."""
        if failure_probability >= 0.75:
            return "critical"
        elif failure_probability >= 0.50:
            return "high"
        elif failure_probability >= 0.25:
            return "medium"
        else:
            return "low"
