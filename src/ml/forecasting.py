import pandas as pd
import numpy as np
from prophet import Prophet
from sklearn.metrics import mean_absolute_error, mean_squared_error
import warnings
from typing import Dict, List, Any, Optional, Tuple
import logging

warnings.filterwarnings('ignore', category=RuntimeWarning)

class Forecaster:
    """
    Time series forecasting for urban analytics data.
    Supports multiple forecasting models including Prophet, ARIMA, and simple statistical methods.
    """
    
    def __init__(self):
        self.logger = logging.getLogger(__name__)
        self.models = {}
        
    def generate_forecast(self, df: pd.DataFrame, date_column: str, value_column: str,
                         forecast_periods: int = 30, model_type: str = 'prophet') -> Dict[str, Any]:
        """
        Generate forecasts for time series data.
        
        Args:
            df: Input DataFrame with time series data
            date_column: Name of the date/time column
            value_column: Name of the value column to forecast
            forecast_periods: Number of periods to forecast
            model_type: Type of model ('prophet', 'arima', 'linear_trend')
            
        Returns:
            Dictionary containing forecast results
        """
        # Validate inputs
        if date_column not in df.columns:
            raise ValueError(f"Date column '{date_column}' not found in data")
        if value_column not in df.columns:
            raise ValueError(f"Value column '{value_column}' not found in data")
        
        # Prepare data
        ts_data = self._prepare_time_series_data(df, date_column, value_column)
        
        if len(ts_data) < 10:
            raise ValueError("Need at least 10 data points for forecasting")
        
        # Generate forecast based on model type
        if model_type == 'prophet':
            results = self._prophet_forecast(ts_data, forecast_periods)
        elif model_type == 'linear_trend':
            results = self._linear_trend_forecast(ts_data, forecast_periods)
        elif model_type == 'seasonal_naive':
            results = self._seasonal_naive_forecast(ts_data, forecast_periods)
        else:
            raise ValueError(f"Unsupported model type: {model_type}")
        
        # Add metadata
        results.update({
            'model_type': model_type,
            'date_column': date_column,
            'value_column': value_column,
            'forecast_periods': forecast_periods,
            'training_data_points': len(ts_data)
        })
        
        return results
    
    def _prepare_time_series_data(self, df: pd.DataFrame, date_column: str, 
                                 value_column: str) -> pd.DataFrame:
        """Prepare and clean time series data"""
        # Create working copy
        ts_data = df[[date_column, value_column]].copy()
        
        # Convert date column to datetime
        ts_data[date_column] = pd.to_datetime(ts_data[date_column])
        
        # Remove missing values
        ts_data = ts_data.dropna()
        
        # Sort by date
        ts_data = ts_data.sort_values(date_column)
        
        # Remove duplicates (keep last occurrence)
        ts_data = ts_data.drop_duplicates(subset=[date_column], keep='last')
        
        # Reset index
        ts_data = ts_data.reset_index(drop=True)
        
        return ts_data
    
    def _prophet_forecast(self, ts_data: pd.DataFrame, forecast_periods: int) -> Dict[str, Any]:
        """Generate forecast using Facebook Prophet"""
        try:
            # Prepare data for Prophet (needs 'ds' and 'y' columns)
            prophet_data = ts_data.copy()
            prophet_data.columns = ['ds', 'y']
            
            # Initialize and fit Prophet model
            model = Prophet(
                daily_seasonality=True,
                weekly_seasonality=True,
                yearly_seasonality=True,
                changepoint_prior_scale=0.05
            )
            
            model.fit(prophet_data)
            
            # Create future dataframe
            future = model.make_future_dataframe(periods=forecast_periods)
            
            # Generate forecast
            forecast = model.predict(future)
            
            # Extract results
            historical_data = forecast[:-forecast_periods] if forecast_periods > 0 else forecast
            forecast_data = forecast[-forecast_periods:] if forecast_periods > 0 else pd.DataFrame()
            
            # Calculate accuracy metrics on historical data
            actual = prophet_data['y'].values
            predicted = historical_data['yhat'].values
            
            metrics = self._calculate_metrics(actual, predicted)
            
            # Store model
            self.models['prophet'] = model
            
            return {
                'historical_data': {
                    'dates': historical_data['ds'].dt.strftime('%Y-%m-%d').tolist(),
                    'actual': actual.tolist(),
                    'predicted': predicted.tolist(),
                    'lower_bound': historical_data['yhat_lower'].tolist(),
                    'upper_bound': historical_data['yhat_upper'].tolist()
                },
                'forecast_data': {
                    'dates': forecast_data['ds'].dt.strftime('%Y-%m-%d').tolist() if not forecast_data.empty else [],
                    'predicted': forecast_data['yhat'].tolist() if not forecast_data.empty else [],
                    'lower_bound': forecast_data['yhat_lower'].tolist() if not forecast_data.empty else [],
                    'upper_bound': forecast_data['yhat_upper'].tolist() if not forecast_data.empty else []
                },
                'metrics': metrics,
                'model_components': self._extract_prophet_components(model, forecast)
            }
            
        except Exception as e:
            self.logger.error(f"Prophet forecasting failed: {str(e)}")
            # Fallback to linear trend
            return self._linear_trend_forecast(ts_data, forecast_periods)
    
    def _linear_trend_forecast(self, ts_data: pd.DataFrame, forecast_periods: int) -> Dict[str, Any]:
        """Generate forecast using linear trend"""
        dates = ts_data.iloc[:, 0]
        values = ts_data.iloc[:, 1]
        
        # Convert dates to numeric for trend calculation
        date_numeric = pd.to_numeric(dates)
        
        # Fit linear trend
        z = np.polyfit(date_numeric, values, 1)
        trend_func = np.poly1d(z)
        
        # Generate predictions for historical data
        historical_predicted = trend_func(date_numeric)
        
        # Generate future dates
        last_date = dates.iloc[-1]
        freq = self._infer_frequency(dates)
        future_dates = pd.date_range(start=last_date, periods=forecast_periods+1, freq=freq)[1:]
        future_numeric = pd.to_numeric(future_dates)
        
        # Generate forecasts
        forecast_predicted = trend_func(future_numeric)
        
        # Calculate simple confidence intervals (±10% of predicted value)
        historical_lower = historical_predicted * 0.9
        historical_upper = historical_predicted * 1.1
        forecast_lower = forecast_predicted * 0.9
        forecast_upper = forecast_predicted * 1.1
        
        # Calculate metrics
        metrics = self._calculate_metrics(values.values, historical_predicted)
        
        return {
            'historical_data': {
                'dates': dates.dt.strftime('%Y-%m-%d').tolist(),
                'actual': values.tolist(),
                'predicted': historical_predicted.tolist(),
                'lower_bound': historical_lower.tolist(),
                'upper_bound': historical_upper.tolist()
            },
            'forecast_data': {
                'dates': future_dates.strftime('%Y-%m-%d').tolist(),
                'predicted': forecast_predicted.tolist(),
                'lower_bound': forecast_lower.tolist(),
                'upper_bound': forecast_upper.tolist()
            },
            'metrics': metrics,
            'trend_coefficient': float(z[0]),
            'trend_intercept': float(z[1])
        }
    
    def _seasonal_naive_forecast(self, ts_data: pd.DataFrame, forecast_periods: int) -> Dict[str, Any]:
        """Generate forecast using seasonal naive method"""
        dates = ts_data.iloc[:, 0]
        values = ts_data.iloc[:, 1]
        
        # Determine seasonality (assume daily data, weekly season = 7 days)
        season_length = min(7, len(values) // 2)
        
        if season_length < 2:
            # Fall back to naive forecast (last value)
            last_value = values.iloc[-1]
            forecast_values = [last_value] * forecast_periods
        else:
            # Use seasonal pattern
            seasonal_pattern = values[-season_length:].values
            forecast_values = np.tile(seasonal_pattern, forecast_periods // season_length + 1)[:forecast_periods]
        
        # Generate future dates
        last_date = dates.iloc[-1]
        freq = self._infer_frequency(dates)
        future_dates = pd.date_range(start=last_date + freq, periods=forecast_periods, freq=freq)
        
        # Simple confidence intervals
        forecast_std = values.std()
        forecast_lower = forecast_values - 1.96 * forecast_std
        forecast_upper = forecast_values + 1.96 * forecast_std
        
        # For historical data, use actual values as "predictions"
        historical_predicted = values.values
        metrics = self._calculate_metrics(values.values, historical_predicted)
        
        return {
            'historical_data': {
                'dates': dates.dt.strftime('%Y-%m-%d').tolist(),
                'actual': values.tolist(),
                'predicted': historical_predicted.tolist(),
                'lower_bound': (values - forecast_std).tolist(),
                'upper_bound': (values + forecast_std).tolist()
            },
            'forecast_data': {
                'dates': future_dates.strftime('%Y-%m-%d').tolist(),
                'predicted': forecast_values.tolist(),
                'lower_bound': forecast_lower.tolist(),
                'upper_bound': forecast_upper.tolist()
            },
            'metrics': metrics,
            'season_length': season_length
        }
    
    def _infer_frequency(self, dates: pd.Series) -> str:
        """Infer the frequency of the time series"""
        if len(dates) < 2:
            return 'D'  # Default to daily
        
        # Calculate most common difference
        diffs = dates.diff().dropna()
        most_common_diff = diffs.mode()[0] if not diffs.empty else pd.Timedelta(days=1)
        
        # Map to pandas frequency strings
        if most_common_diff <= pd.Timedelta(hours=1):
            return 'H'  # Hourly
        elif most_common_diff <= pd.Timedelta(days=1):
            return 'D'  # Daily
        elif most_common_diff <= pd.Timedelta(weeks=1):
            return 'W'  # Weekly
        elif most_common_diff <= pd.Timedelta(days=31):
            return 'M'  # Monthly
        else:
            return 'Y'  # Yearly
    
    def _calculate_metrics(self, actual: np.ndarray, predicted: np.ndarray) -> Dict[str, float]:
        """Calculate forecast accuracy metrics"""
        try:
            mae = mean_absolute_error(actual, predicted)
            mse = mean_squared_error(actual, predicted)
            rmse = np.sqrt(mse)
            mape = np.mean(np.abs((actual - predicted) / actual)) * 100
            
            return {
                'mae': float(mae),
                'mse': float(mse),
                'rmse': float(rmse),
                'mape': float(mape) if not np.isinf(mape) else None
            }
        except Exception as e:
            self.logger.error(f"Error calculating metrics: {str(e)}")
            return {
                'mae': None,
                'mse': None,
                'rmse': None,
                'mape': None
            }
    
    def _extract_prophet_components(self, model: Prophet, forecast: pd.DataFrame) -> Dict[str, Any]:
        """Extract trend and seasonal components from Prophet model"""
        try:
            components = {
                'trend': forecast['trend'].tolist(),
                'seasonal_components': {}
            }
            
            # Add seasonal components if they exist
            if 'weekly' in forecast.columns:
                components['seasonal_components']['weekly'] = forecast['weekly'].tolist()
            if 'yearly' in forecast.columns:
                components['seasonal_components']['yearly'] = forecast['yearly'].tolist()
            if 'daily' in forecast.columns:
                components['seasonal_components']['daily'] = forecast['daily'].tolist()
            
            return components
        except Exception as e:
            self.logger.error(f"Error extracting Prophet components: {str(e)}")
            return {}
    
    def detect_anomalies(self, df: pd.DataFrame, date_column: str, value_column: str,
                        method: str = 'statistical') -> Dict[str, Any]:
        """
        Detect anomalies in time series data.
        
        Args:
            df: Input DataFrame
            date_column: Date column name
            value_column: Value column name
            method: Detection method ('statistical', 'prophet')
            
        Returns:
            Anomaly detection results
        """
        ts_data = self._prepare_time_series_data(df, date_column, value_column)
        
        if method == 'statistical':
            return self._statistical_anomaly_detection(ts_data)
        elif method == 'prophet':
            return self._prophet_anomaly_detection(ts_data)
        else:
            raise ValueError(f"Unsupported anomaly detection method: {method}")
    
    def _statistical_anomaly_detection(self, ts_data: pd.DataFrame) -> Dict[str, Any]:
        """Detect anomalies using statistical methods (Z-score and IQR)"""
        dates = ts_data.iloc[:, 0]
        values = ts_data.iloc[:, 1]
        
        # Z-score method
        z_scores = np.abs((values - values.mean()) / values.std())
        z_anomalies = z_scores > 3
        
        # IQR method
        Q1 = values.quantile(0.25)
        Q3 = values.quantile(0.75)
        IQR = Q3 - Q1
        iqr_anomalies = (values < (Q1 - 1.5 * IQR)) | (values > (Q3 + 1.5 * IQR))
        
        # Combine methods
        combined_anomalies = z_anomalies | iqr_anomalies
        
        return {
            'method': 'statistical',
            'anomaly_dates': dates[combined_anomalies].dt.strftime('%Y-%m-%d').tolist(),
            'anomaly_values': values[combined_anomalies].tolist(),
            'anomaly_indices': combined_anomalies.tolist(),
            'total_anomalies': combined_anomalies.sum(),
            'anomaly_percentage': (combined_anomalies.sum() / len(values)) * 100,
            'thresholds': {
                'z_score_threshold': 3,
                'iqr_lower': Q1 - 1.5 * IQR,
                'iqr_upper': Q3 + 1.5 * IQR
            }
        }
    
    def _prophet_anomaly_detection(self, ts_data: pd.DataFrame) -> Dict[str, Any]:
        """Detect anomalies using Prophet model predictions"""
        try:
            # Use Prophet to model the data
            prophet_data = ts_data.copy()
            prophet_data.columns = ['ds', 'y']
            
            model = Prophet(interval_width=0.95)
            model.fit(prophet_data)
            
            # Get predictions for historical data
            forecast = model.predict(prophet_data[['ds']])
            
            # Identify anomalies (values outside confidence intervals)
            anomalies = (prophet_data['y'] < forecast['yhat_lower']) | (prophet_data['y'] > forecast['yhat_upper'])
            
            return {
                'method': 'prophet',
                'anomaly_dates': prophet_data['ds'][anomalies].dt.strftime('%Y-%m-%d').tolist(),
                'anomaly_values': prophet_data['y'][anomalies].tolist(),
                'anomaly_indices': anomalies.tolist(),
                'total_anomalies': anomalies.sum(),
                'anomaly_percentage': (anomalies.sum() / len(prophet_data)) * 100,
                'confidence_interval': 0.95
            }
            
        except Exception as e:
            self.logger.error(f"Prophet anomaly detection failed: {str(e)}")
            # Fallback to statistical method
            return self._statistical_anomaly_detection(ts_data)
    
    def forecast_aqi(self, df: pd.DataFrame, forecast_days: int = 30) -> Dict[str, Any]:
        """Specialized AQI forecasting"""
        # Look for common AQI column names
        aqi_columns = [col for col in df.columns if 'aqi' in col.lower()]
        date_columns = [col for col in df.columns if any(term in col.lower() for term in ['date', 'time', 'timestamp'])]
        
        if not aqi_columns:
            raise ValueError("No AQI column found in data")
        if not date_columns:
            raise ValueError("No date column found in data")
        
        return self.generate_forecast(df, date_columns[0], aqi_columns[0], forecast_days)
    
    def forecast_traffic(self, df: pd.DataFrame, forecast_periods: int = 168) -> Dict[str, Any]:
        """Specialized traffic forecasting (default to 1 week = 168 hours)"""
        # Look for traffic-related columns
        traffic_columns = [col for col in df.columns if any(term in col.lower() for term in ['traffic', 'volume', 'speed', 'congestion'])]
        date_columns = [col for col in df.columns if any(term in col.lower() for term in ['date', 'time', 'timestamp'])]
        
        if not traffic_columns:
            raise ValueError("No traffic-related column found in data")
        if not date_columns:
            raise ValueError("No date column found in data")
        
        return self.generate_forecast(df, date_columns[0], traffic_columns[0], forecast_periods)
