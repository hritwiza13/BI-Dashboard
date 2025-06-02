from sqlalchemy import create_engine, text
from datetime import datetime
import pandas as pd

# Replace with your actual database connection string
# Examples:
# PostgreSQL: 'postgresql://user:password@host:port/database'
# MySQL: 'mysql+mysqlconnector://user:password@host:port/database'
# SQLite: 'sqlite:///path/to/your/database.db'
DATABASE_URL = "sqlite:///./bi_dashboard.db" # Using a dummy SQLite for now

engine = create_engine(DATABASE_URL)

def fetch_sales_data(start_date: datetime, end_date: datetime) -> pd.DataFrame:
    """Fetches sales data from the database within the specified date range."""
    try:
        # Replace with your actual SQL query
        # This is a placeholder assuming a 'sales_data' table with 'date', 'sales', 'customers', 'conversion_rate' columns
        query = text("""
            SELECT date, sales, customers, conversion_rate
            FROM sales_data
            WHERE date BETWEEN :start_date AND :end_date
            ORDER BY date ASC
        """)
        with engine.connect() as connection:
            result = connection.execute(query, {'start_date': start_date, 'end_date': end_date})
            df = pd.DataFrame(result.fetchall(), columns=result.keys())
            # Ensure date column is datetime objects if not already
            if 'date' in df.columns:
                 df['date'] = pd.to_datetime(df['date'])
            return df
    except Exception as e:
        print(f"Error fetching data: {e}")
        return pd.DataFrame()

# You can add more functions here to fetch other types of data if needed 