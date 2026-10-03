"""
Feature Export Runner

Owner: Abhishek
Project: Customer Churn Prediction & LTV Engine

Purpose:
Runs feature engineering pipeline and exports train/test datasets
to data/processed.
"""

import sys
from pathlib import Path


# =============================================================================
# PROJECT ROOT
# =============================================================================

PROJECT_ROOT = Path(__file__).resolve().parent.parent

# Ensure project root is available for imports
sys.path.insert(0, str(PROJECT_ROOT))


# =============================================================================
# IMPORT
# =============================================================================

from src.features.feature_engineering import prepare_model_dataset


# =============================================================================
# MAIN
# =============================================================================

def main():

    raw_path = (
        PROJECT_ROOT
        / "data"
        / "raw"
        / "telco_customer_churn.csv"
    )

    output_dir = (
        PROJECT_ROOT
        / "data"
        / "processed"
    )

    print("=" * 80)
    print(
        "CUSTOMER CHURN & LTV ENGINE "
        "- EXPORTING MODEL-READY DATASETS"
    )
    print("=" * 80)

    print(f"Reading raw data from: {raw_path}")
    print(f"Export target directory: {output_dir}")

    # -------------------------------------------------------------------------
    # Validate raw dataset
    # -------------------------------------------------------------------------

    if not raw_path.exists():
        raise FileNotFoundError(
            f"Raw dataset not found: {raw_path}"
        )

    # -------------------------------------------------------------------------
    # Run feature engineering
    # -------------------------------------------------------------------------

    results = prepare_model_dataset(
        raw_csv_path=raw_path,
        test_size=0.2,
        random_state=42,
        output_dir=output_dir
    )

    # -------------------------------------------------------------------------
    # Print results
    # -------------------------------------------------------------------------

    print()
    print("=" * 80)
    print("[SUCCESS] Dataset Preparation Complete")
    print("=" * 80)

    print(
        f"Total Features Generated: "
        f"{len(results['feature_names'])}"
    )

    print(
        f"Training set shape: "
        f"{results['X_train'].shape}"
    )

    print(
        f"Test set shape: "
        f"{results['X_test'].shape}"
    )

    print(
        f"Train Churn Rate: "
        f"{results['y_churn_train'].mean():.2%}"
    )

    print(
        f"Test Churn Rate: "
        f"{results['y_churn_test'].mean():.2%}"
    )

    print(
        f"Processed files written to: "
        f"{output_dir}"
    )

    print()
    print(
        "Feature pipeline:"
    )

    print(
        output_dir
        / "feature_pipeline.joblib"
    )

    print("=" * 80)


# =============================================================================
# ENTRY POINT
# =============================================================================

if __name__ == "__main__":
    main()
