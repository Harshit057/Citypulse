import streamlit as st
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
import folium
from streamlit_folium import st_folium
import sys
import os

# Add src to Python path
sys.path.append(os.path.join(os.path.dirname(__file__), '..', 'src'))

from data.processor import DataProcessor
from visualization.maps import MapGenerator
from visualization.charts import ChartGenerator
from ml.forecasting import Forecaster
from ml.clustering import ClusterAnalyzer
from api.nlp_query import NLPQueryProcessor

# Page configuration
st.set_page_config(
    page_title="CityPulse - Urban Analytics Platform",
    page_icon="🏙️",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Custom CSS
st.markdown("""
<style>
    .main-header {
        font-size: 2.5rem;
        color: #1f77b4;
        text-align: center;
        margin-bottom: 1rem;
    }
    .metric-card {
        background-color: #f0f2f6;
        padding: 1rem;
        border-radius: 0.5rem;
        border-left: 4px solid #1f77b4;
    }
</style>
""", unsafe_allow_html=True)

# Initialize session state
if 'data' not in st.session_state:
    st.session_state.data = None
if 'processed_data' not in st.session_state:
    st.session_state.processed_data = None

def main():
    st.markdown('<h1 class="main-header">🏙️ CityPulse Urban Analytics Platform</h1>', unsafe_allow_html=True)
    
    # Sidebar for navigation
    st.sidebar.title("Navigation")
    page = st.sidebar.selectbox(
        "Choose a section:",
        ["Data Upload", "Data Exploration", "Visualizations", "ML Analysis", "Natural Language Queries"]
    )
    
    if page == "Data Upload":
        data_upload_page()
    elif page == "Data Exploration":
        data_exploration_page()
    elif page == "Visualizations":
        visualization_page()
    elif page == "ML Analysis":
        ml_analysis_page()
    elif page == "Natural Language Queries":
        nlp_query_page()

def data_upload_page():
    st.header("📊 Data Upload & Processing")
    
    # File upload
    uploaded_file = st.file_uploader(
        "Choose a CSV file",
        type=['csv'],
        help="Upload city-level datasets (traffic, pollution, population, etc.)"
    )
    
    if uploaded_file is not None:
        try:
            # Load data
            data = pd.read_csv(uploaded_file)
            st.session_state.data = data
            
            st.success(f"✅ Successfully loaded {len(data)} rows and {len(data.columns)} columns")
            
            # Data preview
            st.subheader("Data Preview")
            st.dataframe(data.head())
            
            # Data info
            col1, col2, col3 = st.columns(3)
            with col1:
                st.metric("Total Rows", len(data))
            with col2:
                st.metric("Total Columns", len(data.columns))
            with col3:
                st.metric("Memory Usage", f"{data.memory_usage(deep=True).sum() / 1024**2:.2f} MB")
            
            # Data processing options
            st.subheader("Data Processing Options")
            
            if st.button("🔄 Process Data"):
                processor = DataProcessor()
                processed_data = processor.clean_data(data)
                st.session_state.processed_data = processed_data
                st.success("Data processed successfully!")
                st.dataframe(processed_data.head())
                
        except Exception as e:
            st.error(f"Error loading data: {str(e)}")
    
    # Sample datasets
    st.subheader("📋 Try Sample Datasets")
    col1, col2 = st.columns(2)
    
    with col1:
        if st.button("🚦 Load Traffic Data Sample"):
            load_sample_traffic_data()
    
    with col2:
        if st.button("🌫️ Load Air Quality Sample"):
            load_sample_air_quality_data()

def data_exploration_page():
    st.header("🔍 Data Exploration")
    
    if st.session_state.data is None:
        st.warning("Please upload data first in the Data Upload section.")
        return
    
    data = st.session_state.data
    
    # Basic statistics
    st.subheader("📈 Basic Statistics")
    st.dataframe(data.describe())
    
    # Column analysis
    st.subheader("🔍 Column Analysis")
    selected_column = st.selectbox("Select column to analyze:", data.columns)
    
    if selected_column:
        col1, col2 = st.columns(2)
        
        with col1:
            # Histogram
            if data[selected_column].dtype in ['int64', 'float64']:
                fig = px.histogram(data, x=selected_column, title=f"Distribution of {selected_column}")
                st.plotly_chart(fig, use_container_width=True)
            else:
                # Value counts for categorical data
                value_counts = data[selected_column].value_counts().head(10)
                fig = px.bar(x=value_counts.index, y=value_counts.values, 
                           title=f"Top 10 values in {selected_column}")
                st.plotly_chart(fig, use_container_width=True)
        
        with col2:
            st.write("**Column Info:**")
            st.write(f"- Type: {data[selected_column].dtype}")
            st.write(f"- Non-null values: {data[selected_column].count()}")
            st.write(f"- Null values: {data[selected_column].isnull().sum()}")
            st.write(f"- Unique values: {data[selected_column].nunique()}")

def visualization_page():
    st.header("📊 Visualizations")
    
    if st.session_state.data is None:
        st.warning("Please upload data first in the Data Upload section.")
        return
    
    data = st.session_state.data
    
    # Visualization type selection
    viz_type = st.selectbox(
        "Choose visualization type:",
        ["Heatmap", "Line Chart", "Scatter Plot", "Bar Chart", "Geographic Map"]
    )
    
    if viz_type == "Heatmap":
        create_heatmap(data)
    elif viz_type == "Line Chart":
        create_line_chart(data)
    elif viz_type == "Scatter Plot":
        create_scatter_plot(data)
    elif viz_type == "Bar Chart":
        create_bar_chart(data)
    elif viz_type == "Geographic Map":
        create_geographic_map(data)

def ml_analysis_page():
    st.header("🤖 Machine Learning Analysis")
    
    if st.session_state.data is None:
        st.warning("Please upload data first in the Data Upload section.")
        return
    
    data = st.session_state.data
    
    # ML task selection
    ml_task = st.selectbox(
        "Choose ML task:",
        ["Time Series Forecasting", "Clustering Analysis", "Anomaly Detection"]
    )
    
    if ml_task == "Time Series Forecasting":
        time_series_forecasting(data)
    elif ml_task == "Clustering Analysis":
        clustering_analysis(data)
    elif ml_task == "Anomaly Detection":
        anomaly_detection(data)

def nlp_query_page():
    st.header("💬 Natural Language Queries")
    
    if st.session_state.data is None:
        st.warning("Please upload data first in the Data Upload section.")
        return
    
    st.write("Ask questions about your data in natural language!")
    
    # Sample queries
    st.subheader("📝 Sample Queries")
    sample_queries = [
        "Show me areas with highest pollution levels",
        "What are the traffic patterns during rush hours?",
        "Which neighborhoods have the highest crime rates?",
        "Display temperature trends over time"
    ]
    
    for query in sample_queries:
        if st.button(f"💡 {query}"):
            st.session_state.nlp_query = query
    
    # Custom query input
    user_query = st.text_input("Enter your question:", 
                              value=st.session_state.get('nlp_query', ''))
    
    if user_query and st.button("🔍 Process Query"):
        with st.spinner("Processing query..."):
            try:
                nlp_processor = NLPQueryProcessor()
                result = nlp_processor.process_query(user_query, st.session_state.data)
                st.write("**Query Result:**")
                st.write(result)
            except Exception as e:
                st.error(f"Error processing query: {str(e)}")

# Helper functions for visualizations
def create_heatmap(data):
    st.subheader("🔥 Heatmap")
    numeric_columns = data.select_dtypes(include=['number']).columns.tolist()
    
    if len(numeric_columns) < 2:
        st.warning("Need at least 2 numeric columns for heatmap.")
        return
    
    selected_columns = st.multiselect("Select columns for heatmap:", numeric_columns)
    
    if selected_columns:
        correlation_matrix = data[selected_columns].corr()
        fig = px.imshow(correlation_matrix, text_auto=True, aspect="auto",
                       title="Correlation Heatmap")
        st.plotly_chart(fig, use_container_width=True)

def create_line_chart(data):
    st.subheader("📈 Line Chart")
    
    x_column = st.selectbox("Select X-axis:", data.columns)
    y_column = st.selectbox("Select Y-axis:", data.select_dtypes(include=['number']).columns)
    
    if x_column and y_column:
        fig = px.line(data, x=x_column, y=y_column, title=f"{y_column} vs {x_column}")
        st.plotly_chart(fig, use_container_width=True)

def create_scatter_plot(data):
    st.subheader("📊 Scatter Plot")
    
    numeric_columns = data.select_dtypes(include=['number']).columns.tolist()
    
    x_column = st.selectbox("Select X-axis:", numeric_columns)
    y_column = st.selectbox("Select Y-axis:", numeric_columns)
    
    if x_column and y_column:
        fig = px.scatter(data, x=x_column, y=y_column, title=f"{y_column} vs {x_column}")
        st.plotly_chart(fig, use_container_width=True)

def create_bar_chart(data):
    st.subheader("📊 Bar Chart")
    
    x_column = st.selectbox("Select category column:", data.columns)
    y_column = st.selectbox("Select value column:", data.select_dtypes(include=['number']).columns)
    
    if x_column and y_column:
        # Aggregate data if needed
        agg_data = data.groupby(x_column)[y_column].mean().reset_index()
        fig = px.bar(agg_data, x=x_column, y=y_column, title=f"Average {y_column} by {x_column}")
        st.plotly_chart(fig, use_container_width=True)

def create_geographic_map(data):
    st.subheader("🗺️ Geographic Map")
    
    # Check for latitude and longitude columns
    lat_columns = [col for col in data.columns if 'lat' in col.lower()]
    lon_columns = [col for col in data.columns if 'lon' in col.lower() or 'lng' in col.lower()]
    
    if not lat_columns or not lon_columns:
        st.warning("Geographic data requires latitude and longitude columns.")
        return
    
    lat_col = st.selectbox("Select latitude column:", lat_columns)
    lon_col = st.selectbox("Select longitude column:", lon_columns)
    
    if lat_col and lon_col:
        # Create folium map
        center_lat = data[lat_col].mean()
        center_lon = data[lon_col].mean()
        
        m = folium.Map(location=[center_lat, center_lon], zoom_start=10)
        
        # Add points to map
        for idx, row in data.iterrows():
            if pd.notna(row[lat_col]) and pd.notna(row[lon_col]):
                folium.Marker(
                    [row[lat_col], row[lon_col]],
                    popup=f"Point {idx}"
                ).add_to(m)
        
        # Display map
        st_folium(m, width=700, height=500)

# ML helper functions
def time_series_forecasting(data):
    st.subheader("📈 Time Series Forecasting")
    
    date_columns = data.select_dtypes(include=['datetime64', 'object']).columns.tolist()
    numeric_columns = data.select_dtypes(include=['number']).columns.tolist()
    
    date_col = st.selectbox("Select date column:", date_columns)
    value_col = st.selectbox("Select value column:", numeric_columns)
    
    if date_col and value_col:
        st.info("Time series forecasting implementation would go here using Prophet or ARIMA models.")

def clustering_analysis(data):
    st.subheader("🎯 Clustering Analysis")
    
    numeric_columns = data.select_dtypes(include=['number']).columns.tolist()
    selected_features = st.multiselect("Select features for clustering:", numeric_columns)
    
    if len(selected_features) >= 2:
        n_clusters = st.slider("Number of clusters:", 2, 10, 3)
        st.info(f"K-means clustering with {n_clusters} clusters would be performed on selected features.")

def anomaly_detection(data):
    st.subheader("🚨 Anomaly Detection")
    
    numeric_columns = data.select_dtypes(include=['number']).columns.tolist()
    selected_column = st.selectbox("Select column for anomaly detection:", numeric_columns)
    
    if selected_column:
        st.info("Isolation Forest or statistical methods would be used to detect anomalies.")

# Sample data loading functions
def load_sample_traffic_data():
    """Load sample traffic data"""
    import numpy as np
    
    # Generate sample traffic data
    np.random.seed(42)
    n_points = 1000
    
    sample_data = pd.DataFrame({
        'latitude': np.random.normal(28.6139, 0.1, n_points),  # Delhi coordinates
        'longitude': np.random.normal(77.2090, 0.1, n_points),
        'timestamp': pd.date_range('2024-01-01', periods=n_points, freq='H'),
        'traffic_volume': np.random.poisson(50, n_points),
        'avg_speed': np.random.normal(30, 10, n_points),
        'congestion_level': np.random.choice(['Low', 'Medium', 'High'], n_points)
    })
    
    st.session_state.data = sample_data
    st.success("Sample traffic data loaded!")
    st.dataframe(sample_data.head())

def load_sample_air_quality_data():
    """Load sample air quality data"""
    import numpy as np
    
    # Generate sample air quality data
    np.random.seed(42)
    n_points = 500
    
    sample_data = pd.DataFrame({
        'latitude': np.random.normal(28.6139, 0.15, n_points),
        'longitude': np.random.normal(77.2090, 0.15, n_points),
        'timestamp': pd.date_range('2024-01-01', periods=n_points, freq='D'),
        'pm25': np.random.exponential(50, n_points),
        'pm10': np.random.exponential(80, n_points),
        'no2': np.random.exponential(30, n_points),
        'aqi': np.random.randint(0, 300, n_points),
        'station_id': [f'AQ_{i:03d}' for i in range(n_points)]
    })
    
    st.session_state.data = sample_data
    st.success("Sample air quality data loaded!")
    st.dataframe(sample_data.head())

if __name__ == "__main__":
    main()
