"""
Customer Lifetime Value Prediction Model

Owner: Varsha
"""

from sklearn.ensemble import RandomForestRegressor


def create_ltv_model():
    """Create the baseline LTV regression model."""

    model = RandomForestRegressor(
        n_estimators=200,
        random_state=42
    )

    return model