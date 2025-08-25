#!/usr/bin/env python3
"""
Database initialization script for CityPulse platform.
Creates necessary tables and sets up PostGIS extension for geographic data.
"""

import psycopg2
from psycopg2.extensions import ISOLATION_LEVEL_AUTOCOMMIT
import os
import sys

# Add project root to Python path
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from config.settings import Config

def create_database():
    """Create the CityPulse database if it doesn't exist"""
    try:
        # Connect to default postgres database
        conn = psycopg2.connect(
            host=Config.DB_HOST,
            port=Config.DB_PORT,
            user=Config.DB_USER,
            password=Config.DB_PASSWORD,
            database='postgres'
        )
        conn.set_isolation_level(ISOLATION_LEVEL_AUTOCOMMIT)
        
        cursor = conn.cursor()
        
        # Check if database exists
        cursor.execute(f"SELECT 1 FROM pg_catalog.pg_database WHERE datname = '{Config.DB_NAME}'")
        exists = cursor.fetchone()
        
        if not exists:
            cursor.execute(f'CREATE DATABASE "{Config.DB_NAME}"')
            print(f"✅ Database '{Config.DB_NAME}' created successfully")
        else:
            print(f"ℹ️  Database '{Config.DB_NAME}' already exists")
        
        cursor.close()
        conn.close()
        
    except Exception as e:
        print(f"❌ Error creating database: {str(e)}")
        return False
    
    return True

def setup_postgis():
    """Set up PostGIS extension for geographic data"""
    try:
        conn = psycopg2.connect(
            host=Config.DB_HOST,
            port=Config.DB_PORT,
            user=Config.DB_USER,
            password=Config.DB_PASSWORD,
            database=Config.DB_NAME
        )
        conn.set_isolation_level(ISOLATION_LEVEL_AUTOCOMMIT)
        
        cursor = conn.cursor()
        
        # Enable PostGIS extension
        cursor.execute("CREATE EXTENSION IF NOT EXISTS postgis")
        print("✅ PostGIS extension enabled")
        
        cursor.close()
        conn.close()
        
    except Exception as e:
        print(f"⚠️  Warning: Could not enable PostGIS extension: {str(e)}")
        print("   Geographic features may be limited without PostGIS")

