# database.py
import pandas as pd
from sqlalchemy import create_engine, inspect, text
import os

DATABASE_URL = "sqlite:///./ecommerce.db" # SQLite database file in the current directory
engine = create_engine(DATABASE_URL)

def load_data_to_db():
    """Loads CSV data into SQLite tables."""
    BASE_DIR = os.path.dirname(os.path.abspath(__file__))
    data_dir = os.path.join(BASE_DIR, "data")
    if not os.path.exists(data_dir):
        print(f"Error: Data directory '{data_dir}' not found. Please run generate_data.py first.")
        return

    csv_files = {
        'product_ad_sales': 'product_ad_sales.csv',
        'product_total_sales': 'product_total_sales.csv',
        'product_eligibility': 'product_eligibility.csv'
    }

    for table_name, csv_file in csv_files.items():
        file_path = os.path.join(data_dir, csv_file)
        if os.path.exists(file_path):
            print(f"Loading {csv_file} into table {table_name}...")
            df = pd.read_csv(file_path)
            df.to_sql(table_name, engine, if_exists='replace', index=False)
            print(f"Successfully loaded {len(df)} records into {table_name}.")
        else:
            print(f"Warning: {csv_file} not found. Skipping table {table_name}.")

def get_db_schema():
    """Extracts and returns the database schema as a string."""
    inspector = inspect(engine)
    schema_info = []
    for table_name in inspector.get_table_names():
        schema_info.append(f"Table: {table_name}")
        columns = inspector.get_columns(table_name)
        for col in columns:
            schema_info.append(f"  - {col['name']} ({col['type']})")
        schema_info.append("") # Add a blank line for readability
    return "\n".join(schema_info)

def test_db_connection():
    """Tests the database connection and data retrieval."""
    try:
        with engine.connect() as connection:
            result = connection.execute(text("SELECT name FROM sqlite_master WHERE type='table';"))
            tables = [row for row in result]
            print(f"\nSuccessfully connected to DB. Tables found: {tables}")

            if 'product_total_sales' in tables:
                result = connection.execute(text("SELECT SUM(total_revenue) FROM product_total_sales;"))
                total_sales = result.scalar()
                print(f"Sample query (Total Sales): {total_sales}")
            else:
                print("Table 'product_total_sales' not found for sample query.")

    except Exception as e:
        print(f"Error connecting to database: {e}")

if __name__ == "__main__":
    load_data_to_db()
    test_db_connection()
    print("\nDatabase schema:\n", get_db_schema())