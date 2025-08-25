from flask import Flask, request, jsonify, render_template
from flask_cors import CORS
import pandas as pd
import json
import os
import sys

# Add src to Python path
sys.path.append(os.path.join(os.path.dirname(__file__), '..', 'src'))

from data.processor import DataProcessor
from ml.forecasting import Forecaster
from ml.clustering import ClusterAnalyzer
from api.nlp_query import NLPQueryProcessor

app = Flask(__name__)
CORS(app)

# Configuration
app.config['MAX_CONTENT_LENGTH'] = 100 * 1024 * 1024  # 100MB max file size
app.config['UPLOAD_FOLDER'] = 'data/raw'

# Initialize components
data_processor = DataProcessor()
forecaster = Forecaster()
cluster_analyzer = ClusterAnalyzer()
nlp_processor = NLPQueryProcessor()

@app.route('/')
def index():
    """Home page"""
    return jsonify({
        "message": "Welcome to CityPulse API",
        "version": "1.0.0",
        "endpoints": {
            "upload": "/api/upload",
            "process": "/api/process",
            "visualize": "/api/visualize",
            "forecast": "/api/forecast",
            "cluster": "/api/cluster",
            "query": "/api/query"
        }
    })

@app.route('/api/upload', methods=['POST'])
def upload_data():
    """Upload and preview dataset"""
    try:
        if 'file' not in request.files:
            return jsonify({"error": "No file provided"}), 400
        
        file = request.files['file']
        if file.filename == '':
            return jsonify({"error": "No file selected"}), 400
        
        if file and file.filename.endswith('.csv'):
            # Read the uploaded CSV
            data = pd.read_csv(file)
            
            # Basic info about the dataset
            info = {
                "filename": file.filename,
                "shape": data.shape,
                "columns": list(data.columns),
                "dtypes": data.dtypes.to_dict(),
                "memory_usage": data.memory_usage(deep=True).sum(),
                "preview": data.head().to_dict('records'),
                "null_counts": data.isnull().sum().to_dict()
            }
            
            return jsonify({
                "status": "success",
                "message": "File uploaded successfully",
                "data_info": info
            })
        
        return jsonify({"error": "Only CSV files are supported"}), 400
        
    except Exception as e:
        return jsonify({"error": str(e)}), 500

@app.route('/api/process', methods=['POST'])
def process_data():
    """Process and clean dataset"""
    try:
        data = request.get_json()
        
        if 'data' not in data:
            return jsonify({"error": "No data provided"}), 400
        
        # Convert JSON to DataFrame
        df = pd.DataFrame(data['data'])
        
        # Process the data
        processed_df = data_processor.clean_data(df)
        
        # Return processed data info
        result = {
            "status": "success",
            "message": "Data processed successfully",
            "processed_shape": processed_df.shape,
            "processed_preview": processed_df.head().to_dict('records'),
            "processing_summary": data_processor.get_processing_summary()
        }
        
        return jsonify(result)
        
    except Exception as e:
        return jsonify({"error": str(e)}), 500

@app.route('/api/visualize', methods=['POST'])
def create_visualization():
    """Generate visualization data"""
    try:
        request_data = request.get_json()
        
        if 'data' not in request_data or 'viz_type' not in request_data:
            return jsonify({"error": "Data and visualization type required"}), 400
        
        df = pd.DataFrame(request_data['data'])
        viz_type = request_data['viz_type']
        
        # Generate visualization based on type
        if viz_type == 'correlation_heatmap':
            result = generate_correlation_heatmap(df)
        elif viz_type == 'time_series':
            result = generate_time_series_data(df, request_data.get('params', {}))
        elif viz_type == 'geographic':
            result = generate_geographic_data(df, request_data.get('params', {}))
        elif viz_type == 'distribution':
            result = generate_distribution_data(df, request_data.get('params', {}))
        else:
            return jsonify({"error": "Unsupported visualization type"}), 400
        
        return jsonify({
            "status": "success",
            "visualization_data": result
        })
        
    except Exception as e:
        return jsonify({"error": str(e)}), 500

@app.route('/api/forecast', methods=['POST'])
def forecast_data():
    """Generate forecasts using time series models"""
    try:
        request_data = request.get_json()
        
        if 'data' not in request_data:
            return jsonify({"error": "No data provided"}), 400
        
        df = pd.DataFrame(request_data['data'])
        params = request_data.get('params', {})
        
        # Extract parameters
        date_column = params.get('date_column')
        value_column = params.get('value_column')
        forecast_periods = params.get('forecast_periods', 30)
        
        if not date_column or not value_column:
            return jsonify({"error": "Date and value columns required"}), 400
        
        # Generate forecast
        forecast_result = forecaster.generate_forecast(
            df, date_column, value_column, forecast_periods
        )
        
        return jsonify({
            "status": "success",
            "forecast": forecast_result
        })
        
    except Exception as e:
        return jsonify({"error": str(e)}), 500

