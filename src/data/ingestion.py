from pathlib import Path
import os

import pandas as pd
from dotenv import load_dotenv
from sqlalchemy import create_engine, text


# ============================================================
# 1. PROJECT PATHS
# ============================================================

BASE_DIR = Path(__file__).resolve().parents[2]

CSV_FILE = (
    BASE_DIR
    / "data"
    / "raw"
    / "WA_Fn-UseC_-Telco-Customer-Churn.csv"
)

ENV_FILE = BASE_DIR / ".env"


# ============================================================
# 2. CHECK FILES
# ============================================================

if not CSV_FILE.exists():
    raise FileNotFoundError(
        f"CSV file not found:\n{CSV_FILE}"
    )

if not ENV_FILE.exists():
    raise FileNotFoundError(
        f".env file not found:\n{ENV_FILE}"
    )


# ============================================================
# 3. LOAD ENVIRONMENT VARIABLES
# ============================================================

load_dotenv(ENV_FILE)

DB_HOST = os.getenv("DB_HOST")
DB_PORT = os.getenv("DB_PORT")
DB_NAME = os.getenv("DB_NAME")
DB_USER = os.getenv("DB_USER")
DB_PASSWORD = os.getenv("DB_PASSWORD")


if not all(
    [DB_HOST, DB_PORT, DB_NAME, DB_USER, DB_PASSWORD]
):
    raise ValueError(
        "Database configuration is incomplete. "
        "Please check your .env file."
    )


# ============================================================
# 4. CREATE POSTGRESQL CONNECTION
# ============================================================

DATABASE_URL = (
    f"postgresql+psycopg2://"
    f"{DB_USER}:{DB_PASSWORD}@"
    f"{DB_HOST}:{DB_PORT}/{DB_NAME}"
)

print("Connecting to PostgreSQL...")

engine = create_engine(
    DATABASE_URL,
    pool_pre_ping=True
)


# ============================================================
# 5. TEST DATABASE CONNECTION
# ============================================================

try:
    with engine.connect() as connection:
        connection.execute(text("SELECT 1"))

    print("PostgreSQL connection successful.")

except Exception as e:
    raise ConnectionError(
        f"Could not connect to PostgreSQL.\n{e}"
    )


# ============================================================
# 6. READ CSV DATASET
# ============================================================

print("\nReading Telco Customer Churn dataset...")

df = pd.read_csv(CSV_FILE)

print(f"Original dataset shape: {df.shape}")


# ============================================================
# 7. CLEAN COLUMN NAMES
# ============================================================

df.columns = df.columns.str.strip()


# ============================================================
# 8. RENAME COLUMNS
# ============================================================

column_mapping = {
    "customerID": "customer_id",
    "gender": "gender",
    "SeniorCitizen": "senior_citizen",
    "Partner": "partner",
    "Dependents": "dependents",
    "tenure": "tenure",
    "PhoneService": "phone_service",
    "MultipleLines": "multiple_lines",
    "InternetService": "internet_service",
    "OnlineSecurity": "online_security",
    "OnlineBackup": "online_backup",
    "DeviceProtection": "device_protection",
    "TechSupport": "tech_support",
    "StreamingTV": "streaming_tv",
    "StreamingMovies": "streaming_movies",
    "Contract": "contract",
    "PaperlessBilling": "paperless_billing",
    "PaymentMethod": "payment_method",
    "MonthlyCharges": "monthly_charges",
    "TotalCharges": "total_charges",
    "Churn": "churn"
}

df = df.rename(columns=column_mapping)


# ============================================================
# 9. CHECK REQUIRED COLUMNS
# ============================================================

required_columns = [
    "customer_id",
    "gender",
    "senior_citizen",
    "partner",
    "dependents",
    "tenure",
    "phone_service",
    "multiple_lines",
    "internet_service",
    "online_security",
    "online_backup",
    "device_protection",
    "tech_support",
    "streaming_tv",
    "streaming_movies",
    "contract",
    "paperless_billing",
    "payment_method",
    "monthly_charges",
    "total_charges",
    "churn"
]

missing_columns = [
    column
    for column in required_columns
    if column not in df.columns
]

if missing_columns:
    raise ValueError(
        f"Missing required columns: {missing_columns}"
    )


# ============================================================
# 10. CONVERT NUMERIC COLUMNS
# ============================================================

df["senior_citizen"] = pd.to_numeric(
    df["senior_citizen"],
    errors="coerce"
)

df["tenure"] = pd.to_numeric(
    df["tenure"],
    errors="coerce"
)

df["monthly_charges"] = pd.to_numeric(
    df["monthly_charges"],
    errors="coerce"
)

df["total_charges"] = pd.to_numeric(
    df["total_charges"],
    errors="coerce"
)


# ============================================================
# 11. REMOVE DUPLICATE CUSTOMERS
# ============================================================

before_duplicates = len(df)

df = df.drop_duplicates(
    subset=["customer_id"],
    keep="first"
)

after_duplicates = len(df)

print(
    f"Rows before duplicate removal: "
    f"{before_duplicates}"
)

print(
    f"Rows after duplicate removal: "
    f"{after_duplicates}"
)

print(
    f"Duplicate rows removed: "
    f"{before_duplicates - after_duplicates}"
)


# ============================================================
# 12. CHECK MISSING VALUES
# ============================================================

print("\nMissing values:")

missing_values = df.isnull().sum()

missing_values = missing_values[
    missing_values > 0
]

if len(missing_values) == 0:
    print("No missing values found.")

else:
    print(missing_values)


# ============================================================
# 13. REPLACE NaN WITH NONE
# ============================================================
# PostgreSQL understands Python None as SQL NULL.

df = df.where(
    pd.notnull(df),
    None
)


# ============================================================
# 14. LOAD DATA INTO POSTGRESQL
# ============================================================

print("\nLoading data into PostgreSQL...")

try:

    df.to_sql(
        name="customer_churn",
        con=engine,
        if_exists="replace",
        index=False,
        chunksize=500,
        method="multi"
    )

except Exception as e:

    print("\nDatabase insertion failed.")

    raise e


# ============================================================
# 15. VERIFY DATA IN DATABASE
# ============================================================

try:

    with engine.connect() as connection:

        result = connection.execute(
            text(
                "SELECT COUNT(*) "
                "FROM customer_churn"
            )
        )

        database_count = result.scalar()

except Exception as e:

    raise RuntimeError(
        f"Could not verify database data.\n{e}"
    )


# ============================================================
# 16. FINAL MESSAGE
# ============================================================

print("\n" + "=" * 60)

print("DATA INGESTION COMPLETED SUCCESSFULLY")

print("=" * 60)

print(f"CSV rows processed      : {len(df)}")
print(f"PostgreSQL rows loaded  : {database_count}")
print(f"Table name              : customer_churn")

print("=" * 60)