"""
Feature Engineering Pipeline

Owner: Abhishek
Project: Customer Churn Prediction & LTV Engine
Purpose:
Clean raw customer data, engineer domain features (tenure, charges, contracts, 
service bundling, behavioral risk), perform customer segmentation, and prepare 
leakage-free model-ready datasets for Churn (classification) and LTV (regression) models.
"""

import json
import logging
from pathlib import Path
from typing import Dict, List, Optional, Tuple, Union

import joblib
import numpy as np
import pandas as pd
from sklearn.base import BaseEstimator, TransformerMixin
from sklearn.model_selection import train_test_split
from sklearn.preprocessing import OneHotEncoder, StandardScaler

logging.basicConfig(level=logging.INFO, format="%(asctime)s - %(levelname)s - %(message)s")
logger = logging.getLogger(__name__)


# -----------------------------------------------------------------------------
# 1. Raw Data Cleaning & Ingestion Normalization
# -----------------------------------------------------------------------------

def clean_raw_data(df: pd.DataFrame) -> pd.DataFrame:
    """
    Clean and sanitize raw telecommunications churn data.

    Operations performed:
    - Standardize column names (if needed)
    - Cast and sanitize TotalCharges (strip whitespace, convert blanks to 0.0)
    - Impute TotalCharges for 0-tenure accounts
    - Ensure numerical data types for tenure and charges
    - Create binary churn target (is_churned: 0 or 1)

    Args:
        df: Raw DataFrame matching Telco Churn schema.

    Returns:
        Cleaned pandas DataFrame.
    """
    cleaned = df.copy()

    # Normalize column names: strip whitespace
    cleaned.columns = [c.strip() for c in cleaned.columns]

    # Handle TotalCharges: raw data often contains blank spaces ' ' for tenure=0
    if "TotalCharges" in cleaned.columns:
        cleaned["TotalCharges"] = (
            cleaned["TotalCharges"]
            .astype(str)
            .str.strip()
            .replace("", "0.0")
            .replace("nan", "0.0")
            .astype(float)
        )

    # Ensure tenure is integer
    if "tenure" in cleaned.columns:
        cleaned["tenure"] = pd.to_numeric(cleaned["tenure"], errors="coerce").fillna(0).astype(int)

    # Ensure MonthlyCharges is float
    if "MonthlyCharges" in cleaned.columns:
        cleaned["MonthlyCharges"] = pd.to_numeric(cleaned["MonthlyCharges"], errors="coerce").fillna(0.0).astype(float)

    # If tenure == 0 and TotalCharges == 0, impute with 0
    mask_zero_tenure = cleaned["tenure"] == 0
    cleaned.loc[mask_zero_tenure, "TotalCharges"] = 0.0

    # Ensure Churn target is mapped to binary integer if present
    if "Churn" in cleaned.columns:
        cleaned["is_churned"] = cleaned["Churn"].apply(
            lambda x: 1 if str(x).strip().lower() in ["yes", "1", "true"] else 0
        )

    # Ensure SeniorCitizen is integer
    if "SeniorCitizen" in cleaned.columns:
        cleaned["SeniorCitizen"] = pd.to_numeric(cleaned["SeniorCitizen"], errors="coerce").fillna(0).astype(int)

    logger.info("Raw data cleaned successfully. Shape: %s", cleaned.shape)
    return cleaned


# -----------------------------------------------------------------------------
# 2. Domain Feature Engineering & Segmentation
# -----------------------------------------------------------------------------

