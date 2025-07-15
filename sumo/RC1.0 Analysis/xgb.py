import os
import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
from xgboost import XGBRegressor
from sklearn.metrics import mean_squared_error as mse, r2_score
from sklearn.metrics.pairwise import cosine_similarity
from sklearn.preprocessing import StandardScaler
import shap
import xgboost as xgb

# 1. Load data
f = r'junction_data_race_course.csv'
df = pd.read_csv(f)
print(f"Initial data shape: {df.shape}")

# 2. Drop Time column if exists
if 'Time' in df.columns:
    df.drop(columns=['Time'], inplace=True)
print(f"Shape after dropping 'Time' column: {df.shape}")

# 3. Sample by averaging every sample_n rows
sample_n = 1
suffix = 'per_sec'
df = df.groupby(df.index // sample_n).mean().reset_index(drop=True)
print(f"Shape after sampling: {df.shape}")

# 4. Create lag features for FP_D_Count
n_lags = 10
for lag in range(1, n_lags + 1):
    df[f'FP_D_Count_lag{lag}'] = df['FP_D_Count'].shift(lag)
df.dropna(inplace=True)  # remove rows with NaNs from shifting
print(f"Shape after creating lag features: {df.shape}")

# 5. Split into X (features) and y (target)
y = df['FP_D_Count']
X = df.drop(columns=['FP_D_Count'])
print(f"Shape of X (features): {X.shape}")
print(f"Shape of y (target): {y.shape}")

# 6. Scale features (helps model convergence and cosine similarity)
scaler = StandardScaler()
X_scaled = scaler.fit_transform(X)
print(f"Shape of scaled X: {X_scaled.shape}")

# 7. Time-based train/test split (70/30)
split_idx = int(0.7 * len(df))
X_train, X_test = X_scaled[:split_idx], X_scaled[split_idx:]
y_train, y_test = y[:split_idx], y[split_idx:]
print(f"Shape of X_train: {X_train.shape}")
print(f"Shape of X_test: {X_test.shape}")
print(f"Shape of y_train: {y_train.shape}")
print(f"Shape of y_test: {y_test.shape}")

# 8. Instantiate XGBRegressor with eval_metric & early_stopping_rounds
model = XGBRegressor(
    n_estimators=500,
    learning_rate=0.1,
    random_state=42,
    eval_metric='rmse',           
    early_stopping_rounds=10      
)

# 9. Fit with eval_set only
eval_set = [(X_train, y_train), (X_test, y_test)]
model.fit(X_train, y_train, eval_set=eval_set, verbose=False)

# 10. Make predictions
y_pred = model.predict(X_test)
print(f"Shape of y_pred: {y_pred.shape}")

# 11. Evaluate
rmse = np.sqrt(mse(y_test, y_pred))
r2 = r2_score(y_test, y_pred)
cos_sim = cosine_similarity([y_test.values], [y_pred])[0][0]

# Print Evaluation Metrics
print(suffix)
print(f'RMSE: {rmse:.2f}')
print(f'R² Score: {r2:.2f}')
print(f'Cosine Similarity: {cos_sim:.4f}')

# Define the directory based on the suffix variable
plot_dir = suffix  # This will create a folder named 'per_minute' or any other value of suffix

# Check if the directory exists, if not, create it
if not os.path.exists(plot_dir):
    os.makedirs(plot_dir)

# 12. Plot: Actual vs Predicted
plt.figure(figsize=(25,5))
plt.plot(y_test.values, label='Actual', linewidth=2)
plt.plot(y_pred, label='Predicted')
plt.title('FP_D_Count: Actual vs Predicted')
plt.xlabel('Time Steps')
plt.ylabel('Vehicle Count')
plt.legend()
plt.grid(True)
plt.tight_layout()
plt.savefig(os.path.join(plot_dir, 'actual_vs_predicted_'+suffix+'.png'))  # Save the plot to the folder
plt.show()

# 13. Plot: Train vs Test RMSE over boosting rounds
results = model.evals_result()
epochs = len(results['validation_0']['rmse'])
x_axis = range(epochs)

plt.figure(figsize=(10,5))
plt.plot(x_axis, results['validation_0']['rmse'], label='Train RMSE')
plt.plot(x_axis, results['validation_1']['rmse'], label='Test RMSE')
plt.title('XGBoost Training vs Test RMSE')
plt.xlabel('Boosting Round')
plt.ylabel('RMSE')
plt.legend()
plt.grid(True)
plt.tight_layout()
plt.savefig(os.path.join(plot_dir, 'train_vs_test_rmse_'+suffix+'.png'))  # Save the plot to the folder
plt.show()

# 14. Plot: Residuals histogram
residuals = y_test - y_pred
plt.figure(figsize=(8,4))
plt.hist(residuals, bins=50, edgecolor='black')
plt.title('Prediction Residuals')
plt.xlabel('Error')
plt.ylabel('Frequency')
plt.grid(True)
plt.tight_layout()
plt.savefig(os.path.join(plot_dir, 'residuals_histogram_'+suffix+'.png'))  # Save the plot to the folder
plt.show()

# 15. Feature Importance Plot (using XGBoost's plot_importance)
plt.figure(figsize=(10,60))
xgb.plot_importance(model, importance_type='weight', max_num_features=len(X.columns))
plt.title('Feature Importance')
plt.tight_layout()
plt.savefig(os.path.join(plot_dir, 'feature_importance_'+suffix+'.png'))  # Save the plot to the folder
plt.show()

# 16. SHAP Summary Plot
X_train_df = pd.DataFrame(X_train, columns=X.columns)

# Create SHAP explainer with the original data and the model
explainer = shap.Explainer(model)

# Get SHAP values
shap_values = explainer(X_train_df)

# SHAP summary plot
shap.summary_plot(shap_values, X_train_df)
plt.savefig(os.path.join(plot_dir, 'shap_summary_plot_'+suffix+'.png'))  # Save the plot to the folder
plt.show()

