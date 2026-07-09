import os
import pandas as pd
from sklearn.ensemble import IsolationForest
import joblib
from utils.logger import get_logger
import sys

# Add parent directory to path to import utils
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))
logger = get_logger("train_anomaly")

def train_anomaly_model():
    script_dir = os.path.dirname(os.path.abspath(__file__))
    train_path = os.path.join(script_dir, "../dataset/train_processed.csv")
    
    logger.info("Loading processed dataset for Anomaly Detection training...")
    train_df = pd.read_csv(train_path)
    
    # Exclude targets
    target_col = 'RUL [min]'
    cols_to_drop = ['Machine failure', 'TWF', 'HDF', 'PWF', 'OSF', 'RNF', target_col]
    
    X_train = train_df.drop(columns=cols_to_drop, errors='ignore')
    
    # Train Isolation Forest
    # Contamination is the expected proportion of outliers (anomalies). We set it to 0.05 (5%)
    logger.info("Training Isolation Forest for Sensor Anomaly Detection...")
    model = IsolationForest(n_estimators=100, contamination=0.05, random_state=42, n_jobs=-1)
    
    model.fit(X_train)
    
    # Save
    models_dir = os.path.join(script_dir, "../models")
    os.makedirs(models_dir, exist_ok=True)
    model_path = os.path.join(models_dir, "anomaly_model.pkl")
    joblib.dump(model, model_path)
    
    logger.info(f"Saved Anomaly Detection model to {os.path.abspath(model_path)}")

if __name__ == '__main__':
    train_anomaly_model()
