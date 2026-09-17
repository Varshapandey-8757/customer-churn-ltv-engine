from pathlib import Path

import pandas as pd
from sqlalchemy import text

from database import engine


# Find the project root
PROJECT_ROOT = Path(__file__).resolve().parents[2]

# Raw dataset location
DATA_FILE = PROJECT_ROOT / "data" / "raw" / "telco_customer_churn.csv"


def load_database():

    print("=" * 60)
    print("POSTGRESQL DATA LOADING PIPELINE")
    print("=" * 60)

    # ---------------------------------------------------------
    # 1. Check that the CSV exists
    # ---------------------------------------------------------

    if not DATA_FILE.exists():
        print("ERROR: Dataset not found.")
        print("Expected file:", DATA_FILE)
        return

    print("\nDataset found:")
    print(DATA_FILE)

    # ---------------------------------------------------------
    # 2. Read CSV using Pandas
    # ---------------------------------------------------------

    df = pd.read_csv(DATA_FILE)

    print("\nCSV loaded successfully!")
    print("Rows:", len(df))
    print("Columns:", len(df.columns))

    # ---------------------------------------------------------
    # 3. Clean column names
    # ---------------------------------------------------------

    df.columns = [
        column.strip()
        .lower()
        .replace(" ", "_")
        for column in df.columns
    ]

    # ---------------------------------------------------------
    # 4. Clean blank values
    # ---------------------------------------------------------

    df = df.replace(r"^\s*$", None, regex=True)

    print("\nBlank values converted to NULL-compatible values.")

    # ---------------------------------------------------------
    # 5. Load data into PostgreSQL raw table
    # ---------------------------------------------------------

    with engine.begin() as connection:

        print("\nClearing existing raw staging data...")

        connection.execute(
            text(
                "TRUNCATE TABLE "
                "staging.telco_customer_churn_raw;"
            )
        )

    df.to_sql(
        "telco_customer_churn_raw",
        engine,
        schema="staging",
        if_exists="append",
        index=False,
        method="multi"
    )

    print("Raw staging table loaded successfully.")

    # ---------------------------------------------------------
    # 6. Rebuild cleaned staging table
    # ---------------------------------------------------------

    with engine.begin() as connection:

        print("\nRefreshing cleaned staging table...")

        connection.execute(
            text(
                "TRUNCATE TABLE "
                "staging.telco_customer_churn;"
            )
        )

        connection.execute(
            text(
                """
                INSERT INTO staging.telco_customer_churn (
                    customer_id,
                    gender,
                    senior_citizen,
                    partner,
                    dependents,
                    tenure,
                    phone_service,
                    multiple_lines,
                    internet_service,
                    online_security,
                    online_backup,
                    device_protection,
                    tech_support,
                    streaming_tv,
                    streaming_movies,
                    contract,
                    paperless_billing,
                    payment_method,
                    monthly_charges,
                    total_charges,
                    churn
                )
                SELECT
                    NULLIF(TRIM(customer_id), ''),
                    NULLIF(TRIM(gender), ''),
                    NULLIF(TRIM(senior_citizen), '')::INTEGER,
                    NULLIF(TRIM(partner), ''),
                    NULLIF(TRIM(dependents), ''),
                    NULLIF(TRIM(tenure), '')::INTEGER,
                    NULLIF(TRIM(phone_service), ''),
                    NULLIF(TRIM(multiple_lines), ''),
                    NULLIF(TRIM(internet_service), ''),
                    NULLIF(TRIM(online_security), ''),
                    NULLIF(TRIM(online_backup), ''),
                    NULLIF(TRIM(device_protection), ''),
                    NULLIF(TRIM(tech_support), ''),
                    NULLIF(TRIM(streaming_tv), ''),
                    NULLIF(TRIM(streaming_movies), ''),
                    NULLIF(TRIM(contract), ''),
                    NULLIF(TRIM(paperless_billing), ''),
                    NULLIF(TRIM(payment_method), ''),
                    NULLIF(TRIM(monthly_charges), '')::NUMERIC(10,2),
                    NULLIF(TRIM(total_charges), '')::NUMERIC(10,2),
                    NULLIF(TRIM(churn), '')
                FROM staging.telco_customer_churn_raw;
                """
            )
        )

    print("Cleaned staging table refreshed successfully.")

    # ---------------------------------------------------------
    # 7. Refresh analytics table
    # ---------------------------------------------------------

    with engine.begin() as connection:

        print("\nRefreshing analytics table...")

        connection.execute(
            text(
                "TRUNCATE TABLE analytics.customer_churn;"
            )
        )

        connection.execute(
            text(
                """
                INSERT INTO analytics.customer_churn
                SELECT *
                FROM staging.telco_customer_churn;
                """
            )
        )

    print("Analytics table refreshed successfully.")

    # ---------------------------------------------------------
    # 8. Final validation
    # ---------------------------------------------------------

    with engine.connect() as connection:

        result = connection.execute(
            text(
                """
                SELECT
                    COUNT(*) AS total_customers,
                    COUNT(DISTINCT customer_id) AS unique_customers
                FROM analytics.customer_churn;
                """
            )
        )

        row = result.fetchone()

    print("\nFinal database validation:")
    print("Total customers:", row.total_customers)
    print("Unique customers:", row.unique_customers)

    print("\n" + "=" * 60)
    print("DATABASE LOADING COMPLETED SUCCESSFULLY")
    print("=" * 60)


if __name__ == "__main__":
    load_database()