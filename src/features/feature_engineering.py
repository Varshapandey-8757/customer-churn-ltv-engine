"""
Feature Engineering Pipeline

Owner: Abhishek
Project: Customer Churn Prediction & LTV Engine

Purpose:
- Clean raw Telco Customer Churn data
- Create business/domain features
- Create customer segmentation features
- Prepare leakage-free model features
- Split data into train/test
- Save model-ready datasets
- Save reusable feature engineering pipeline
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


# =============================================================================
# LOGGING
# =============================================================================

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(levelname)s - %(message)s"
)

logger = logging.getLogger(__name__)


# =============================================================================
# 1. RAW DATA CLEANING
# =============================================================================

def clean_raw_data(df: pd.DataFrame) -> pd.DataFrame:
    """
    Clean and normalize raw Telco Customer Churn data.
    """

    cleaned = df.copy()

    # -------------------------------------------------------------------------
    # Standardize column names
    # -------------------------------------------------------------------------

    cleaned.columns = [str(column).strip() for column in cleaned.columns]

    # -------------------------------------------------------------------------
    # Clean TotalCharges
    # -------------------------------------------------------------------------

    if "TotalCharges" in cleaned.columns:

        cleaned["TotalCharges"] = (
            cleaned["TotalCharges"]
            .astype(str)
            .str.strip()
            .replace("", np.nan)
        )

        cleaned["TotalCharges"] = pd.to_numeric(
            cleaned["TotalCharges"],
            errors="coerce"
        )

    # -------------------------------------------------------------------------
    # Clean tenure
    # -------------------------------------------------------------------------

    if "tenure" in cleaned.columns:

        cleaned["tenure"] = pd.to_numeric(
            cleaned["tenure"],
            errors="coerce"
        ).fillna(0)

        cleaned["tenure"] = cleaned["tenure"].astype(int)

    # -------------------------------------------------------------------------
    # Clean MonthlyCharges
    # -------------------------------------------------------------------------

    if "MonthlyCharges" in cleaned.columns:

        cleaned["MonthlyCharges"] = pd.to_numeric(
            cleaned["MonthlyCharges"],
            errors="coerce"
        )

        cleaned["MonthlyCharges"] = (
            cleaned["MonthlyCharges"]
            .fillna(cleaned["MonthlyCharges"].median())
        )

    # -------------------------------------------------------------------------
    # TotalCharges for new customers
    # -------------------------------------------------------------------------

    if "tenure" in cleaned.columns and "TotalCharges" in cleaned.columns:

        zero_tenure = cleaned["tenure"] == 0

        cleaned.loc[zero_tenure, "TotalCharges"] = 0.0

        # For any remaining missing TotalCharges,
        # use MonthlyCharges * tenure.
        missing_total = cleaned["TotalCharges"].isna()

        cleaned.loc[missing_total, "TotalCharges"] = (
            cleaned.loc[missing_total, "MonthlyCharges"]
            * cleaned.loc[missing_total, "tenure"]
        )

        cleaned["TotalCharges"] = cleaned["TotalCharges"].fillna(0.0)

    # -------------------------------------------------------------------------
    # SeniorCitizen
    # -------------------------------------------------------------------------

    if "SeniorCitizen" in cleaned.columns:

        cleaned["SeniorCitizen"] = pd.to_numeric(
            cleaned["SeniorCitizen"],
            errors="coerce"
        ).fillna(0).astype(int)

    # -------------------------------------------------------------------------
    # Create binary churn target
    # -------------------------------------------------------------------------

    if "Churn" in cleaned.columns:

        cleaned["is_churned"] = (
            cleaned["Churn"]
            .astype(str)
            .str.strip()
            .str.lower()
            .isin(["yes", "1", "true"])
            .astype(int)
        )

    logger.info(
        "Raw data cleaned successfully. Shape: %s",
        cleaned.shape
    )

    return cleaned


# =============================================================================
# 2. DOMAIN FEATURE ENGINEERING
# =============================================================================

def engineer_features(df: pd.DataFrame) -> pd.DataFrame:
    """
    Generate business/domain features for churn and LTV analysis.
    """

    feat = df.copy()

    # =========================================================================
    # A. TENURE FEATURES
    # =========================================================================

    if "tenure" in feat.columns:

        feat["tenure_months"] = feat["tenure"]

        feat["tenure_years"] = np.round(
            feat["tenure"] / 12.0,
            2
        )

        feat["log_tenure"] = np.round(
            np.log1p(feat["tenure"]),
            4
        )

        feat["is_new_customer"] = (
            feat["tenure"] <= 6
        ).astype(int)

        bins = [-1, 6, 12, 24, 48, np.inf]

        labels = [
            "0-6m [New]",
            "7-12m [Adopter]",
            "13-24m [Established]",
            "25-48m [Mature]",
            "49+m [Veteran]"
        ]

        feat["tenure_cohort"] = pd.cut(
            feat["tenure"],
            bins=bins,
            labels=labels
        ).astype(str)

    # =========================================================================
    # B. CHARGE FEATURES
    # =========================================================================

    if (
        "tenure" in feat.columns
        and "MonthlyCharges" in feat.columns
        and "TotalCharges" in feat.columns
    ):

        expected_cumulative = (
            feat["tenure"]
            * feat["MonthlyCharges"]
        )

        feat["expected_cumulative_charges"] = np.round(
            expected_cumulative,
            2
        )

        feat["charges_ratio"] = np.where(
            expected_cumulative > 0,
            feat["TotalCharges"] / expected_cumulative,
            1.0
        )

        feat["charges_ratio"] = np.round(
            feat["charges_ratio"],
            4
        )

        feat["avg_historical_monthly_charge"] = np.round(
            feat["TotalCharges"]
            / (feat["tenure"] + 1.0),
            2
        )

        feat["charge_velocity"] = np.round(
            feat["MonthlyCharges"]
            - feat["avg_historical_monthly_charge"],
            2
        )

        feat["monthly_charge_tier"] = pd.cut(
            feat["MonthlyCharges"],
            bins=[
                -np.inf,
                35,
                70,
                90,
                np.inf
            ],
            labels=[
                "Low (<$35)",
                "Medium ($35-$70)",
                "High ($70-$90)",
                "Premium (>$90)"
            ]
        ).astype(str)

    # =========================================================================
    # C. CONTRACT FEATURES
    # =========================================================================

    if "Contract" in feat.columns:

        contract_map = {
            "Month-to-month": 1,
            "One year": 12,
            "Two year": 24
        }

        feat["contract_term_months"] = (
            feat["Contract"]
            .map(contract_map)
            .fillna(1)
            .astype(int)
        )

        feat["is_month_to_month"] = (
            feat["Contract"] == "Month-to-month"
        ).astype(int)

    # =========================================================================
    # D. PAYMENT FEATURES
    # =========================================================================

    if "PaymentMethod" in feat.columns:

        payment_method = (
            feat["PaymentMethod"]
            .fillna("")
            .astype(str)
        )

        feat["is_autopay_enabled"] = (
            payment_method
            .str.lower()
            .str.contains("automatic")
            .astype(int)
        )

        feat["is_electronic_check"] = (
            payment_method
            .str.lower()
            .str.contains("electronic check")
            .astype(int)
        )

    # =========================================================================
    # E. PAPERLESS BILLING
    # =========================================================================

    if "PaperlessBilling" in feat.columns:

        feat["is_paperless_billing"] = (
            feat["PaperlessBilling"]
            .astype(str)
            .str.strip()
            .str.lower()
            .isin(["yes", "1", "true"])
            .astype(int)
        )

    # =========================================================================
    # F. PAYMENT FRICTION
    # =========================================================================

    if (
        "is_paperless_billing" in feat.columns
        and "is_autopay_enabled" in feat.columns
    ):

        feat["has_paperless_manual_payment_risk"] = (
            (
                feat["is_paperless_billing"] == 1
            )
            &
            (
                feat["is_autopay_enabled"] == 0
            )
        ).astype(int)

    # =========================================================================
    # G. SERVICE FEATURES
    # =========================================================================

    vas_services = [
        "OnlineSecurity",
        "OnlineBackup",
        "DeviceProtection",
        "TechSupport",
        "StreamingTV",
        "StreamingMovies"
    ]

    for service in vas_services:

        if service in feat.columns:

            feat[f"has_{service.lower()}"] = (
                feat[service]
                .astype(str)
                .str.strip()
                .eq("Yes")
                .astype(int)
            )

    # =========================================================================
    # H. PHONE SERVICE
    # =========================================================================

    if "PhoneService" in feat.columns:

        feat["has_phone_service"] = (
            feat["PhoneService"]
            .astype(str)
            .str.strip()
            .eq("Yes")
            .astype(int)
        )

    # =========================================================================
    # I. MULTIPLE LINES
    # =========================================================================

    if "MultipleLines" in feat.columns:

        feat["has_multiple_lines"] = (
            feat["MultipleLines"]
            .astype(str)
            .str.strip()
            .eq("Yes")
            .astype(int)
        )

    # =========================================================================
    # J. INTERNET SERVICE
    # =========================================================================

    if "InternetService" in feat.columns:

        feat["has_internet_service"] = (
            feat["InternetService"]
            .astype(str)
            .str.strip()
            .ne("No")
            .astype(int)
        )

    # =========================================================================
    # K. TOTAL SERVICE COUNT
    # =========================================================================

    active_service_cols = [
        f"has_{service.lower()}"
        for service in vas_services
        if f"has_{service.lower()}" in feat.columns
    ]

    active_service_cols += [
        column
        for column in [
            "has_phone_service",
            "has_multiple_lines"
        ]
        if column in feat.columns
    ]

    if active_service_cols:

        feat["total_services_count"] = (
            feat[active_service_cols]
            .sum(axis=1)
        )

        feat["service_breadth_score"] = np.round(
            feat["total_services_count"]
            / len(active_service_cols),
            2
        )

    else:

        feat["total_services_count"] = 0
        feat["service_breadth_score"] = 0.0

    feat["is_single_play"] = (
        feat["total_services_count"] <= 1
    ).astype(int)

    # =========================================================================
    # L. STREAMING BUNDLE
    # =========================================================================

    if (
        "has_streamingtv" in feat.columns
        and "has_streamingmovies" in feat.columns
    ):

        feat["has_streaming_bundle"] = (
            (
                feat["has_streamingtv"] == 1
            )
            &
            (
                feat["has_streamingmovies"] == 1
            )
        ).astype(int)

    # =========================================================================
    # M. SECURITY BUNDLE
    # =========================================================================

    if (
        "has_onlinesecurity" in feat.columns
        and "has_techsupport" in feat.columns
    ):

        feat["has_security_bundle"] = (
            (
                feat["has_onlinesecurity"] == 1
            )
            &
            (
                feat["has_techsupport"] == 1
            )
        ).astype(int)

    # =========================================================================
    # N. FIBER + NO TECH SUPPORT RISK
    # =========================================================================

    if (
        "InternetService" in feat.columns
        and "has_techsupport" in feat.columns
    ):

        feat["has_fiber_no_techsupport_risk"] = (
            (
                feat["InternetService"]
                .astype(str)
                .eq("Fiber optic")
            )
            &
            (
                feat["has_techsupport"] == 0
            )
        ).astype(int)

    # =========================================================================
    # O. VALUE TIER
    # =========================================================================

    if "MonthlyCharges" in feat.columns:

        feat["value_tier"] = np.select(
            [
                feat["MonthlyCharges"] >= 80,
                feat["MonthlyCharges"] >= 40
            ],
            [
                "High Value",
                "Medium Value"
            ],
            default="Low Value"
        )

    # =========================================================================
    # P. RISK PROFILE
    # =========================================================================

    is_month_to_month = (
        feat["is_month_to_month"]
        if "is_month_to_month" in feat.columns
        else pd.Series(0, index=feat.index)
    )

    tenure = (
        feat["tenure"]
        if "tenure" in feat.columns
        else pd.Series(0, index=feat.index)
    )

    fiber_risk = (
        feat["has_fiber_no_techsupport_risk"]
        if "has_fiber_no_techsupport_risk" in feat.columns
        else pd.Series(0, index=feat.index)
    )

    electronic_check = (
        feat["is_electronic_check"]
        if "is_electronic_check" in feat.columns
        else pd.Series(0, index=feat.index)
    )

    autopay = (
        feat["is_autopay_enabled"]
        if "is_autopay_enabled" in feat.columns
        else pd.Series(0, index=feat.index)
    )

    contract = (
        feat["Contract"]
        if "Contract" in feat.columns
        else pd.Series("", index=feat.index)
    )

    cond_high_risk = (
        (is_month_to_month == 1)
        &
        (
            (tenure <= 12)
            | (fiber_risk == 1)
            | (electronic_check == 1)
        )
    )

    cond_low_risk = (
        (
            contract.isin(
                ["One year", "Two year"]
            )
        )
        &
        (autopay == 1)
    ) | (tenure >= 36)

    feat["risk_profile"] = np.select(
        [
            cond_high_risk,
            cond_low_risk
        ],
        [
            "High Risk",
            "Low Risk"
        ],
        default="Moderate Risk"
    )

    # =========================================================================
    # Q. STRATEGIC CUSTOMER SEGMENT
    # =========================================================================

    monthly_charges = (
        feat["MonthlyCharges"]
        if "MonthlyCharges" in feat.columns
        else pd.Series(0, index=feat.index)
    )

    cond_urgent_save = (
        (monthly_charges >= 80)
        &
        (
            (is_month_to_month == 1)
            | (fiber_risk == 1)
        )
    )

    cond_vip_loyal = (
        monthly_charges >= 80
    )

    cond_price_sensitive = (
        (monthly_charges < 40)
        &
        (is_month_to_month == 1)
    )

    feat["customer_strategic_segment"] = np.select(
        [
            cond_urgent_save,
            cond_vip_loyal,
            cond_price_sensitive
        ],
        [
            "High Value - Urgent Retention",
            "High Value - Loyal VIP",
            "Low Value - Price Sensitive"
        ],
        default="Core Mid-Market"
    )

    # =========================================================================
    # R. LTV PROXY FEATURES
    # =========================================================================

    if "TotalCharges" in feat.columns:

        feat["historical_ltv"] = feat["TotalCharges"]

    # Estimated remaining months
    if "Contract" in feat.columns:

        remaining_months = np.select(
            [
                feat["Contract"] == "Two year",

                feat["Contract"] == "One year",

                (
                    (is_month_to_month == 1)
                    &
                    (tenure <= 6)
                ),

                (
                    (is_month_to_month == 1)
                    &
                    (tenure <= 18)
                )
            ],
            [
                24,
                12,
                3,
                6
            ],
            default=12
        )

    else:

        remaining_months = np.full(
            len(feat),
            12
        )

    feat["estimated_remaining_months"] = (
        remaining_months
    )

    if (
        "TotalCharges" in feat.columns
        and "MonthlyCharges" in feat.columns
    ):

        feat["estimated_total_ltv"] = np.round(
            feat["TotalCharges"]
            + (
                feat["MonthlyCharges"]
                * feat["estimated_remaining_months"]
            ),
            2
        )

    logger.info(
        "Feature engineering completed. Columns generated: %d",
        feat.shape[1]
    )

    return feat


# =============================================================================
# 3. CUSTOMER FEATURE ENGINEER
# =============================================================================

class CustomerFeatureEngineer(
    BaseEstimator,
    TransformerMixin
):
    """
    Scikit-learn compatible feature engineering transformer.

    IMPORTANT:
    This class is defined inside the importable module
    src.features.feature_engineering.

    Therefore joblib can correctly save and reload it.
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

        self.scaler = (
            StandardScaler()
            if scale_numeric
            else None
        )

        # Compatible with current scikit-learn
        self.encoder = OneHotEncoder(
            handle_unknown="ignore",
            sparse_output=False
        )

        self.fitted_feature_names_: List[str] = []

        self._is_fitted = False

    # -------------------------------------------------------------------------
    # Feature lists
    # -------------------------------------------------------------------------

    def _default_feature_lists(
        self,
        df: pd.DataFrame
    ) -> Tuple[List[str], List[str]]:

        # Columns that must NOT become model input features.
        exclude_cols = [
            "customerID",
            "customer_id",
            "Churn",
            "is_churned",

            # LTV target / future-derived features
            "historical_ltv",
            "estimated_total_ltv",
            "estimated_remaining_months"
        ]

        candidate_cols = [
            column
            for column in df.columns
            if column not in exclude_cols
        ]

        numerical = []

        categorical = []

        for column in candidate_cols:

            if pd.api.types.is_numeric_dtype(
                df[column]
            ):
                numerical.append(column)

            else:
                categorical.append(column)

        return numerical, categorical

    # -------------------------------------------------------------------------
    # FIT
    # -------------------------------------------------------------------------

    def fit(
        self,
        X: pd.DataFrame,
        y=None
    ):

        logger.info(
            "Fitting CustomerFeatureEngineer..."
        )

        X_clean = clean_raw_data(X)

        X_eng = engineer_features(
            X_clean
        )

        # ---------------------------------------------------------------------
        # Automatically identify features
        # ---------------------------------------------------------------------

        if (
            self.numerical_features is None
            or self.categorical_features is None
        ):

            num_cols, cat_cols = (
                self._default_feature_lists(
                    X_eng
                )
            )

            if self.numerical_features is None:
                self.numerical_features = num_cols

            if self.categorical_features is None:
                self.categorical_features = cat_cols

        # ---------------------------------------------------------------------
        # Numeric preprocessing
        # ---------------------------------------------------------------------

        if (
            self.scale_numeric
            and self.numerical_features
        ):

            numeric_data = (
                X_eng[
                    self.numerical_features
                ]
                .apply(
                    pd.to_numeric,
                    errors="coerce"
                )
                .fillna(0)
            )

            self.scaler.fit(
                numeric_data
            )

        # ---------------------------------------------------------------------
        # Categorical preprocessing
        # ---------------------------------------------------------------------

        if self.categorical_features:

            categorical_data = (
                X_eng[
                    self.categorical_features
                ]
                .fillna("Unknown")
                .astype(str)
            )

            self.encoder.fit(
                categorical_data
            )

            encoded_cat_names = list(
                self.encoder.get_feature_names_out(
                    self.categorical_features
                )
            )

        else:

            encoded_cat_names = []

        # ---------------------------------------------------------------------
        # Final feature names
        # ---------------------------------------------------------------------

        self.fitted_feature_names_ = (
            (self.numerical_features or [])
            + encoded_cat_names
        )

        self._is_fitted = True

        logger.info(
            "Feature engineering transformer fitted successfully."
        )

        logger.info(
            "Numerical features: %d",
            len(self.numerical_features or [])
        )

        logger.info(
            "Categorical features: %d",
            len(self.categorical_features or [])
        )

        logger.info(
            "Final model features: %d",
            len(self.fitted_feature_names_)
        )

        return self

    # -------------------------------------------------------------------------
    # TRANSFORM
    # -------------------------------------------------------------------------

    def transform(
        self,
        X: pd.DataFrame
    ) -> pd.DataFrame:

        if not self._is_fitted:

            raise RuntimeError(
                "CustomerFeatureEngineer must be fitted "
                "before calling transform()."
            )

        X_clean = clean_raw_data(X)

        X_eng = engineer_features(
            X_clean
        )

        parts = []

        # ---------------------------------------------------------------------
        # Numeric transformation
        # ---------------------------------------------------------------------

        if self.numerical_features:

            numeric_data = (
                X_eng[
                    self.numerical_features
                ]
                .apply(
                    pd.to_numeric,
                    errors="coerce"
                )
                .fillna(0)
            )

            if self.scale_numeric:

                numeric_array = (
                    self.scaler.transform(
                        numeric_data
                    )
                )

            else:

                numeric_array = (
                    numeric_data.values
                )

            numeric_df = pd.DataFrame(
                numeric_array,
                columns=self.numerical_features,
                index=X.index
            )

            parts.append(
                numeric_df
            )

        # ---------------------------------------------------------------------
        # Categorical transformation
        # ---------------------------------------------------------------------

        if self.categorical_features:

            categorical_data = (
                X_eng[
                    self.categorical_features
                ]
                .fillna("Unknown")
                .astype(str)
            )

            categorical_array = (
                self.encoder.transform(
                    categorical_data
                )
            )

            categorical_names = list(
                self.encoder.get_feature_names_out(
                    self.categorical_features
                )
            )

            categorical_df = pd.DataFrame(
                categorical_array,
                columns=categorical_names,
                index=X.index
            )

            parts.append(
                categorical_df
            )

        # ---------------------------------------------------------------------
        # Combine features
        # ---------------------------------------------------------------------

        if parts:

            result = pd.concat(
                parts,
                axis=1
            )

        else:

            result = pd.DataFrame(
                index=X.index
            )

        return result

    # -------------------------------------------------------------------------
    # FIT TRANSFORM
    # -------------------------------------------------------------------------

    def fit_transform(
        self,
        X: pd.DataFrame,
        y=None,
        **fit_params
    ):

        return (
            self.fit(X, y)
            .transform(X)
        )

    # -------------------------------------------------------------------------
    # SAVE
    # -------------------------------------------------------------------------

    def save(
        self,
        filepath: Union[str, Path]
    ):

        filepath = Path(filepath)

        filepath.parent.mkdir(
            parents=True,
            exist_ok=True
        )

        joblib.dump(
            self,
            filepath
        )

        logger.info(
            "Saved feature pipeline to: %s",
            filepath
        )

    # -------------------------------------------------------------------------
    # LOAD
    # -------------------------------------------------------------------------

    @classmethod
    def load(
        cls,
        filepath: Union[str, Path]
    ):

        return joblib.load(
            filepath
        )


