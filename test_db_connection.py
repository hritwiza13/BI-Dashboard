from data_handler import get_db_connection
from setup_database import setup_database
import os

# Set database URL
os.environ['DATABASE_URL'] = 'postgresql://bi_dashboard_user:Y4CJcOwpda7FBq1IvXxZViic8o52wS6h@dpg-d0um76re5dus739m2ang-a.oregon-postgres.render.com/bi_dashboard_bpft'

def test_connection():
    try:
        print("Testing database connection...")
        engine = get_db_connection()
        print("✅ Database connection successful!")
        
        print("\nSetting up database tables...")
        setup_database()
        print("✅ Database setup completed!")
        
        # Test data insertion
        print("\nTesting data insertion...")
        from data_handler import generate_sample_data
        from datetime import datetime, timedelta
        
        # Generate sample data for the last 30 days
        end_date = datetime.now()
        start_date = end_date - timedelta(days=30)
        
        df = generate_sample_data(start_date, end_date)
        df.to_sql('sales_data', engine, if_exists='append', index=False)
        print(f"✅ Successfully inserted {len(df)} records!")
        
    except Exception as e:
        print(f"❌ Error: {str(e)}")
        raise

if __name__ == "__main__":
    test_connection() 