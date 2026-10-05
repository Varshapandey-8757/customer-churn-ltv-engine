"""
Check the PostgreSQL connection configured in .env

Run from the project root:
    python scripts/check_db_connection.py

Replaces the old src/test_db_connection.py and src/data/test_connection.py,
whose names started with "test_" even though they need a real database.
"""

import os
import sys
from pathlib import Path

from dotenv import load_dotenv
from sqlalchemy import create_engine, text

PROJECT_ROOT = Path(__file__).resolve().parents[1]
load_dotenv(PROJECT_ROOT / ".env")

REQUIRED = ["DB_HOST", "DB_PORT", "DB_NAME", "DB_USER", "DB_PASSWORD"]


def main() -> int:
    missing = [key for key in REQUIRED if not os.getenv(key)]
    if missing:
        print("Missing values in .env:", ", ".join(missing))
        print("Copy .env.example to .env and fill in the values.")
        return 1

    url = (
        f"postgresql+psycopg2://{os.getenv('DB_USER')}:{os.getenv('DB_PASSWORD')}"
        f"@{os.getenv('DB_HOST')}:{os.getenv('DB_PORT')}/{os.getenv('DB_NAME')}"
    )

    print(f"Connecting to {os.getenv('DB_HOST')}:{os.getenv('DB_PORT')}"
          f"/{os.getenv('DB_NAME')} as {os.getenv('DB_USER')} ...")

    try:
        engine = create_engine(url)
        with engine.connect() as connection:
            result = connection.execute(text("SELECT 1")).scalar()
        print("PostgreSQL connection successful. Test result:", result)
        return 0
    except Exception as error:  # noqa: BLE001
        print("PostgreSQL connection failed.")
        print(error)
        return 1


if __name__ == "__main__":
    sys.exit(main())
