import os
import pandas as pd
from database import engine


def export_postgres_features():
    query = """
        SELECT *
        FROM staging.fct_churn_ltv_features
        ORDER BY customer_id;
    """

    df = pd.read_sql(query, engine)

    print("PostgreSQL feature data loaded successfully!")
    print("Rows:", len(df))
    print("Columns:", len(df.columns))

    output_folder = "data/processed"
    os.makedirs(output_folder, exist_ok=True)

    output_file = os.path.join(
        output_folder,
        "postgres_fct_churn_ltv_features.csv"
    )

    df.to_csv(output_file, index=False)

    print("PostgreSQL feature data exported successfully!")
    print("File:", output_file)


if __name__ == "__main__":
    export_postgres_features()