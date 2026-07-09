import os
import sys
import subprocess
from utils.logger import get_logger

# Add parent directory to path to import utils
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))
logger = get_logger("retrain")

def run_script(script_path):
    """Executes a python script and logs the output."""
    try:
        logger.info(f"Starting execution of {script_path}...")
        result = subprocess.run([sys.executable, script_path], capture_output=True, text=True, check=True)
        logger.info(f"Successfully executed {script_path}\nOutput:\n{result.stdout}")
    except subprocess.CalledProcessError as e:
        logger.error(f"Failed to execute {script_path}\nError:\n{e.stderr}")
        raise

def main():
    script_dir = os.path.dirname(os.path.abspath(__file__))
    
    logger.info("==================================================")
    logger.info("INITIATING AUTOMATED MODEL RETRAINING PIPELINE")
    logger.info("==================================================")
    
    # Define script paths
    clean_data_script = os.path.abspath(os.path.join(script_dir, "../preprocessing/clean_data.py"))
    train_model_script = os.path.join(script_dir, "train_model.py")
    train_rul_script = os.path.join(script_dir, "train_rul.py")
    train_anomaly_script = os.path.join(script_dir, "train_anomaly.py")
    
    try:
        # Step 1: Preprocess Data (which splits and scales)
        logger.info("Step 1: Running Data Cleaning and Preprocessing...")
        run_script(clean_data_script)
        
        # Step 2: Retrain Base Classifier
        logger.info("Step 2: Retraining Base Classifier (Machine Failure)...")
        run_script(train_model_script)
        
        # Step 3: Retrain RUL Model
        logger.info("Step 3: Retraining RUL (Remaining Useful Life) Model...")
        run_script(train_rul_script)
        
        # Step 4: Retrain Anomaly Model
        logger.info("Step 4: Retraining Isolation Forest Anomaly Model...")
        run_script(train_anomaly_script)
        
        logger.info("==================================================")
        logger.info("ALL MODELS AUTOMATICALLY RETRAINED AND SAVED!")
        logger.info("==================================================")
        
    except Exception as e:
        logger.critical(f"Retraining Pipeline aborted due to error: {e}")

if __name__ == '__main__':
    main()
