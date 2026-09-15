from pathlib import Path
import os

from dotenv import load_dotenv
from sqlalchemy import create_engine, text


# --------------------------------------------------
# 1. Project root
# --------------------------------------------------

BASE_DIR = Path(__file__).resolve().parents[2]


# --------------------------------------------------
# 2. Load environment variables
# --------------------------------------------------

load_dotenv(BASE_DIR / ".env")


DB_HOST = os.getenv("DB_HOST")
DB_PORT = os.getenv("DB_PORT")
DB_NAME = os.getenv("DB_NAME")
DB_USER = os.getenv("DB_USER")
DB_PASSWORD = os.getenv("DB_PASSWORD")


if not all([DB_HOST, DB_PORT, DB_NAME, DB_USER, DB_PASSWORD]):
    raise ValueError(
        "Database configuration is incomplete. "
        "Please check your .env file."
    )


# --------------------------------------------------
# 3. PostgreSQL connection
# --------------------------------------------------

DATABASE_URL = (
    f"postgresql+psycopg2://"
    f"{DB_USER}:{DB_PASSWORD}@"
    f"{DB_HOST}:{DB_PORT}/{DB_NAME}"
)

engine = create_engine(DATABASE_URL)


# --------------------------------------------------
# 4. Row count
# --------------------------------------------------

with engine.connect() as connection:

    result = connection.execute(
        text("""
            SELECT COUNT(*)
            FROM customer_churn
        """)
    )

    row_count = result.scalar()

    print(f"Total rows: {row_count}")


# --------------------------------------------------
# 5. Duplicate customer IDs
# --------------------------------------------------

with engine.connect() as connection:

    result = connection.execute(
        text("""
            SELECT
                COUNT(*) - COUNT(DISTINCT customer_id)
            FROM customer_churn
        """)
    )

    duplicate_count = result.scalar()

    print(f"Duplicate customer IDs: {duplicate_count}")


# --------------------------------------------------
# 6. Churn distribution
# --------------------------------------------------

with engine.connect() as connection:

    result = connection.execute(
        text("""
            SELECT
                churn,
                COUNT(*)
            FROM customer_churn
            GROUP BY churn
            ORDER BY churn
        """)
    )

    print("\nChurn distribution:")

    for row in result:
        print(row)


# --------------------------------------------------
# 7. Average monthly charges by churn
# --------------------------------------------------

with engine.connect() as connection:

    result = connection.execute(
        text("""
            SELECT
                churn,
                ROUND(AVG(monthly_charges)::numeric, 2)
            FROM customer_churn
            GROUP BY churn
            ORDER BY churn
        """)
    )

    print("\nAverage monthly charges by churn:")

    for row in result:
        print(row)


# --------------------------------------------------
# 8. Validation completed
# --------------------------------------------------

print("\nValidation completed successfully.")