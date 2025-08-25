# CityPulse Test Suite

import unittest
import pandas as pd
import numpy as np
import sys
import os

# Add src to path for testing
sys.path.append(os.path.join(os.path.dirname(__file__), '..', 'src'))

from data.processor import DataProcessor
from ml.clustering import ClusterAnalyzer
from ml.forecasting import Forecaster
from api.nlp_query import NLPQueryProcessor

class TestDataProcessor(unittest.TestCase):
    """Test the DataProcessor class"""
    
    def setUp(self):
        self.processor = DataProcessor()
        
        # Create sample data
        self.sample_data = pd.DataFrame({
            'Date': pd.date_range('2024-01-01', periods=100, freq='D'),
            'Traffic Volume': np.random.randint(50, 200, 100),
            'Air Quality Index': np.random.randint(20, 300, 100),
            'Temperature': np.random.normal(25, 5, 100),
            'Latitude': np.random.normal(28.6, 0.1, 100),
            'Longitude': np.random.normal(77.2, 0.1, 100),
            'Category': np.random.choice(['High', 'Medium', 'Low'], 100)
        })
        
        # Add some missing values
        self.sample_data.loc[5:10, 'Air Quality Index'] = np.nan
        self.sample_data.loc[15:20, 'Temperature'] = np.nan
    
    def test_clean_data(self):
        """Test data cleaning functionality"""
        cleaned_data = self.processor.clean_data(self.sample_data)
        
        # Check that data is cleaned
        self.assertIsInstance(cleaned_data, pd.DataFrame)
        self.assertGreater(len(cleaned_data), 0)
        
        # Check that missing values are handled
        self.assertEqual(cleaned_data.isnull().sum().sum(), 0)
    
    def test_validate_geographic_data(self):
        """Test geographic data validation"""
        validation = self.processor.validate_geographic_data(self.sample_data)
        
        self.assertTrue(validation['has_coordinates'])
        self.assertIn('latitude', validation['coordinate_columns'])
        self.assertIn('longitude', validation['coordinate_columns'])
    
    def test_generate_data_profile(self):
        """Test data profiling"""
        profile = self.processor.generate_data_profile(self.sample_data)
        
        self.assertIn('basic_info', profile)
        self.assertIn('column_stats', profile)
        self.assertIn('missing_data', profile)
        self.assertEqual(profile['basic_info']['shape'], self.sample_data.shape)

class TestClusterAnalyzer(unittest.TestCase):
    """Test the ClusterAnalyzer class"""
    
    def setUp(self):
        self.analyzer = ClusterAnalyzer()
        
        # Create sample geographic data
        self.geo_data = pd.DataFrame({
            'latitude': np.random.normal(28.6, 0.1, 100),
            'longitude': np.random.normal(77.2, 0.1, 100),
            'value': np.random.randint(1, 100, 100)
        })
    
    def test_perform_clustering(self):
        """Test K-means clustering"""
        features = ['latitude', 'longitude']
        results = self.analyzer.perform_clustering(self.geo_data, features, n_clusters=3)
        
        self.assertIn('labels', results)
        self.assertIn('cluster_centers', results)
        self.assertIn('silhouette_score', results)
        self.assertEqual(len(results['labels']), len(self.geo_data))
    
    def test_detect_hotspots(self):
        """Test hotspot detection"""
        results = self.analyzer.detect_hotspots(
            self.geo_data, 'latitude', 'longitude', 'value'
        )
        
        self.assertIn('clustering_results', results)
        self.assertIn('hotspot_analysis', results)
        self.assertIn('ranked_hotspots', results)

class TestForecaster(unittest.TestCase):
    """Test the Forecaster class"""
    
    def setUp(self):
        self.forecaster = Forecaster()
        
        # Create sample time series data
        dates = pd.date_range('2024-01-01', periods=50, freq='D')
        values = np.cumsum(np.random.randn(50)) + 100
        
        self.ts_data = pd.DataFrame({
            'date': dates,
            'value': values
        })
    
    def test_linear_trend_forecast(self):
        """Test linear trend forecasting"""
        results = self.forecaster.generate_forecast(
            self.ts_data, 'date', 'value', 
            forecast_periods=10, model_type='linear_trend'
        )
        
        self.assertIn('historical_data', results)
        self.assertIn('forecast_data', results)
        self.assertIn('metrics', results)
        self.assertEqual(len(results['forecast_data']['dates']), 10)
    
    def test_detect_anomalies(self):
        """Test anomaly detection"""
        results = self.forecaster.detect_anomalies(
            self.ts_data, 'date', 'value', method='statistical'
        )
        
        self.assertIn('anomaly_dates', results)
        self.assertIn('total_anomalies', results)
        self.assertIn('anomaly_percentage', results)

class TestNLPQueryProcessor(unittest.TestCase):
    """Test the NLPQueryProcessor class"""
    
    def setUp(self):
        self.processor = NLPQueryProcessor()
        
        # Create sample data
        self.sample_data = pd.DataFrame({
            'timestamp': pd.date_range('2024-01-01', periods=100, freq='h'),
            'traffic_volume': np.random.randint(50, 200, 100),
            'aqi': np.random.randint(20, 300, 100),
            'latitude': np.random.normal(28.6, 0.1, 100),
            'longitude': np.random.normal(77.2, 0.1, 100)
        })
    
    def test_process_simple_query(self):
        """Test processing simple queries"""
        query = "What is the average traffic volume?"
        result = self.processor.process_query(query, self.sample_data)
        
        self.assertEqual(result['status'], 'success')
        self.assertIn('result', result)
        self.assertIn('parsed_intent', result)
    
    def test_process_filter_query(self):
        """Test processing filter queries"""
        query = "Show me data where traffic volume > 100"
        result = self.processor.process_query(query, self.sample_data)
        
        self.assertEqual(result['status'], 'success')
        self.assertIn('filtered_data_shape', result['result'])
    
    def test_find_mentioned_columns(self):
        """Test column detection in queries"""
        query = "show me pollution levels"
        columns = self.processor._find_mentioned_columns(query, self.sample_data)
        
        self.assertIn('aqi', columns)

def run_tests():
    """Run all tests"""
    print("🧪 Running CityPulse Test Suite...")
    print("=" * 50)
    
    # Create test suite
    test_suite = unittest.TestSuite()
    
    # Add test classes
    test_classes = [
        TestDataProcessor,
        TestClusterAnalyzer,
        TestForecaster,
        TestNLPQueryProcessor
    ]
    
    for test_class in test_classes:
        tests = unittest.TestLoader().loadTestsFromTestCase(test_class)
        test_suite.addTests(tests)
    
    # Run tests
    runner = unittest.TextTestRunner(verbosity=2)
    result = runner.run(test_suite)
    
    print("=" * 50)
    if result.wasSuccessful():
        print("✅ All tests passed!")
    else:
        print(f"❌ {len(result.failures)} test(s) failed")
        print(f"❌ {len(result.errors)} error(s) occurred")
    
    return result.wasSuccessful()

if __name__ == "__main__":
    run_tests()
