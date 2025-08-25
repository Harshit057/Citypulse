# CityPulse - Urban Analytics Platform

A comprehensive data science and machine learning powered urban analytics platform for analyzing city-level datasets, generating visualizations, and running predictive models.

## 🏙️ Features

- **Data Ingestion**: Upload CSV files or connect to APIs (OpenWeather, Government Open Data)
- **Interactive Visualizations**: Heatmaps, graphs, and geospatial maps
- **Natural Language Queries**: Ask questions about your data in plain English
- **Machine Learning**: Forecasting, clustering, and anomaly detection
- **Real-time Dashboards**: Interactive web interface with filters and controls

## 🚀 Quick Start

1. **Install Dependencies**
   ```bash
   pip install -r requirements.txt
   ```

2. **Set up Environment Variables**
   ```bash
   cp .env.example .env
   # Edit .env with your API keys and database settings
   ```

3. **Initialize Database** (Optional - for persistent storage)
   ```bash
   python scripts/init_db.py
   ```

4. **Run the Application**
   ```bash
   # Streamlit Interface
   streamlit run app/streamlit_app.py
   
   # Or Flask API
   python app/flask_app.py
   ```

## 📁 Project Structure

```
citypulse/
├── app/                    # Web applications
│   ├── streamlit_app.py   # Main Streamlit interface
│   ├── flask_app.py       # Flask API backend
│   └── components/        # Reusable UI components
├── src/                   # Core application logic
│   ├── data/             # Data processing modules
│   ├── ml/               # Machine learning models
│   ├── visualization/    # Plotting and mapping
│   └── api/              # External API integrations
├── data/                 # Data storage
│   ├── raw/              # Raw uploaded datasets
│   ├── processed/        # Cleaned datasets
│   └── models/           # Trained ML models
├── config/               # Configuration files
├── scripts/              # Utility scripts
├── tests/                # Unit tests
└── docs/                 # Documentation
```

## 🛠️ Technology Stack

- **Backend**: Python, Flask, FastAPI
- **Frontend**: Streamlit, React (optional)
- **Data Science**: Pandas, NumPy, GeoPandas, Scikit-learn
- **Visualization**: Plotly, Folium, Matplotlib, Seaborn
- **ML**: Prophet, TensorFlow, Statsmodels
- **Database**: PostgreSQL with PostGIS extension
- **APIs**: OpenAI, OpenWeather, Government Open Data

## 📊 Example Use Cases

1. **Traffic Analysis**: Upload traffic data to generate congestion heatmaps
2. **Air Quality Forecasting**: Predict AQI levels using time series models
3. **Crime Hotspot Detection**: Use clustering to identify high-crime areas
4. **Real Estate Trends**: Analyze property prices across different neighborhoods

## 🔧 Configuration

Copy `.env.example` to `.env` and configure:

- Database connection settings
- API keys (OpenWeather, OpenAI, etc.)
- Application settings

## 📈 Development

1. **Setup Development Environment**
   ```bash
   python -m venv venv
   source venv/bin/activate  # On Windows: venv\Scripts\activate
   pip install -r requirements.txt
   ```

2. **Run Tests**
   ```bash
   python -m pytest tests/
   ```

3. **Code Formatting**
   ```bash
   black src/ app/
   flake8 src/ app/
   ```

## 🌍 Data Sources

- OpenWeatherMap API
- Government Open Data portals
- Google Maps API
- User-uploaded CSV files
- Real-time sensor data

## 📝 License

MIT License - see LICENSE file for details.

## 🤝 Contributing

1. Fork the repository
2. Create a feature branch
3. Make your changes
4. Add tests
5. Submit a pull request

## 📞 Support

For questions and support, please open an issue on GitHub or contact the development team.
