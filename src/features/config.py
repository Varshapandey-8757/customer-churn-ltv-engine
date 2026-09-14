"""
Feature Engineering Configuration Constants

Owner: Abhishek
Project: Customer Churn Prediction & LTV Engine
Purpose:
Centralizes thresholds, service lists, bins, and cohort definitions 
to ensure consistent parameters across Python and SQL pipelines.
"""

from typing import Dict, List

# Value Tier Thresholds (in USD / month)
HIGH_VALUE_THRESHOLD = 80.0
MEDIUM_VALUE_THRESHOLD = 40.0

# Tenure Cohort Definitions (in months)
TENURE_BINS: List[int] = [-1, 6, 12, 24, 48, 120]
TENURE_LABELS: List[str] = [
    "0-6m [New]",
    "7-12m [Adopter]",
    "13-24m [Established]",
    "25-48m [Mature]",
    "49+m [Veteran]"
]

# Monthly Charge Tier Bins (in USD)
CHARGE_TIER_BINS: List[float] = [-float("inf"), 35.0, 70.0, 90.0, float("inf")]
CHARGE_TIER_LABELS: List[str] = [
    "Low (<$35)",
    "Medium ($35-$70)",
    "High ($70-$90)",
    "Premium (>$90)"
]

# Contract Term Mapping to Months
CONTRACT_TERM_MAP: Dict[str, int] = {
    "Month-to-month": 1,
    "One year": 12,
    "Two year": 24
}

# Digital Value-Added Services (VAS)
VAS_SERVICES: List[str] = [
    "OnlineSecurity",
    "OnlineBackup",
    "DeviceProtection",
    "TechSupport",
    "StreamingTV",
    "StreamingMovies"
]

# High-Risk First Window Threshold (months)
NEW_CUSTOMER_HAZARD_MONTHS = 6