@app.route('/api/cluster', methods=['POST'])
def cluster_analysis():
    """Perform clustering analysis"""
    try:
        request_data = request.get_json()
        
        if 'data' not in request_data:
            return jsonify({"error": "No data provided"}), 400
        
        df = pd.DataFrame(request_data['data'])
        params = request_data.get('params', {})
        
        # Extract parameters
        features = params.get('features', [])
        n_clusters = params.get('n_clusters', 3)
        
        if not features:
            return jsonify({"error": "Feature columns required"}), 400
        
        # Perform clustering
        cluster_result = cluster_analyzer.perform_clustering(
            df, features, n_clusters
        )
        
        return jsonify({
            "status": "success",
            "clustering": cluster_result
        })
        
    except Exception as e:
        return jsonify({"error": str(e)}), 500

@app.route('/api/query', methods=['POST'])
def natural_language_query():
    """Process natural language queries"""
    try:
        request_data = request.get_json()
        
        if 'query' not in request_data or 'data' not in request_data:
            return jsonify({"error": "Query and data required"}), 400
        
        query = request_data['query']
        df = pd.DataFrame(request_data['data'])
        
        # Process the natural language query
        result = nlp_processor.process_query(query, df)
        
        return jsonify({
            "status": "success",
            "query": query,
            "result": result
        })
        
    except Exception as e:
        return jsonify({"error": str(e)}), 500

@app.route('/api/health', methods=['GET'])
def health_check():
    """Health check endpoint"""
    return jsonify({
        "status": "healthy",
        "timestamp": pd.Timestamp.now().isoformat()
    })

# Helper functions for visualizations
def generate_correlation_heatmap(df):
    """Generate correlation heatmap data"""
    numeric_columns = df.select_dtypes(include=['number']).columns.tolist()
    
    if len(numeric_columns) < 2:
        raise ValueError("Need at least 2 numeric columns for correlation")
    
    correlation_matrix = df[numeric_columns].corr()
    
    return {
        "type": "heatmap",
        "data": correlation_matrix.to_dict(),
        "columns": numeric_columns
    }

def generate_time_series_data(df, params):
    """Generate time series visualization data"""
    date_column = params.get('date_column')
    value_column = params.get('value_column')
    
    if not date_column or not value_column:
        raise ValueError("Date and value columns required")
    
    # Convert date column to datetime
    df[date_column] = pd.to_datetime(df[date_column])
    
    # Sort by date
    df_sorted = df.sort_values(date_column)
    
    return {
        "type": "time_series",
        "dates": df_sorted[date_column].dt.strftime('%Y-%m-%d').tolist(),
        "values": df_sorted[value_column].tolist(),
        "x_label": date_column,
        "y_label": value_column
    }

def generate_geographic_data(df, params):
    """Generate geographic visualization data"""
    lat_column = params.get('lat_column')
    lon_column = params.get('lon_column')
    
    if not lat_column or not lon_column:
        raise ValueError("Latitude and longitude columns required")
    
    # Filter out null coordinates
    geo_df = df.dropna(subset=[lat_column, lon_column])
    
    return {
        "type": "geographic",
        "points": [
            {
                "lat": row[lat_column],
                "lon": row[lon_column],
                "data": row.to_dict()
            }
            for _, row in geo_df.iterrows()
        ],
        "center": {
            "lat": geo_df[lat_column].mean(),
            "lon": geo_df[lon_column].mean()
        }
    }

def generate_distribution_data(df, params):
    """Generate distribution visualization data"""
    column = params.get('column')
    
    if not column:
        raise ValueError("Column required for distribution")
    
    if df[column].dtype in ['int64', 'float64']:
        # Numeric distribution
        values = df[column].dropna()
        
        return {
            "type": "histogram",
            "values": values.tolist(),
            "column": column,
            "stats": {
                "mean": values.mean(),
                "median": values.median(),
                "std": values.std(),
                "min": values.min(),
                "max": values.max()
            }
        }
    else:
        # Categorical distribution
        value_counts = df[column].value_counts().head(20)
        
        return {
            "type": "bar",
            "categories": value_counts.index.tolist(),
            "counts": value_counts.values.tolist(),
            "column": column
        }

if __name__ == '__main__':
    # Create upload directory if it doesn't exist
    os.makedirs(app.config['UPLOAD_FOLDER'], exist_ok=True)
    
    # Run the Flask app
    app.run(debug=True, host='0.0.0.0', port=5000)