def engineer_features(df: pd.DataFrame) -> pd.DataFrame:
    """
    Generate business and domain-specific features related to:
    - Tenure (cohorts, log tenure, lifecycle stage)
    - Monthly & Total Charges (ratios, historical averages, charge velocity)
    - Contract & Billing (friction flags, commitment duration, auto-pay)
    - Service usage & bundling (active service count, fiber risk, bundles)
    - Customer segmentation (value tiers, behavioral risk profiles, LTV proxies)

    Args:
        df: Cleaned input DataFrame.

    Returns:
        DataFrame enriched with all engineered features.
    """
    feat = df.copy()

    # -------------------------------------------------------------------------
    # A. Tenure Features
    # -------------------------------------------------------------------------
    if "tenure" in feat.columns:
        feat["tenure_months"] = feat["tenure"]
        feat["tenure_years"] = np.round(feat["tenure"] / 12.0, 2)
        feat["log_tenure"] = np.round(np.log1p(feat["tenure"]), 4)
        feat["is_new_customer"] = (feat["tenure"] <= 6).astype(int)
        
        # Tenure Cohort Bins
        bins = [-1, 6, 12, 24, 48, 120]
        labels = ["0-6m [New]", "7-12m [Adopter]", "13-24m [Established]", "25-48m [Mature]", "49+m [Veteran]"]
        feat["tenure_cohort"] = pd.cut(feat["tenure"], bins=bins, labels=labels).astype(str)

    # -------------------------------------------------------------------------
    # B. Monthly Charges & Total Charges Features
    # -------------------------------------------------------------------------
    if "MonthlyCharges" in feat.columns and "TotalCharges" in feat.columns:
        expected_cumulative = feat["tenure"] * feat["MonthlyCharges"]
        feat["expected_cumulative_charges"] = np.round(expected_cumulative, 2)

        # Charges ratio: total charges vs expected (detects promotional discounts / price shifts)
        feat["charges_ratio"] = np.where(
            expected_cumulative > 0,
            np.round(feat["TotalCharges"] / expected_cumulative, 4),
            1.0
        )

        # Historical average monthly charges paid
        feat["avg_historical_monthly_charge"] = np.round(
            feat["TotalCharges"] / (feat["tenure"] + 1.0), 2
        )

        # Charge velocity: current monthly charge minus historical average
        feat["charge_velocity"] = np.round(
            feat["MonthlyCharges"] - feat["avg_historical_monthly_charge"], 2
        )

        # Monthly charge tiers
        feat["monthly_charge_tier"] = pd.cut(
            feat["MonthlyCharges"],
            bins=[-np.inf, 35.0, 70.0, 90.0, np.inf],
            labels=["Low (<$35)", "Medium ($35-$70)", "High ($70-$90)", "Premium (>$90)"]
        ).astype(str)

    # -------------------------------------------------------------------------
    # C. Contract & Billing Features
    # -------------------------------------------------------------------------
    if "Contract" in feat.columns:
        contract_map = {"Month-to-month": 1, "One year": 12, "Two year": 24}
        feat["contract_term_months"] = feat["Contract"].map(contract_map).fillna(1).astype(int)
        feat["is_month_to_month"] = (feat["Contract"] == "Month-to-month").astype(int)

    if "PaymentMethod" in feat.columns:
        feat["is_autopay_enabled"] = feat["PaymentMethod"].str.lower().str.contains("automatic").astype(int)

    if "PaperlessBilling" in feat.columns:
        feat["is_paperless_billing"] = feat["PaperlessBilling"].apply(
            lambda x: 1 if str(x).strip().lower() in ["yes", "1", "true"] else 0
        )

    if "is_paperless_billing" in feat.columns and "is_autopay_enabled" in feat.columns:
        # High friction: receives paperless invoice but has to pay manually (electronic check)
        feat["has_paperless_manual_payment_risk"] = (
            (feat["is_paperless_billing"] == 1) & (feat["is_autopay_enabled"] == 0)
        ).astype(int)

    # -------------------------------------------------------------------------
    # D. Service Usage & Bundling Features
    # -------------------------------------------------------------------------
    vas_services = [
        "OnlineSecurity", "OnlineBackup", "DeviceProtection",
        "TechSupport", "StreamingTV", "StreamingMovies"
    ]
    
    # Standardize individual service indicators (1 if 'Yes', 0 otherwise)
    for service in vas_services:
        if service in feat.columns:
            feat[f"has_{service.lower()}"] = (feat[service] == "Yes").astype(int)

    if "PhoneService" in feat.columns:
        feat["has_phone_service"] = (feat["PhoneService"] == "Yes").astype(int)

    if "MultipleLines" in feat.columns:
        feat["has_multiple_lines"] = (feat["MultipleLines"] == "Yes").astype(int)

    if "InternetService" in feat.columns:
        feat["has_internet_service"] = (feat["InternetService"] != "No").astype(int)

    # Total active value-added & telephony services
    active_service_cols = [
        f"has_{s.lower()}" for s in vas_services if f"has_{s.lower()}" in feat.columns
    ] + [c for c in ["has_phone_service", "has_multiple_lines"] if c in feat.columns]

    feat["total_services_count"] = feat[active_service_cols].sum(axis=1) if active_service_cols else 0
    feat["service_breadth_score"] = np.round(feat["total_services_count"] / max(len(active_service_cols), 1), 2)
    feat["is_single_play"] = (feat["total_services_count"] <= 1).astype(int)

    # Bundles
    if "has_streamingtv" in feat.columns and "has_streamingmovies" in feat.columns:
        feat["has_streaming_bundle"] = (
            (feat["has_streamingtv"] == 1) & (feat["has_streamingmovies"] == 1)
        ).astype(int)

    if "has_onlinesecurity" in feat.columns and "has_techsupport" in feat.columns:
        feat["has_security_bundle"] = (
            (feat["has_onlinesecurity"] == 1) & (feat["has_techsupport"] == 1)
        ).astype(int)

    # Key Churn Risk Interaction: Fiber Optic internet without Tech Support
    if "InternetService" in feat.columns and "has_techsupport" in feat.columns:
        feat["has_fiber_no_techsupport_risk"] = (
            (feat["InternetService"] == "Fiber optic") & (feat["has_techsupport"] == 0)
        ).astype(int)

    # -------------------------------------------------------------------------
    # E. Customer Segmentation & LTV Proxies
    # -------------------------------------------------------------------------
    # 1. Monetary Value Tier
    if "MonthlyCharges" in feat.columns:
        feat["value_tier"] = np.select(
            [feat["MonthlyCharges"] >= 80.0, feat["MonthlyCharges"] >= 40.0],
            ["High Value", "Medium Value"],
            default="Low Value"
        )

    # 2. Risk Profile
    cond_high_risk = (
        (feat.get("is_month_to_month", 0) == 1) &
        (
            (feat.get("tenure", 0) <= 12) |
            (feat.get("has_fiber_no_techsupport_risk", 0) == 1) |
            (feat.get("PaymentMethod", "").str.contains("Electronic check", case=False, na=False))
        )
    )
    cond_low_risk = (
        (feat.get("Contract", "").isin(["One year", "Two year"])) &
        (feat.get("is_autopay_enabled", 0) == 1)
    ) | (feat.get("tenure", 0) >= 36)

    feat["risk_profile"] = np.select(
        [cond_high_risk, cond_low_risk],
        ["High Risk", "Low Risk"],
        default="Moderate Risk"
    )

    # 3. Strategic Action Segment Matrix
    cond_urgent_save = (feat.get("MonthlyCharges", 0) >= 80.0) & (
        (feat.get("is_month_to_month", 0) == 1) | (feat.get("has_fiber_no_techsupport_risk", 0) == 1)
    )
    cond_vip_loyal = (feat.get("MonthlyCharges", 0) >= 80.0)
    cond_price_sensitive = (feat.get("MonthlyCharges", 0) < 40.0) & (feat.get("is_month_to_month", 0) == 1)

    feat["customer_strategic_segment"] = np.select(
        [cond_urgent_save, cond_vip_loyal, cond_price_sensitive],
        ["High Value - Urgent Retention", "High Value - Loyal VIP", "Low Value - Price Sensitive"],
        default="Core Mid-Market"
    )

    # 4. LTV Proxies
    if "TotalCharges" in feat.columns:
        feat["historical_ltv"] = feat["TotalCharges"]

    remaining_months = np.select(
        [
            feat.get("Contract", "") == "Two year",
            feat.get("Contract", "") == "One year",
            (feat.get("is_month_to_month", 0) == 1) & (feat.get("tenure", 0) <= 6),
            (feat.get("is_month_to_month", 0) == 1) & (feat.get("tenure", 0) <= 18)
        ],
        [24, 12, 3, 6],
        default=12
    )
    feat["estimated_remaining_months"] = remaining_months
    feat["estimated_total_ltv"] = np.round(
        feat["TotalCharges"] + (feat["MonthlyCharges"] * remaining_months), 2
    )

    logger.info("Feature engineering completed. Columns generated: %d", feat.shape[1])
    return feat


