import joblib
import pandas as pd
from sklearn.metrics import accuracy_score, classification_report


# --------------------------------------------------
# 1. Load RAW test data
# --------------------------------------------------

df = pd.read_csv(
    "data/raw/telco_customer_churn.csv"
)

df.columns = df.columns.str.strip()

df["TotalCharges"] = pd.to_numeric(
    df["TotalCharges"],
    errors="coerce"
)

df["Churn"] = df["Churn"].map({
    "No": 0,
    "Yes": 1
})

X = df.drop(
    columns=["Churn", "customerID"],
    errors="ignore"
)

y = df["Churn"]


# --------------------------------------------------
# 2. Recreate the SAME test split used during training
# --------------------------------------------------

from sklearn.model_selection import train_test_split

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
# 3. Load trained churn model
# --------------------------------------------------

model = joblib.load(
    "models/churn_model.pkl"
)

print("Churn model loaded successfully.")
print("Model type:", type(model))


# --------------------------------------------------
# 4. Generate predictions
# --------------------------------------------------

y_pred = model.predict(X_test)

print("Predictions generated successfully.")
print("First 10 predictions:", y_pred[:10])


# --------------------------------------------------
# 5. Evaluate model
# --------------------------------------------------

accuracy = accuracy_score(
    y_test,
    y_pred
)

print("\nChurn Model Evaluation")
print("----------------------")
print("Accuracy:", accuracy)

print("\nClassification Report")
print("---------------------")

print(
    classification_report(
        y_test,
        y_pred,
        target_names=["No Churn", "Churn"],
        zero_division=0
    )
)

print("Churn model test completed successfully.")
