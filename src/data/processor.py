import pandas as pd
import numpy as np
from typing import Dict, List, Any, Optional
import logging

class DataProcessor:
    """
    Core data processing class for CityPulse platform.
    Handles data cleaning, validation, and preprocessing.
    """
    
    def __init__(self):
        self.processing_log = []
        self.logger = logging.getLogger(__name__)
    
    def clean_data(self, df: pd.DataFrame) -> pd.DataFrame:
        """
        Clean and preprocess the input dataset.
        
        Args:
            df: Input DataFrame
            
        Returns:
            Cleaned DataFrame
        """
        df_cleaned = df.copy()
        
        # Log original shape
        self._log_step(f"Original data shape: {df.shape}")
        
        # Remove duplicate rows
        df_cleaned = self._remove_duplicates(df_cleaned)
        
        # Handle missing values
        df_cleaned = self._handle_missing_values(df_cleaned)
        
        # Standardize column names
        df_cleaned = self._standardize_columns(df_cleaned)
        
        # Convert data types
        df_cleaned = self._convert_data_types(df_cleaned)
        
        # Remove outliers (optional)
        df_cleaned = self._handle_outliers(df_cleaned)
        
        self._log_step(f"Final data shape: {df_cleaned.shape}")
        
        return df_cleaned
    
    def _remove_duplicates(self, df: pd.DataFrame) -> pd.DataFrame:
        """Remove duplicate rows"""
        initial_count = len(df)
        df_cleaned = df.drop_duplicates()
        removed_count = initial_count - len(df_cleaned)
        
        if removed_count > 0:
            self._log_step(f"Removed {removed_count} duplicate rows")
        
        return df_cleaned
    
    def _handle_missing_values(self, df: pd.DataFrame) -> pd.DataFrame:
        """Handle missing values using appropriate strategies"""
        df_cleaned = df.copy()
        
        for column in df_cleaned.columns:
            missing_count = df_cleaned[column].isnull().sum()
            
            if missing_count > 0:
                missing_pct = (missing_count / len(df_cleaned)) * 100
                
                if missing_pct > 50:
                    # Drop columns with >50% missing values
                    df_cleaned = df_cleaned.drop(columns=[column])
                    self._log_step(f"Dropped column '{column}' ({missing_pct:.1f}% missing)")
                
                elif df_cleaned[column].dtype in ['int64', 'float64']:
                    # Fill numeric columns with median
                    median_value = df_cleaned[column].median()
                    df_cleaned[column] = df_cleaned[column].fillna(median_value)
                    self._log_step(f"Filled {missing_count} missing values in '{column}' with median ({median_value})")
                
                else:
                    # Fill categorical columns with mode or 'Unknown'
                    if df_cleaned[column].mode().empty:
                        fill_value = 'Unknown'
                    else:
                        fill_value = df_cleaned[column].mode()[0]
                    
                    df_cleaned[column] = df_cleaned[column].fillna(fill_value)
                    self._log_step(f"Filled {missing_count} missing values in '{column}' with '{fill_value}'")
        
        return df_cleaned
    
    def _standardize_columns(self, df: pd.DataFrame) -> pd.DataFrame:
        """Standardize column names"""
        df_cleaned = df.copy()
        
        # Convert to lowercase and replace spaces with underscores
        new_columns = {}
        for col in df_cleaned.columns:
            new_col = col.lower().replace(' ', '_').replace('-', '_')
            new_col = ''.join(c if c.isalnum() or c == '_' else '' for c in new_col)
            new_columns[col] = new_col
        
        df_cleaned = df_cleaned.rename(columns=new_columns)
        
        if new_columns:
            self._log_step("Standardized column names")
        
        return df_cleaned
    
    def _convert_data_types(self, df: pd.DataFrame) -> pd.DataFrame:
        """Convert data types for optimal storage and processing"""
        df_cleaned = df.copy()
        
        for column in df_cleaned.columns:
            # Try to convert potential date columns
            if any(keyword in column.lower() for keyword in ['date', 'time', 'timestamp']):
                try:
                    df_cleaned[column] = pd.to_datetime(df_cleaned[column])
                    self._log_step(f"Converted '{column}' to datetime")
                except:
                    pass
            
            # Convert object columns to categorical if they have few unique values
            elif df_cleaned[column].dtype == 'object':
                unique_ratio = df_cleaned[column].nunique() / len(df_cleaned)
                if unique_ratio < 0.1:  # Less than 10% unique values
                    df_cleaned[column] = df_cleaned[column].astype('category')
                    self._log_step(f"Converted '{column}' to categorical")
            
            # Optimize numeric types
            elif df_cleaned[column].dtype in ['int64', 'float64']:
                df_cleaned[column] = pd.to_numeric(df_cleaned[column], downcast='integer' if df_cleaned[column].dtype == 'int64' else 'float')
        
        return df_cleaned
    
    def _handle_outliers(self, df: pd.DataFrame, method: str = 'iqr') -> pd.DataFrame:
        """Remove or cap outliers in numeric columns"""
        df_cleaned = df.copy()
        numeric_columns = df_cleaned.select_dtypes(include=[np.number]).columns
        
        for column in numeric_columns:
            if method == 'iqr':
                Q1 = df_cleaned[column].quantile(0.25)
                Q3 = df_cleaned[column].quantile(0.75)
                IQR = Q3 - Q1
                
                lower_bound = Q1 - 1.5 * IQR
                upper_bound = Q3 + 1.5 * IQR
                
                outliers_count = len(df_cleaned[(df_cleaned[column] < lower_bound) | (df_cleaned[column] > upper_bound)])
                
                if outliers_count > 0:
                    # Cap outliers instead of removing them
                    df_cleaned[column] = df_cleaned[column].clip(lower=lower_bound, upper=upper_bound)
                    self._log_step(f"Capped {outliers_count} outliers in '{column}'")
        
        return df_cleaned
    
    def validate_geographic_data(self, df: pd.DataFrame) -> Dict[str, Any]:
        """Validate geographic data columns"""
        validation_results = {
            'has_coordinates': False,
            'coordinate_columns': {},
            'coordinate_ranges': {},
            'issues': []
        }
        
        # Look for latitude and longitude columns
        lat_columns = [col for col in df.columns if 'lat' in col.lower()]
        lon_columns = [col for col in df.columns if 'lon' in col.lower() or 'lng' in col.lower()]
        
        if lat_columns and lon_columns:
            validation_results['has_coordinates'] = True
            validation_results['coordinate_columns'] = {
                'latitude': lat_columns[0],
                'longitude': lon_columns[0]
            }
            
            # Check coordinate ranges
            lat_col = lat_columns[0]
            lon_col = lon_columns[0]
            
            lat_range = (df[lat_col].min(), df[lat_col].max())
            lon_range = (df[lon_col].min(), df[lon_col].max())
            
            validation_results['coordinate_ranges'] = {
                'latitude': lat_range,
                'longitude': lon_range
            }
            
            # Validate ranges
            if not (-90 <= lat_range[0] <= lat_range[1] <= 90):
                validation_results['issues'].append(f"Invalid latitude range: {lat_range}")
            
            if not (-180 <= lon_range[0] <= lon_range[1] <= 180):
                validation_results['issues'].append(f"Invalid longitude range: {lon_range}")
        
        return validation_results
    
    def generate_data_profile(self, df: pd.DataFrame) -> Dict[str, Any]:
        """Generate comprehensive data profile"""
        profile = {
            'basic_info': {
                'shape': df.shape,
                'memory_usage': df.memory_usage(deep=True).sum(),
                'dtypes': df.dtypes.to_dict()
            },
            'column_stats': {},
            'missing_data': df.isnull().sum().to_dict(),
            'geographic_validation': self.validate_geographic_data(df)
        }
        
        # Column-wise statistics
        for column in df.columns:
            if df[column].dtype in ['int64', 'float64']:
                profile['column_stats'][column] = {
                    'type': 'numeric',
                    'mean': df[column].mean(),
                    'median': df[column].median(),
                    'std': df[column].std(),
                    'min': df[column].min(),
                    'max': df[column].max(),
                    'unique_count': df[column].nunique()
                }
            else:
                profile['column_stats'][column] = {
                    'type': 'categorical',
                    'unique_count': df[column].nunique(),
                    'top_values': df[column].value_counts().head(5).to_dict()
                }
        
        return profile
    
    def _log_step(self, message: str):
        """Log processing step"""
        self.processing_log.append(message)
        self.logger.info(message)
    
    def get_processing_summary(self) -> List[str]:
        """Get summary of processing steps"""
        return self.processing_log
    
    def reset_log(self):
        """Reset processing log"""
        self.processing_log = []
