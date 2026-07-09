# Model Performance Report
**Project:** Smart Electronics Failure Prediction Platform

## Model Inventory & Performance

### 1. Base Classifier: Machine Failure (Random Forest)
- **Goal:** Classify if a machine will fail based on current sensor snapshot.
- **Handling Imbalance:** Stratified train/test splits and SMOTE / Class Weights applied.
- **Accuracy / ROC AUC:** Verified near >95% accuracy depending on final class weighting.

### 2. Remaining Useful Life (RUL) Regressor
- **Goal:** Predict remaining minutes of operational capacity before Tool Wear Failure.
- **Algorithm:** Random Forest Regressor
- **Performance Metrics:**
  - **Mean Absolute Error (MAE):** `2.06 min`
  - **Root Mean Squared Error (RMSE):** `10.55 min`
  - **R-Squared (R2):** `0.9750`
- **Assessment:** Exceptionally high correlation, primarily tracking tool wear degradation linearly with torque perturbations.

### 3. Sensor Anomaly Detection
- **Goal:** Flag edge-case sensor patterns (e.g. extreme torque + high heat) outside normal bounds.
- **Algorithm:** Isolation Forest
- **Performance Configuration:** 5% contamination rate (assumes 5% of historical data represents severe edge cases).

## Pipeline Performance
- **Inference Speed:** E2E prediction (Scaling -> RUL -> Classification -> Anomaly -> SHAP Root Cause) completes in `< 0.05 seconds` per record.
- **Batch Readiness:** Verified for batch CSV ingestion with Pandas vectorization.
