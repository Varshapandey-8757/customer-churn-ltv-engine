import joblib
import pandas as pd
from pathlib import Path

from sklearn.model_selection import train_test_split
from sklearn.metrics import (
    accuracy_score,
    precision_score,
    recall_score,
    f1_score,
    roc_auc_score,
    confusion_matrix,
    classification_report
)

# Project root
BASE_DIR = Path(__file__).resolve().parents[1]

# Same raw dataset used for training
DATA_FILE = BASE_DIR / "data" / "raw" / "telco_customer_churn.csv"
MODEL_FILE = BASE_DIR / "models" / "churn_model.pkl"

# --------------------------------------------------
# 1. Load RAW dataset
# --------------------------------------------------

print("Loading raw dataset...")

df = pd.read_csv(DATA_FILE)
df.columns = df.columns.str.strip()

df["TotalCharges"] = pd.to_numeric(
    df["TotalCharges"],
    errors="coerce"
)

df["Churn"] = df["Churn"].map({
    "No": 0,
    "Yes": 1
})

# --------------------------------------------------
# 2. Prepare features exactly like training notebook
# --------------------------------------------------

X = df.drop(
    columns=["Churn", "customerID"],
    errors="ignore"
)

y = df["Churn"]

print("Full X shape:", X.shape)
print("Full y shape:", y.shape)

# --------------------------------------------------
# 3. Same train/test split as training
# --------------------------------------------------

X_train, X_test, y_train, y_test = train_test_split(
    X,
    y,
    test_size=0.20,
    random_state=42,
    stratify=y
)

print("X_test shape:", X_test.shape)
print("y_test shape:", y_test.shape)

# --------------------------------------------------
# 4. Load trained model
# --------------------------------------------------

print("\nLoading churn model...")

model = joblib.load(MODEL_FILE)

print("Churn model loaded successfully.")
print("Model type:", type(model))
print("Model steps:", list(model.named_steps.keys()))

# --------------------------------------------------
# 5. Predict
# --------------------------------------------------

print("\nGenerating predictions...")

y_pred = model.predict(X_test)
y_prob = model.predict_proba(X_test)[:, 1]

print("Predictions generated successfully.")
print("First 10 predictions:", y_pred[:10])

# --------------------------------------------------
# 6. Evaluation
# --------------------------------------------------

accuracy = accuracy_score(y_test, y_pred)

precision = precision_score(
    y_test,
    y_pred,
    zero_division=0
)

recall = recall_score(
    y_test,
    y_pred,
    zero_division=0
)

f1 = f1_score(
    y_test,
    y_pred,
    zero_division=0
)

roc_auc = roc_auc_score(
    y_test,
    y_prob
)

print("\n========================================")
print("CHURN MODEL EVALUATION")
print("========================================")

print(f"Accuracy : {accuracy:.4f}")
print(f"Precision: {precision:.4f}")
print(f"Recall   : {recall:.4f}")
print(f"F1 Score : {f1:.4f}")
print(f"ROC-AUC  : {roc_auc:.4f}")

print("\nClassification Report")
print("----------------------------------------")

print(
    classification_report(
        y_test,
        y_pred,
        target_names=["No Churn", "Churn"],
        zero_division=0
    )
)

print("Confusion Matrix")
print("----------------------------------------")
print(confusion_matrix(y_test, y_pred))
