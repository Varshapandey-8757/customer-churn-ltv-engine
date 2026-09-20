import joblib
import pandas as pd

from src.features.feature_engineering import CustomerFeatureEngineer


# --------------------------------------------------
# 1. Load feature pipeline
# --------------------------------------------------

pipeline = joblib.load(
    "data/processed/feature_pipeline.joblib"
)

print("Feature pipeline loaded successfully.")
print("Pipeline type:", type(pipeline))


# --------------------------------------------------
# 2. Load RAW customer data
# --------------------------------------------------

X_raw = pd.read_csv(
    "data/raw/telco_customer_churn.csv"
)

X_raw.columns = X_raw.columns.str.strip()

X_raw = X_raw.drop(
    columns=["Churn", "customerID"],
    errors="ignore"
)

print("Raw input shape:", X_raw.shape)


# --------------------------------------------------
# 3. Transform raw data
# --------------------------------------------------

X_transformed = pipeline.transform(X_raw)

print("Feature transformation successful.")
print("Output shape:", X_transformed.shape)


# --------------------------------------------------
# 4. Basic validation
# --------------------------------------------------

assert X_transformed.shape[0] == X_raw.shape[0]

print("Row count validation: PASS")
print("Feature test completed successfully.")
