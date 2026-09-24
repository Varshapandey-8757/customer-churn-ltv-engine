"""
Feature Engineering Package

Owner: Abhishek
Project: Customer Churn Prediction & LTV Engine
"""

from .config import (
    HIGH_VALUE_THRESHOLD,
    MEDIUM_VALUE_THRESHOLD,
    TENURE_BINS,
    TENURE_LABELS,
    CHARGE_TIER_BINS,
    CHARGE_TIER_LABELS,
    CONTRACT_TERM_MAP,
    VAS_SERVICES,
)
from .feature_engineering import (
    CustomerFeatureEngineer,
    clean_raw_data,
    engineer_features,
    prepare_model_dataset,
)

__all__ = [
    "CustomerFeatureEngineer",
    "clean_raw_data",
    "engineer_features",
    "prepare_model_dataset",
    "HIGH_VALUE_THRESHOLD",
    "MEDIUM_VALUE_THRESHOLD",
    "TENURE_BINS",
    "TENURE_LABELS",
    "CHARGE_TIER_BINS",
    "CHARGE_TIER_LABELS",
    "CONTRACT_TERM_MAP",
    "VAS_SERVICES",
]
