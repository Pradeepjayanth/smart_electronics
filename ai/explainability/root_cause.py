import os
import sys
import pandas as pd
import numpy as np
import shap
import joblib

class RootCauseAnalyzer:
    def __init__(self, model_path=None, scaler_path=None):
        script_dir = os.path.dirname(os.path.abspath(__file__))
        self.model_path = model_path or os.path.join(script_dir, "../models/model.pkl")
        self.scaler_path = scaler_path or os.path.join(script_dir, "../models/scaler.joblib")
        
        if not os.path.exists(self.model_path):
            raise FileNotFoundError(f"Model not found at {self.model_path}")
            
        self.model = joblib.load(self.model_path)
        self.scaler = joblib.load(self.scaler_path)
        
        # Initialize SHAP TreeExplainer
        self.explainer = shap.TreeExplainer(self.model)
        
    def analyze(self, processed_df):
        """
        Analyzes the root causes of failure for given processed data points using SHAP.
        
        Args:
            processed_df (pd.DataFrame): Scaled/Engineered dataframe (ready for model prediction).
            
        Returns:
            list of dicts: Root cause analysis for each row.
        """
        # Calculate SHAP values
        shap_values = self.explainer.shap_values(processed_df)
        
        # For RandomForestClassifier, shap_values is typically a list of arrays (one for each class).
        # We are interested in class 1 (Failure)
        if isinstance(shap_values, list):
            shap_values = shap_values[1]
            
        results = []
        feature_names = processed_df.columns
        
        for i in range(len(processed_df)):
            row_shap = shap_values[i]
            # Get the top 3 contributing features to the failure prediction
            top_indices = np.argsort(row_shap)[-3:][::-1]
            
            top_factors = []
            for idx in top_indices:
                if row_shap[idx] > 0: # Only include features that *push* towards failure
                    top_factors.append({
                        "feature": feature_names[idx],
                        "impact": round(row_shap[idx], 4),
                        "scaled_value": round(processed_df.iloc[i, idx], 2)
                    })
                    
            results.append({
                "top_risk_factors": top_factors
            })
            
        return results

if __name__ == '__main__':
    # Simple test
    print("Initializing Root Cause Analyzer...")
    analyzer = RootCauseAnalyzer()
    print("Analyzer ready!")
