"""
Churn Prediction Model

Owner: Varsha
Purpose:
Train and evaluate classification models for customer churn prediction.
"""

import pandas as pd

from sklearn.linear_model import LogisticRegression
from sklearn.ensemble import RandomForestClassifier
from xgboost import XGBClassifier


def create_models():
    """Create the classification models used for churn prediction."""

    models = {
        "logistic_regression": LogisticRegression(
            max_iter=1000
        ),
        "random_forest": RandomForestClassifier(
            n_estimators=200,
            random_state=42
        ),
        "xgboost": XGBClassifier(
            random_state=42,
            eval_metric="logloss"
        )
    }

    return models