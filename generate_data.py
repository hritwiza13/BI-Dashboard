import pandas as pd
import numpy as np
from datetime import datetime, timedelta
from data_handler import get_db_connection
import os
from sqlalchemy import text

# Set database URL
os.environ['DATABASE_URL'] = 'postgresql://bi_dashboard_user:Y4CJcOwpda7FBq1IvXxZViic8o52wS6h@dpg-d0um76re5dus739m2ang-a.oregon-postgres.render.com/bi_dashboard_bpft'

def generate_realistic_data(start_date, end_date):
    # Generate dates
    date_range = pd.date_range(start=start_date, end=end_date, freq='D')
    n_days = len(date_range)
    
    # Base values with some randomness
    base_sales = 3000
    base_customers = 100
    base_conversion = 0.15
    
    # Add weekly seasonality
    weekly_pattern = np.sin(np.arange(n_days) * (2 * np.pi / 7)) * 0.2
    
    # Add monthly trend
    monthly_trend = np.linspace(0, 0.3, n_days)
    
    # Generate sales with trend and seasonality
    sales = base_sales * (1 + weekly_pattern + monthly_trend) + np.random.normal(0, 200, n_days)
    sales = np.maximum(sales, 500)  # Ensure minimum sales
    
    # Generate customers with correlation to sales
    customers = (sales / 30) * (1 + np.random.normal(0, 0.1, n_days))
    customers = np.maximum(customers, 20)  # Ensure minimum customers
    
    # Calculate conversion rate
    conversion_rate = customers / (customers * 5)  # Assuming 5x more visitors than customers
    conversion_rate = np.clip(conversion_rate, 0.05, 0.35)  # Keep within realistic range
    
    # Create DataFrame
    data = {
        'date': date_range,
        'sales': np.round(sales, 2),
        'customers': np.round(customers).astype(int),
        'conversion_rate': np.round(conversion_rate, 4)
    }
    
    return pd.DataFrame(data)

def insert_data():
    try:
        print("Connecting to database...")
        engine = get_db_connection()
        print("✅ Database connection successful!")
        
        # Use fixed historical date range
        end_date = datetime(2024, 5, 31)  # End of May 2024
        start_date = datetime(2023, 6, 1)  # Start of June 2023
        
        print(f"\nGenerating data from {start_date.date()} to {end_date.date()}...")
        df = generate_realistic_data(start_date, end_date)
        
        # Check for existing dates
        print("\nChecking for existing dates...")
        query = text("SELECT date FROM sales_data WHERE date BETWEEN :start_date AND :end_date")
        with engine.connect() as conn:
            existing_dates = pd.read_sql(query, conn, params={'start_date': start_date, 'end_date': end_date})
        
        if not existing_dates.empty:
            # Convert dates to datetime for proper comparison
            existing_dates['date'] = pd.to_datetime(existing_dates['date'])
            df['date'] = pd.to_datetime(df['date'])
            
            # Use merge to find non-duplicate dates
            merged = pd.merge(df, existing_dates, on='date', how='left', indicator=True)
            df = merged[merged['_merge'] == 'left_only'].drop('_merge', axis=1)
            
            print(f"Found {len(existing_dates)} existing dates. Will insert {len(df)} new records.")
        
        if len(df) == 0:
            print("No new data to insert!")
            return
        
        # Insert data into database
        print("\nInserting data into database...")
        df.to_sql('sales_data', engine, if_exists='append', index=False)
        print(f"✅ Successfully inserted {len(df)} records!")
        
        # Print some statistics
        print("\nData Statistics:")
        print(f"Total Sales: ${df['sales'].sum():,.2f}")
        print(f"Total Customers: {df['customers'].sum():,}")
        print(f"Average Conversion Rate: {df['conversion_rate'].mean()*100:.1f}%")
        print(f"Average Daily Sales: ${df['sales'].mean():,.2f}")
        print(f"Average Daily Customers: {df['customers'].mean():.1f}")
        
    except Exception as e:
        print(f"❌ Error: {str(e)}")
        raise

if __name__ == "__main__":
    insert_data() 