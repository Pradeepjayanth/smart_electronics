import os
import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import seaborn as sns
from sklearn.ensemble import RandomForestClassifier
from sklearn.metrics import (
    classification_report,
    confusion_matrix,
    roc_auc_score,
    average_precision_score,
    ConfusionMatrixDisplay
)
import joblib
import sys
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))
from utils.logger import get_logger

logger = get_logger("train_model")
def load_processed_data():
    """Loads the preprocessed training and test sets."""
    script_dir = os.path.dirname(os.path.abspath(__file__))
    train_path = os.path.join(script_dir, "../dataset/train_processed.csv")
    test_path = os.path.join(script_dir, "../dataset/test_processed.csv")
    
    if not os.path.exists(train_path) or not os.path.exists(test_path):
        raise FileNotFoundError(
            f"Processed data files not found. Please run clean_data.py first. "
            f"Checked paths:\nTrain: {train_path}\nTest: {test_path}"
        )
        
    logger.info(f"Loading train data from: {train_path}")
    train_df = pd.read_csv(train_path)
    logger.info(f"Loading test data from: {test_path}")
    test_df = pd.read_csv(test_path)
    
    return train_df, test_df

def separate_features_and_target(train_df, test_df, target_col='Machine failure'):
    """Separates features and targets, dropping non-predictive failure modes."""
    # List of all targets and sub-failure mode labels
    failure_modes = ['TWF', 'HDF', 'PWF', 'OSF', 'RNF']
    cols_to_drop = [target_col] + failure_modes
    
    X_train = train_df.drop(columns=cols_to_drop, errors='ignore')
    y_train = train_df[target_col]
    
    X_test = test_df.drop(columns=cols_to_drop, errors='ignore')
    y_test = test_df[target_col]
    
    return X_train, X_test, y_train, y_test

def train_random_forest(X_train, y_train):
    """Trains a Random Forest Classifier with balanced class weights."""
    print("Training Random Forest Classifier...")
    
    # Using class_weight='balanced' to handle the severe class imbalance (3.39% failures)
    rf_model = RandomForestClassifier(
        n_estimators=150,
        max_depth=12,
        min_samples_split=5,
        min_samples_leaf=2,
        class_weight='balanced',
        random_state=42,
        n_jobs=-1
    )
    
    rf_model.fit(X_train, y_train)
    print("Model training complete.")
    return rf_model

def evaluate_model(model, X_test, y_test, output_dir):
    """Evaluates the model and prints detailed classification metrics."""
    print("=" * 60)
    print("MODEL EVALUATION RESULTS")
    print("=" * 60)
    
    # Predictions
    y_pred = model.predict(X_test)
    y_proba = model.predict_proba(X_test)[:, 1]
    
    # 1. Classification Report
    print("Classification Report:")
    print(classification_report(y_test, y_pred, target_names=['No Failure (0)', 'Failure (1)']))
    
    # 2. Key Area Under Curves (AUC)
    roc_auc = roc_auc_score(y_test, y_proba)
    avg_precision = average_precision_score(y_test, y_proba)
    print(f"ROC AUC Score: {roc_auc:.4f}")
    print(f"Average Precision (PR AUC) Score: {avg_precision:.4f}\n")
    
    # 3. Confusion Matrix
    cm = confusion_matrix(y_test, y_pred)
    print("Confusion Matrix:")
    print(cm)
    print("-" * 60)
    
    # Save Confusion Matrix Plot
    os.makedirs(output_dir, exist_ok=True)
    plt.figure(figsize=(6, 5))
    ConfusionMatrixDisplay.from_predictions(
        y_test, 
        y_pred, 
        display_labels=['No Failure', 'Failure'], 
        cmap='Blues', 
        colorbar=False
    )
    plt.title('Confusion Matrix')
    plt.tight_layout()
    plt.savefig(os.path.join(output_dir, 'confusion_matrix.png'))
    plt.close()
    
    # Save ROC & PR curves
    plot_curves(y_test, y_proba, output_dir, roc_auc, avg_precision)

