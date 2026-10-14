"""
Telco Churn Data Cleaning Pipeline
Owner: Ravi - Data Analytics
Description: Cleans raw telco dataset, handles blank TotalCharges,
             normalizes text columns, and sets up binary churn target.
"""

import os
import sys
import pandas as pd
import numpy as np

# File paths
RAW_PATH_1 = os.path.join("data", "raw", "WA_Fn-UseC_-Telco-Customer-Churn.csv")
RAW_PATH_2 = os.path.join("data", "raw", "telco_customer_churn.csv")
OUTPUT_PATH = os.path.join("data", "processed", "customer_features.csv")


def load_raw_data(path=RAW_PATH_1):
    """Loads raw dataset from primary or fallback path."""
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
    """
    Cleans raw customer records:
    - Removes duplicate customer IDs
    - Strips whitespace from categorical columns
    - Casts TotalCharges to numeric and fills tenure=0 blanks
    - Enforces integer type on SeniorCitizen flag
    - Encodes Churn to binary (1 = Churned, 0 = Active)
    """
    data = df.copy()

    # 1. Remove duplicate customer entries if any
    init_count = len(data)
    data = data.drop_duplicates(subset=["customerID"])
    if len(data) < init_count:
        print(f"[INFO] Removed {init_count - len(data)} duplicate records")

    # 2. Trim accidental whitespace from string columns
    text_columns = data.select_dtypes(include=["object", "string"]).columns
    for col in text_columns:
        data[col] = data[col].astype(str).str.strip()

    # 3. Handle TotalCharges: raw data has blank spaces " " for tenure=0 customers
    data["TotalCharges"] = pd.to_numeric(data["TotalCharges"], errors="coerce")
    null_totals = data["TotalCharges"].isnull().sum()
    if null_totals > 0:
        print(f"[INFO] Found {null_totals} blank TotalCharges (tenure=0). Filling with MonthlyCharges * tenure...")
        data["TotalCharges"] = data["TotalCharges"].fillna(data["MonthlyCharges"] * data["tenure"])

    # 4. Enforce clean integer type for SeniorCitizen flag
    if "SeniorCitizen" in data.columns:
        data["SeniorCitizen"] = pd.to_numeric(data["SeniorCitizen"], errors="coerce").fillna(0).astype("int64")

    # 5. Create binary churn target column for modeling (Yes -> 1, No -> 0)
    if "Churn" in data.columns:
        data["ChurnBinary"] = (
            data["Churn"].astype(str).str.strip().str.lower().map({"yes": 1, "no": 0}).fillna(0).astype("int64")
        )

    print(f"[INFO] Cleaned dataset ready: {data.shape[0]} rows, {data.shape[1]} columns")
    return data


def validate_cleaned_data(df):
    """Prints a quick sanity check of the cleaned dataset."""
    nulls = df.isnull().sum().sum()
    churn_rate = (df['ChurnBinary'].mean() * 100) if 'ChurnBinary' in df.columns else 0.0
    print(f"[VERIFY] Total records: {len(df)} | Remaining NaNs: {nulls} | Baseline Churn: {churn_rate:.2f}%")


def save_processed_data(df, output_path=OUTPUT_PATH):
    """Saves the cleaned dataframe to CSV."""
    os.makedirs(os.path.dirname(output_path), exist_ok=True)
    df.to_csv(output_path, index=False)
    print(f"[SUCCESS] Cleaned data saved to: {output_path}")


def run_cleaning_pipeline(input_path=RAW_PATH_1, output_path=OUTPUT_PATH):
    """Runs the full cleaning pipeline end-to-end."""
    raw_df = load_raw_data(input_path)
    cleaned_df = clean_dataset(raw_df)
    validate_cleaned_data(cleaned_df)
    save_processed_data(cleaned_df, output_path)
    return cleaned_df


if __name__ == "__main__":
    if len(sys.argv) > 1:
        custom_input = sys.argv[1]
        print(f"[INFO] Using custom input path: {custom_input}")
        run_cleaning_pipeline(input_path=custom_input)
    else:
        run_cleaning_pipeline()
