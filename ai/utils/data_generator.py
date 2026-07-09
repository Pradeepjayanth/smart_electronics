import os
import random
import pandas as pd
from logger import get_logger

logger = get_logger(__name__)

class SyntheticDataGenerator:
    def __init__(self):
        """Initializes the data generator for simulating machine sensors."""
        pass
        
    def generate_batch(self, n_samples=10, condition="mixed"):
        """
        Generates a synthetic batch of sensor data.
        
        Args:
            n_samples (int): Number of samples to generate.
            condition (str): "healthy", "warning", "critical", or "mixed".
            
        Returns:
            pd.DataFrame: Synthetic dataset.
        """
        data = []
        for i in range(n_samples):
            # Determine current row condition if mixed
            current_cond = condition
            if condition == "mixed":
                current_cond = random.choices(["healthy", "warning", "critical"], weights=[0.8, 0.15, 0.05])[0]
                
            # Base variables
            type_val = random.choice(["L", "M", "H"])
            
            if current_cond == "healthy":
                air_temp = random.uniform(295.0, 300.0)
                proc_temp = air_temp + random.uniform(8.0, 10.0)
                speed = random.uniform(1400, 1600)
                torque = random.uniform(30.0, 50.0)
                tool_wear = random.uniform(0, 100)
            elif current_cond == "warning":
                air_temp = random.uniform(298.0, 302.0)
                proc_temp = air_temp + random.uniform(9.0, 11.5)
                speed = random.uniform(1350, 1450)
                torque = random.uniform(45.0, 58.0)
                tool_wear = random.uniform(100, 180)
            else: # critical
                air_temp = random.uniform(301.0, 305.0)
                proc_temp = air_temp + random.uniform(10.0, 13.0)
                speed = random.uniform(1200, 1380) # Speed drops under heavy load
                torque = random.uniform(55.0, 75.0)
                tool_wear = random.uniform(180, 250)
                
            row = {
                "Type": type_val,
                "Air temperature [K]": round(air_temp, 1),
                "Process temperature [K]": round(proc_temp, 1),
                "Rotational speed [rpm]": int(speed),
                "Torque [Nm]": round(torque, 1),
                "Tool wear [min]": int(tool_wear)
            }
            data.append(row)
            
        df = pd.DataFrame(data)
        logger.info(f"Generated {n_samples} synthetic records with '{condition}' condition.")
        return df
        
    def generate_and_save(self, output_path, n_samples=100, condition="mixed"):
        df = self.generate_batch(n_samples, condition)
        os.makedirs(os.path.dirname(output_path), exist_ok=True)
        df.to_csv(output_path, index=False)
        logger.info(f"Saved synthetic batch to {os.path.abspath(output_path)}")
        return output_path

if __name__ == '__main__':
    generator = SyntheticDataGenerator()
    script_dir = os.path.dirname(os.path.abspath(__file__))
    output_file = os.path.join(script_dir, "../dataset/synthetic_batch.csv")
    generator.generate_and_save(output_file, n_samples=50)
