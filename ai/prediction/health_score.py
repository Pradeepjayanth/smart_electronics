import os
import sys

# Add current directory to path so we can import the predictor
sys.path.append(os.path.dirname(os.path.abspath(__file__)))
from predict import PredictiveMaintenanceModel

class MachineHealthScorer:
    def __init__(self):
        """Initializes the Health Scorer using the underlying predictive model."""
        self.predictor = PredictiveMaintenanceModel()

    def determine_status(self, score):
        """
        Determines the qualitative status based on the health score.
        
        Args:
            score (float): Health score (0-100)
            
        Returns:
            str: Status description
        """
        if score >= 90:
            return "Excellent"
        elif score >= 75:
            return "Good"
        elif score >= 50:
            return "Warning"
        else:
            return "Critical"

    def calculate_health(self, raw_data):
        """
        Calculates a 0-100 health score for the machine.
        
        Args:
            raw_data (dict or list of dicts): Raw input features.
            
        Returns:
            list of dicts: Health score results containing score and status.
        """
        # Ensure it's a list for iteration
        data_list = raw_data if isinstance(raw_data, list) else [raw_data]
        
        # Get raw predictions and probabilities from the underlying model
        predictions = self.predictor.predict(data_list)
        
        results = []
        for pred, data_point in zip(predictions, data_list):
            # Base probability of failure
            fail_prob = pred['failure_probability']
            
            # Base score: Inverse of failure probability
            health_score = (1.0 - fail_prob) * 100.0
            
            # --- Domain-Specific Smoothing Adjustments ---
            # Random Forest models often have sharp step-function thresholds.
            # To provide a smoother "degradation" curve for the health score,
            # we apply soft penalties for known wear-and-tear factors even if 
            # the model hasn't crossed the hard failure threshold yet.
            
            tool_wear = data_point.get('Tool wear [min]', 0)
            if tool_wear > 100:
                # Gradual penalty for aging tool
                penalty = (tool_wear - 100) * 0.15
                health_score -= penalty
                
            temp_diff = data_point.get('Process temperature [K]', 0) - data_point.get('Air temperature [K]', 0)
            if temp_diff > 10.5:
                # Gradual penalty for overheating trends
                penalty = (temp_diff - 10.5) * 2.0
                health_score -= penalty
            
            # Ensure score remains bound between 0 and 100
            health_score = max(0.0, min(100.0, health_score))
            
            status = self.determine_status(health_score)
            
            results.append({
                "health_score": round(health_score, 2),
                "status": status,
                "failure_probability": round(fail_prob * 100, 2)
            })
            
        return results if isinstance(raw_data, list) else results[0]

if __name__ == '__main__':
    print("Initializing Machine Health Scorer...")
    try:
        scorer = MachineHealthScorer()
        
        sample_inputs = [
            {
                # Brand new tool, normal conditions -> Excellent
                "Type": "L",
                "Air temperature [K]": 298.1,
                "Process temperature [K]": 308.6,
                "Rotational speed [rpm]": 1551,
                "Torque [Nm]": 42.8,
                "Tool wear [min]": 0
            },
            {
                # Tool moderately worn, normal operating params -> Good/Warning
                "Type": "M",
                "Air temperature [K]": 298.5,
                "Process temperature [K]": 309.0,
                "Rotational speed [rpm]": 1400,
                "Torque [Nm]": 48.0,
                "Tool wear [min]": 140
            },
            {
                # High stress and extremely worn tool -> Critical
                "Type": "H",
                "Air temperature [K]": 300.0,
                "Process temperature [K]": 312.0,
                "Rotational speed [rpm]": 1300,
                "Torque [Nm]": 65.0,
                "Tool wear [min]": 220
            }
        ]
        
        print("\nCalculating Health Scores:")
        scores = scorer.calculate_health(sample_inputs)
        
        for i, (input_data, res) in enumerate(zip(sample_inputs, scores)):
            print(f"\n--- Machine {i+1} ---")
            print(f"Tool Wear: {input_data['Tool wear [min]']} min | Torque: {input_data['Torque [Nm]']} Nm")
            print(f"Health Score: {res['health_score']}/100")
            print(f"Status:       {res['status']}")
            print(f"Failure Prob: {res['failure_probability']}%")
            
    except Exception as e:
        print(f"Error: {e}")
