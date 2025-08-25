# CityPulse Deployment Guide

## 🚀 Deployment Options

### Option 1: Streamlit Cloud (Easiest - Free)

1. **Prepare your repository:**
   ```bash
   git add .
   git commit -m "Prepare for deployment"
   git push origin main
   ```

2. **Deploy:**
   - Visit [share.streamlit.io](https://share.streamlit.io)
   - Sign in with GitHub
   - Click "New app"
   - Select your repository and `app/streamlit_app.py`
   - Click "Deploy"

3. **Environment variables (if needed):**
   - Add secrets in Streamlit Cloud dashboard
   - Format: `KEY = "value"`

---

### Option 2: Heroku (Full-Featured)

1. **Install Heroku CLI**
2. **Login and create app:**
   ```bash
   heroku login
   heroku create your-citypulse-app
   ```

3. **Set environment variables:**
   ```bash
   heroku config:set DATABASE_URL=your_db_url
   heroku config:set OPENWEATHER_API_KEY=your_api_key
   ```

4. **Deploy:**
   ```bash
   git add .
   git commit -m "Deploy to Heroku"
   git push heroku main
   ```

5. **Open app:**
   ```bash
   heroku open
   ```

---

### Option 3: Railway (Modern & Simple)

1. **Install Railway CLI:**
   ```bash
   npm install -g @railway/cli
   ```

2. **Login and deploy:**
   ```bash
   railway login
   railway init
   railway up
   ```

3. **Add environment variables in Railway dashboard**

---

### Option 4: Google Cloud Platform

1. **Install Google Cloud SDK**
2. **Initialize project:**
   ```bash
   gcloud init
   gcloud app create
   ```

3. **Deploy:**
   ```bash
   gcloud app deploy
   ```

---

### Option 5: Digital Ocean App Platform

1. **Connect GitHub repository in DO dashboard**
2. **Use the provided `.do/app.yaml` configuration**
3. **Deploy via dashboard**

---

### Option 6: Docker + Any Cloud Provider

1. **Build Docker image:**
   ```bash
   docker build -t citypulse .
   docker run -p 8501:8501 citypulse
   ```

2. **Deploy to:**
   - AWS ECS/Fargate
   - Google Cloud Run
   - Azure Container Instances
   - DigitalOcean Droplets

---

## 🔧 Pre-Deployment Checklist

### 1. Environment Configuration
- [ ] Create `.env` file with API keys
- [ ] Set database connection strings
- [ ] Configure CORS settings for Flask API

### 2. Security
- [ ] Remove debug flags in production
- [ ] Set strong passwords for database
- [ ] Use HTTPS for production
- [ ] Validate all user inputs

### 3. Performance
- [ ] Optimize data loading
- [ ] Enable caching where appropriate
- [ ] Compress static assets
- [ ] Set up database connection pooling

### 4. Monitoring
- [ ] Set up logging
- [ ] Configure error tracking (Sentry)
- [ ] Monitor resource usage
- [ ] Set up health checks

---

## 💡 Recommendations by Use Case

**For Demo/Portfolio:** Streamlit Cloud
**For Production App:** Railway or Google Cloud
**For Enterprise:** AWS/Azure with Kubernetes
**For Cost-Effective:** DigitalOcean or Heroku

---

## 🔄 CI/CD Setup

### GitHub Actions Example:
```yaml
name: Deploy to Railway
on:
  push:
    branches: [main]
jobs:
  deploy:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v2
      - name: Deploy to Railway
        uses: railway/cli@v2
        with:
          command: up
        env:
          RAILWAY_TOKEN: ${{ secrets.RAILWAY_TOKEN }}
```

---

## 📊 Database Considerations

For production deployment, consider:
- **PostgreSQL on Railway/Heroku**
- **Google Cloud SQL**
- **AWS RDS**
- **Supabase** (PostgreSQL with real-time features)

Update your database configuration in `config/settings.py` for production use.