def create_tables():
    """Create necessary tables for the application"""
    try:
        conn = psycopg2.connect(
            host=Config.DB_HOST,
            port=Config.DB_PORT,
            user=Config.DB_USER,
            password=Config.DB_PASSWORD,
            database=Config.DB_NAME
        )
        
        cursor = conn.cursor()
        
        # Datasets table
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS datasets (
                id SERIAL PRIMARY KEY,
                name VARCHAR(255) NOT NULL,
                description TEXT,
                file_path VARCHAR(500),
                upload_date TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                file_size BIGINT,
                row_count INTEGER,
                column_count INTEGER,
                data_types JSONB,
                metadata JSONB
            )
        """)
        
        # Processing logs table
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS processing_logs (
                id SERIAL PRIMARY KEY,
                dataset_id INTEGER REFERENCES datasets(id),
                operation_type VARCHAR(100),
                operation_details JSONB,
                timestamp TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                status VARCHAR(50),
                error_message TEXT
            )
        """)
        
        # ML models table
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS ml_models (
                id SERIAL PRIMARY KEY,
                name VARCHAR(255) NOT NULL,
                model_type VARCHAR(100),
                dataset_id INTEGER REFERENCES datasets(id),
                parameters JSONB,
                metrics JSONB,
                model_path VARCHAR(500),
                created_date TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                status VARCHAR(50)
            )
        """)
        
        # User queries table (for NLP query history)
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS user_queries (
                id SERIAL PRIMARY KEY,
                query_text TEXT NOT NULL,
                dataset_id INTEGER REFERENCES datasets(id),
                parsed_intent JSONB,
                results JSONB,
                timestamp TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                execution_time FLOAT
            )
        """)
        
        # Geographic data table (optional, for storing processed geographic data)
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS geographic_data (
                id SERIAL PRIMARY KEY,
                dataset_id INTEGER REFERENCES datasets(id),
                location_name VARCHAR(255),
                latitude DECIMAL(10, 8),
                longitude DECIMAL(11, 8),
                geom GEOMETRY(POINT, 4326),
                properties JSONB,
                created_date TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            )
        """)
        
        # Create indexes for better performance
        cursor.execute("CREATE INDEX IF NOT EXISTS idx_datasets_upload_date ON datasets(upload_date)")
        cursor.execute("CREATE INDEX IF NOT EXISTS idx_processing_logs_dataset_id ON processing_logs(dataset_id)")
        cursor.execute("CREATE INDEX IF NOT EXISTS idx_ml_models_dataset_id ON ml_models(dataset_id)")
        cursor.execute("CREATE INDEX IF NOT EXISTS idx_user_queries_timestamp ON user_queries(timestamp)")
        cursor.execute("CREATE INDEX IF NOT EXISTS idx_geographic_data_location ON geographic_data(latitude, longitude)")
        
        # Create spatial index for geographic data (if PostGIS is available)
        try:
            cursor.execute("CREATE INDEX IF NOT EXISTS idx_geographic_data_geom ON geographic_data USING GIST(geom)")
        except:
            pass  # PostGIS not available
        
        conn.commit()
        cursor.close()
        conn.close()
        
        print("✅ Database tables created successfully")
        
    except Exception as e:
        print(f"❌ Error creating tables: {str(e)}")
        return False
    
    return True

def insert_sample_data():
    """Insert some sample data for testing"""
    try:
        conn = psycopg2.connect(
            host=Config.DB_HOST,
            port=Config.DB_PORT,
            user=Config.DB_USER,
            password=Config.DB_PASSWORD,
            database=Config.DB_NAME
        )
        
        cursor = conn.cursor()
        
        # Insert sample dataset
        cursor.execute("""
            INSERT INTO datasets (name, description, row_count, column_count, data_types, metadata)
            VALUES (%s, %s, %s, %s, %s, %s)
            ON CONFLICT DO NOTHING
        """, (
            'Sample Traffic Data',
            'Sample traffic dataset for Delhi',
            1000,
            6,
            '{"latitude": "float64", "longitude": "float64", "traffic_volume": "int64"}',
            '{"source": "sample", "city": "Delhi", "data_type": "traffic"}'
        ))
        
        conn.commit()
        cursor.close()
        conn.close()
        
        print("✅ Sample data inserted")
        
    except Exception as e:
        print(f"⚠️  Warning: Could not insert sample data: {str(e)}")

def main():
    """Main initialization function"""
    print("🚀 Initializing CityPulse Database...")
    print("=" * 50)
    
    # Check if we can connect to PostgreSQL
    try:
        conn = psycopg2.connect(
            host=Config.DB_HOST,
            port=Config.DB_PORT,
            user=Config.DB_USER,
            password=Config.DB_PASSWORD,
            database='postgres'
        )
        conn.close()
        print("✅ PostgreSQL connection successful")
    except Exception as e:
        print(f"❌ Cannot connect to PostgreSQL: {str(e)}")
        print("Please ensure PostgreSQL is running and connection settings are correct")
        return False
    
    # Create database
    if not create_database():
        return False
    
    # Set up PostGIS
    setup_postgis()
    
    # Create tables
    if not create_tables():
        return False
    
    # Insert sample data
    insert_sample_data()
    
    print("=" * 50)
    print("🎉 Database initialization completed successfully!")
    print(f"Database: {Config.DB_NAME}")
    print(f"Host: {Config.DB_HOST}:{Config.DB_PORT}")
    print("\nYou can now run the CityPulse application.")
    
    return True

if __name__ == "__main__":
    main()
