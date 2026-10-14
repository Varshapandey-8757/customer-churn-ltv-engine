"""
Unit Tests for Data Cleaning Module
Owner: Ravi - Data Analytics
"""

import sys
from pathlib import Path

# Add project root to sys.path so imports work cleanly from any directory
PROJECT_ROOT = Path(__file__).resolve().parent.parent
if str(PROJECT_ROOT) not in sys.path:
    sys.path.insert(0, str(PROJECT_ROOT))

import unittest
import pandas as pd
from src.data.cleaning import clean_dataset


class TestDataCleaning(unittest.TestCase):

    def setUp(self):
        """Create sample dummy records with common raw data quirks."""
        self.sample_df = pd.DataFrame({
            "customerID": ["C01", "C02", "C03", "C01"],  # C01 is duplicated
            "gender": [" Female ", "Male", "Female", " Female "],
            "SeniorCitizen": [0, "1", None, 0],
            "tenure": [12, 0, 24, 12],
            "MonthlyCharges": [70.50, 20.00, 85.00, 70.50],
            "TotalCharges": ["846.00", " ", "2040.00", "846.00"],  # C02 has whitespace
            "Churn": ["No", "Yes", "No", "No"]
        })

    def test_duplicate_removal(self):
        """Verify that duplicate customerIDs are removed."""
        cleaned = clean_dataset(self.sample_df)
        self.assertEqual(len(cleaned), 3)
        self.assertEqual(cleaned["customerID"].nunique(), 3)

    def test_missing_total_charges_imputed(self):
        """Verify that blank string TotalCharges for tenure=0 becomes 0.0."""
        cleaned = clean_dataset(self.sample_df)
        c02_total = cleaned.loc[cleaned["customerID"] == "C02", "TotalCharges"].values[0]
        self.assertEqual(c02_total, 0.0)
        self.assertEqual(cleaned["TotalCharges"].dtype, float)

    def test_senior_citizen_integer_type(self):
        """Verify SeniorCitizen is converted to clean integer."""
        cleaned = clean_dataset(self.sample_df)
        self.assertTrue(pd.api.types.is_integer_dtype(cleaned["SeniorCitizen"]))

    def test_churn_binary_encoding(self):
        """Verify Churn is mapped to 1 for Yes and 0 for No."""
        cleaned = clean_dataset(self.sample_df)
        # Unique customers in order: C01 -> 0, C02 -> 1, C03 -> 0
        expected = [0, 1, 0]
        self.assertEqual(list(cleaned["ChurnBinary"]), expected)

    def test_whitespace_trimmed(self):
        """Verify that leading/trailing whitespaces in string columns are stripped."""
        cleaned = clean_dataset(self.sample_df)
        self.assertEqual(cleaned.loc[cleaned["customerID"] == "C01", "gender"].values[0], "Female")


if __name__ == "__main__":
    unittest.main(verbosity=2)