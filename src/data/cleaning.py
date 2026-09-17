"""
Data Cleaning & Preprocessing Module
Owner: Ravi (Data Cleaning & EDA Engineer)
"""

import os
import pandas as pd
import numpy as np

PRIMARY_RAW_PATH = os.path.join("data", "raw", "WA_Fn-UseC_-Telco-Customer-Churn.csv")
ALT_RAW_PATH = os.path.join("data", "raw", "telco_customer_churn.csv")
PROCESSED_DATA_PATH = os.path.join("data", "processed", "customer_features.csv")

def load_raw_data(file_path: str = PRIMARY_RAW_PATH) -> pd.DataFrame:
    if not os.path.exists(file_path):
        if os.path.exists(ALT_RAW_PATH):
            file_path = ALT_RAW_PATH
        else:
            raise FileNotFoundError(f"Raw data file not found at: {file_path}")
    
    df = pd.read_csv(file_path)
    print(f"[INFO] Loaded raw dataset with shape: {df.shape}")
    return df  

def clean_dataset(df: pd.DataFrame) -> pd.DataFrame:
    df = df.copy()

    df = df.drop_duplicates(subset=["customerID"])
    df["TotalCharges"] = pd.to_numeric(df["TotalCharges"].astype(str).str.strip(), errors="coerce")
    missing_count = df["TotalCharges"].isnull().sum()
    if missing_count > 0:
        print(f"[INFO]Found{missing_count} missing values in TotalCharges. Imputing...")
        df["TotalCharges"] = df["TotalCharges"].fillna(df["MonthlyCharges"] * df["tenure"])

        if "Churn" in df.columns:
            df["ChurnBinary"] = df["Churn"].apply(lambda x: 1 if str(x).strip().lower() == "yes" else 0)

            print(f"[INFO] Data cleaning complete. Final dataset shape: {df. shape}")
            return df

def save_processed_data(df: pd.DataFrame, output_path: str = PROCESSED_DATA_PATH) -> None:
            os.makedirs(os.path.dirname(output_path), exist_ok=True)
            df.to_csv(output_path, index=False)
            print(f"[SUCCESS] Processed dataset saved to: {output_path}")

def run_cleaning_pipeline() -> pd.DataFrame:
            raw_df = load_raw_data()
            clean_df = clean_dataset(raw_df)
            save_processed_data(clean_df)
            return clean_df

if __name__=="__main__":
        run_cleaning_pipeline()         