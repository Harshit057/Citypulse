import pandas as pd
import numpy as np
from sklearn.preprocessing import StandardScaler
from sklearn.cluster import KMeans, DBSCAN
from sklearn.decomposition import PCA
from sklearn.metrics import silhouette_score
from typing import Dict, List, Any, Optional
import logging

class ClusterAnalyzer:
    """
    Machine learning clustering analysis for urban data.
    Supports various clustering algorithms for different use cases.
    """
    
    def __init__(self):
        self.logger = logging.getLogger(__name__)
        self.scaler = StandardScaler()
        self.models = {}
        
    def perform_clustering(self, df: pd.DataFrame, features: List[str], 
                          n_clusters: int = 3, algorithm: str = 'kmeans') -> Dict[str, Any]:
        """
        Perform clustering analysis on the dataset.
        
        Args:
            df: Input DataFrame
            features: List of feature columns to use for clustering
            n_clusters: Number of clusters (for KMeans)
            algorithm: Clustering algorithm ('kmeans', 'dbscan')
            
        Returns:
            Dictionary containing clustering results
        """
        # Validate features
        missing_features = [f for f in features if f not in df.columns]
        if missing_features:
            raise ValueError(f"Features not found in data: {missing_features}")
        
        # Prepare data
        X = self._prepare_features(df, features)
        
        # Perform clustering
        if algorithm == 'kmeans':
            results = self._kmeans_clustering(X, n_clusters)
        elif algorithm == 'dbscan':
            results = self._dbscan_clustering(X)
        else:
            raise ValueError(f"Unsupported algorithm: {algorithm}")
        
        # Add cluster labels to original data
        df_with_clusters = df.copy()
        df_with_clusters['cluster'] = results['labels']
        
        # Generate cluster analysis
        cluster_analysis = self._analyze_clusters(df_with_clusters, features)
        
        results.update({
            'features_used': features,
            'cluster_analysis': cluster_analysis,
            'data_with_clusters': df_with_clusters.to_dict('records')
        })
        
        return results
    
    def _prepare_features(self, df: pd.DataFrame, features: List[str]) -> np.ndarray:
        """Prepare and scale features for clustering"""
        # Select features and handle missing values
        X = df[features].copy()
        
        # Fill missing values with median for numeric columns
        for col in X.columns:
            if X[col].dtype in ['int64', 'float64']:
                X[col] = X[col].fillna(X[col].median())
            else:
                # Convert categorical to numeric if needed
                X[col] = pd.Categorical(X[col]).codes
        
        # Scale features
        X_scaled = self.scaler.fit_transform(X)
        
        return X_scaled
    
    def _kmeans_clustering(self, X: np.ndarray, n_clusters: int) -> Dict[str, Any]:
        """Perform K-means clustering"""
        # Find optimal number of clusters if not specified
        if n_clusters == 'auto':
            n_clusters = self._find_optimal_clusters(X)
        
        # Fit K-means
        kmeans = KMeans(n_clusters=n_clusters, random_state=42, n_init=10)
        labels = kmeans.fit_predict(X)
        
        # Calculate metrics
        silhouette_avg = silhouette_score(X, labels)
        inertia = kmeans.inertia_
        
        # Store model
        self.models['kmeans'] = kmeans
        
        return {
            'algorithm': 'kmeans',
            'n_clusters': n_clusters,
            'labels': labels,
            'cluster_centers': kmeans.cluster_centers_.tolist(),
            'silhouette_score': silhouette_avg,
            'inertia': inertia,
            'metrics': {
                'silhouette_score': silhouette_avg,
                'inertia': inertia
            }
        }
    
    def _dbscan_clustering(self, X: np.ndarray, eps: float = 0.5, min_samples: int = 5) -> Dict[str, Any]:
        """Perform DBSCAN clustering"""
        dbscan = DBSCAN(eps=eps, min_samples=min_samples)
        labels = dbscan.fit_predict(X)
        
        # Calculate metrics
        n_clusters = len(set(labels)) - (1 if -1 in labels else 0)
        n_noise = list(labels).count(-1)
        
        silhouette_avg = None
        if n_clusters > 1:
            # Only calculate silhouette score if we have valid clusters
            mask = labels != -1
            if np.sum(mask) > 1:
                silhouette_avg = silhouette_score(X[mask], labels[mask])
        
        # Store model
        self.models['dbscan'] = dbscan
        
        return {
            'algorithm': 'dbscan',
            'n_clusters': n_clusters,
            'n_noise_points': n_noise,
            'labels': labels,
            'eps': eps,
            'min_samples': min_samples,
            'silhouette_score': silhouette_avg,
            'metrics': {
                'n_clusters': n_clusters,
                'n_noise_points': n_noise,
                'silhouette_score': silhouette_avg
            }
        }
    
    def _find_optimal_clusters(self, X: np.ndarray, max_clusters: int = 10) -> int:
        """Find optimal number of clusters using elbow method"""
        inertias = []
        silhouette_scores = []
        
        K_range = range(2, min(max_clusters + 1, len(X)))
        
        for k in K_range:
            kmeans = KMeans(n_clusters=k, random_state=42, n_init=10)
            labels = kmeans.fit_predict(X)
            
            inertias.append(kmeans.inertia_)
            silhouette_scores.append(silhouette_score(X, labels))
        
        # Find elbow point (simplified)
        if len(silhouette_scores) > 0:
            optimal_k = K_range[np.argmax(silhouette_scores)]
        else:
            optimal_k = 3  # Default
        
        return optimal_k
    
    def _analyze_clusters(self, df_with_clusters: pd.DataFrame, features: List[str]) -> Dict[str, Any]:
        """Analyze characteristics of each cluster"""
        analysis = {}
        
        for cluster_id in df_with_clusters['cluster'].unique():
            cluster_data = df_with_clusters[df_with_clusters['cluster'] == cluster_id]
            
            cluster_stats = {
                'size': len(cluster_data),
                'percentage': len(cluster_data) / len(df_with_clusters) * 100,
                'feature_means': {},
                'feature_stats': {}
            }
            
            # Calculate feature statistics for this cluster
            for feature in features:
                if df_with_clusters[feature].dtype in ['int64', 'float64']:
                    cluster_stats['feature_means'][feature] = cluster_data[feature].mean()
                    cluster_stats['feature_stats'][feature] = {
                        'mean': cluster_data[feature].mean(),
                        'median': cluster_data[feature].median(),
                        'std': cluster_data[feature].std(),
                        'min': cluster_data[feature].min(),
                        'max': cluster_data[feature].max()
                    }
                else:
                    # For categorical features
                    cluster_stats['feature_stats'][feature] = cluster_data[feature].value_counts().to_dict()
            
            analysis[f'cluster_{cluster_id}'] = cluster_stats
        
        return analysis
    
    def detect_hotspots(self, df: pd.DataFrame, lat_col: str, lon_col: str, 
                       value_col: str, method: str = 'kmeans') -> Dict[str, Any]:
        """
        Detect hotspots (high-value clusters) in geographic data.
        
        Args:
            df: DataFrame with geographic data
            lat_col: Latitude column name
            lon_col: Longitude column name  
            value_col: Value column to analyze (e.g., crime count, pollution level)
            method: Clustering method ('kmeans', 'dbscan')
            
        Returns:
            Hotspot analysis results
        """
        # Validate required columns
        required_cols = [lat_col, lon_col, value_col]
        missing_cols = [col for col in required_cols if col not in df.columns]
        if missing_cols:
            raise ValueError(f"Required columns not found: {missing_cols}")
        
        # Filter out missing coordinates
        valid_data = df.dropna(subset=[lat_col, lon_col, value_col])
        
        if len(valid_data) == 0:
            raise ValueError("No valid geographic data found")
        
        # Perform clustering on coordinates
        coord_features = [lat_col, lon_col]
        clustering_results = self.perform_clustering(
            valid_data, coord_features, algorithm=method
        )
        
        # Analyze clusters by value column
        df_with_clusters = pd.DataFrame(clustering_results['data_with_clusters'])
        
        hotspot_analysis = {}
        for cluster_id in df_with_clusters['cluster'].unique():
            cluster_data = df_with_clusters[df_with_clusters['cluster'] == cluster_id]
            
            hotspot_analysis[f'cluster_{cluster_id}'] = {
                'center_lat': cluster_data[lat_col].mean(),
                'center_lon': cluster_data[lon_col].mean(),
                'size': len(cluster_data),
                'avg_value': cluster_data[value_col].mean(),
                'total_value': cluster_data[value_col].sum(),
                'max_value': cluster_data[value_col].max(),
                'min_value': cluster_data[value_col].min(),
                'value_std': cluster_data[value_col].std()
            }
        
        # Rank clusters by average value (hotspots = high values)
        cluster_rankings = sorted(
            hotspot_analysis.items(),
            key=lambda x: x[1]['avg_value'],
            reverse=True
        )
        
        return {
            'clustering_results': clustering_results,
            'hotspot_analysis': hotspot_analysis,
            'ranked_hotspots': cluster_rankings,
            'top_hotspot': cluster_rankings[0] if cluster_rankings else None
        }
    
    def crime_hotspot_analysis(self, df: pd.DataFrame, lat_col: str = 'latitude', 
                              lon_col: str = 'longitude') -> Dict[str, Any]:
        """Specialized analysis for crime hotspot detection"""
        # Count crimes per location
        crime_counts = df.groupby([lat_col, lon_col]).size().reset_index(name='crime_count')
        
        # Detect hotspots
        return self.detect_hotspots(crime_counts, lat_col, lon_col, 'crime_count')
    
    def pollution_hotspot_analysis(self, df: pd.DataFrame, lat_col: str = 'latitude',
                                  lon_col: str = 'longitude', pollution_col: str = 'aqi') -> Dict[str, Any]:
        """Specialized analysis for pollution hotspot detection"""
        return self.detect_hotspots(df, lat_col, lon_col, pollution_col)
    
    def traffic_congestion_analysis(self, df: pd.DataFrame, lat_col: str = 'latitude',
                                   lon_col: str = 'longitude', congestion_col: str = 'congestion_level') -> Dict[str, Any]:
        """Specialized analysis for traffic congestion clustering"""
        return self.detect_hotspots(df, lat_col, lon_col, congestion_col)
    
    def perform_pca_analysis(self, df: pd.DataFrame, features: List[str], 
                            n_components: int = 2) -> Dict[str, Any]:
        """
        Perform Principal Component Analysis for dimensionality reduction.
        
        Args:
            df: Input DataFrame
            features: Features to include in PCA
            n_components: Number of principal components
            
        Returns:
            PCA analysis results
        """
        # Prepare features
        X = self._prepare_features(df, features)
        
        # Fit PCA
        pca = PCA(n_components=n_components)
        X_pca = pca.fit_transform(X)
        
        # Create results
        results = {
            'n_components': n_components,
            'explained_variance_ratio': pca.explained_variance_ratio_.tolist(),
            'cumulative_variance_ratio': np.cumsum(pca.explained_variance_ratio_).tolist(),
            'components': pca.components_.tolist(),
            'transformed_data': X_pca.tolist(),
            'feature_importance': {}
        }
        
        # Feature importance for each component
        for i, component in enumerate(pca.components_):
            results['feature_importance'][f'PC{i+1}'] = {
                feature: float(importance) 
                for feature, importance in zip(features, component)
            }
        
        return results
