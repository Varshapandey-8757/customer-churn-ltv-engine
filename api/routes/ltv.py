"""Customer lifetime value endpoints."""

from typing import List

from fastapi import APIRouter, HTTPException

from api.schemas import CustomerInput, LTVPrediction
from api.services import prediction_service

router = APIRouter(prefix="/ltv", tags=["ltv"])

MAX_BATCH_SIZE = 1000


@router.post("/predict", response_model=LTVPrediction)
def predict_one(customer: CustomerInput):
    return prediction_service.predict_ltv([customer.model_dump()])[0]


@router.post("/predict/batch", response_model=List[LTVPrediction])
def predict_batch(customers: List[CustomerInput]):
    if not customers:
        raise HTTPException(
            status_code=422, detail="Send at least one customer."
        )
    if len(customers) > MAX_BATCH_SIZE:
        raise HTTPException(
            status_code=422,
            detail=f"A batch can contain at most {MAX_BATCH_SIZE} customers.",
        )
    return prediction_service.predict_ltv([c.model_dump() for c in customers])