# -----------------------------------------------------------------------------
# 3. Scikit-Learn Compatible Feature Transformer Class
# -----------------------------------------------------------------------------

class CustomerFeatureEngineer(BaseEstimator, TransformerMixin):
    """
    Production-grade, leakage-free feature engineering transformer.
    Fits scalers and encoders on training data and applies them to test/serving data.
    """

    def __init__(
        self,
        numerical_features: Optional[List[str]] = None,
        categorical_features: Optional[List[str]] = None,
        scale_numeric: bool = True
    ):
        self.numerical_features = numerical_features
        self.categorical_features = categorical_features
        self.scale_numeric = scale_numeric
        self.scaler = StandardScaler() if scale_numeric else None
        self.encoder = OneHotEncoder(handle_unknown="ignore", sparse_output=False)
        self.fitted_feature_names_: List[str] = []
        self._is_fitted = False

    def _default_feature_lists(self, df: pd.DataFrame) -> Tuple[List[str], List[str]]:
        """Identify numerical and categorical columns suitable for modeling."""
        exclude_cols = [
            "customerID", "Churn", "is_churned", "churn_label",
            "historical_ltv", "estimated_total_ltv", "estimated_remaining_months"
        ]
        candidate_cols = [c for c in df.columns if c not in exclude_cols]

        numeric = [
            c for c in candidate_cols 
            if pd.api.types.is_numeric_dtype(df[c])
        ]
        categorical = [
            c for c in candidate_cols 
            if not pd.api.types.is_numeric_dtype(df[c])
        ]
        return numeric, categorical

    def fit(self, X: pd.DataFrame, y=None):
        """Fit scaler and categorical encoder on training data."""
        X_eng = engineer_features(clean_raw_data(X))

        if self.numerical_features is None or self.categorical_features is None:
            num_cols, cat_cols = self._default_feature_lists(X_eng)
            self.numerical_features = self.numerical_features or num_cols
            self.categorical_features = self.categorical_features or cat_cols

        # Fit numerical scaler
        if self.scale_numeric and self.numerical_features:
            self.scaler.fit(X_eng[self.numerical_features])

        # Fit categorical encoder
        if self.categorical_features:
            self.encoder.fit(X_eng[self.categorical_features])
            encoded_cat_names = list(self.encoder.get_feature_names_out(self.categorical_features))
        else:
            encoded_cat_names = []

        self.fitted_feature_names_ = (self.numerical_features or []) + encoded_cat_names
        self._is_fitted = True
        return self

    def transform(self, X: pd.DataFrame) -> pd.DataFrame:
        """Transform raw DataFrame into model-ready numerical feature matrix."""
        if not self._is_fitted:
            raise RuntimeError("CustomerFeatureEngineer must be fitted before transforming data.")

        X_eng = engineer_features(clean_raw_data(X))

        parts = []

        # Transform numerical features
        if self.numerical_features:
            num_data = X_eng[self.numerical_features]
            if self.scale_numeric:
                num_scaled = self.scaler.transform(num_data)
            else:
                num_scaled = num_data.values
            df_num = pd.DataFrame(num_scaled, columns=self.numerical_features, index=X.index)
            parts.append(df_num)

        # Transform categorical features
        if self.categorical_features:
            cat_data = self.encoder.transform(X_eng[self.categorical_features])
            cat_names = list(self.encoder.get_feature_names_out(self.categorical_features))
            df_cat = pd.DataFrame(cat_data, columns=cat_names, index=X.index)
            parts.append(df_cat)

        result = pd.concat(parts, axis=1) if parts else pd.DataFrame(index=X.index)
        return result

    def fit_transform(self, X: pd.DataFrame, y=None) -> pd.DataFrame:
        """Fit and transform input data."""
        return self.fit(X, y).transform(X)

    def save(self, filepath: Union[str, Path]):
        """Serialize fitted transformer to disk."""
        filepath = Path(filepath)
        filepath.parent.mkdir(parents=True, exist_ok=True)
        joblib.dump(self, filepath)
        logger.info("Saved CustomerFeatureEngineer pipeline to %s", filepath)

    @classmethod
    def load(cls, filepath: Union[str, Path]) -> "CustomerFeatureEngineer":
        """Load serialized transformer from disk."""
        return joblib.load(filepath)


