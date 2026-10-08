"""
Telco Churn Data Cleaning Pipeline
Ravi - Data Analytics
"""

import os
import pandas as pd
import numpy as np

# File paths
RAW_PATH_1 = os.path.join("data", "raw", "WA_Fn-UseC_-Telco-Customer-Churn.csv")
RAW_PATH_2 = os.path.join("data", "raw", "telco_customer_churn.csv")
OUTPUT_PATH = os.path.join("data", "processed", "customer_features.csv")


def load_raw_data(path=RAW_PATH_1):
    # Check if primary or fallback file exists
    if os.path.exists(path):
        target_path = path
    elif os.path.exists(RAW_PATH_2):
        target_path = RAW_PATH_2
    else:
        raise FileNotFoundError(f"Could not find raw dataset at {path} or {RAW_PATH_2}")

    df = pd.read_csv(target_path)
    print(f"[INFO] Loaded raw dataset: {df.shape[0]} rows, {df.shape[1]} columns")
    return df


def clean_dataset(df):
    data = df.copy()

    # 1. Remove duplicate customer entries if any
    init_count = len(data)
    data = data.drop_duplicates(subset=["customerID"])
    if len(data) < init_count:
        print(f"[INFO] Removed {init_count - len(data)} duplicate records")

    # 2. Fix TotalCharges: raw data has blank spaces " " for tenure=0 customers
    data["TotalCharges"] = pd.to_numeric(data["TotalCharges"].astype(str).str.strip(), errors="coerce")
    null_totals = data["TotalCharges"].isnull().sum()
    if null_totals > 0:
        print(f"[INFO] Found {null_totals} blank TotalCharges (tenure=0). Filling with MonthlyCharges * tenure...")
        data["TotalCharges"] = data["TotalCharges"].fillna(data["MonthlyCharges"] * data["tenure"])

    # 3. Create binary churn target column for modeling (Yes -> 1, No -> 0)
    if "Churn" in data.columns:
        data["ChurnBinary"] = data["Churn"].astype(str).str.strip().str.lower().map({"yes": 1, "no": 0}).fillna(0).astype(int)

    print(f"[INFO] Cleaned dataset ready: {data.shape[0]} rows, {data.shape[1]} columns")
    return data

def validate_cleaned_data(df):
    """Prints a quick sanity check of the cleaned dataset."""
    nulls = df.isnull().sum().sum()
    churn_rate = (df['ChurnBinary'].mean() * 100) if 'ChurnBinary' in df.columns else 0
    print(f"[VERIFY] Total records: {len(df)} | Remaining NaNs: {nulls} | Baseline Churn: {churn_rate:.2f}%")


def save_processed_data(df, output_path=OUTPUT_PATH):
    os.makedirs(os.path.dirname(output_path), exist_ok=True)
    df.to_csv(output_path, index=False)
    print(f"[SUCCESS] Cleaned data saved to: {output_path}")


def run_cleaning_pipeline():
    raw_df = load_raw_data()
    cleaned_df = clean_dataset(raw_df)
    validate_cleaned_data(cleaned_df)
    save_processed_data(cleaned_df)
    return cleaned_df


if __name__ == "__main__":
    run_cleaning_pipeline()