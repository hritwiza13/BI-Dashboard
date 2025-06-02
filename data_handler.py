import pandas as pd
import os
from sqlalchemy import create_engine, text
from datetime import datetime, timedelta
import random

def get_db_connection():
    # Get database URL from environment variable
    database_url = os.getenv('DATABASE_URL')
    
    if not database_url:
        raise ValueError("DATABASE_URL environment variable is not set")
    
    # If using Render's DATABASE_URL, it might need modification
    if database_url.startswith('postgres://'):
        database_url = database_url.replace('postgres://', 'postgresql://', 1)
    
    try:
        engine = create_engine(database_url)
        # Test the connection
        with engine.connect() as conn:
            conn.execute(text("SELECT 1"))
        return engine
    except Exception as e:
        print(f"Error connecting to database: {str(e)}")
        raise

def fetch_sales_data(start_date, end_date):
    try:
        engine = get_db_connection()
        
        # Try to fetch from database first
        query = text("""
        SELECT date, sales, customers, conversion_rate
        FROM sales_data
        WHERE date BETWEEN :start_date AND :end_date
        ORDER BY date;
        """)
        
        df = pd.read_sql(query, engine, params={'start_date': start_date, 'end_date': end_date})
        
        # If no data in database, generate sample data
        if df.empty:
            print("No data found, generating sample data...")
            df = generate_sample_data(start_date, end_date)
            
            # Store the generated data in the database
            df.to_sql('sales_data', engine, if_exists='append', index=False)
            print("Sample data generated and stored in database")
        
        return df
        
    except Exception as e:
        print(f"Error fetching data: {str(e)}")
        # If database connection fails, return sample data
        return generate_sample_data(start_date, end_date)

def generate_sample_data(start_date, end_date):
    # Generate dates between start_date and end_date
    date_range = pd.date_range(start=start_date, end=end_date, freq='D')
    
    # Generate random data
    data = {
        'date': date_range,
        'sales': [random.randint(1000, 5000) for _ in range(len(date_range))],
        'customers': [random.randint(50, 200) for _ in range(len(date_range))],
        'conversion_rate': [random.uniform(0.1, 0.3) for _ in range(len(date_range))]
    }
    
    return pd.DataFrame(data)

# You can add more functions here to fetch other types of data if needed 