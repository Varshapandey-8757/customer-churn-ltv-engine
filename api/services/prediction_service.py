"""Turns raw customer records into churn and LTV predictions."""

from typing import List

import pandas as pd

from api.services.model_loader import (
    load_churn_bundle, load_ltv_bundle, load_pipeline,
)
from src.features.feature_engineering import clean_raw_data, engineer_features
from src.models.utils import drop_leaky_ltv_columns, sanitize_columns


def _to_frame(records: List[dict]) -> pd.DataFrame:
    return pd.DataFrame(records)


def _model_features(raw: pd.DataFrame) -> pd.DataFrame:
    """Raw customers -> scaled/encoded model features (same as training)."""
    features = load_pipeline().transform(raw)
    return sanitize_columns(features)


def _risk_level(probability: float, threshold: float) -> str:
    if probability >= threshold:
        return "high"
    if probability >= threshold / 2:
        return "medium"
    return "low"


def churn_probabilities(raw: pd.DataFrame):
    bundle = load_churn_bundle()
    X = _model_features(raw)[bundle["feature_names"]]
    return bundle["model"].predict_proba(X)[:, 1], bundle["threshold"]


def predict_churn(records: List[dict]) -> List[dict]:
    raw = _to_frame(records)
    probabilities, threshold = churn_probabilities(raw)

    results = []
    for record, p in zip(records, probabilities):
        results.append({
            "customerID": record.get("customerID"),
            "churn_probability": round(float(p), 4),
            "will_churn": bool(p >= threshold),
            "risk_level": _risk_level(float(p), threshold),
        })
    return results


def predict_ltv(records: List[dict]) -> List[dict]:
    """
    predicted_historical_ltv : ML model estimate of value earned to date
    projected_ltv            : business formula
        TotalCharges + MonthlyCharges x remaining_months x (1 - churn_prob)
    remaining_months comes from the project's own feature engineering rule.
    """
    raw = _to_frame(records)

    bundle = load_ltv_bundle()
    X = drop_leaky_ltv_columns(_model_features(raw))[bundle["feature_names"]]
    historical = bundle["model"].predict(X)

    probabilities, _ = churn_probabilities(raw)

    engineered = engineer_features(clean_raw_data(raw))
    remaining = engineered["estimated_remaining_months"].to_numpy()
    monthly = engineered["MonthlyCharges"].to_numpy()
    total = engineered["TotalCharges"].to_numpy()

    results = []
    for i, record in enumerate(records):
        projected = total[i] + monthly[i] * remaining[i] * (1 - probabilities[i])
        results.append({
            "customerID": record.get("customerID"),
            "predicted_historical_ltv": round(float(historical[i]), 2),
            "projected_ltv": round(float(projected), 2),
            "churn_probability": round(float(probabilities[i]), 4),
            "estimated_remaining_months": int(remaining[i]),
        })
    return results
