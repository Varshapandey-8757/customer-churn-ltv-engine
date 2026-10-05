"""Churn prediction and explanation endpoints."""

from typing import List

from fastapi import APIRouter

from api.schemas import ChurnPrediction, CustomerInput, ExplanationResponse
from api.services import prediction_service

router = APIRouter(prefix="/churn", tags=["churn"])


@router.post("/predict", response_model=ChurnPrediction)
def predict_one(customer: CustomerInput):
    return prediction_service.predict_churn([customer.model_dump()])[0]


@router.post("/predict/batch", response_model=List[ChurnPrediction])
def predict_batch(customers: List[CustomerInput]):
    return prediction_service.predict_churn([c.model_dump() for c in customers])


@router.post("/explain", response_model=ExplanationResponse)
def explain(customer: CustomerInput):
    # Imported here so the API still starts if SHAP is not installed
    from src.explainability.shap_explainer import explain_customer

    return explain_customer(customer.model_dump())
