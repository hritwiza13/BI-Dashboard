# Business Intelligence Dashboard

A comprehensive BI dashboard for sales and marketing analytics with interactive visualizations, KPI tracking, and automated reporting features.

## Features

- Interactive Visualizations
  - Sales trends
  - Customer acquisition
  - Conversion rate analysis
- KPI Tracking
  - Total sales
  - Customer count
  - Conversion rates
  - Average order value
- Real-time Analytics
  - Date range filtering
  - Dynamic updates
  - Detailed data view

## Technologies Used

- Python
- Streamlit
- Pandas
- Plotly
- SQL (for database integration)

## Setup Instructions

1. Clone the repository
2. Create a virtual environment:
   ```bash
   python -m venv venv
   source venv/bin/activate  # On Windows: venv\Scripts\activate
   ```
3. Install dependencies:
   ```bash
   pip install -r requirements.txt
   ```
4. Run the dashboard:
   ```bash
   streamlit run app.py
   ```

## Data Integration

The current version uses sample data. To integrate with your actual data source:

1. Modify the `generate_sample_data()` function in `app.py`
2. Connect to your database or data source
3. Update the data processing logic accordingly

## Customization

- Modify the KPI metrics in the dashboard
- Add new visualizations
- Customize the date range filter
- Add additional data sources

## Contributing

Feel free to submit issues and enhancement requests! 