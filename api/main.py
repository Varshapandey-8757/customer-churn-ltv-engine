"""
FastAPI application: churn + LTV prediction service.

Run from the project root:
    uvicorn api.main:app --reload
Docs: http://127.0.0.1:8000/docs
"""

from fastapi import FastAPI, Request
from fastapi.responses import JSONResponse

from api.routes import churn, ltv
from api.services.model_loader import ModelsNotFoundError

app = FastAPI(
    title="Customer Churn & LTV Engine",
    description="Predict customer churn risk and lifetime value.",
    version="0.1.0",
)

app.include_router(churn.router)
app.include_router(ltv.router)


@app.exception_handler(ModelsNotFoundError)
async def models_missing_handler(request: Request, exc: ModelsNotFoundError):
    return JSONResponse(status_code=503, content={"detail": str(exc)})


@app.get("/", tags=["health"])
def root():
    return {"service": "churn-ltv-engine", "docs": "/docs"}


@app.get("/health", tags=["health"])
def health():
    return {"status": "ok"}
