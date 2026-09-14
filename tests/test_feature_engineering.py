"""
Unit Tests for Feature Engineering Pipeline

Owner: Abhishek
Project: Customer Churn Prediction & LTV Engine
"""

import sys
from pathlib import Path

# Add project root to sys.path
PROJECT_ROOT = Path(__file__).resolve().parent.parent
if str(PROJECT_ROOT) not in sys.path:
    sys.path.insert(0, str(PROJECT_ROOT))

import unittest
import numpy as np
import pandas as pd

from src.features.feature_engineering import (
    CustomerFeatureEngineer,
    clean_raw_data,
    engineer_features,
    prepare_model_dataset,
)


class TestFeatureEngineering(unittest.TestCase):

    def setUp(self):
        """Create realistic sample customer dataframe."""
        self.sample_raw_data = pd.DataFrame({
            "customerID": ["001-A", "002-B", "003-C", "004-D"],
            "gender": ["Female", "Male", "Male", "Female"],
            "SeniorCitizen": [0, 1, 0, 0],
            "Partner": ["Yes", "No", "No", "Yes"],
            "Dependents": ["No", "No", "Yes", "No"],
            "tenure": [1, 34, 0, 72],
            "PhoneService": ["No", "Yes", "Yes", "Yes"],
            "MultipleLines": ["No phone service", "No", "Yes", "Yes"],
            "InternetService": ["DSL", "Fiber optic", "Fiber optic", "No"],
            "OnlineSecurity": ["No", "No", "No", "No internet service"],
            "OnlineBackup": ["Yes", "No", "No", "No internet service"],
            "DeviceProtection": ["No", "Yes", "No", "No internet service"],
            "TechSupport": ["No", "No", "No", "No internet service"],
            "StreamingTV": ["No", "Yes", "No", "No internet service"],
            "StreamingMovies": ["No", "Yes", "Yes", "No internet service"],
            "Contract": ["Month-to-month", "One year", "Month-to-month", "Two year"],
            "PaperlessBilling": ["Yes", "No", "Yes", "No"],
            "PaymentMethod": [
                "Electronic check",
                "Mailed check",
                "Electronic check",
                "Credit card (automatic)",
            ],
            "MonthlyCharges": [29.85, 89.10, 85.50, 25.00],
            "TotalCharges": ["29.85", "3029.40", " ", "1800.00"],
            "Churn": ["No", "No", "Yes", "No"],
        })

    def test_clean_raw_data(self):
        """Test cleaning whitespace, empty TotalCharges, and target flags."""
        cleaned = clean_raw_data(self.sample_raw_data)

        # Empty string TotalCharges for tenure=0 row must become 0.0
        row_c = cleaned.loc[cleaned["customerID"] == "003-C", "TotalCharges"].values[0]
        self.assertEqual(row_c, 0.0)
        self.assertEqual(cleaned["TotalCharges"].dtype, float)
        self.assertIn(cleaned["tenure"].dtype, [int, np.int32, np.int64])
        self.assertEqual(list(cleaned["is_churned"]), [0, 0, 1, 0])

    def test_engineer_features(self):
        """Test domain feature creation, ratios, bundling, and customer segments."""
        cleaned = clean_raw_data(self.sample_raw_data)
        engineered = engineer_features(cleaned)

        # Tenure features
        self.assertIn("tenure_cohort", engineered.columns)
        self.assertIn("tenure_years", engineered.columns)
        self.assertIn("log_tenure", engineered.columns)
        self.assertEqual(engineered.loc[engineered["customerID"] == "001-A", "is_new_customer"].values[0], 1)
        self.assertEqual(engineered.loc[engineered["customerID"] == "004-D", "is_new_customer"].values[0], 0)

        # Charge features
        self.assertIn("charges_ratio", engineered.columns)
        self.assertIn("avg_historical_monthly_charge", engineered.columns)
        self.assertIn("charge_velocity", engineered.columns)

        # High risk interaction: Fiber optic without Tech Support
        self.assertEqual(engineered.loc[engineered["customerID"] == "002-B", "has_fiber_no_techsupport_risk"].values[0], 1)

        # Bundles
        self.assertIn("has_streaming_bundle", engineered.columns)
        self.assertIn("has_security_bundle", engineered.columns)
        self.assertIn("total_services_count", engineered.columns)

        # Customer Segmentation
        self.assertIn("value_tier", engineered.columns)
        self.assertIn("risk_profile", engineered.columns)
        self.assertIn("customer_strategic_segment", engineered.columns)
        self.assertIn("estimated_total_ltv", engineered.columns)

    def test_customer_feature_engineer_transformer(self):
        """Test scikit-learn compatible transformer fit and transform."""
        transformer = CustomerFeatureEngineer()
        X_trans = transformer.fit_transform(self.sample_raw_data)

        self.assertIsInstance(X_trans, pd.DataFrame)
        self.assertFalse(X_trans.empty)
        self.assertEqual(len(X_trans), len(self.sample_raw_data))
        self.assertEqual(len(transformer.fitted_feature_names_), X_trans.shape[1])
        # Check zero NaNs
        self.assertEqual(X_trans.isna().sum().sum(), 0)


    def test_extreme_tenure_boundary_conditions(self):
        """Test boundary tenure values (0 months, 72 months, >100 months)."""
        df_boundary = self.sample_raw_data.copy()
        df_boundary["tenure"] = [0, 6, 72, 120]
        cleaned = clean_raw_data(df_boundary)
        engineered = engineer_features(cleaned)

        self.assertEqual(engineered.loc[0, "tenure_cohort"], "0-6m [New]")
        self.assertEqual(engineered.loc[1, "tenure_cohort"], "0-6m [New]")
        self.assertEqual(engineered.loc[2, "tenure_cohort"], "49+m [Veteran]")
        self.assertEqual(engineered.loc[3, "tenure_cohort"], "49+m [Veteran]")


if __name__ == "__main__":
    unittest.main(verbosity=2)

