import os
from pathlib import Path

from dotenv import load_dotenv
from sqlalchemy import create_engine, text


# Project root directory
BASE_DIR = Path(__file__).resolve().parents[1]

# Load .env from project root
ENV_FILE = BASE_DIR / ".env"
load_dotenv(ENV_FILE)

# Database configuration
DB_HOST = os.getenv("DB_HOST")
DB_PORT = os.getenv("DB_PORT")
DB_NAME = os.getenv("DB_NAME")
DB_USER = os.getenv("DB_USER")
DB_PASSWORD = os.getenv("DB_PASSWORD")

print("Checking database configuration...")
print(f"DB_HOST: {DB_HOST}")
print(f"DB_PORT: {DB_PORT}")
print(f"DB_NAME: {DB_NAME}")
print(f"DB_USER: {DB_USER}")

if not all([DB_HOST, DB_PORT, DB_NAME, DB_USER, DB_PASSWORD]):
    raise ValueError(
        "Database configuration is incomplete. "
        "Please check your .env file."
    )

DATABASE_URL = (
    f"postgresql+psycopg2://{DB_USER}:{DB_PASSWORD}"
    f"@{DB_HOST}:{DB_PORT}/{DB_NAME}"
)

engine = create_engine(DATABASE_URL)

try:
    with engine.connect() as connection:
        result = connection.execute(text("SELECT version();"))

        print("\nPostgreSQL connection successful!")
        print(result.fetchone())

except Exception as e:
    print("\nPostgreSQL connection failed:")
    print(e)