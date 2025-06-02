import streamlit as st
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
from datetime import datetime, timedelta
import numpy as np
from data_handler import fetch_sales_data

# Page configuration
st.set_page_config(
    page_title="Business Intelligence Dashboard",
    page_icon="📊",
    layout="wide"
)

# Custom CSS
st.markdown("""
    <style>
    .main {
        padding: 2rem;
    }
    .stMetric {
        background-color: #f0f2f6;
        padding: 1rem;
        border-radius: 0.5rem;
    }
    </style>
""", unsafe_allow_html=True)

# Header
st.title("📊 Business Intelligence Dashboard")
st.markdown("---")

# Sidebar filters
st.sidebar.header("Filters")
date_range = st.sidebar.date_input(
    "Select Date Range",
    value=(datetime.now() - timedelta(days=30), datetime.now())
)

# Load data from database
try:
    data = fetch_sales_data(date_range[0], date_range[1])
    if data.empty:
        st.warning("No data found for the selected date range. Please try a different range.")
        st.stop()
except Exception as e:
    st.error(f"Error loading data: {str(e)}")
    st.stop()

# Function to convert DataFrame to CSV
@st.cache_data
def convert_df_to_csv(df):
    # IMPORTANT: Cache the conversion to prevent computation on every rerun
    return df.to_csv(index=False).encode('utf-8')

csv_data = convert_df_to_csv(data)

# KPI Cards
col1, col2, col3, col4 = st.columns(4)

with col1:
    st.metric(
        "Total Sales",
        f"${data['sales'].sum():,.2f}",
        f"{((data['sales'].iloc[-1] - data['sales'].iloc[0]) / data['sales'].iloc[0] * 100):.1f}%"
    )

with col2:
    st.metric(
        "Total Customers",
        f"{data['customers'].sum():,.0f}",
        f"{((data['customers'].iloc[-1] - data['customers'].iloc[0]) / data['customers'].iloc[0] * 100):.1f}%"
    )

with col3:
    st.metric(
        "Average Conversion Rate",
        f"{data['conversion_rate'].mean():.1%}",
        f"{((data['conversion_rate'].iloc[-1] - data['conversion_rate'].iloc[0]) / data['conversion_rate'].iloc[0] * 100):.1f}%"
    )

with col4:
    st.metric(
        "Average Order Value",
        f"${(data['sales'].sum() / data['customers'].sum()):,.2f}",
        f"{((data['sales'].iloc[-1] / data['customers'].iloc[-1]) - (data['sales'].iloc[0] / data['customers'].iloc[0])) / (data['sales'].iloc[0] / data['customers'].iloc[0]) * 100:.1f}%"
    )

# Export button
st.download_button(
    label="Export Report",
    data=csv_data,
    file_name='sales_data_report.csv',
    mime='text/csv',
    help="Download the current data as a CSV file"
)

# Charts
st.markdown("### Sales Analytics")
col1, col2 = st.columns(2)

with col1:
    # Sales Trend
    fig_sales = px.line(
        data,
        x='date',
        y='sales',
        title='Daily Sales Trend'
    )
    st.plotly_chart(fig_sales, use_container_width=True)

with col2:
    # Customer Acquisition
    fig_customers = px.bar(
        data,
        x='date',
        y='customers',
        title='Daily Customer Acquisition'
    )
    st.plotly_chart(fig_customers, use_container_width=True)

# Conversion Rate Analysis
st.markdown("### Conversion Rate Analysis")
fig_conversion = px.line(
    data,
    x='date',
    y='conversion_rate',
    title='Conversion Rate Trend'
)
st.plotly_chart(fig_conversion, use_container_width=True)

# Data Table
st.markdown("### Detailed Data")
st.dataframe(
    data.style.format({
        'sales': '${:,.2f}',
        'customers': '{:,.0f}',
        'conversion_rate': '{:.1%}'
    }),
    use_container_width=True
) 