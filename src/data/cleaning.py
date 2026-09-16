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

if __name__ == "__main__":
    df = load_raw_data()