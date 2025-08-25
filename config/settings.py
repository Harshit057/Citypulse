import os
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

class Config:
    """Application configuration"""
    
    # Database configuration
    DATABASE_URL = os.getenv('DATABASE_URL', 'postgresql://localhost/citypulse')
    DB_HOST = os.getenv('DB_HOST', 'localhost')
    DB_PORT = os.getenv('DB_PORT', '5432')
    DB_NAME = os.getenv('DB_NAME', 'citypulse')
    DB_USER = os.getenv('DB_USER', 'postgres')
    DB_PASSWORD = os.getenv('DB_PASSWORD', '')
    
    # API Keys
    OPENWEATHER_API_KEY = os.getenv('OPENWEATHER_API_KEY', '')
    GOOGLE_MAPS_API_KEY = os.getenv('GOOGLE_MAPS_API_KEY', '')
    OPENAI_API_KEY = os.getenv('OPENAI_API_KEY', '')
    
    # Application settings
    DEBUG = os.getenv('DEBUG', 'False').lower() == 'true'
    SECRET_KEY = os.getenv('SECRET_KEY', 'your-secret-key-change-this')
    
    # File upload settings
    MAX_UPLOAD_SIZE = os.getenv('MAX_UPLOAD_SIZE', '100MB')
    UPLOAD_FOLDER = os.getenv('UPLOAD_FOLDER', 'data/raw')
    
    # Cache settings
    REDIS_URL = os.getenv('REDIS_URL', 'redis://localhost:6379/0')
    
    # Logging
    LOG_LEVEL = os.getenv('LOG_LEVEL', 'INFO')
    LOG_FILE = os.getenv('LOG_FILE', 'logs/citypulse.log')
    
    # Data processing settings
    DEFAULT_CITY_CENTER = [28.6139, 77.2090]  # Delhi coordinates
    DEFAULT_ZOOM_LEVEL = 10
    
    # ML model settings
    FORECAST_DEFAULT_PERIODS = 30
    CLUSTERING_DEFAULT_CLUSTERS = 3
    
    # Map settings
    DEFAULT_MAP_STYLE = 'OpenStreetMap'
    HEATMAP_RADIUS = 15
    HEATMAP_BLUR = 20

class DevelopmentConfig(Config):
    """Development configuration"""
    DEBUG = True
    
class ProductionConfig(Config):
    """Production configuration"""
    DEBUG = False
    
class TestingConfig(Config):
    """Testing configuration"""
    TESTING = True
    DATABASE_URL = 'sqlite:///:memory:'

# Configuration dictionary
config = {
    'development': DevelopmentConfig,
    'production': ProductionConfig,
    'testing': TestingConfig,
    'default': DevelopmentConfig
}
