import os
import pandas as pd
import numpy as np
from sklearn.ensemble import RandomForestRegressor
from sklearn.metrics import mean_squared_error, mean_absolute_error, r2_score
import joblib
from utils.logger import get_logger
import sys

# Add parent directory to path to import utils
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))
logger = get_logger("train_rul")

def train_rul_model():
    script_dir = os.path.dirname(os.path.abspath(__file__))
    train_path = os.path.join(script_dir, "../dataset/train_processed.csv")
    test_path = os.path.join(script_dir, "../dataset/test_processed.csv")
    
    logger.info("Loading processed datasets for RUL training...")
    train_df = pd.read_csv(train_path)
    test_df = pd.read_csv(test_path)
    
    # RUL is the target
    target_col = 'RUL [min]'
    
    # Exclude other targets
    cols_to_drop = ['Machine failure', 'TWF', 'HDF', 'PWF', 'OSF', 'RNF', target_col]
    
    X_train = train_df.drop(columns=cols_to_drop, errors='ignore')
    y_train = train_df[target_col]
    
    X_test = test_df.drop(columns=cols_to_drop, errors='ignore')
    y_test = test_df[target_col]
    
    logger.info("Training Random Forest Regressor for Remaining Useful Life (RUL)...")
    model = RandomForestRegressor(n_estimators=100, max_depth=10, random_state=42, n_jobs=-1)
    model.fit(X_train, y_train)
    
    # Evaluate
    y_pred = model.predict(X_test)
    mae = mean_absolute_error(y_test, y_pred)
    rmse = np.sqrt(mean_squared_error(y_test, y_pred))
    r2 = r2_score(y_test, y_pred)
    
    logger.info(f"RUL Model Evaluation - MAE: {mae:.2f} min, RMSE: {rmse:.2f} min, R2: {r2:.4f}")
    
    # Save
    models_dir = os.path.join(script_dir, "../models")
    os.makedirs(models_dir, exist_ok=True)
    model_path = os.path.join(models_dir, "rul_model.pkl")
    joblib.dump(model, model_path)
    
    logger.info(f"Saved RUL model to {os.path.abspath(model_path)}")

if __name__ == '__main__':
    train_rul_model()
