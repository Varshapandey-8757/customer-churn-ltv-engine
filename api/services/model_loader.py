"""Loads the trained models and the fitted feature pipeline (cached)."""

from functools import lru_cache

import joblib

from src.models.utils import CHURN_MODEL_PATH, LTV_MODEL_PATH, PIPELINE_PATH


class ModelsNotFoundError(FileNotFoundError):
    """Raised when a model file has not been trained yet."""


def _require(path):
    if not path.exists():
        raise ModelsNotFoundError(
            f"Missing file: {path}. Train the models first with: make train"
        )
    return path


@lru_cache(maxsize=1)
def load_pipeline():
    return joblib.load(_require(PIPELINE_PATH))


@lru_cache(maxsize=1)
def load_churn_bundle() -> dict:
    return joblib.load(_require(CHURN_MODEL_PATH))


@lru_cache(maxsize=1)
def load_ltv_bundle() -> dict:
    return joblib.load(_require(LTV_MODEL_PATH))
