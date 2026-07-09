import os
import pandas as pd
import numpy as np
from sklearn.model_selection import train_test_split
from sklearn.preprocessing import StandardScaler
import joblib

def load_raw_data():
    """Loads the raw AI4I 2020 dataset."""
    script_dir = os.path.dirname(os.path.abspath(__file__))
    possible_paths = [
        os.path.join(script_dir, "../dataset/ai4i2020.csv"),
        os.path.join(script_dir, "../dataset/ai412020.csv")
    ]
    
    for path in possible_paths:
        if os.path.exists(path):
            print(f"Loading raw data from: {path}")
            return pd.read_csv(path)
            
    raise FileNotFoundError(
        f"Raw dataset not found. Tried: {[os.path.abspath(p) for p in possible_paths]}"
    )

def preprocess_and_feature_engineer(df):
    """Cleans data and performs feature engineering."""
    print("Starting preprocessing and feature engineering...")
    
    # 1. Drop irrelevant columns
    # UDI is just row index, Product ID is unique identifier (Type is a prefix of Product ID)
    df_cleaned = df.drop(columns=['UDI', 'Product ID'], errors='ignore')
    
    # 2. Encode categorical 'Type' (L, M, H represent quality variants)
    # Mapping ordinal values: Low -> 0, Medium -> 1, High -> 2
    type_mapping = {'L': 0, 'M': 1, 'H': 2}
    df_cleaned['Type'] = df_cleaned['Type'].map(type_mapping)
    
    # 3. Feature Engineering
    # A. Temperature difference: failure often happens due to high temperature differentials
    df_cleaned['Temp_Diff'] = df_cleaned['Process temperature [K]'] - df_cleaned['Air temperature [K]']
    
    # B. Power proxy: Torque * Rotational Speed (represents rotational power)
    df_cleaned['Power_Proxy'] = df_cleaned['Torque [Nm]'] * df_cleaned['Rotational speed [rpm]']
    
    # C. Strain proxy: Tool wear * Torque (tool wear severity weighted by torque load)
    df_cleaned['Tool_Wear_Torque'] = df_cleaned['Tool wear [min]'] * df_cleaned['Torque [Nm]']
    
    # 4. Target Engineering
    # A. Remaining Useful Life (RUL)
    # Typical tool failure occurs around 240 minutes. We define RUL as remaining minutes until 240.
    # If already failed, RUL is 0. If above 240, RUL is 0.
    df_cleaned['RUL [min]'] = np.maximum(0, 240 - df_cleaned['Tool wear [min]'])
    df_cleaned.loc[df_cleaned['Machine failure'] == 1, 'RUL [min]'] = 0
    
    print(f"Feature engineering complete. Created features: Temp_Diff, Power_Proxy, Tool_Wear_Torque")
    print(f"Target engineering complete. Created target: RUL [min]")
    return df_cleaned

def split_and_scale_data(df, target_col='Machine failure', test_size=0.2, random_state=42):
    """Splits data into train/test, fits scaler on train, and transforms both."""
    print("Splitting dataset into train and test sets (stratified)...")
    
    # Feature columns (exclude target columns and failure modes)
    # The targets are 'Machine failure', individual failure modes, and 'RUL [min]'
    failure_modes = ['TWF', 'HDF', 'PWF', 'OSF', 'RNF']
    targets = [target_col, 'RUL [min]'] + failure_modes
    
    X = df.drop(columns=targets, errors='ignore')
    y = df[targets]
    
    # Split using stratify to keep class imbalance ratio consistent in train and test splits
    X_train, X_test, y_train, y_test = train_test_split(
        X, y, test_size=test_size, random_state=random_state, stratify=y[target_col]
    )
    
    # Identify numerical columns to scale (everything except 'Type')
    num_cols = [col for col in X_train.columns if col != 'Type']
    
    print("Scaling numerical features...")
    scaler = StandardScaler()
    
    # Fit on training data only to avoid data leakage
    X_train_scaled = X_train.copy()
    X_test_scaled = X_test.copy()
    
    X_train_scaled[num_cols] = scaler.fit_transform(X_train[num_cols])
    X_test_scaled[num_cols] = scaler.transform(X_test[num_cols])
    
    return X_train_scaled, X_test_scaled, y_train, y_test, scaler

def main():
    try:
        script_dir = os.path.dirname(os.path.abspath(__file__))
        dataset_dir = os.path.join(script_dir, "../dataset")
        models_dir = os.path.join(script_dir, "../models")
        os.makedirs(dataset_dir, exist_ok=True)
        os.makedirs(models_dir, exist_ok=True)
        
        # Load and clean data
        df = load_raw_data()
        df_cleaned = preprocess_and_feature_engineer(df)
        
        # Save a single fully cleaned dataset (unscaled, but feature engineered)
        cleaned_path = os.path.join(dataset_dir, "cleaned_ai4i2020.csv")
        df_cleaned.to_csv(cleaned_path, index=False)
        print(f"Saved full cleaned dataset to: {os.path.abspath(cleaned_path)}")
        
        # Split and scale
        X_train_scaled, X_test_scaled, y_train, y_test, scaler = split_and_scale_data(df_cleaned)
        
        # Save Scaler for deployment/inference
        scaler_path = os.path.join(models_dir, "scaler.joblib")
        joblib.dump(scaler, scaler_path)
        print(f"Saved fitted StandardScaler scaler to: {os.path.abspath(scaler_path)}")
        
        # Save the train/test splits (including targets) for model training scripts
        train_df = pd.concat([X_train_scaled, y_train], axis=1)
        test_df = pd.concat([X_test_scaled, y_test], axis=1)
        
        train_path = os.path.join(dataset_dir, "train_processed.csv")
        test_path = os.path.join(dataset_dir, "test_processed.csv")
        
        train_df.to_csv(train_path, index=False)
        test_df.to_csv(test_path, index=False)
        
        print(f"Saved processed train split ({train_df.shape}) to: {os.path.abspath(train_path)}")
        print(f"Saved processed test split ({test_df.shape}) to: {os.path.abspath(test_path)}")
        print("\nData cleaning and preprocessing complete successfully!")
        
    except Exception as e:
        print(f"An error occurred: {e}")

if __name__ == '__main__':
    main()
