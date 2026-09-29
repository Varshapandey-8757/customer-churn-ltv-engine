from pathlib import Path
import os

from dotenv import load_dotenv
from sqlalchemy import create_engine, text


# ============================================================
# 1. PROJECT ROOT
# ============================================================

BASE_DIR = Path(__file__).resolve().parents[2]


# ============================================================
# 2. LOAD ENVIRONMENT VARIABLES
# ============================================================

ENV_FILE = BASE_DIR / ".env"

if not ENV_FILE.exists():
    raise FileNotFoundError(
        f".env file not found:\n{ENV_FILE}"
    )

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
# 3. POSTGRESQL CONNECTION
# ============================================================

DATABASE_URL = (
    f"postgresql+psycopg2://"
    f"{DB_USER}:{DB_PASSWORD}@"
    f"{DB_HOST}:{DB_PORT}/{DB_NAME}"
)

engine = create_engine(
    DATABASE_URL,
    pool_pre_ping=True
)


# ============================================================
# 4. ROW COUNT
# ============================================================

with engine.connect() as connection:

    result = connection.execute(
        text(
            """
            SELECT COUNT(*)
            FROM customer_churn
            """
        )
    )

    row_count = result.scalar()

    print(
        f"Total rows: {row_count}"
    )


# ============================================================
# 5. DUPLICATE CUSTOMER IDs
# ============================================================

with engine.connect() as connection:

    result = connection.execute(
        text(
            """
            SELECT
                COUNT(*) - COUNT(DISTINCT customer_id)
            FROM customer_churn
            """
        )
    )

    duplicate_count = result.scalar()

    print(
        f"Duplicate customer IDs: "
        f"{duplicate_count}"
    )


# ============================================================
# 6. CHURN DISTRIBUTION
# ============================================================

with engine.connect() as connection:

    result = connection.execute(
        text(
            """
            SELECT
                churn,
                COUNT(*)
            FROM customer_churn
            GROUP BY churn
            ORDER BY churn
            """
        )
    )

    print("\nChurn distribution:")

    for row in result:
        print(row)


# ============================================================
# 7. AVERAGE MONTHLY CHARGES BY CHURN
# ============================================================

with engine.connect() as connection:

    result = connection.execute(
        text(
            """
            SELECT
                churn,
                ROUND(
                    AVG(monthly_charges)::numeric,
                    2
                )
            FROM customer_churn
            GROUP BY churn
            ORDER BY churn
            """
        )
    )

    print(
        "\nAverage monthly charges by churn:"
    )

    for row in result:
        print(row)


# ============================================================
# 8. VALIDATION COMPLETED
# ============================================================

print(
    "\nValidation completed successfully."
)
