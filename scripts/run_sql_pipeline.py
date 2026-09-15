"""
SQL Pipeline Verification Runner

Owner: Abhishek
Project: Customer Churn Prediction & LTV Engine
Purpose:
Loads the raw CSV into an in-memory SQLite database, runs all SQL staging, 
transformation, and business analytics queries, and prints summary outputs to 
verify SQL correctness and business metrics.
"""

import re
import sqlite3
from pathlib import Path
import pandas as pd


def clean_sql_for_sqlite(sql_content: str) -> str:
    """Strip dbt macros like {{ ref(...) }} for raw ANSI/SQLite execution."""
    sql = re.sub(r"\{\{\s*ref\('(\w+)'\)\s*\}\}", r"\1", sql_content)
    return sql


def run_pipeline():
    project_root = Path(__file__).resolve().parent.parent
    data_path = project_root / "data" / "raw" / "WA_Fn-UseC_-Telco-Customer-Churn.csv"
    sql_dir = project_root / "sql"

    if not data_path.exists():
        raise FileNotFoundError(f"Raw data not found at {data_path}")

    print("=" * 80)
    print("CUSTOMER CHURN PREDICTION & LTV ENGINE - SQL PIPELINE (Abhishek)")
    print("=" * 80)

    # 1. Initialize SQLite in-memory database
    conn = sqlite3.connect(":memory:")
    df_raw = pd.read_csv(data_path)
    df_raw.to_sql("raw_telco_churn", conn, index=False, if_exists="replace")
    print(f"[OK] Ingested raw dataset into 'raw_telco_churn' ({len(df_raw)} records)")

    # 2. Run Staging Queries
    print("\n--- Running Staging Models ---")
    stg_customers_sql = clean_sql_for_sqlite((sql_dir / "staging" / "stg_customers.sql").read_text())
    conn.execute(f"CREATE TABLE stg_customers AS {stg_customers_sql}")
    stg_count = conn.execute("SELECT COUNT(*) FROM stg_customers").fetchone()[0]
    print(f"[OK] stg_customers created successfully ({stg_count} rows)")

    stg_subscriptions_sql = clean_sql_for_sqlite((sql_dir / "staging" / "stg_subscriptions.sql").read_text())
    conn.execute(f"CREATE TABLE stg_subscriptions AS {stg_subscriptions_sql}")
    stg_sub_count = conn.execute("SELECT COUNT(*) FROM stg_subscriptions").fetchone()[0]
    print(f"[OK] stg_subscriptions created successfully ({stg_sub_count} rows)")

    # 3. Run Transformation Models
    print("\n--- Running Intermediate & Mart Transformations ---")
    int_feat_sql = clean_sql_for_sqlite((sql_dir / "transformations" / "int_customer_features.sql").read_text())
    conn.execute(f"CREATE TABLE int_customer_features AS {int_feat_sql}")
    print("[OK] int_customer_features created successfully")

    int_seg_sql = clean_sql_for_sqlite((sql_dir / "transformations" / "int_customer_segmentation.sql").read_text())
    conn.execute(f"CREATE TABLE int_customer_segmentation AS {int_seg_sql}")
    print("[OK] int_customer_segmentation created successfully")

    fct_sql = clean_sql_for_sqlite((sql_dir / "transformations" / "fct_churn_ltv_features.sql").read_text())
    conn.execute(f"CREATE TABLE fct_churn_ltv_features AS {fct_sql}")
    fct_count = conn.execute("SELECT COUNT(*) FROM fct_churn_ltv_features").fetchone()[0]
    print(f"[OK] fct_churn_ltv_features created successfully ({fct_count} rows)")

    # 4. Run Business Analytics Queries
    print("\n--- Running Business Analytics Queries ---")
    
    # A. Executive Retention Summary
    exec_sql = clean_sql_for_sqlite((sql_dir / "analytics" / "executive_retention_summary.sql").read_text())
    df_exec = pd.read_sql_query(exec_sql, conn)
    print("\n>>> Executive Retention Summary KPI Scorecard:")
    print(df_exec.to_string(index=False))

    # B. ARPU & LTV by Segment
    arpu_sql = clean_sql_for_sqlite((sql_dir / "analytics" / "arpu_and_ltv_analysis.sql").read_text())
    df_arpu = pd.read_sql_query(arpu_sql, conn)
    print("\n>>> ARPU & LTV by Strategic Segment (Top 5):")
    print(df_arpu.head(5).to_string(index=False))

    # C. Service Penetration Churn Impact
    service_sql = clean_sql_for_sqlite((sql_dir / "analytics" / "service_penetration_churn_impact.sql").read_text())
    df_service = pd.read_sql_query(service_sql, conn)
    print("\n>>> Service Penetration & Churn Impact:")
    print(df_service.to_string(index=False))

    # D. Churn by Cohort & Contract
    cohort_sql = clean_sql_for_sqlite((sql_dir / "analytics" / "churn_by_cohort_segment.sql").read_text())
    df_cohort = pd.read_sql_query(cohort_sql, conn)
    print("\n>>> Top Churn Cohorts (Highest Churn %):")
    print(df_cohort.head(5).to_string(index=False))

    print("\n" + "=" * 80)
    print("[SUCCESS] All SQL Staging, Transformation, and Analytics queries validated!")
    print("=" * 80)


if __name__ == "__main__":
    run_pipeline()
