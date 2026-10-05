"""Request / response schemas for the prediction API."""

from typing import List, Literal, Optional

from pydantic import BaseModel, Field

YesNo = Literal["Yes", "No"]
YesNoNoInternet = Literal["Yes", "No", "No internet service"]


class CustomerInput(BaseModel):
    """One customer, using the raw Telco dataset columns.

    Categorical fields only accept the values found in the training data,
    so a typo returns a clear 422 error instead of a silent wrong prediction.
    """

    customerID: Optional[str] = None
    gender: Literal["Female", "Male"]
    SeniorCitizen: int = Field(ge=0, le=1)
    Partner: YesNo
    Dependents: YesNo
    tenure: int = Field(ge=0, le=72, description="Months with the company (0-72)")
    PhoneService: YesNo
    MultipleLines: Literal["Yes", "No", "No phone service"]
    InternetService: Literal["DSL", "Fiber optic", "No"]
    OnlineSecurity: YesNoNoInternet
    OnlineBackup: YesNoNoInternet
    DeviceProtection: YesNoNoInternet
    TechSupport: YesNoNoInternet
    StreamingTV: YesNoNoInternet
    StreamingMovies: YesNoNoInternet
    Contract: Literal["Month-to-month", "One year", "Two year"]
    PaperlessBilling: YesNo
    PaymentMethod: Literal[
        "Electronic check",
        "Mailed check",
        "Bank transfer (automatic)",
        "Credit card (automatic)",
    ]
    MonthlyCharges: float = Field(ge=0, le=500)
    TotalCharges: float = Field(ge=0)

    model_config = {
        "json_schema_extra": {
            "example": {
                "customerID": "7590-VHVEG",
                "gender": "Female",
                "SeniorCitizen": 0,
                "Partner": "Yes",
                "Dependents": "No",
                "tenure": 1,
                "PhoneService": "No",
                "MultipleLines": "No phone service",
                "InternetService": "DSL",
                "OnlineSecurity": "No",
                "OnlineBackup": "Yes",
                "DeviceProtection": "No",
                "TechSupport": "No",
                "StreamingTV": "No",
                "StreamingMovies": "No",
                "Contract": "Month-to-month",
                "PaperlessBilling": "Yes",
                "PaymentMethod": "Electronic check",
                "MonthlyCharges": 29.85,
                "TotalCharges": 29.85,
            }
        }
    }


class ChurnPrediction(BaseModel):
    customerID: Optional[str] = None
    churn_probability: float
    will_churn: bool
    risk_level: str


class LTVPrediction(BaseModel):
    customerID: Optional[str] = None
    predicted_historical_ltv: float
    projected_ltv: float
    churn_probability: float
    estimated_remaining_months: int


class FeatureContribution(BaseModel):
    feature: str
    shap_value: float
    direction: str


class ExplanationResponse(BaseModel):
    customerID: Optional[str] = None
    churn_probability: float
    top_factors: List[FeatureContribution]
