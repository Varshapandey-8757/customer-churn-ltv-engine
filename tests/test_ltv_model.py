"""LTV model tests, including a target-leakage guard."""

import joblib
import numpy as np
import pytest
from sklearn.metrics import mean_absolute_error, r2_score

from src.models.utils import (
    LEAKY_LTV_COLUMNS, LTV_MODEL_PATH, drop_leaky_ltv_columns, load_split,
)

pytestmark = pytest.mark.skipif(
    not LTV_MODEL_PATH.exists(), reason="Run `make train` first"
)


@pytest.fixture(scope="module")
def bundle():
    return joblib.load(LTV_MODEL_PATH)


def test_model_does_not_use_leaky_columns(bundle):
    leaked = [c for c in LEAKY_LTV_COLUMNS if c in bundle["feature_names"]]
    assert leaked == [], f"Target leakage: {leaked}"


def test_predictions_are_sane(bundle):
    _, X_test, _, _, _, y_test = load_split()
    X_test = drop_leaky_ltv_columns(X_test)[bundle["feature_names"]]
    pred = bundle["model"].predict(X_test)

    assert len(pred) == len(y_test)
    assert not np.isnan(pred).any()
    assert (pred >= 0).all()
    assert r2_score(y_test, pred) > 0.5
    assert mean_absolute_error(y_test, pred) < y_test.mean()

