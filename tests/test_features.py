"""
Feature Pipeline Test

Project:
Customer Churn Prediction & LTV Engine
"""

from pathlib import Path

import joblib
import pandas as pd


# =============================================================================
# PROJECT ROOT
# =============================================================================

PROJECT_ROOT = (
    Path(__file__)
    .resolve()
    .parents[1]
)


# =============================================================================
# FILE PATHS
# =============================================================================

PIPELINE_FILE = (
    PROJECT_ROOT
    / "data"
    / "processed"
    / "feature_pipeline.joblib"
)

RAW_DATA_FILE = (
    PROJECT_ROOT
    / "data"
    / "raw"
    / "telco_customer_churn.csv"
)


# =============================================================================
# 1. CHECK FILES
# =============================================================================

assert PIPELINE_FILE.exists(), (
    f"Feature pipeline not found: {PIPELINE_FILE}"
)

assert RAW_DATA_FILE.exists(), (
    f"Raw dataset not found: {RAW_DATA_FILE}"
)


print("=" * 60)
print("FEATURE PIPELINE TEST")
print("=" * 60)


# =============================================================================
# 2. LOAD PIPELINE
# =============================================================================

pipeline = joblib.load(
    PIPELINE_FILE
)

print()
print("Feature pipeline loaded successfully.")
print(
    "Pipeline type:",
    type(pipeline)
)


# =============================================================================
# 3. CHECK PIPELINE CLASS
# =============================================================================

assert (
    type(pipeline).__module__
    == "src.features.feature_engineering"
), (
    "Pipeline was saved from the wrong module: "
    f"{type(pipeline).__module__}"
)

assert (
    type(pipeline).__name__
    == "CustomerFeatureEngineer"
), (
    "Unexpected pipeline class: "
    f"{type(pipeline).__name__}"
)

print(
    "Pipeline module validation: PASS"
)


# =============================================================================
# 4. LOAD RAW DATA
# =============================================================================

X_raw = pd.read_csv(
    RAW_DATA_FILE
)

X_raw.columns = (
    X_raw.columns
    .str.strip()
)

print()
print(
    "Original raw shape:",
    X_raw.shape
)


# =============================================================================
# 5. REMOVE TARGET / ID
# =============================================================================

X_raw = X_raw.drop(
    columns=[
        "Churn",
        "customerID"
    ],
    errors="ignore"
)

print(
    "Model input shape:",
    X_raw.shape
)


# =============================================================================
# 6. TRANSFORM
# =============================================================================

X_transformed = (
    pipeline.transform(X_raw)
)

print()
print(
    "Feature transformation successful."
)

print(
    "Transformed shape:",
    X_transformed.shape
)


# =============================================================================
# 7. VALIDATE ROW COUNT
# =============================================================================

assert (
    X_transformed.shape[0]
    == X_raw.shape[0]
)

print(
    "Row count validation: PASS"
)


# =============================================================================
# 8. VALIDATE FEATURE COUNT
# =============================================================================

assert (
    X_transformed.shape[1]
    == len(
        pipeline.fitted_feature_names_
    )
)

print(
    "Feature count validation: PASS"
)


# =============================================================================
# 9. CHECK FOR NaN
# =============================================================================

assert (
    X_transformed.isna().sum().sum()
    == 0
)

print(
    "Missing-value validation: PASS"
)


# =============================================================================
# 10. FINAL
# =============================================================================

print()
print("=" * 60)
print("FEATURE TEST COMPLETED SUCCESSFULLY")
print("=" * 60)
