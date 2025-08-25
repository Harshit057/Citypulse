#!/usr/bin/env python3
"""
Sample data generator for CityPulse platform.
Generates realistic urban datasets for testing and demonstration.
"""

import pandas as pd
import numpy as np
from datetime import datetime, timedelta
import os

def generate_traffic_data(n_points=1000, city_center=[28.6139, 77.2090], city_name="Delhi"):
    """Generate sample traffic data"""
    np.random.seed(42)
    
    # Time series over 30 days with hourly data
    start_date = datetime.now() - timedelta(days=30)
    timestamps = [start_date + timedelta(hours=i) for i in range(n_points)]
    
    # Generate coordinates around city center
    lat_std, lon_std = 0.1, 0.1
    latitudes = np.random.normal(city_center[0], lat_std, n_points)
    longitudes = np.random.normal(city_center[1], lon_std, n_points)
    
    # Generate traffic patterns based on time of day
    traffic_data = []
    for i, timestamp in enumerate(timestamps):
        hour = timestamp.hour
        day_of_week = timestamp.weekday()
        
        # Base traffic volume
        base_volume = 50
        
        # Rush hour patterns
        if 7 <= hour <= 9 or 17 <= hour <= 19:
            base_volume += np.random.randint(50, 100)
        elif 22 <= hour or hour <= 5:
            base_volume += np.random.randint(-20, 10)
        
        # Weekend patterns
        if day_of_week >= 5:  # Weekend
            base_volume *= 0.7
        
        # Add some noise
        traffic_volume = max(0, base_volume + np.random.randint(-20, 30))
        
        # Speed inversely related to volume
        avg_speed = max(5, 60 - (traffic_volume * 0.3) + np.random.randint(-10, 10))
        
        # Congestion level
        if traffic_volume > 120:
            congestion = 'High'
        elif traffic_volume > 80:
            congestion = 'Medium'
        else:
            congestion = 'Low'
        
        traffic_data.append({
            'timestamp': timestamp,
            'latitude': latitudes[i],
            'longitude': longitudes[i],
            'traffic_volume': traffic_volume,
            'avg_speed_kmh': round(avg_speed, 1),
            'congestion_level': congestion,
            'road_id': f'RD_{i % 50:03d}',
            'city': city_name
        })
    
    return pd.DataFrame(traffic_data)

def generate_air_quality_data(n_points=500, city_center=[28.6139, 77.2090], city_name="Delhi"):
    """Generate sample air quality data"""
    np.random.seed(123)
    
    # Daily data over ~1.5 years
    start_date = datetime.now() - timedelta(days=n_points)
    dates = [start_date + timedelta(days=i) for i in range(n_points)]
    
    # Generate station locations
    lat_std, lon_std = 0.15, 0.15
    latitudes = np.random.normal(city_center[0], lat_std, n_points)
    longitudes = np.random.normal(city_center[1], lon_std, n_points)
    
    air_quality_data = []
    for i, date in enumerate(dates):
        month = date.month
        
        # Seasonal patterns (winter pollution is higher in Delhi)
        if 11 <= month <= 2:  # Winter months
            base_aqi = np.random.normal(150, 50)
            pm25_base = np.random.normal(80, 30)
            pm10_base = np.random.normal(120, 40)
        elif 3 <= month <= 5:  # Summer
            base_aqi = np.random.normal(100, 30)
            pm25_base = np.random.normal(50, 20)
            pm10_base = np.random.normal(80, 25)
        else:  # Monsoon
            base_aqi = np.random.normal(80, 25)
            pm25_base = np.random.normal(35, 15)
            pm10_base = np.random.normal(60, 20)
        
        # Ensure positive values
        aqi = max(0, int(base_aqi))
        pm25 = max(0, round(pm25_base, 1))
        pm10 = max(0, round(pm10_base, 1))
        no2 = max(0, round(np.random.exponential(30), 1))
        so2 = max(0, round(np.random.exponential(15), 1))
        co = max(0, round(np.random.exponential(1.5), 2))
        
        air_quality_data.append({
            'date': date.date(),
            'latitude': latitudes[i],
            'longitude': longitudes[i],
            'aqi': aqi,
            'pm25': pm25,
            'pm10': pm10,
            'no2': no2,
            'so2': so2,
            'co': co,
            'station_id': f'AQ_{i % 25:03d}',
            'city': city_name
        })
    
    return pd.DataFrame(air_quality_data)

