import pandas as pd
import re
from typing import Dict, List, Any, Optional
import logging

class NLPQueryProcessor:
    """
    Process natural language queries and convert them to data operations.
    This is a simplified version - in production, you'd use more sophisticated NLP.
    """
    
    def __init__(self):
        self.logger = logging.getLogger(__name__)
        
        # Query patterns and corresponding operations
        self.query_patterns = {
            'filter_patterns': [
                (r'show.*(?:where|with|having).*(\w+)\s*(>|<|=|>=|<=)\s*(\d+(?:\.\d+)?)', 'filter_numeric'),
                (r'show.*(?:where|with).*(\w+)\s*(?:is|equals?)\s*["\']?([^"\']+)["\']?', 'filter_categorical'),
                (r'(?:find|show|get).*(\w+)\s*(?:above|over|greater than)\s*(\d+(?:\.\d+)?)', 'filter_greater'),
                (r'(?:find|show|get).*(\w+)\s*(?:below|under|less than)\s*(\d+(?:\.\d+)?)', 'filter_less'),
            ],
            'aggregation_patterns': [
                (r'(?:average|mean)\s*(\w+)', 'mean'),
                (r'(?:sum|total)\s*(?:of\s*)?(\w+)', 'sum'),
                (r'(?:max|maximum|highest)\s*(\w+)', 'max'),
                (r'(?:min|minimum|lowest)\s*(\w+)', 'min'),
                (r'(?:count|number)\s*(?:of\s*)?(\w+)', 'count'),
            ],
            'geographic_patterns': [
                (r'(?:near|around|close to)\s*(\w+)', 'near_location'),
                (r'(?:in|at)\s*(\w+)', 'in_location'),
                (r'hotspots?', 'hotspots'),
                (r'clusters?', 'clusters'),
            ],
            'temporal_patterns': [
                (r'(?:during|in|at)\s*(\d{1,2})\s*(?:am|pm|:\d{2})', 'time_filter'),
                (r'(?:between|from)\s*(\d{1,2})\s*(?:am|pm|:\d{2})?\s*(?:to|and|-)\s*(\d{1,2})\s*(?:am|pm|:\d{2})?', 'time_range'),
                (r'(?:last|past)\s*(\d+)\s*(day|week|month|year)s?', 'recent_period'),
                (r'(?:trend|forecast|predict)', 'trend_analysis'),
            ]
        }
    
    def process_query(self, query: str, df: pd.DataFrame) -> Dict[str, Any]:
        """
        Process natural language query and return results.
        
        Args:
            query: Natural language query string
            df: DataFrame to query
            
        Returns:
            Dictionary containing query results
        """
        query_lower = query.lower()
        
        try:
            # Parse the query to understand intent
            parsed_query = self._parse_query(query_lower, df)
            
            # Execute the parsed query
            result = self._execute_query(parsed_query, df)
            
            return {
                'status': 'success',
                'query': query,
                'parsed_intent': parsed_query,
                'result': result
            }
            
        except Exception as e:
            self.logger.error(f"Error processing query '{query}': {str(e)}")
            return {
                'status': 'error',
                'query': query,
                'error': str(e),
                'suggestion': self._get_query_suggestions(df)
            }
    
    def _parse_query(self, query: str, df: pd.DataFrame) -> Dict[str, Any]:
        """Parse query to understand intent and extract parameters"""
        parsed = {
            'intent': 'unknown',
            'operations': [],
            'columns_mentioned': [],
            'filters': [],
            'aggregations': [],
            'geographic': [],
            'temporal': []
        }
        
        # Find columns mentioned in the query
        parsed['columns_mentioned'] = self._find_mentioned_columns(query, df)
        
        # Check for different types of patterns
        for pattern_type, patterns in self.query_patterns.items():
            for pattern, operation in patterns:
                matches = re.finditer(pattern, query, re.IGNORECASE)
                for match in matches:
                    if pattern_type == 'filter_patterns':
                        parsed['filters'].append({
                            'type': operation,
                            'groups': match.groups(),
                            'match': match.group()
                        })
                    elif pattern_type == 'aggregation_patterns':
                        parsed['aggregations'].append({
                            'type': operation,
                            'column': match.group(1),
                            'match': match.group()
                        })
                    elif pattern_type == 'geographic_patterns':
                        parsed['geographic'].append({
                            'type': operation,
                            'groups': match.groups() if match.groups() else [],
                            'match': match.group()
                        })
                    elif pattern_type == 'temporal_patterns':
                        parsed['temporal'].append({
                            'type': operation,
                            'groups': match.groups() if match.groups() else [],
                            'match': match.group()
                        })
        
        # Determine primary intent
        if parsed['aggregations']:
            parsed['intent'] = 'aggregation'
        elif parsed['geographic']:
            parsed['intent'] = 'geographic'
        elif parsed['temporal']:
            parsed['intent'] = 'temporal'
        elif parsed['filters']:
            parsed['intent'] = 'filter'
        else:
            parsed['intent'] = 'exploration'
        
        return parsed
    
    def _find_mentioned_columns(self, query: str, df: pd.DataFrame) -> List[str]:
        """Find column names mentioned in the query"""
        mentioned_columns = []
        
        # Direct column name matches
        for col in df.columns:
            col_lower = col.lower()
            # Check for exact matches and variations
            variations = [col_lower, col_lower.replace('_', ' '), col_lower.replace('_', '')]
            
            for variation in variations:
                if variation in query:
                    mentioned_columns.append(col)
                    break
        
        # Keyword-based column mapping
        keyword_mappings = {
            'pollution': ['aqi', 'pm25', 'pm10', 'no2', 'pollution'],
            'traffic': ['traffic', 'volume', 'speed', 'congestion'],
            'crime': ['crime', 'incident', 'offense'],
            'temperature': ['temperature', 'temp'],
            'location': ['latitude', 'longitude', 'lat', 'lon', 'address'],
            'time': ['timestamp', 'date', 'time', 'datetime'],
            'population': ['population', 'density'],
            'price': ['price', 'cost', 'value', 'amount']
        }
        
        for keyword, possible_cols in keyword_mappings.items():
            if keyword in query:
                for col in df.columns:
                    if any(possible_col in col.lower() for possible_col in possible_cols):
                        if col not in mentioned_columns:
                            mentioned_columns.append(col)
        
        return mentioned_columns
    
    def _execute_query(self, parsed_query: Dict[str, Any], df: pd.DataFrame) -> Dict[str, Any]:
        """Execute the parsed query on the DataFrame"""
        result_df = df.copy()
        summary = []
        
        # Apply filters
        for filter_op in parsed_query['filters']:
            result_df, filter_summary = self._apply_filter(result_df, filter_op)
            summary.append(filter_summary)
        
        # Apply aggregations
        aggregation_results = {}
        for agg_op in parsed_query['aggregations']:
            agg_result = self._apply_aggregation(result_df, agg_op)
            aggregation_results.update(agg_result)
            summary.append(f"Calculated {agg_op['type']} of {agg_op['column']}")
        
        # Handle geographic queries
        geographic_results = {}
        for geo_op in parsed_query['geographic']:
            geo_result = self._handle_geographic_query(result_df, geo_op)
            geographic_results.update(geo_result)
            summary.append(f"Performed geographic analysis: {geo_op['type']}")
        
        # Handle temporal queries
        temporal_results = {}
        for temp_op in parsed_query['temporal']:
            temp_result = self._handle_temporal_query(result_df, temp_op)
            temporal_results.update(temp_result)
            summary.append(f"Performed temporal analysis: {temp_op['type']}")
        
        # Prepare final result
        result = {
            'summary': summary,
            'filtered_data_shape': result_df.shape,
            'aggregations': aggregation_results,
            'geographic_analysis': geographic_results,
            'temporal_analysis': temporal_results
        }
        
        # Include sample of filtered data if not too large
        if len(result_df) <= 100:
            result['sample_data'] = result_df.to_dict('records')
        else:
            result['sample_data'] = result_df.head(10).to_dict('records')
            result['note'] = f"Showing first 10 of {len(result_df)} results"
        
        return result
    
    def _apply_filter(self, df: pd.DataFrame, filter_op: Dict[str, Any]) -> tuple:
        """Apply filter operation to DataFrame"""
        filter_type = filter_op['type']
        groups = filter_op['groups']
        
        if filter_type == 'filter_numeric' and len(groups) >= 3:
            column, operator, value = groups[0], groups[1], float(groups[2])
            
            # Find best matching column
            matching_col = self._find_best_column_match(df, column)
            if matching_col:
                if operator == '>':
                    filtered_df = df[df[matching_col] > value]
                elif operator == '<':
                    filtered_df = df[df[matching_col] < value]
                elif operator == '>=':
                    filtered_df = df[df[matching_col] >= value]
                elif operator == '<=':
                    filtered_df = df[df[matching_col] <= value]
                elif operator == '=':
                    filtered_df = df[df[matching_col] == value]
                else:
                    filtered_df = df
                
                summary = f"Filtered {matching_col} {operator} {value}: {len(filtered_df)} rows remaining"
                return filtered_df, summary
        
        elif filter_type == 'filter_categorical' and len(groups) >= 2:
            column, value = groups[0], groups[1]
            
            matching_col = self._find_best_column_match(df, column)
            if matching_col:
                filtered_df = df[df[matching_col].astype(str).str.contains(value, case=False, na=False)]
                summary = f"Filtered {matching_col} containing '{value}': {len(filtered_df)} rows remaining"
                return filtered_df, summary
        
        return df, "No filter applied"
    
    def _apply_aggregation(self, df: pd.DataFrame, agg_op: Dict[str, Any]) -> Dict[str, float]:
        """Apply aggregation operation"""
        agg_type = agg_op['type']
        column = agg_op['column']
        
        matching_col = self._find_best_column_match(df, column)
        if not matching_col:
            return {}
        
        try:
            if agg_type == 'mean':
                result = df[matching_col].mean()
            elif agg_type == 'sum':
                result = df[matching_col].sum()
            elif agg_type == 'max':
                result = df[matching_col].max()
            elif agg_type == 'min':
                result = df[matching_col].min()
            elif agg_type == 'count':
                result = df[matching_col].count()
            else:
                return {}
            
            return {f"{agg_type}_{matching_col}": float(result)}
        
        except Exception as e:
            self.logger.error(f"Aggregation error: {str(e)}")
            return {}
    
    def _handle_geographic_query(self, df: pd.DataFrame, geo_op: Dict[str, Any]) -> Dict[str, Any]:
        """Handle geographic-related queries"""
        geo_type = geo_op['type']
        
        # Find latitude and longitude columns
        lat_cols = [col for col in df.columns if 'lat' in col.lower()]
        lon_cols = [col for col in df.columns if 'lon' in col.lower() or 'lng' in col.lower()]
        
        if not lat_cols or not lon_cols:
            return {'error': 'No geographic columns found'}
        
        lat_col, lon_col = lat_cols[0], lon_cols[0]
        
        if geo_type == 'hotspots':
            # Simple hotspot detection - find areas with highest values
            numeric_cols = df.select_dtypes(include=['number']).columns
            if len(numeric_cols) > 0:
                value_col = numeric_cols[0]  # Use first numeric column
                
                # Group by approximate location and sum values
                df_geo = df.copy()
                df_geo['lat_rounded'] = df_geo[lat_col].round(2)
                df_geo['lon_rounded'] = df_geo[lon_col].round(2)
                
                hotspots = df_geo.groupby(['lat_rounded', 'lon_rounded'])[value_col].sum().reset_index()
                hotspots = hotspots.sort_values(value_col, ascending=False).head(5)
                
                return {
                    'hotspots': hotspots.to_dict('records'),
                    'analysis': f'Top 5 hotspots based on {value_col}'
                }
        
        elif geo_type == 'clusters':
            return {
                'clusters': 'Clustering analysis would be performed here',
                'note': 'This would use the ClusterAnalyzer module'
            }
        
        return {}
    
    def _handle_temporal_query(self, df: pd.DataFrame, temp_op: Dict[str, Any]) -> Dict[str, Any]:
        """Handle time-related queries"""
        temp_type = temp_op['type']
        
        # Find date/time columns
        date_cols = [col for col in df.columns if any(term in col.lower() for term in ['date', 'time', 'timestamp'])]
        
        if not date_cols:
            return {'error': 'No time columns found'}
        
        date_col = date_cols[0]
        
        try:
            df_temp = df.copy()
            df_temp[date_col] = pd.to_datetime(df_temp[date_col])
            
            if temp_type == 'trend_analysis':
                # Simple trend analysis
                numeric_cols = df_temp.select_dtypes(include=['number']).columns
                if len(numeric_cols) > 0:
                    value_col = numeric_cols[0]
                    
                    # Calculate trend
                    df_temp = df_temp.sort_values(date_col)
                    df_temp['trend'] = df_temp[value_col].rolling(window=min(7, len(df_temp))).mean()
                    
                    recent_trend = df_temp['trend'].tail(3).mean() - df_temp['trend'].head(3).mean()
                    
                    return {
                        'trend_direction': 'increasing' if recent_trend > 0 else 'decreasing',
                        'trend_magnitude': abs(recent_trend),
                        'analysis': f'Trend analysis of {value_col} over time'
                    }
            
            elif temp_type == 'recent_period':
                groups = temp_op['groups']
                if len(groups) >= 2:
                    period_value, period_unit = int(groups[0]), groups[1]
                    
                    # Filter for recent period
                    cutoff_date = df_temp[date_col].max() - pd.Timedelta(**{f"{period_unit}s": period_value})
                    recent_data = df_temp[df_temp[date_col] >= cutoff_date]
                    
                    return {
                        'recent_data_points': len(recent_data),
                        'period': f"Last {period_value} {period_unit}(s)",
                        'date_range': f"{recent_data[date_col].min()} to {recent_data[date_col].max()}"
                    }
        
        except Exception as e:
            return {'error': f'Temporal analysis error: {str(e)}'}
        
        return {}
    
    def _find_best_column_match(self, df: pd.DataFrame, target_column: str) -> Optional[str]:
        """Find the best matching column name"""
        target_lower = target_column.lower()
        
        # Exact match first
        for col in df.columns:
            if col.lower() == target_lower:
                return col
        
        # Partial match
        for col in df.columns:
            if target_lower in col.lower() or col.lower() in target_lower:
                return col
        
        # Fuzzy match using common variations
        variations = [target_lower.replace(' ', '_'), target_lower.replace('_', ' '), target_lower.replace('_', '')]
        
        for variation in variations:
            for col in df.columns:
                if variation in col.lower():
                    return col
        
        return None
    
    def _get_query_suggestions(self, df: pd.DataFrame) -> List[str]:
        """Generate query suggestions based on the DataFrame structure"""
        suggestions = []
        
        # Column-based suggestions
        numeric_cols = df.select_dtypes(include=['number']).columns.tolist()
        if numeric_cols:
            suggestions.extend([
                f"What is the average {numeric_cols[0]}?",
                f"Show me values where {numeric_cols[0]} > 100",
                f"What is the maximum {numeric_cols[0]}?"
            ])
        
        # Geographic suggestions
        lat_cols = [col for col in df.columns if 'lat' in col.lower()]
        if lat_cols:
            suggestions.extend([
                "Show me pollution hotspots",
                "Find areas with high traffic",
                "Display geographic clusters"
            ])
        
        # Temporal suggestions
        date_cols = [col for col in df.columns if any(term in col.lower() for term in ['date', 'time'])]
        if date_cols:
            suggestions.extend([
                "Show me trends over time",
                "What happened in the last 7 days?",
                "Predict future values"
            ])
        
        return suggestions[:5]  # Return top 5 suggestions
