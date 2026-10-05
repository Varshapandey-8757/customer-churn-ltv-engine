
"""API tests. They are skipped automatically if models are not trained yet."""

import pytest
from fastapi.testclient import TestClient

from api.main import app
from src.models.utils import CHURN_MODEL_PATH, LTV_MODEL_PATH, PIPELINE_PATH

client = TestClient(app)

models_ready = (
    CHURN_MODEL_PATH.exists()
    and LTV_MODEL_PATH.exists()
    and PIPELINE_PATH.exists()
)
needs_models = pytest.mark.skipif(
    not models_ready, reason="Run `make train` first"
)

RISKY_CUSTOMER = {
    "customerID": "T-001", "gender": "Female", "SeniorCitizen": 0,
    "Partner": "No", "Dependents": "No", "tenure": 1,
    "PhoneService": "Yes", "MultipleLines": "No",
    "InternetService": "Fiber optic", "OnlineSecurity": "No",
    "OnlineBackup": "No", "DeviceProtection": "No", "TechSupport": "No",
    "StreamingTV": "No", "StreamingMovies": "No",
    "Contract": "Month-to-month", "PaperlessBilling": "Yes",
    "PaymentMethod": "Electronic check",
    "MonthlyCharges": 85.0, "TotalCharges": 85.0,
}

LOYAL_CUSTOMER = {
    **RISKY_CUSTOMER, "customerID": "T-002", "tenure": 60,
    "Partner": "Yes", "Dependents": "Yes", "Contract": "Two year",
    "TechSupport": "Yes", "OnlineSecurity": "Yes",
    "PaymentMethod": "Bank transfer (automatic)",
    "PaperlessBilling": "No", "MonthlyCharges": 60.0, "TotalCharges": 3600.0,
}


def test_health():
    response = client.get("/health")
    assert response.status_code == 200
    assert response.json() == {"status": "ok"}


def test_invalid_input_returns_422():
    response = client.post("/churn/predict", json={"gender": "Female"})
    assert response.status_code == 422


def test_unknown_category_returns_422():
    bad = {**RISKY_CUSTOMER, "Contract": "Weekly"}
    assert client.post("/churn/predict", json=bad).status_code == 422
    assert client.post("/ltv/predict", json=bad).status_code == 422


def test_out_of_range_tenure_returns_422():
    bad = {**RISKY_CUSTOMER, "tenure": 500}
    assert client.post("/churn/predict", json=bad).status_code == 422


def test_empty_batch_returns_422():
    assert client.post("/churn/predict/batch", json=[]).status_code == 422
    assert client.post("/ltv/predict/batch", json=[]).status_code == 422


@needs_models
def test_churn_predict_fields():
    body = client.post("/churn/predict", json=RISKY_CUSTOMER).json()
    assert 0.0 <= body["churn_probability"] <= 1.0
    assert body["risk_level"] in {"low", "medium", "high"}


@needs_models
def test_risky_customer_scores_higher_than_loyal():
    risky = client.post("/churn/predict", json=RISKY_CUSTOMER).json()
    loyal = client.post("/churn/predict", json=LOYAL_CUSTOMER).json()
    assert risky["churn_probability"] > loyal["churn_probability"]


@needs_models
def test_churn_batch():
    response = client.post(
        "/churn/predict/batch", json=[RISKY_CUSTOMER, LOYAL_CUSTOMER]
    )
    assert response.status_code == 200
    assert len(response.json()) == 2


@needs_models
def test_ltv_predict():
    body = client.post("/ltv/predict", json=LOYAL_CUSTOMER).json()
    assert body["predicted_historical_ltv"] > 0
    assert body["projected_ltv"] >= LOYAL_CUSTOMER["TotalCharges"]


@needs_models
def test_explain_returns_factors():
    body = client.post("/churn/explain", json=RISKY_CUSTOMER).json()
    assert len(body["top_factors"]) > 0
    assert "shap_value" in body["top_factors"][0]
