"""
Train the LTV model WITHOUT target leakage and save it.

Run from the project root:
    python -m src.models.train_ltv

Why this file exists
--------------------
The LTV target is TotalCharges. The old model received TotalCharges (and
columns computed from it) as inputs, so it reported R2 = 1.00. That score
was invalid. Here every leaking column is removed before training.

Note: TotalCharges is billing arithmetic (about tenure x monthly charge),
so a high R2 is still expected from tenure and MonthlyCharges. That is
legitimate, but it means this model estimates *historical* value. The
forward-looking value is computed in the API from the churn probability.
"""

import json

import joblib
import numpy as np
from sklearn.ensemble import RandomForestRegressor
from sklearn.metrics import mean_absolute_error, mean_squared_error, r2_score

from src.models.utils import (
    LEAKY_LTV_COLUMNS, LTV_MODEL_PATH, METRICS_PATH, MODELS_DIR,
    drop_leaky_ltv_columns, load_split,
)


def main() -> None:
    X_train, X_test, _, _, y_train, y_test = load_split()

    X_train = drop_leaky_ltv_columns(X_train)
    X_test = drop_leaky_ltv_columns(X_test)

    # Safety check: fail loudly if a leaking column is still present
    leaked = [c for c in LEAKY_LTV_COLUMNS if c in X_train.columns]
    assert not leaked, f"Leaky columns still present: {leaked}"

    model = RandomForestRegressor(
        n_estimators=100, min_samples_leaf=5,
        random_state=42, n_jobs=-1,
    )
    model.fit(X_train, y_train)

    pred = model.predict(X_test)
    metrics = {
        "mae": round(float(mean_absolute_error(y_test, pred)), 2),
        "rmse": round(float(np.sqrt(mean_squared_error(y_test, pred))), 2),
        "r2": round(float(r2_score(y_test, pred)), 4),
        "n_features": int(X_train.shape[1]),
        "dropped_columns": LEAKY_LTV_COLUMNS,
    }
    print("LTV test metrics:", metrics)

    LTV_MODEL_PATH.parent.mkdir(parents=True, exist_ok=True)
    joblib.dump(
        {"model": model, "feature_names": list(X_train.columns)},
        LTV_MODEL_PATH,
    )

    all_metrics = {}
    if METRICS_PATH.exists():
        all_metrics = json.loads(METRICS_PATH.read_text())
    all_metrics["ltv"] = metrics
    MODELS_DIR.mkdir(parents=True, exist_ok=True)
    METRICS_PATH.write_text(json.dumps(all_metrics, indent=2))
    print("Saved:", LTV_MODEL_PATH)


if __name__ == "__main__":
    main()
