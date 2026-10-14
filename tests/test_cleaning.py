import unittest
import pandas as pd
from src.data.cleaning import clean_dataset

class TestDataCleaning(unittest.TestCase):
    def setUp(self):
        self.sample_data = pd.DataFrame({
            "customerID": ["C1", "C2", "C3"],
            "MonthlyCharges": [50.0, 70.0, 90.0],
            "TotalCharges": ["50.0", " ", "180.0"],
            "tenure": [1, 0, 2],
            "Churn": ["No", "Yes", "No"],
            "SeniorCitizen": [0, 1, 0]
        })

    def test_missing_total_charges_imputation(self):
        cleaned = clean_dataset(self.sample_data)
        # Tenure 0 should impute to 0.0
        self.assertEqual(cleaned.loc[cleaned["customerID"] == "C2", "TotalCharges"].values[0], 0.0)

    def test_churn_binary_encoding(self):
        cleaned = clean_dataset(self.sample_data)
        self.assertEqual(list(cleaned["ChurnBinary"]), [0, 1, 0])

if __name__ == "__main__":
    unittest.main()