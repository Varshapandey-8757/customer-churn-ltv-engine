"""Churn model tests on the held-out engineered test set."""

import joblib
import pytest
from sklearn.metrics import recall_score, roc_auc_score

from src.models.utils import CHURN_MODEL_PATH, load_split

pytestmark = pytest.mark.skipif(
    not CHURN_MODEL_PATH.exists(), reason="Run `make train` first"
)


@pytest.fixture(scope="module")
def bundle():
    return joblib.load(CHURN_MODEL_PATH)


def test_bundle_has_required_keys(bundle):
    for key in ("model", "feature_names", "threshold"):
        assert key in bundle


def test_probabilities_are_valid(bundle):
    _, X_test, _, y_test, _, _ = load_split()
    proba = bundle["model"].predict_proba(X_test[bundle["feature_names"]])[:, 1]

    assert len(proba) == len(y_test)
    assert ((proba >= 0) & (proba <= 1)).all()


def test_model_quality(bundle):
    _, X_test, _, y_test, _, _ = load_split()
    proba = bundle["model"].predict_proba(X_test[bundle["feature_names"]])[:, 1]
    pred = (proba >= bundle["threshold"]).astype(int)

    assert roc_auc_score(y_test, proba) > 0.80
    assert recall_score(y_test, pred) > 0.65
