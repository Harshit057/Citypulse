#!/bin/bash

# CityPulse Deployment Script
# Usage: ./deploy.sh [platform]
# Platforms: streamlit, heroku, railway, docker

set -e

PLATFORM=${1:-streamlit}

echo "🚀 Deploying CityPulse to $PLATFORM..."

case $PLATFORM in
  "streamlit")
    echo "📋 Streamlit Cloud Deployment Steps:"
    echo "1. Push your code to GitHub"
    echo "2. Visit https://share.streamlit.io"
    echo "3. Connect your repository"
    echo "4. Select app/streamlit_app.py as main file"
    echo "5. Deploy!"
    ;;
    
  "heroku")
    echo "🔧 Deploying to Heroku..."
    
    # Check if Heroku CLI is installed
    if ! command -v heroku &> /dev/null; then
        echo "❌ Heroku CLI not found. Install from https://devcenter.heroku.com/articles/heroku-cli"
        exit 1
    fi
    
    # Create Heroku app if it doesn't exist
    echo "Creating Heroku app..."
    heroku create citypulse-$(date +%s) 2>/dev/null || echo "App might already exist"
    
    # Deploy
    git add .
    git commit -m "Deploy to Heroku" || echo "No changes to commit"
    git push heroku main
    
    echo "✅ Deployed to Heroku!"
    heroku open
    ;;
    
  "railway")
    echo "🚂 Deploying to Railway..."
    
    if ! command -v railway &> /dev/null; then
        echo "❌ Railway CLI not found. Install with: npm install -g @railway/cli"
        exit 1
    fi
    
    railway login
    railway init
    railway up
    
    echo "✅ Deployed to Railway!"
    ;;
    
  "docker")
    echo "🐳 Building and running Docker container..."
    
    # Build image
    docker build -t citypulse .
    
    # Run container
    docker run -d -p 8501:8501 --name citypulse-app citypulse
    
    echo "✅ Docker container running at http://localhost:8501"
    ;;
    
  *)
    echo "❌ Unknown platform: $PLATFORM"
    echo "Available platforms: streamlit, heroku, railway, docker"
    exit 1
    ;;
esac

echo "🎉 Deployment complete!"
