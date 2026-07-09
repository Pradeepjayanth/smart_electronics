import os
import pandas as pd
import joblib

# Paths relative to this script
SCRIPT_DIR = os.path.dirname(os.path.abspath(__file__))
MODEL_PATH = os.path.join(SCRIPT_DIR, "../models/model.pkl")
SCALER_PATH = os.path.join(SCRIPT_DIR, "../models/scaler.joblib")

class PredictiveMaintenanceModel:
    def __init__(self):
        """Initializes the predictor by loading the model and scaler."""
        if not os.path.exists(MODEL_PATH) or not os.path.exists(SCALER_PATH):
            raise FileNotFoundError(
                f"Model or scaler not found. Please ensure they exist at:\n"
                f"- {MODEL_PATH}\n- {SCALER_PATH}"
            )
        
        self.model = joblib.load(MODEL_PATH)
        self.scaler = joblib.load(SCALER_PATH)
        print("Model and scaler loaded successfully.")

    def preprocess(self, raw_data):
        """
        Preprocesses raw input data to match the training feature space.
        
        Args:
            raw_data (dict or list of dicts): Raw input features.
            
        Returns:
            pd.DataFrame: Scaled and engineered features ready for prediction.
        """
        # Convert to DataFrame
        if isinstance(raw_data, dict):
            df = pd.DataFrame([raw_data])
        else:
            df = pd.DataFrame(raw_data)
            
        # 1. Validate raw required columns
        required_raw_cols = [
            'Air temperature [K]', 'Process temperature [K]',
            'Rotational speed [rpm]', 'Torque [Nm]', 'Tool wear [min]'
        ]
        missing_raw = set(required_raw_cols) - set(df.columns)
        if missing_raw:
            raise ValueError(f"Missing required input columns: {missing_raw}")

        # 2. Encode categorical 'Type'
        type_mapping = {'L': 0, 'M': 1, 'H': 2}
        if 'Type' in df.columns:
            df['Type'] = df['Type'].map(type_mapping)
        df['Type'] = df.get('Type', 0).fillna(0) # Default to 'L' if missing
            
        # 3. Feature Engineering (must exactly match training)
        df['Temp_Diff'] = df['Process temperature [K]'] - df['Air temperature [K]']
        df['Power_Proxy'] = df['Torque [Nm]'] * df['Rotational speed [rpm]']
        df['Tool_Wear_Torque'] = df['Tool wear [min]'] * df['Torque [Nm]']
        
        # 4. Ensure final column order matches training data
        expected_cols = [
            'Type', 'Air temperature [K]', 'Process temperature [K]',
            'Rotational speed [rpm]', 'Torque [Nm]', 'Tool wear [min]',
            'Temp_Diff', 'Power_Proxy', 'Tool_Wear_Torque'
        ]
        
        df = df[expected_cols]
        
        # 4. Scale numerical features
        num_cols = [col for col in expected_cols if col != 'Type']
        df_scaled = df.copy()
        df_scaled[num_cols] = self.scaler.transform(df[num_cols])
        
        return df_scaled

    def predict(self, raw_data):
        """
        Predicts machine failure for the given raw data.
        
        Args:
            raw_data (dict or list of dicts): Raw input features.
            
        Returns:
            list of dicts: Prediction results containing 'prediction' and 'probability'.
        """
        processed_data = self.preprocess(raw_data)
        
        predictions = self.model.predict(processed_data)
        probabilities = self.model.predict_proba(processed_data)[:, 1]
        
        results = []
        for i in range(len(predictions)):
            results.append({
                "prediction": int(predictions[i]),
                "failure_probability": float(probabilities[i]),
                "status": "Failure Predicted" if predictions[i] == 1 else "Normal Operation"
            })
            
        return results

if __name__ == '__main__':
    # Sample usage
    print("Initializing Predictive Maintenance Predictor...")
    try:
        predictor = PredictiveMaintenanceModel()
        
        # Sample data (one normal, one likely failure based on EDA insights)
        sample_inputs = [
            {
                # Normal operation example (low torque, high rpm, low tool wear)
                "Type": "L",
                "Air temperature [K]": 298.1,
                "Process temperature [K]": 308.6,
                "Rotational speed [rpm]": 1551,
                "Torque [Nm]": 42.8,
                "Tool wear [min]": 0
            },
            {
                # Likely failure example (high torque, low rpm, high tool wear, high temp diff)
                "Type": "H",
                "Air temperature [K]": 300.0,
                "Process temperature [K]": 312.0,
                "Rotational speed [rpm]": 1300,
                "Torque [Nm]": 65.0,
                "Tool wear [min]": 220
            }
        ]
        
        print("\nRunning predictions on sample data:")
        results = predictor.predict(sample_inputs)
        
        for i, (input_data, result) in enumerate(zip(sample_inputs, results)):
            print(f"\n--- Sample {i+1} ---")
            print(f"Input: {input_data}")
            print(f"Prediction: {result['status']} (Probability: {result['failure_probability']:.2%})")
            
    except Exception as e:
        print(f"Error during prediction setup or execution: {e}")
