"""Customer lifetime value endpoints."""

from typing import List

from fastapi import APIRouter, Body

from api.schemas import CustomerInput, LTVPrediction
from api.services import prediction_service

router = APIRouter(prefix="/ltv", tags=["ltv"])


@router.post("/predict", response_model=LTVPrediction)
def predict_one(customer: CustomerInput):
    return prediction_service.predict_ltv([customer.model_dump()])[0]


@router.post("/predict/batch", response_model=List[LTVPrediction])
def predict_batch(
    customers: List[CustomerInput] = Body(..., min_length=1, max_length=1000),
):
    return prediction_service.predict_ltv([c.model_dump() for c in customers])
