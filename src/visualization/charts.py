import plotly.express as px
import plotly.graph_objects as go
from plotly.subplots import make_subplots
import pandas as pd
import numpy as np
from typing import Dict, List, Any, Optional, Tuple

class ChartGenerator:
    """
    Generate various types of charts and visualizations for urban data analysis.
    """
    
    def __init__(self):
        self.default_colors = px.colors.qualitative.Set1
        
    def create_time_series_chart(self, df: pd.DataFrame, date_column: str, 
                               value_columns: List[str], title: str = "Time Series") -> go.Figure:
        """Create interactive time series chart"""
        fig = go.Figure()
        
        for i, column in enumerate(value_columns):
            fig.add_trace(go.Scatter(
                x=df[date_column],
                y=df[column],
                mode='lines+markers',
                name=column,
                line=dict(color=self.default_colors[i % len(self.default_colors)])
            ))
        
        fig.update_layout(
            title=title,
            xaxis_title=date_column,
            yaxis_title="Value",
            hovermode='x unified',
            showlegend=True
        )
        
        return fig
    
    def create_correlation_heatmap(self, df: pd.DataFrame, title: str = "Correlation Matrix") -> go.Figure:
        """Create correlation heatmap"""
        # Select only numeric columns
        numeric_df = df.select_dtypes(include=[np.number])
        
        if numeric_df.empty:
            raise ValueError("No numeric columns found for correlation analysis")
        
        correlation_matrix = numeric_df.corr()
        
        fig = go.Figure(data=go.Heatmap(
            z=correlation_matrix.values,
            x=correlation_matrix.columns,
            y=correlation_matrix.columns,
            colorscale='RdBu',
            zmid=0,
            text=correlation_matrix.round(2).values,
            texttemplate="%{text}",
            textfont={"size": 10},
            hoverongaps=False
        ))
        
        fig.update_layout(
            title=title,
            width=600,
            height=600
        )
        
        return fig
    
    def create_distribution_plot(self, df: pd.DataFrame, column: str, 
                               plot_type: str = "histogram") -> go.Figure:
        """Create distribution plots (histogram, box plot, violin plot)"""
        
        if plot_type == "histogram":
            fig = px.histogram(df, x=column, title=f"Distribution of {column}")
            
        elif plot_type == "box":
            fig = px.box(df, y=column, title=f"Box Plot of {column}")
            
        elif plot_type == "violin":
            fig = px.violin(df, y=column, title=f"Violin Plot of {column}")
            
        else:
            raise ValueError(f"Unsupported plot type: {plot_type}")
        
        return fig
    
    def create_scatter_plot(self, df: pd.DataFrame, x_column: str, y_column: str,
                          color_column: Optional[str] = None, size_column: Optional[str] = None,
                          title: str = "Scatter Plot") -> go.Figure:
        """Create interactive scatter plot"""
        
        kwargs = {
            'data_frame': df,
            'x': x_column,
            'y': y_column,
            'title': title
        }
        
        if color_column:
            kwargs['color'] = color_column
        if size_column:
            kwargs['size'] = size_column
            
        fig = px.scatter(**kwargs)
        
        return fig
    
    def create_bar_chart(self, df: pd.DataFrame, x_column: str, y_column: str,
                        orientation: str = "vertical", title: str = "Bar Chart") -> go.Figure:
        """Create bar chart"""
        
        if orientation == "vertical":
            fig = px.bar(df, x=x_column, y=y_column, title=title)
        else:
            fig = px.bar(df, x=y_column, y=x_column, orientation='h', title=title)
        
        return fig
    
    def create_line_chart(self, df: pd.DataFrame, x_column: str, y_column: str,
                         color_column: Optional[str] = None, title: str = "Line Chart") -> go.Figure:
        """Create line chart"""
        
        kwargs = {
            'data_frame': df,
            'x': x_column,
            'y': y_column,
            'title': title
        }
        
        if color_column:
            kwargs['color'] = color_column
            
        fig = px.line(**kwargs)
        
        return fig
    
    def create_3d_scatter(self, df: pd.DataFrame, x_column: str, y_column: str, z_column: str,
                         color_column: Optional[str] = None, title: str = "3D Scatter Plot") -> go.Figure:
        """Create 3D scatter plot"""
        
        kwargs = {
            'data_frame': df,
            'x': x_column,
            'y': y_column,
            'z': z_column,
            'title': title
        }
        
        if color_column:
            kwargs['color'] = color_column
            
        fig = px.scatter_3d(**kwargs)
        
        return fig
    
    def create_forecasting_chart(self, historical_data: Dict, forecast_data: Dict,
                               title: str = "Forecast Results") -> go.Figure:
        """Create forecasting visualization with confidence intervals"""
        
        fig = go.Figure()
        
        # Historical actual data
        fig.add_trace(go.Scatter(
            x=historical_data['dates'],
            y=historical_data['actual'],
            mode='lines+markers',
            name='Historical (Actual)',
            line=dict(color='blue')
        ))
        
        # Historical predicted data
        fig.add_trace(go.Scatter(
            x=historical_data['dates'],
            y=historical_data['predicted'],
            mode='lines',
            name='Historical (Predicted)',
            line=dict(color='orange', dash='dash')
        ))
        
        # Forecast data
        if forecast_data['dates']:
            fig.add_trace(go.Scatter(
                x=forecast_data['dates'],
                y=forecast_data['predicted'],
                mode='lines+markers',
                name='Forecast',
                line=dict(color='red')
            ))
            
            # Confidence intervals for forecast
            fig.add_trace(go.Scatter(
                x=forecast_data['dates'] + forecast_data['dates'][::-1],
                y=forecast_data['upper_bound'] + forecast_data['lower_bound'][::-1],
                fill='toself',
                fillcolor='rgba(255,0,0,0.1)',
                line=dict(color='rgba(255,255,255,0)'),
                name='Confidence Interval',
                showlegend=True
            ))
        
        fig.update_layout(
            title=title,
            xaxis_title="Date",
            yaxis_title="Value",
            hovermode='x unified'
        )
        
        return fig
    
    def create_clustering_chart(self, df: pd.DataFrame, x_column: str, y_column: str,
                              cluster_column: str = 'cluster', title: str = "Clustering Results") -> go.Figure:
        """Create clustering visualization"""
        
        fig = px.scatter(
            df, 
            x=x_column, 
            y=y_column, 
            color=cluster_column,
            title=title,
            color_discrete_sequence=self.default_colors
        )
        
        return fig
    
    def create_anomaly_detection_chart(self, df: pd.DataFrame, date_column: str, value_column: str,
                                     anomaly_column: str = 'is_anomaly', 
                                     title: str = "Anomaly Detection") -> go.Figure:
        """Create anomaly detection visualization"""
        
        fig = go.Figure()
        
        # Normal data points
        normal_data = df[~df[anomaly_column]]
        fig.add_trace(go.Scatter(
            x=normal_data[date_column],
            y=normal_data[value_column],
            mode='lines+markers',
            name='Normal',
            line=dict(color='blue'),
            marker=dict(size=4)
        ))
        
        # Anomaly data points
        anomaly_data = df[df[anomaly_column]]
        if not anomaly_data.empty:
            fig.add_trace(go.Scatter(
                x=anomaly_data[date_column],
                y=anomaly_data[value_column],
                mode='markers',
                name='Anomalies',
                marker=dict(color='red', size=8, symbol='x')
            ))
        
        fig.update_layout(
            title=title,
            xaxis_title=date_column,
            yaxis_title=value_column,
            hovermode='x unified'
        )
        
        return fig
    
    def create_multi_metric_dashboard(self, df: pd.DataFrame, date_column: str, 
                                    metric_columns: List[str], title: str = "Multi-Metric Dashboard") -> go.Figure:
        """Create dashboard with multiple metrics"""
        
        # Create subplots
        fig = make_subplots(
            rows=len(metric_columns), 
            cols=1,
            subplot_titles=metric_columns,
            shared_xaxes=True,
            vertical_spacing=0.1
        )
        
        for i, metric in enumerate(metric_columns, 1):
            fig.add_trace(
                go.Scatter(
                    x=df[date_column],
                    y=df[metric],
                    mode='lines',
                    name=metric,
                    line=dict(color=self.default_colors[i % len(self.default_colors)])
                ),
                row=i, col=1
            )
        
        fig.update_layout(
            title=title,
            height=200 * len(metric_columns),
            showlegend=False
        )
        
        return fig
    
    def create_geographic_density_chart(self, df: pd.DataFrame, lat_column: str, lon_column: str,
                                      title: str = "Geographic Density") -> go.Figure:
        """Create geographic density visualization"""
        
        fig = px.density_mapbox(
            df,
            lat=lat_column,
            lon=lon_column,
            radius=10,
            center=dict(lat=df[lat_column].mean(), lon=df[lon_column].mean()),
            zoom=10,
            mapbox_style="open-street-map",
            title=title
        )
        
        return fig
    
    def create_comparative_bar_chart(self, data: Dict[str, List], title: str = "Comparative Analysis") -> go.Figure:
        """Create comparative bar chart from dictionary data"""
        
        categories = list(data.keys())
        values = list(data.values())
        
        fig = go.Figure(data=[
            go.Bar(x=categories, y=values, marker_color=self.default_colors)
        ])
        
        fig.update_layout(
            title=title,
            xaxis_title="Categories",
            yaxis_title="Values"
        )
        
        return fig
    
    def create_heatmap_calendar(self, df: pd.DataFrame, date_column: str, value_column: str,
                              title: str = "Calendar Heatmap") -> go.Figure:
        """Create calendar heatmap showing values over time"""
        
        # Prepare data
        df_cal = df.copy()
        df_cal[date_column] = pd.to_datetime(df_cal[date_column])
        df_cal['day_of_week'] = df_cal[date_column].dt.day_name()
        df_cal['week'] = df_cal[date_column].dt.isocalendar().week
        
        # Create pivot table
        pivot_data = df_cal.pivot_table(
            values=value_column,
            index='day_of_week',
            columns='week',
            aggfunc='mean'
        )
        
        fig = go.Figure(data=go.Heatmap(
            z=pivot_data.values,
            x=pivot_data.columns,
            y=pivot_data.index,
            colorscale='Viridis',
            hoverongaps=False
        ))
        
        fig.update_layout(
            title=title,
            xaxis_title="Week of Year",
            yaxis_title="Day of Week"
        )
        
        return fig
