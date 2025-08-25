import folium
from folium import plugins
import pandas as pd
import numpy as np
from typing import Dict, List, Any, Optional, Tuple
import json

class MapGenerator:
    """
    Generate interactive maps for geographic data visualization using Folium.
    """
    
    def __init__(self):
        self.default_center = [28.6139, 77.2090]  # Delhi coordinates as default
        self.default_zoom = 10
        
    def create_base_map(self, center: Optional[List[float]] = None, 
                       zoom: int = 10, tiles: str = 'OpenStreetMap') -> folium.Map:
        """Create base map with specified center and zoom"""
        
        if center is None:
            center = self.default_center
            
        map_obj = folium.Map(
            location=center,
            zoom_start=zoom,
            tiles=tiles
        )
        
        return map_obj
    
    def create_point_map(self, df: pd.DataFrame, lat_column: str, lon_column: str,
                        popup_columns: Optional[List[str]] = None, 
                        color_column: Optional[str] = None,
                        title: str = "Point Map") -> folium.Map:
        """Create map with point markers"""
        
        # Calculate center
        center_lat = df[lat_column].mean()
        center_lon = df[lon_column].mean()
        
        # Create base map
        map_obj = self.create_base_map([center_lat, center_lon])
        
        # Color mapping
        if color_column:
            unique_values = df[color_column].unique()
            colors = ['red', 'blue', 'green', 'purple', 'orange', 'darkred',
                     'lightred', 'beige', 'darkblue', 'darkgreen', 'cadetblue',
                     'darkpurple', 'white', 'pink', 'lightblue', 'lightgreen',
                     'gray', 'black', 'lightgray']
            color_map = {val: colors[i % len(colors)] for i, val in enumerate(unique_values)}
        
        # Add points
        for idx, row in df.iterrows():
            if pd.notna(row[lat_column]) and pd.notna(row[lon_column]):
                # Prepare popup content
                if popup_columns:
                    popup_text = "<br>".join([f"<b>{col}:</b> {row[col]}" for col in popup_columns])
                else:
                    popup_text = f"Point {idx}"
                
                # Determine marker color
                marker_color = 'blue'  # default
                if color_column and color_column in row:
                    marker_color = color_map.get(row[color_column], 'blue')
                
                folium.Marker(
                    location=[row[lat_column], row[lon_column]],
                    popup=folium.Popup(popup_text, max_width=300),
                    icon=folium.Icon(color=marker_color)
                ).add_to(map_obj)
        
        return map_obj
    
    def create_heatmap(self, df: pd.DataFrame, lat_column: str, lon_column: str,
                      intensity_column: Optional[str] = None, title: str = "Heatmap") -> folium.Map:
        """Create heatmap visualization"""
        
        # Calculate center
        center_lat = df[lat_column].mean()
        center_lon = df[lon_column].mean()
        
        # Create base map
        map_obj = self.create_base_map([center_lat, center_lon])
        
        # Prepare heat data
        if intensity_column:
            heat_data = [[row[lat_column], row[lon_column], row[intensity_column]] 
                        for idx, row in df.iterrows() 
                        if pd.notna(row[lat_column]) and pd.notna(row[lon_column]) and pd.notna(row[intensity_column])]
        else:
            heat_data = [[row[lat_column], row[lon_column]] 
                        for idx, row in df.iterrows() 
                        if pd.notna(row[lat_column]) and pd.notna(row[lon_column])]
        
        # Add heatmap layer
        plugins.HeatMap(heat_data, radius=15, blur=20, max_zoom=1).add_to(map_obj)
        
        return map_obj
    
    def create_cluster_map(self, df: pd.DataFrame, lat_column: str, lon_column: str,
                          cluster_column: str = 'cluster', popup_columns: Optional[List[str]] = None,
                          title: str = "Cluster Map") -> folium.Map:
        """Create map showing clustering results"""
        
        # Calculate center
        center_lat = df[lat_column].mean()
        center_lon = df[lon_column].mean()
        
        # Create base map
        map_obj = self.create_base_map([center_lat, center_lon])
        
        # Color mapping for clusters
        unique_clusters = df[cluster_column].unique()
        colors = ['red', 'blue', 'green', 'purple', 'orange', 'darkred',
                 'lightred', 'beige', 'darkblue', 'darkgreen']
        cluster_colors = {cluster: colors[i % len(colors)] for i, cluster in enumerate(unique_clusters)}
        
        # Add markers for each cluster
        for cluster in unique_clusters:
            cluster_data = df[df[cluster_column] == cluster]
            
            for idx, row in cluster_data.iterrows():
                if pd.notna(row[lat_column]) and pd.notna(row[lon_column]):
                    # Prepare popup content
                    popup_content = [f"<b>Cluster:</b> {cluster}"]
                    if popup_columns:
                        popup_content.extend([f"<b>{col}:</b> {row[col]}" for col in popup_columns])
                    popup_text = "<br>".join(popup_content)
                    
                    folium.CircleMarker(
                        location=[row[lat_column], row[lon_column]],
                        radius=8,
                        popup=folium.Popup(popup_text, max_width=300),
                        color=cluster_colors[cluster],
                        fillColor=cluster_colors[cluster],
                        fillOpacity=0.7
                    ).add_to(map_obj)
        
        # Add cluster centers if available
        if 'cluster_center_lat' in df.columns and 'cluster_center_lon' in df.columns:
            cluster_centers = df.groupby(cluster_column)[['cluster_center_lat', 'cluster_center_lon']].first()
            
            for cluster, center in cluster_centers.iterrows():
                folium.Marker(
                    location=[center['cluster_center_lat'], center['cluster_center_lon']],
                    popup=f"Cluster {cluster} Center",
                    icon=folium.Icon(color='black', icon='star')
                ).add_to(map_obj)
        
        return map_obj
    
    def create_choropleth_map(self, geojson_data: Dict, df: pd.DataFrame, 
                             key_column: str, value_column: str,
                             title: str = "Choropleth Map") -> folium.Map:
        """Create choropleth map for administrative boundaries"""
        
        # Create base map
        map_obj = self.create_base_map()
        
        # Create choropleth
        folium.Choropleth(
            geo_data=geojson_data,
            name='choropleth',
            data=df,
            columns=[key_column, value_column],
            key_on=f'feature.properties.{key_column}',
            fill_color='YlOrRd',
            fill_opacity=0.7,
            line_opacity=0.2,
            legend_name=value_column
        ).add_to(map_obj)
        
        folium.LayerControl().add_to(map_obj)
        
        return map_obj
    
    def create_traffic_flow_map(self, df: pd.DataFrame, lat_column: str, lon_column: str,
                               traffic_column: str, title: str = "Traffic Flow Map") -> folium.Map:
        """Create traffic flow visualization"""
        
        # Calculate center
        center_lat = df[lat_column].mean()
        center_lon = df[lon_column].mean()
        
        # Create base map
        map_obj = self.create_base_map([center_lat, center_lon])
        
        # Normalize traffic values for color coding
        min_traffic = df[traffic_column].min()
        max_traffic = df[traffic_column].max()
        
        def get_color(traffic_value):
            # Normalize to 0-1 range
            normalized = (traffic_value - min_traffic) / (max_traffic - min_traffic)
            if normalized < 0.3:
                return 'green'  # Low traffic
            elif normalized < 0.7:
                return 'orange'  # Medium traffic
            else:
                return 'red'  # High traffic
        
        # Add circle markers with size based on traffic
        for idx, row in df.iterrows():
            if pd.notna(row[lat_column]) and pd.notna(row[lon_column]) and pd.notna(row[traffic_column]):
                normalized_traffic = (row[traffic_column] - min_traffic) / (max_traffic - min_traffic)
                radius = 5 + (normalized_traffic * 15)  # Scale radius from 5 to 20
                
                folium.CircleMarker(
                    location=[row[lat_column], row[lon_column]],
                    radius=radius,
                    popup=f"Traffic: {row[traffic_column]}",
                    color=get_color(row[traffic_column]),
                    fillColor=get_color(row[traffic_column]),
                    fillOpacity=0.6
                ).add_to(map_obj)
        
        return map_obj
    
    def create_pollution_map(self, df: pd.DataFrame, lat_column: str, lon_column: str,
                           pollution_column: str = 'aqi', title: str = "Air Quality Map") -> folium.Map:
        """Create air quality/pollution visualization"""
        
        # Calculate center
        center_lat = df[lat_column].mean()
        center_lon = df[lon_column].mean()
        
        # Create base map
        map_obj = self.create_base_map([center_lat, center_lon])
        
        def get_aqi_color(aqi_value):
            """Get color based on AQI standards"""
            if aqi_value <= 50:
                return 'green'  # Good
            elif aqi_value <= 100:
                return 'yellow'  # Moderate
            elif aqi_value <= 150:
                return 'orange'  # Unhealthy for Sensitive Groups
            elif aqi_value <= 200:
                return 'red'  # Unhealthy
            elif aqi_value <= 300:
                return 'purple'  # Very Unhealthy
            else:
                return 'darkred'  # Hazardous
        
        def get_aqi_category(aqi_value):
            """Get AQI category"""
            if aqi_value <= 50:
                return 'Good'
            elif aqi_value <= 100:
                return 'Moderate'
            elif aqi_value <= 150:
                return 'Unhealthy for Sensitive Groups'
            elif aqi_value <= 200:
                return 'Unhealthy'
            elif aqi_value <= 300:
                return 'Very Unhealthy'
            else:
                return 'Hazardous'
        
        # Add markers
        for idx, row in df.iterrows():
            if pd.notna(row[lat_column]) and pd.notna(row[lon_column]) and pd.notna(row[pollution_column]):
                aqi_value = row[pollution_column]
                
                folium.CircleMarker(
                    location=[row[lat_column], row[lon_column]],
                    radius=10,
                    popup=f"AQI: {aqi_value}<br>Category: {get_aqi_category(aqi_value)}",
                    color=get_aqi_color(aqi_value),
                    fillColor=get_aqi_color(aqi_value),
                    fillOpacity=0.7
                ).add_to(map_obj)
        
        return map_obj
    
    def create_route_map(self, route_data: List[Tuple[float, float]], 
                        start_location: Optional[Tuple[float, float]] = None,
                        end_location: Optional[Tuple[float, float]] = None,
                        title: str = "Route Map") -> folium.Map:
        """Create map showing a route"""
        
        if not route_data:
            raise ValueError("Route data cannot be empty")
        
        # Calculate center from route points
        lats = [point[0] for point in route_data]
        lons = [point[1] for point in route_data]
        center_lat = sum(lats) / len(lats)
        center_lon = sum(lons) / len(lons)
        
        # Create base map
        map_obj = self.create_base_map([center_lat, center_lon])
        
        # Add route line
        folium.PolyLine(
            locations=route_data,
            color='blue',
            weight=5,
            opacity=0.8
        ).add_to(map_obj)
        
        # Add start marker
        if start_location:
            folium.Marker(
                location=start_location,
                popup="Start",
                icon=folium.Icon(color='green', icon='play')
            ).add_to(map_obj)
        
        # Add end marker
        if end_location:
            folium.Marker(
                location=end_location,
                popup="End",
                icon=folium.Icon(color='red', icon='stop')
            ).add_to(map_obj)
        
        return map_obj
    
    def create_multi_layer_map(self, datasets: Dict[str, pd.DataFrame], 
                             lat_column: str, lon_column: str,
                             title: str = "Multi-Layer Map") -> folium.Map:
        """Create map with multiple layers"""
        
        # Calculate overall center
        all_lats = []
        all_lons = []
        
        for df in datasets.values():
            all_lats.extend(df[lat_column].dropna().tolist())
            all_lons.extend(df[lon_column].dropna().tolist())
        
        center_lat = sum(all_lats) / len(all_lats)
        center_lon = sum(all_lons) / len(all_lons)
        
        # Create base map
        map_obj = self.create_base_map([center_lat, center_lon])
        
        # Colors for different layers
        colors = ['red', 'blue', 'green', 'purple', 'orange']
        
        # Add each dataset as a separate layer
        for i, (layer_name, df) in enumerate(datasets.items()):
            color = colors[i % len(colors)]
            
            feature_group = folium.FeatureGroup(name=layer_name)
            
            for idx, row in df.iterrows():
                if pd.notna(row[lat_column]) and pd.notna(row[lon_column]):
                    folium.CircleMarker(
                        location=[row[lat_column], row[lon_column]],
                        radius=6,
                        popup=f"{layer_name}: Point {idx}",
                        color=color,
                        fillColor=color,
                        fillOpacity=0.6
                    ).add_to(feature_group)
            
            feature_group.add_to(map_obj)
        
        # Add layer control
        folium.LayerControl().add_to(map_obj)
        
        return map_obj
    
    def save_map(self, map_obj: folium.Map, filename: str):
        """Save map to HTML file"""
        map_obj.save(filename)
        
    def add_legend(self, map_obj: folium.Map, legend_dict: Dict[str, str]):
        """Add custom legend to map"""
        legend_html = '''
        <div style="position: fixed; 
                    bottom: 50px; left: 50px; width: 150px; height: 90px; 
                    background-color: white; border:2px solid grey; z-index:9999; 
                    font-size:14px; ">
        <p style="margin: 10px;"><b>Legend</b></p>
        '''
        
        for label, color in legend_dict.items():
            legend_html += f'<p style="margin: 5px;"><i style="background:{color}; width: 15px; height: 15px; float: left; margin-right: 8px;"></i>{label}</p>'
        
        legend_html += '</div>'
        
        map_obj.get_root().html.add_child(folium.Element(legend_html))
