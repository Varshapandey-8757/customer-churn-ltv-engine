"""
Customer Lifetime Value Prediction Model

Owner: Varsha

Training happens in src/models/train_ltv.py. This module only defines the
estimator so notebooks and scripts build it the same way.
"""

from sklearn.ensemble import RandomForestRegressor


def create_ltv_model():
    """Create the LTV regression model (regularised to keep the file small)."""

    return RandomForestRegressor(
        n_estimators=100,
        min_samples_leaf=5,
        random_state=42,
        n_jobs=-1,
    )