def plot_curves(y_test, y_proba, output_dir, roc_auc, avg_precision):
    """Plots and saves ROC and Precision-Recall curves."""
    from sklearn.metrics import roc_curve, precision_recall_curve
    
    fig, (ax1, ax2) = plt.subplots(1, 2, figsize=(14, 6))
    
    # ROC Curve
    fpr, tpr, _ = roc_curve(y_test, y_proba)
    ax1.plot(fpr, tpr, color='darkorange', lw=2, label=f'ROC curve (area = {roc_auc:.3f})')
    ax1.plot([0, 1], [0, 1], color='navy', lw=2, linestyle='--')
    ax1.set_xlim([0.0, 1.0])
    ax1.set_ylim([0.0, 1.05])
    ax1.set_xlabel('False Positive Rate')
    ax1.set_ylabel('True Positive Rate')
    ax1.set_title('Receiver Operating Characteristic (ROC)')
    ax1.legend(loc="lower right")
    
    # Precision-Recall Curve
    precision, recall, _ = precision_recall_curve(y_test, y_proba)
    ax2.plot(recall, precision, color='blue', lw=2, label=f'PR curve (area = {avg_precision:.3f})')
    ax2.set_xlim([0.0, 1.0])
    ax2.set_ylim([0.0, 1.05])
    ax2.set_xlabel('Recall')
    ax2.set_ylabel('Precision')
    ax2.set_title('Precision-Recall Curve')
    ax2.legend(loc="lower left")
    
    plt.tight_layout()
    plt.savefig(os.path.join(output_dir, 'evaluation_curves.png'))
    plt.close()

def save_and_plot_feature_importances(model, feature_names, output_dir):
    """Saves and plots random forest feature importances."""
    importances = model.feature_importances_
    indices = np.argsort(importances)[::-1]
    
    print("Feature Importances:")
    for f in range(len(feature_names)):
        print(f"  {f+1}. {feature_names[indices[f]]}: {importances[indices[f]]:.4f}")
    print("=" * 60)
    
    # Plot importances
    plt.figure(figsize=(10, 6))
    sns.barplot(x=importances[indices], y=np.array(feature_names)[indices], hue=np.array(feature_names)[indices], palette='viridis', legend=False)
    plt.title('Feature Importances for Predictive Maintenance')
    plt.xlabel('Relative Importance')
    plt.ylabel('Features')
    plt.tight_layout()
    plt.savefig(os.path.join(output_dir, 'feature_importances.png'))
    plt.close()

def main():
    try:
        # Create directories
        script_dir = os.path.dirname(os.path.abspath(__file__))
        models_dir = os.path.join(script_dir, "../models")
        plots_dir = os.path.join(script_dir, "plots")
        os.makedirs(models_dir, exist_ok=True)
        os.makedirs(plots_dir, exist_ok=True)
        
        # 1. Load Data
        train_df, test_df = load_processed_data()
        X_train, X_test, y_train, y_test = separate_features_and_target(train_df, test_df)
        
        # 2. Train Model
        rf_model = train_random_forest(X_train, y_train)
        
        # 3. Save Model Artifact
        model_path = os.path.join(models_dir, "model.pkl")
        joblib.dump(rf_model, model_path)
        print(f"Saved trained Random Forest model to: {os.path.abspath(model_path)}")
        
        # 4. Evaluate Model
        evaluate_model(rf_model, X_test, y_test, plots_dir)
        
        # 5. Extract Feature Importances
        save_and_plot_feature_importances(rf_model, list(X_train.columns), plots_dir)
        
        print(f"Evaluation plots and curves saved to: {os.path.abspath(plots_dir)}")
        
    except Exception as e:
        print(f"An error occurred during training: {e}")

if __name__ == '__main__':
    main()