# -----------------------------------------------------------------------------
# 4. Model-Ready Dataset Preparation (Split, Transform, Export)
# -----------------------------------------------------------------------------

def prepare_model_dataset(
    raw_csv_path: Union[str, Path],
    test_size: float = 0.2,
    random_state: int = 42,
    output_dir: Optional[Union[str, Path]] = None
) -> Dict[str, Union[pd.DataFrame, pd.Series, List[str]]]:
    """
    End-to-end dataset preparation pipeline.
    Reads raw CSV, splits into train/test with stratification on Churn, fits
    the feature engineering transformer on train, transforms both sets, and
    exports model-ready CSVs and metadata.

    Args:
        raw_csv_path: Path to raw input CSV.
        test_size: Fraction of samples for test set (default 0.2).
        random_state: Seed for reproducibility.
        output_dir: Optional directory to export processed data.

    Returns:
        Dictionary containing:
        - 'X_train', 'X_test': Processed feature matrices
        - 'y_churn_train', 'y_churn_test': Binary churn targets
        - 'y_ltv_train', 'y_ltv_test': LTV continuous regression targets
        - 'feature_names': List of final feature column names
        - 'engineered_full': Complete unscaled engineered dataset for EDA
    """
    raw_path = Path(raw_csv_path)
    if not raw_path.exists():
        raise FileNotFoundError(f"Raw data file not found: {raw_path}")

    raw_df = pd.read_csv(raw_path)
    cleaned = clean_raw_data(raw_df)
    engineered = engineer_features(cleaned)

    # Churn target (classification) and LTV target (regression)
    y_churn = engineered["is_churned"]
    y_ltv = engineered["TotalCharges"]

    # Stratified Train/Test Split on Churn outcome
    train_idx, test_idx = train_test_split(
        engineered.index,
        test_size=test_size,
        random_state=random_state,
        stratify=y_churn
    )

    train_raw = raw_df.loc[train_idx]
    test_raw = raw_df.loc[test_idx]

    # Fit transformer strictly on training data
    pipeline = CustomerFeatureEngineer(scale_numeric=True)
    X_train = pipeline.fit_transform(train_raw)
    X_test = pipeline.transform(test_raw)

    y_churn_train = y_churn.loc[train_idx]
    y_churn_test = y_churn.loc[test_idx]
    y_ltv_train = y_ltv.loc[train_idx]
    y_ltv_test = y_ltv.loc[test_idx]

    results = {
        "X_train": X_train,
        "X_test": X_test,
        "y_churn_train": y_churn_train,
        "y_churn_test": y_churn_test,
        "y_ltv_train": y_ltv_train,
        "y_ltv_test": y_ltv_test,
        "feature_names": pipeline.fitted_feature_names_,
        "engineered_full": engineered,
        "pipeline": pipeline
    }

    # Export to processed directory if specified
    if output_dir:
        out = Path(output_dir)
        out.mkdir(parents=True, exist_ok=True)

        X_train.to_csv(out / "X_train.csv", index=False)
        X_test.to_csv(out / "X_test.csv", index=False)
        y_churn_train.to_csv(out / "y_churn_train.csv", index=False)
        y_churn_test.to_csv(out / "y_churn_test.csv", index=False)
        y_ltv_train.to_csv(out / "y_ltv_train.csv", index=False)
        y_ltv_test.to_csv(out / "y_ltv_test.csv", index=False)
        engineered.to_csv(out / "fct_churn_ltv_features.csv", index=False)

        pipeline.save(out / "feature_pipeline.joblib")

        metadata = {
            "num_samples_total": len(raw_df),
            "num_samples_train": len(train_idx),
            "num_samples_test": len(test_idx),
            "num_features": len(pipeline.fitted_feature_names_),
            "feature_names": pipeline.fitted_feature_names_,
            "numerical_features": pipeline.numerical_features,
            "categorical_features": pipeline.categorical_features,
            "churn_rate_train": float(y_churn_train.mean()),
            "churn_rate_test": float(y_churn_test.mean())
        }
        with open(out / "feature_metadata.json", "w") as f:
            json.dump(metadata, f, indent=2)

        logger.info("Successfully exported model-ready datasets to %s", out)

    return results


if __name__ == "__main__":
    import argparse
    parser = argparse.ArgumentParser(description="Run Feature Engineering Pipeline")
    parser.add_argument("--data-path", type=str, default="data/raw/telco_customer_churn.csv")
    parser.add_argument("--output-dir", type=str, default="data/processed")
    args = parser.parse_args()

    prepare_model_dataset(
        raw_csv_path=args.data_path,
        output_dir=args.output_dir
    )
