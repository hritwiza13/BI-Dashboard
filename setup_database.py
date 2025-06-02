from sqlalchemy import create_engine, text
import pandas as pd
from datetime import datetime, timedelta
import numpy as np

# Create SQLite database
DATABASE_URL = "sqlite:///./bi_dashboard.db"
engine = create_engine(DATABASE_URL)

# Create table
create_table_query = text("""
    CREATE TABLE IF NOT EXISTS sales_data (
        date DATE PRIMARY KEY,
        sales FLOAT,
        customers INTEGER,
        conversion_rate FLOAT
    )
""")

# Generate sample data
def generate_sample_data():
    dates = pd.date_range(start='2024-01-01', end='2024-03-31', freq='D')
    sales_data = pd.DataFrame({
        'date': dates,
        'sales': np.random.normal(1000, 200, len(dates)),
        'customers': np.random.normal(50, 10, len(dates)).astype(int),
        'conversion_rate': np.random.normal(0.15, 0.02, len(dates))
    })
    return sales_data

# Insert data
def insert_data():
    try:
        with engine.connect() as connection:
            # Create table
            connection.execute(create_table_query)
            connection.commit()

            # Generate and insert sample data
            data = generate_sample_data()
            data.to_sql('sales_data', engine, if_exists='replace', index=False)
            print("Database setup completed successfully!")
    except Exception as e:
        print(f"Error setting up database: {e}")

if __name__ == "__main__":
    insert_data() 