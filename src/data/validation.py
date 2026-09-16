import pandas as pd

from database import engine


def validate_customer_data():

    query = """
        SELECT *
        FROM analytics.customer_churn;
    """

    df = pd.read_sql(query, engine)

    print("=" * 60)
    print("CUSTOMER CHURN DATA VALIDATION")
    print("=" * 60)

    # 1. Row and column count
    print("\n1. Dataset Shape")
    print("Rows:", df.shape[0])
    print("Columns:", df.shape[1])

    # 2. Duplicate customer IDs
    print("\n2. Duplicate Customer IDs")
    duplicate_ids = df["customer_id"].duplicated().sum()
    print("Duplicate IDs:", duplicate_ids)

    # 3. Missing values
    print("\n3. Missing Values")
    missing_values = df.isnull().sum()
    print(missing_values[missing_values > 0])

    # 4. Churn distribution
    print("\n4. Churn Distribution")
    print(df["churn"].value_counts())

    # 5. Churn percentage
    print("\n5. Churn Percentage")
    churn_percentage = df["churn"].value_counts(normalize=True) * 100
    print(churn_percentage.round(2))

    # 6. Numeric column information
    print("\n6. Numeric Column Summary")
    print(
        df[
            ["tenure", "monthly_charges", "total_charges"]
        ].describe()
    )

    # 7. Data types
    print("\n7. Data Types")
    print(df.dtypes)

    print("\n" + "=" * 60)
    print("VALIDATION COMPLETED")
    print("=" * 60)


if __name__ == "__main__":
    validate_customer_data()