# =============================================================================
# 4. MODEL DATASET PREPARATION
# =============================================================================

def prepare_model_dataset(
    raw_csv_path: Union[str, Path],
    test_size: float = 0.2,
    random_state: int = 42,
    output_dir: Optional[Union[str, Path]] = None
) -> Dict[str, Union[
    pd.DataFrame,
    pd.Series,
    List[str]
]]:

    """
    Prepare complete model-ready dataset.

    Steps:
    1. Read raw CSV
    2. Clean data
    3. Engineer features
    4. Create churn target
    5. Create LTV target
    6. Train/test split
    7. Fit transformer only on training data
    8. Transform train/test data
    9. Save processed files
    10. Save feature pipeline
    """

    # =========================================================================
    # 1. Resolve paths
    # =========================================================================

    raw_path = Path(raw_csv_path)

    if not raw_path.exists():

        raise FileNotFoundError(
            f"Raw data file not found: {raw_path}"
        )

    # =========================================================================
    # 2. Read raw data
    # =========================================================================

    logger.info(
        "Reading raw dataset: %s",
        raw_path
    )

    raw_df = pd.read_csv(
        raw_path
    )

    logger.info(
        "Raw dataset shape: %s",
        raw_df.shape
    )

    # =========================================================================
    # 3. Clean data
    # =========================================================================

    cleaned = clean_raw_data(
        raw_df
    )

    # =========================================================================
    # 4. Engineer features
    # =========================================================================

    engineered = engineer_features(
        cleaned
    )

    # =========================================================================
    # 5. Targets
    # =========================================================================

    if "is_churned" not in engineered.columns:

        raise ValueError(
            "Churn target could not be created."
        )

    if "TotalCharges" not in engineered.columns:

        raise ValueError(
            "TotalCharges column is required "
            "for LTV target."
        )

    y_churn = (
        engineered["is_churned"]
        .astype(int)
    )

    y_ltv = (
        engineered["TotalCharges"]
        .astype(float)
    )

    # =========================================================================
    # 6. Train/Test Split
    # =========================================================================

    train_idx, test_idx = train_test_split(
        engineered.index,
        test_size=test_size,
        random_state=random_state,
        stratify=y_churn
    )

    train_raw = raw_df.loc[
        train_idx
    ].copy()

    test_raw = raw_df.loc[
        test_idx
    ].copy()

    logger.info(
        "Training rows: %d",
        len(train_raw)
    )

    logger.info(
        "Testing rows: %d",
        len(test_raw)
    )

    # =========================================================================
    # 7. Create transformer
    # =========================================================================

    pipeline = CustomerFeatureEngineer(
        scale_numeric=True
    )

    # =========================================================================
    # 8. Fit ONLY on training data
    # =========================================================================

    X_train = pipeline.fit_transform(
        train_raw
    )

    # =========================================================================
    # 9. Transform test data
    # =========================================================================

    X_test = pipeline.transform(
        test_raw
    )

    # =========================================================================
    # 10. Targets
    # =========================================================================

    y_churn_train = (
        y_churn.loc[train_idx]
        .copy()
    )

    y_churn_test = (
        y_churn.loc[test_idx]
        .copy()
    )

    y_ltv_train = (
        y_ltv.loc[train_idx]
        .copy()
    )

    y_ltv_test = (
        y_ltv.loc[test_idx]
        .copy()
    )

    # =========================================================================
    # 11. Results dictionary
    # =========================================================================

    results = {

        "X_train": X_train,

        "X_test": X_test,

        "y_churn_train": y_churn_train,

        "y_churn_test": y_churn_test,

        "y_ltv_train": y_ltv_train,

        "y_ltv_test": y_ltv_test,

        "feature_names":
            pipeline.fitted_feature_names_,

        "engineered_full":
            engineered,

        "pipeline":
            pipeline
    }

    # =========================================================================
    # 12. Export processed data
    # =========================================================================

    if output_dir:

        output_path = Path(
            output_dir
        )

        output_path.mkdir(
            parents=True,
            exist_ok=True
        )

        # ---------------------------------------------------------------------
        # Model features
        # ---------------------------------------------------------------------

        X_train.to_csv(
            output_path / "X_train.csv",
            index=False
        )

        X_test.to_csv(
            output_path / "X_test.csv",
            index=False
        )

        # ---------------------------------------------------------------------
        # Churn target
        # ---------------------------------------------------------------------

        y_churn_train.to_csv(
            output_path / "y_churn_train.csv",
            index=False
        )

        y_churn_test.to_csv(
            output_path / "y_churn_test.csv",
            index=False
        )

        # ---------------------------------------------------------------------
        # LTV target
        # ---------------------------------------------------------------------

        y_ltv_train.to_csv(
            output_path / "y_ltv_train.csv",
            index=False
        )

        y_ltv_test.to_csv(
            output_path / "y_ltv_test.csv",
            index=False
        )

        # ---------------------------------------------------------------------
        # Full engineered dataset
        # ---------------------------------------------------------------------

        engineered.to_csv(
            output_path / "fct_churn_ltv_features.csv",
            index=False
        )

        # ---------------------------------------------------------------------
        # IMPORTANT:
        # Save transformer from IMPORTABLE MODULE
        # ---------------------------------------------------------------------

        pipeline.save(
            output_path / "feature_pipeline.joblib"
        )

        # ---------------------------------------------------------------------
        # Metadata
        # ---------------------------------------------------------------------

        metadata = {

            "num_samples_total":
                int(len(raw_df)),

            "num_samples_train":
                int(len(train_idx)),

            "num_samples_test":
                int(len(test_idx)),

            "num_features":
                int(len(
                    pipeline.fitted_feature_names_
                )),

            "feature_names":
                pipeline.fitted_feature_names_,

            "numerical_features":
                pipeline.numerical_features,

            "categorical_features":
                pipeline.categorical_features,

            "churn_rate_train":
                float(
                    y_churn_train.mean()
                ),

            "churn_rate_test":
                float(
                    y_churn_test.mean()
                )
        }

        with open(
            output_path / "feature_metadata.json",
            "w",
            encoding="utf-8"
        ) as file:

            json.dump(
                metadata,
                file,
                indent=2
            )

        logger.info(
            "Processed data exported to: %s",
            output_path
        )

    return results






