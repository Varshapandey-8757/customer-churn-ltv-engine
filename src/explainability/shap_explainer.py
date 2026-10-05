"""
SHAP explanations for the churn model.

Works for tree models (XGBoost / Random Forest) and for Logistic Regression.
"""

from functools import lru_cache

import pandas as pd

from api.services.model_loader import load_churn_bundle
from api.services.prediction_service import _model_features, churn_probabilities


@lru_cache(maxsize=1)
def _explainer():
    import shap

    bundle = load_churn_bundle()
    model = bundle["model"]
    if hasattr(model, "get_booster") or hasattr(model, "estimators_"):
        return shap.TreeExplainer(model)
    return shap.LinearExplainer(model, bundle["background"])


def explain_customer(record: dict, top_n: int = 8) -> dict:
    """Return the features that push this customer towards / away from churn."""
    bundle = load_churn_bundle()
    raw = pd.DataFrame([record])
    X = _model_features(raw)[bundle["feature_names"]]

    values = _explainer().shap_values(X)
    if isinstance(values, list):          # older shap: one array per class
        values = values[1]
    values = values[0] if getattr(values, "ndim", 1) > 1 else values
    if getattr(values, "ndim", 1) == 2:   # (n_features, n_classes)
        values = values[:, 1]

    contributions = sorted(
        zip(bundle["feature_names"], values),
        key=lambda item: abs(item[1]),
        reverse=True,
    )[:top_n]

    probability, _ = churn_probabilities(raw)
    return {
        "customerID": record.get("customerID"),
        "churn_probability": round(float(probability[0]), 4),
        "top_factors": [
            {
                "feature": name,
                "shap_value": round(float(v), 4),
                "direction": "increases churn risk" if v > 0 else "reduces churn risk",
            }
            for name, v in contributions
        ],
    }
