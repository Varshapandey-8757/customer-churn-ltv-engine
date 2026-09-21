"""
Feature Export Runner

Owner: Abhishek
Project: Customer Churn Prediction & LTV Engine
Purpose:
Runs feature engineering pipeline and exports train/test datasets to data/processed.
"""

import sys
from pathlib import Path

# Ensure project root is in sys.path
PROJECT_ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(PROJECT_ROOT))

from src.features.feature_engineering import prepare_model_dataset


def main():
    raw_path = PROJECT_ROOT / "data" / "raw" / "telco_customer_churn.csv"
    output_dir = PROJECT_ROOT / "data" / "processed"

    print("=" * 80)
    print("CUSTOMER CHURN & LTV ENGINE - EXPORTING MODEL-READY DATASETS (Abhishek)")
    print("=" * 80)
    print(f"Reading raw data from: {raw_path}")
    print(f"Export target directory: {output_dir}")

    results = prepare_model_dataset(
        raw_csv_path=raw_path,
        test_size=0.2,
        random_state=42,
        output_dir=output_dir
    )

    print("\n[SUCCESS] Dataset Preparation Complete:")
    print(f"- Total Features Generated: {len(results['feature_names'])}")
    print(f"- Training set shape: {results['X_train'].shape}")
    print(f"- Test set shape: {results['X_test'].shape}")
    print(f"- Train Churn Rate: {results['y_churn_train'].mean():.2%}")
    print(f"- Test Churn Rate: {results['y_churn_test'].mean():.2%}")
    print(f"- Processed files written to: {output_dir}")
    print("=" * 80)


if __name__ == "__main__":
    main()
