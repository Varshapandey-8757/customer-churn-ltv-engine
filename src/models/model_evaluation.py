"""
Model Evaluation Utilities

Owner: Varsha
"""

from sklearn.metrics import precision_score, recall_score, f1_score


def evaluate_classification_model(y_true, y_pred):
    """Calculate classification performance metrics."""

    return {
        "precision": precision_score(y_true, y_pred, zero_division=0),
        "recall": recall_score(y_true, y_pred, zero_division=0),
        "f1_score": f1_score(y_true, y_pred, zero_division=0),
    }