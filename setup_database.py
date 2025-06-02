import os
from sqlalchemy import create_engine, text
from data_handler import get_db_connection

def setup_database():
    try:
        engine = get_db_connection()
        
        # Create sales_data table if it doesn't exist
        create_table_query = """
        CREATE TABLE IF NOT EXISTS sales_data (
            id SERIAL PRIMARY KEY,
            date DATE NOT NULL,
            sales DECIMAL(10,2) NOT NULL,
            customers INTEGER NOT NULL,
            conversion_rate DECIMAL(5,4) NOT NULL,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        );
        
        -- Create index on date column for better query performance
        CREATE INDEX IF NOT EXISTS idx_sales_data_date ON sales_data(date);
        
        -- Add constraint to ensure unique dates
        DO $$ 
        BEGIN
            IF NOT EXISTS (
                SELECT 1 FROM pg_constraint 
                WHERE conname = 'sales_data_date_unique'
            ) THEN
                ALTER TABLE sales_data ADD CONSTRAINT sales_data_date_unique UNIQUE (date);
            END IF;
        END $$;
        """
        
        with engine.connect() as connection:
            connection.execute(text(create_table_query))
            connection.commit()
            
        print("Database setup completed successfully!")
        
    except Exception as e:
        print(f"Error setting up database: {str(e)}")
        raise

if __name__ == "__main__":
    setup_database() 