import os
import sys
import pytest
import pandas as pd
import numpy as np

# Add parent directory to path to import modules
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))
from prediction.predict import PredictiveMaintenanceModel
from prediction.health_score import MachineHealthScorer
from prediction.recommendation import MaintenanceRecommender

@pytest.fixture(scope="module")
def predictor():
    """Returns an instance of the PredictiveMaintenanceModel."""
    return PredictiveMaintenanceModel()

@pytest.fixture(scope="module")
def health_scorer():
    """Returns an instance of the MachineHealthScorer."""
    return MachineHealthScorer()

@pytest.fixture(scope="module")
def recommender():
    """Returns an instance of the MaintenanceRecommender."""
    return MaintenanceRecommender()

def test_healthy_device(recommender):
    """Test standard healthy machine data."""
    data = {
        "Type": "L",
        "Air temperature [K]": 298.1,
        "Process temperature [K]": 308.6,
        "Rotational speed [rpm]": 1551,
        "Torque [Nm]": 42.8,
        "Tool wear [min]": 0
    }
    
    report = recommender.generate_recommendations(data)
    
    assert report['status'] == "Excellent", f"Expected Excellent, got {report['status']}"
    assert report['urgency'] == "Low"
    assert report['health_score'] >= 90
    assert report['failure_probability_pct'] < 10

def test_critical_device(recommender):
    """Test machine with severe overstrain."""
    data = {
        "Type": "H",
        "Air temperature [K]": 303.0,
        "Process temperature [K]": 312.0,
        "Rotational speed [rpm]": 1300,
        "Torque [Nm]": 65.0,
        "Tool wear [min]": 220
    }
    
    report = recommender.generate_recommendations(data)
    
    assert report['status'] == "Critical"
    assert report['urgency'] == "Immediate Action Required"
    assert report['health_score'] < 50
    assert report['failure_probability_pct'] > 50

def test_missing_sensor_values(recommender):
    """Test how the pipeline handles missing values using pandas fillna logic."""
    data = {
        # Missing 'Type' and 'Tool wear [min]'
        "Air temperature [K]": 298.1,
        "Process temperature [K]": 308.6,
        "Rotational speed [rpm]": 1551,
        "Torque [Nm]": 42.8
    }
    
    # Missing values should be gracefully handled or caught (depending on strictness)
    try:
        report = recommender.generate_recommendations(data)
        # Type should default, missing numeric typically raise ValueError in our current strict implementation
        # Actually our implementation raises ValueError for missing expected cols.
        assert False, "Should have raised ValueError due to missing required columns."
    except ValueError as e:
        assert "Missing required input columns" in str(e)

def test_batch_prediction(predictor):
    """Tests prediction on multiple rows at once."""
    batch_data = [
        {"Type": "L", "Air temperature [K]": 298.1, "Process temperature [K]": 308.6, "Rotational speed [rpm]": 1551, "Torque [Nm]": 42.8, "Tool wear [min]": 0},
        {"Type": "H", "Air temperature [K]": 303.0, "Process temperature [K]": 312.0, "Rotational speed [rpm]": 1300, "Torque [Nm]": 65.0, "Tool wear [min]": 220}
    ]
    
    results = predictor.predict(batch_data)
    assert len(results) == 2
    assert results[0]['status'] == "Normal Operation"
    assert results[1]['status'] == "Failure Predicted"

