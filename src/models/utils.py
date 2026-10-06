"""
Shared helpers for model training and serving.
owner:varsha

Single source of truth for: file paths, the leakage list for the LTV model,
and column-name cleaning (XGBoost rejects the characters [, ] and <).
"""

import re
from pathlib import Path

import pandas as pd

PROJECT_ROOT = Path(__file__).resolve().parents[2]

DATA_DIR = PROJECT_ROOT / "data" / "processed"
MODELS_DIR = PROJECT_ROOT / "models"

CHURN_MODEL_PATH = MODELS_DIR / "churn_model.pkl"
LTV_MODEL_PATH = MODELS_DIR / "ltv" / "ltv_model.pkl"
PIPELINE_PATH = MODELS_DIR / "feature_pipeline.joblib"
METRICS_PATH = MODELS_DIR / "metrics.json"

# The LTV target is TotalCharges. These columns contain TotalCharges itself,
# or are computed directly from it, so they must NEVER be model inputs.
LEAKY_LTV_COLUMNS = [
    "TotalCharges",
    "expected_cumulative_charges",
    "charges_ratio",
    "avg_historical_monthly_charge",
    "charge_velocity",
    "historical_ltv",
    "estimated_total_ltv",
]


def sanitize_columns(df: pd.DataFrame) -> pd.DataFrame:
    """Replace characters that XGBoost does not allow in feature names."""
    return df.rename(columns=lambda c: re.sub(r"[\[\]<>]", "_", str(c)))


def drop_leaky_ltv_columns(df: pd.DataFrame) -> pd.DataFrame:
    """Remove every column that leaks the LTV target."""
    return df.drop(columns=LEAKY_LTV_COLUMNS, errors="ignore")


def load_split():
    """Load the processed train/test split created by the feature pipeline."""
    X_train = sanitize_columns(pd.read_csv(DATA_DIR / "X_train.csv"))
    X_test = sanitize_columns(pd.read_csv(DATA_DIR / "X_test.csv"))

    y_churn_train = pd.read_csv(DATA_DIR / "y_churn_train.csv").squeeze()
    y_churn_test = pd.read_csv(DATA_DIR / "y_churn_test.csv").squeeze()

    y_ltv_train = pd.read_csv(DATA_DIR / "y_ltv_train.csv").squeeze()
    y_ltv_test = pd.read_csv(DATA_DIR / "y_ltv_test.csv").squeeze()

    return (
        X_train, X_test,
        y_churn_train, y_churn_test,
        y_ltv_train, y_ltv_test,
    )
