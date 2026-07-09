import os
import sys

# Add current directory to path to import health_score.py
sys.path.append(os.path.dirname(os.path.abspath(__file__)))
from health_score import MachineHealthScorer

class MaintenanceRecommender:
    def __init__(self):
        """Initializes the recommender and its underlying health scorer."""
        self.scorer = MachineHealthScorer()
        
    def generate_recommendations(self, raw_data):
        """
        Generates actionable maintenance recommendations based on machine data and health score.
        
        Args:
            raw_data (dict): A single dictionary of raw input features for a machine.
            
        Returns:
            dict: Contains health score, status, urgency, and a list of actionable recommendations.
        """
        # Ensure we are working with a single dict
        if isinstance(raw_data, list):
            raw_data = raw_data[0]
            
        # Get health score and failure probability
        health_info = self.scorer.calculate_health(raw_data)
        status = health_info['status']
        score = health_info['health_score']
        prob = health_info['failure_probability']
        
        recommendations = []
        urgency = "Low"
        
        # 1. Base Recommendations on Health Status
        if status == "Critical":
            urgency = "Immediate Action Required"
            recommendations.append("HALT OPERATION: Machine is at critical risk of failure.")
        elif status == "Warning":
            urgency = "High"
            recommendations.append("SCHEDULE MAINTENANCE: Machine is showing signs of degradation.")
        elif status == "Good":
            urgency = "Medium"
            recommendations.append("MONITOR: Machine is operating normally but showing slight wear.")
        else:
            urgency = "Low"
            recommendations.append("CONTINUE: Machine is operating optimally.")
            
        # 2. Domain-Specific Rule-Based Diagnostics (Linked to AI4I 2020 dataset features)
        
        # Tool Wear (Predicts TWF - Tool Wear Failure)
        tool_wear = raw_data.get('Tool wear [min]', 0)
        if tool_wear > 200:
            recommendations.append("TOOL WEAR ALERT: Tool wear has exceeded critical threshold (>200 min). Replace tool immediately to prevent Tool Wear Failure (TWF).")
        elif tool_wear > 150:
            recommendations.append("TOOL WEAR WARNING: Tool is approaching end of life. Schedule a tool replacement in the upcoming shifts.")
            
        # Torque and Speed (Predicts PWF - Power Failure and OSF - Overstrain Failure)
        torque = raw_data.get('Torque [Nm]', 0)
        speed = raw_data.get('Rotational speed [rpm]', 0)
        if torque > 60.0:
            recommendations.append("OVERSTRAIN ALERT: Torque is excessively high (>60 Nm). Reduce operational load to prevent Overstrain Failure (OSF).")
        
        power_proxy = torque * speed
        # High power (high torque * speed) or extremely low speed with high torque
        if power_proxy > 100000 or (speed < 1350 and torque > 55):
             recommendations.append("POWER WARNING: Power/Load ratio is in a high-risk zone. Check motor and drivetrain to prevent Power Failure (PWF).")
             
        # Temperatures (Predicts HDF - Heat Dissipation Failure)
        air_temp = raw_data.get('Air temperature [K]', 0)
        process_temp = raw_data.get('Process temperature [K]', 0)
        temp_diff = process_temp - air_temp
        
        if air_temp > 302.0 or process_temp > 311.0:
            recommendations.append("TEMPERATURE ALERT: Absolute temperatures are critically high. Inspect cooling systems to prevent Heat Dissipation Failure (HDF).")
        elif temp_diff < 8.0 and process_temp > 309.0:
            # Low differential at high temps means poor heat dissipation
            recommendations.append("HEAT DISSIPATION WARNING: Poor temperature differential detected. Check ventilation and ambient cooling.")

        return {
            "health_score": score,
            "status": status,
            "failure_probability_pct": prob,
            "urgency": urgency,
            "recommendations": recommendations
        }

if __name__ == '__main__':
    print("Initializing Maintenance Recommender...")
    try:
        recommender = MaintenanceRecommender()
        
        sample_inputs = [
            {
                "description": "Healthy Machine",
                "data": {
                    "Type": "L", "Air temperature [K]": 298.1, "Process temperature [K]": 308.6,
                    "Rotational speed [rpm]": 1551, "Torque [Nm]": 42.8, "Tool wear [min]": 0
                }
            },
            {
                "description": "Machine with High Tool Wear",
                "data": {
                    "Type": "M", "Air temperature [K]": 298.5, "Process temperature [K]": 309.0,
                    "Rotational speed [rpm]": 1400, "Torque [Nm]": 48.0, "Tool wear [min]": 185
                }
            },
            {
                "description": "Machine with Severe Overheating & Overstrain",
                "data": {
                    "Type": "H", "Air temperature [K]": 303.0, "Process temperature [K]": 312.0,
                    "Rotational speed [rpm]": 1300, "Torque [Nm]": 65.0, "Tool wear [min]": 210
                }
            }
        ]
        
        for sample in sample_inputs:
            print(f"\n{'='*60}\nScenario: {sample['description']}\n{'='*60}")
            report = recommender.generate_recommendations(sample["data"])
            
            print(f"Health Score: {report['health_score']}/100 ({report['status']})")
            print(f"Urgency Level: {report['urgency']}")
            print("\nActionable Recommendations:")
            for i, rec in enumerate(report['recommendations'], 1):
                print(f"  {i}. {rec}")
                
    except Exception as e:
        print(f"Error: {e}")