def generate_crime_data(n_points=2000, city_center=[28.6139, 77.2090], city_name="Delhi"):
    """Generate sample crime data"""
    np.random.seed(456)
    
    # Random timestamps over past 2 years
    start_date = datetime.now() - timedelta(days=730)
    end_date = datetime.now()
    
    timestamps = []
    for _ in range(n_points):
        random_days = np.random.randint(0, 730)
        random_hours = np.random.randint(0, 24)
        timestamp = start_date + timedelta(days=random_days, hours=random_hours)
        timestamps.append(timestamp)
    
    # Generate hotspot areas (higher crime concentration)
    hotspot_centers = [
        [city_center[0] + 0.05, city_center[1] - 0.03],
        [city_center[0] - 0.08, city_center[1] + 0.04],
        [city_center[0] + 0.02, city_center[1] + 0.06]
    ]
    
    crime_data = []
    crime_types = ['Theft', 'Burglary', 'Assault', 'Vehicle Crime', 'Fraud', 'Vandalism']
    severities = ['Low', 'Medium', 'High']
    
    for i in range(n_points):
        # 60% chance of crime in hotspot areas
        if np.random.random() < 0.6:
            hotspot_idx = np.random.choice(len(hotspot_centers))
            hotspot = hotspot_centers[hotspot_idx]
            lat = np.random.normal(hotspot[0], 0.01)
            lon = np.random.normal(hotspot[1], 0.01)
        else:
            lat = np.random.normal(city_center[0], 0.12)
            lon = np.random.normal(city_center[1], 0.12)
        
        crime_data.append({
            'timestamp': timestamps[i],
            'latitude': lat,
            'longitude': lon,
            'crime_type': np.random.choice(crime_types),
            'severity': np.random.choice(severities),
            'resolved': np.random.choice([True, False], p=[0.7, 0.3]),
            'incident_id': f'INC_{i:06d}',
            'district': f'District_{np.random.randint(1, 12)}',
            'city': city_name
        })
    
    return pd.DataFrame(crime_data)

def generate_weather_data(n_points=365, city_center=[28.6139, 77.2090], city_name="Delhi"):
    """Generate sample weather data"""
    np.random.seed(789)
    
    # Daily data for one year
    start_date = datetime.now() - timedelta(days=n_points)
    dates = [start_date + timedelta(days=i) for i in range(n_points)]
    
    weather_data = []
    for i, date in enumerate(dates):
        month = date.month
        
        # Seasonal temperature patterns
        if 11 <= month <= 2:  # Winter
            temp_base = np.random.normal(15, 5)
            humidity_base = np.random.normal(60, 15)
        elif 3 <= month <= 5:  # Summer
            temp_base = np.random.normal(35, 8)
            humidity_base = np.random.normal(40, 12)
        elif 6 <= month <= 9:  # Monsoon
            temp_base = np.random.normal(28, 4)
            humidity_base = np.random.normal(80, 10)
        else:  # Post-monsoon
            temp_base = np.random.normal(25, 5)
            humidity_base = np.random.normal(65, 12)
        
        # Rain probability (higher during monsoon)
        rain_prob = 0.8 if 6 <= month <= 9 else 0.2
        rainfall = np.random.exponential(5) if np.random.random() < rain_prob else 0
        
        weather_data.append({
            'date': date.date(),
            'latitude': city_center[0] + np.random.normal(0, 0.02),
            'longitude': city_center[1] + np.random.normal(0, 0.02),
            'temperature_c': round(max(-5, temp_base), 1),
            'humidity_percent': round(max(0, min(100, humidity_base)), 1),
            'rainfall_mm': round(max(0, rainfall), 1),
            'wind_speed_kmh': round(max(0, np.random.exponential(8)), 1),
            'pressure_hpa': round(np.random.normal(1013, 20), 1),
            'visibility_km': round(max(0.1, np.random.normal(10, 3)), 1),
            'station_id': f'WS_{i % 10:03d}',
            'city': city_name
        })
    
    return pd.DataFrame(weather_data)

def save_sample_datasets():
    """Generate and save all sample datasets"""
    print("🏗️  Generating sample datasets for CityPulse...")
    
    # Create data directories
    os.makedirs('data/raw', exist_ok=True)
    os.makedirs('data/samples', exist_ok=True)
    
    # Generate datasets
    datasets = {
        'traffic_data.csv': generate_traffic_data(1000),
        'air_quality_data.csv': generate_air_quality_data(500),
        'crime_data.csv': generate_crime_data(2000),
        'weather_data.csv': generate_weather_data(365)
    }
    
    # Save datasets
    for filename, df in datasets.items():
        filepath = os.path.join('data', 'samples', filename)
        df.to_csv(filepath, index=False)
        print(f"✅ Generated {filename}: {len(df)} rows, {len(df.columns)} columns")
    
    print(f"\n📊 Sample datasets saved to 'data/samples/' directory")
    print("You can now use these datasets in the CityPulse application!")

if __name__ == "__main__":
    save_sample_datasets()
