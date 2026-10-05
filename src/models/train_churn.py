"""
Train the churn model on the 93 engineered features and save it.

Run from the project root:
    python -m src.models.train_churn

The decision threshold is chosen on out-of-fold predictions of the TRAINING
set, so the test set is used exactly once (for the final report).
"""

import json
import shutil

import joblib
import numpy as np
from sklearn.ensemble import RandomForestClassifier
from sklearn.linear_model import LogisticRegression
from sklearn.metrics import (
    accuracy_score, confusion_matrix, f1_score,
    precision_score, recall_score, roc_auc_score,
)
from sklearn.model_selection import StratifiedKFold, cross_val_predict
from xgboost import XGBClassifier

from src.models.utils import (
    CHURN_MODEL_PATH, DATA_DIR, METRICS_PATH, MODELS_DIR, PIPELINE_PATH,
    load_split,
)


def build_models(scale_pos_weight: float) -> dict:
    return {
        "logistic_regression": LogisticRegression(
            max_iter=2000, class_weight="balanced", random_state=42
        ),
        "random_forest": RandomForestClassifier(
            n_estimators=300, min_samples_leaf=3,
            class_weight="balanced", random_state=42, n_jobs=-1,
        ),
        "xgboost": XGBClassifier(
            n_estimators=300, max_depth=3, learning_rate=0.05,
            subsample=0.8, colsample_bytree=0.8,
            scale_pos_weight=scale_pos_weight,
            eval_metric="logloss", random_state=42, n_jobs=-1,
        ),
    }


def best_f1_threshold(y_true, proba) -> float:
    thresholds = np.arange(0.30, 0.71, 0.01)
    scores = [f1_score(y_true, (proba >= t).astype(int)) for t in thresholds]
    return float(thresholds[int(np.argmax(scores))])


def main() -> None:
    X_train, X_test, y_train, y_test, _, _ = load_split()
    spw = float((y_train == 0).sum() / (y_train == 1).sum())

    results = {}
    fitted = {}
    for name, model in build_models(spw).items():
        model.fit(X_train, y_train)
        proba = model.predict_proba(X_test)[:, 1]
        pred = (proba >= 0.5).astype(int)
        results[name] = {
            "roc_auc": round(float(roc_auc_score(y_test, proba)), 4),
            "accuracy": round(float(accuracy_score(y_test, pred)), 4),
            "precision": round(float(precision_score(y_test, pred)), 4),
            "recall": round(float(recall_score(y_test, pred)), 4),
            "f1": round(float(f1_score(y_test, pred)), 4),
        }
        fitted[name] = model
        print(f"{name:20s}", results[name])

    best_name = max(results, key=lambda n: results[n]["roc_auc"])
    print("\nSelected model:", best_name)

    # Threshold from out-of-fold predictions on TRAIN only
    cv = StratifiedKFold(n_splits=5, shuffle=True, random_state=42)
    oof = cross_val_predict(
        build_models(spw)[best_name], X_train, y_train,
        cv=cv, method="predict_proba",
    )[:, 1]
    threshold = best_f1_threshold(y_train, oof)

    best = fitted[best_name]
    proba = best.predict_proba(X_test)[:, 1]
    pred = (proba >= threshold).astype(int)
    tn, fp, fn, tp = confusion_matrix(y_test, pred).ravel()
    final = {
        "model": best_name,
        "threshold": round(threshold, 2),
        "roc_auc": round(float(roc_auc_score(y_test, proba)), 4),
        "accuracy": round(float(accuracy_score(y_test, pred)), 4),
        "precision": round(float(precision_score(y_test, pred)), 4),
        "recall": round(float(recall_score(y_test, pred)), 4),
        "f1": round(float(f1_score(y_test, pred)), 4),
        "confusion_matrix": {"tn": int(tn), "fp": int(fp),
                             "fn": int(fn), "tp": int(tp)},
    }
    print("\nFinal test metrics at threshold", final["threshold"], final)

    MODELS_DIR.mkdir(parents=True, exist_ok=True)
    joblib.dump(
        {
            "model": best,
            "model_name": best_name,
            "feature_names": list(X_train.columns),
            "threshold": threshold,
            # small sample used by SHAP for linear models
            "background": X_train.sample(100, random_state=42),
        },
        CHURN_MODEL_PATH,
    )

    # The API needs the fitted feature pipeline next to the models
    source_pipeline = DATA_DIR / "feature_pipeline.joblib"
    if source_pipeline.exists():
        shutil.copy(source_pipeline, PIPELINE_PATH)

    metrics = {}
    if METRICS_PATH.exists():
        metrics = json.loads(METRICS_PATH.read_text())
    metrics["churn_comparison"] = results
    metrics["churn_final"] = final
    METRICS_PATH.write_text(json.dumps(metrics, indent=2))
    print("\nSaved:", CHURN_MODEL_PATH)


if __name__ == "__main__":
    main()
