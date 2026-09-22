import joblib
import pandas as pd
import numpy as np
from sklearn.metrics import mean_absolute_error, mean_squared_error, r2_score


# --------------------------------------------------
# 1. Load test data
# --------------------------------------------------

X_test = pd.read_csv("data/processed/X_test.csv")
y_test = pd.read_csv("data/processed/y_ltv_test.csv").squeeze()

print("X_test shape:", X_test.shape)
print("y_test shape:", y_test.shape)


# --------------------------------------------------
# 2. Load trained LTV model
# --------------------------------------------------

model = joblib.load("models/ltv/ltv_model.pkl")

print("LTV model loaded successfully.")
print("Model type:", type(model))


# --------------------------------------------------
# 3. Generate predictions
# --------------------------------------------------

y_pred = model.predict(X_test)

print("Predictions generated successfully.")
print("First 10 predictions:", y_pred[:10])


# --------------------------------------------------
# 4. Evaluate model
# --------------------------------------------------

mae = mean_absolute_error(y_test, y_pred)

rmse = np.sqrt(
    mean_squared_error(y_test, y_pred)
)

r2 = r2_score(y_test, y_pred)


print("\nLTV Model Evaluation")
print("--------------------")
print("MAE :", mae)
print("RMSE:", rmse)
print("R2  :", r2)
