import os
import pandas as pd

from database import engine


def load_customer_data():
    query = """
        SELECT *
        FROM analytics.customer_churn;
    """

    df = pd.read_sql(query, engine)

    print("Customer data loaded successfully!")
    print("Rows:", len(df))
    print("Columns:", len(df.columns))

    # Create processed data folder if it doesn't exist
    output_folder = "data/processed"
    os.makedirs(output_folder, exist_ok=True)

    # Save data as CSV
    output_file = os.path.join(
        output_folder,
        "customer_features.csv"
    )

    df.to_csv(output_file, index=False)

    print("Processed data saved successfully!")
    print("File:", output_file)

    print("\nFirst 5 rows:")
    print(df.head())

    return df


if __name__ == "__main__":
    load_customer_data()