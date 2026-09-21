"""
PostgreSQL Transformation Pipeline

Owner: Harshitha
Project: Customer Churn Prediction & LTV Engine

Purpose:
Runs the Data Engineering transformation pipeline in PostgreSQL.

Flow:
Raw CSV
    ↓
staging.telco_customer_churn_raw
    ↓
staging.telco_customer_churn
    ↓
staging.stg_customers
    ↓
staging.stg_subscriptions
    ↓
staging.int_customer_features
    ↓
staging.int_customer_segmentation
    ↓
staging.fct_churn_ltv_features
"""

from pathlib import Path

from sqlalchemy import text

from database import engine


PROJECT_ROOT = Path(__file__).resolve().parents[2]
SQL_DIR = PROJECT_ROOT / "sql"


def run_sql_file(file_path, source_table, target_table):
    """
    Read a SQL transformation file, replace dbt ref() references,
    replace the raw source table name, and create the PostgreSQL table.
    """

    sql = file_path.read_text(encoding="utf-8")

    # Replace dbt-style references with PostgreSQL table names.
    sql = sql.replace("{{ ref('stg_customers') }}", "staging.stg_customers")
    sql = sql.replace(
        "{{ ref('stg_subscriptions') }}",
        "staging.stg_subscriptions"
    )
    sql = sql.replace(
        "{{ ref('int_customer_features') }}",
        "staging.int_customer_features"
    )
    sql = sql.replace(
        "{{ ref('int_customer_segmentation') }}",
        "staging.int_customer_segmentation"
    )

        # Replace the original raw table reference used by Abhishek's SQL.
    sql = sql.replace("raw_telco_churn", "staging.telco_customer_churn")

    # Translate original CSV column names to PostgreSQL column names.
    column_mapping = {
        "customerID": "customer_id",
        "SeniorCitizen": "senior_citizen",
        "Partner": "partner",
        "Dependents": "dependents",
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

    for old_name, new_name in column_mapping.items():
        sql = sql.replace(old_name, new_name)
        # PostgreSQL source table already stores total_charges as NUMERIC.
    # The original SQLite/dbt SQL uses TRIM() because its source is TEXT.
    # Remove that text-specific check for PostgreSQL.
    sql = sql.replace(
        "WHEN TRIM(total_charges) = '' OR total_charges IS NULL THEN 0.0",
        "WHEN total_charges IS NULL THEN 0.0"
    )
        # PostgreSQL ROUND() with 2 decimal places requires NUMERIC,
    # not DOUBLE PRECISION.
    sql = sql.replace(
        "ROUND(CAST(c.tenure_months AS FLOAT) / 12.0, 2)",
        "ROUND(CAST(c.tenure_months AS NUMERIC) / 12.0, 2)"
    )
    with engine.begin() as connection:

        connection.execute(
            text(f"DROP TABLE IF EXISTS {target_table} CASCADE;")
        )

        connection.execute(
            text(f"CREATE TABLE {target_table} AS {sql}")
        )

    print(f"[OK] {target_table} created successfully.")


def run_pipeline():

    print("=" * 80)
    print("CUSTOMER CHURN LTV ENGINE - POSTGRESQL PIPELINE")
    print("Owner: Harshitha - Data Engineering")
    print("=" * 80)

    # ---------------------------------------------------------
    # 1. Check PostgreSQL connection
    # ---------------------------------------------------------

    with engine.connect() as connection:
        result = connection.execute(text("SELECT 1;"))
        result.fetchone()

    print("\n[OK] PostgreSQL connection successful.")

    # ---------------------------------------------------------
    # 2. Check source data
    # ---------------------------------------------------------

    with engine.connect() as connection:
        result = connection.execute(
            text(
                """
                SELECT COUNT(*)
                FROM staging.telco_customer_churn;
                """
            )
        )

        source_count = result.scalar()

    print(f"[OK] Source table contains {source_count} rows.")

    # ---------------------------------------------------------
    # 3. Create stg_customers
    # ---------------------------------------------------------

    run_sql_file(
        SQL_DIR / "staging" / "stg_customers.sql",
        "staging.telco_customer_churn",
        "staging.stg_customers"
    )

    # ---------------------------------------------------------
    # 4. Create stg_subscriptions
    # ---------------------------------------------------------

    run_sql_file(
        SQL_DIR / "staging" / "stg_subscriptions.sql",
        "staging.telco_customer_churn",
        "staging.stg_subscriptions"
    )

    # ---------------------------------------------------------
    # 5. Create int_customer_features
    # ---------------------------------------------------------

    run_sql_file(
        SQL_DIR / "transformations" / "int_customer_features.sql",
        "staging.stg_customers",
        "staging.int_customer_features"
    )

    # ---------------------------------------------------------
    # 6. Create int_customer_segmentation
    # ---------------------------------------------------------

    run_sql_file(
        SQL_DIR / "transformations" / "int_customer_segmentation.sql",
        "staging.int_customer_features",
        "staging.int_customer_segmentation"
    )

    # ---------------------------------------------------------
    # 7. Create final feature table
    # ---------------------------------------------------------

    run_sql_file(
        SQL_DIR / "transformations" / "fct_churn_ltv_features.sql",
        "staging.int_customer_features",
        "staging.fct_churn_ltv_features"
    )

    # ---------------------------------------------------------
    # 8. Final validation
    # ---------------------------------------------------------

    with engine.connect() as connection:

        result = connection.execute(
            text(
                """
                SELECT
                    COUNT(*) AS total_customers,
                    COUNT(DISTINCT customer_id) AS unique_customers,
                    SUM(is_churned) AS churned_customers,
                    COUNT(*) - SUM(is_churned) AS active_customers,
                    ROUND(
                        100.0 * SUM(is_churned) / COUNT(*),
                        2
                    ) AS churn_rate
                FROM staging.fct_churn_ltv_features;
                """
            )
        )

        row = result.fetchone()

    print("\nFinal PostgreSQL validation:")
    print("Total customers:", row.total_customers)
    print("Unique customers:", row.unique_customers)
    print("Churned customers:", row.churned_customers)
    print("Active customers:", row.active_customers)
    print("Churn rate:", row.churn_rate, "%")

    print("\n" + "=" * 80)
    print("[SUCCESS] PostgreSQL transformation pipeline completed!")
    print("=" * 80)


if __name__ == "__main__":
    run_pipeline()