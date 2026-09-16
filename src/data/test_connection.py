from sqlalchemy import text

from database import engine


try:
    with engine.connect() as connection:
        result = connection.execute(text("SELECT 1"))
        print("PostgreSQL connection successful!")
        print("Test result:", result.scalar())

except Exception as error:
    print("PostgreSQL connection failed.")
    print(error)