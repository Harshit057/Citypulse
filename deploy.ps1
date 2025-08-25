# CityPulse Deployment Script for Windows PowerShell
# Usage: .\deploy.ps1 [platform]
# Platforms: streamlit, heroku, railway, docker

param(
    [string]$Platform = "streamlit"
)

Write-Host "🚀 Deploying CityPulse to $Platform..." -ForegroundColor Green

switch ($Platform) {
    "streamlit" {
        Write-Host "📋 Streamlit Cloud Deployment Steps:" -ForegroundColor Yellow
        Write-Host "1. Push your code to GitHub"
        Write-Host "2. Visit https://share.streamlit.io"
        Write-Host "3. Connect your repository"
        Write-Host "4. Select app/streamlit_app.py as main file"
        Write-Host "5. Deploy!"
    }
    
    "heroku" {
        Write-Host "🔧 Deploying to Heroku..." -ForegroundColor Blue
        
        # Check if Heroku CLI is installed
        if (!(Get-Command heroku -ErrorAction SilentlyContinue)) {
            Write-Host "❌ Heroku CLI not found. Install from https://devcenter.heroku.com/articles/heroku-cli" -ForegroundColor Red
            exit 1
        }
        
        # Create Heroku app if it doesn't exist
        Write-Host "Creating Heroku app..."
        $timestamp = [int](Get-Date -UFormat %s)
        try {
            heroku create "citypulse-$timestamp"
        } catch {
            Write-Host "App might already exist"
        }
        
        # Deploy
        git add .
        try {
            git commit -m "Deploy to Heroku"
        } catch {
            Write-Host "No changes to commit"
        }
        git push heroku main
        
        Write-Host "✅ Deployed to Heroku!" -ForegroundColor Green
        heroku open
    }
    
    "railway" {
        Write-Host "🚂 Deploying to Railway..." -ForegroundColor Blue
        
        if (!(Get-Command railway -ErrorAction SilentlyContinue)) {
            Write-Host "❌ Railway CLI not found. Install with: npm install -g @railway/cli" -ForegroundColor Red
            exit 1
        }
        
        railway login
        railway init
        railway up
        
        Write-Host "✅ Deployed to Railway!" -ForegroundColor Green
    }
    
    "docker" {
        Write-Host "🐳 Building and running Docker container..." -ForegroundColor Blue
        
        # Build image
        docker build -t citypulse .
        
        # Stop existing container if running
        try {
            docker stop citypulse-app
            docker rm citypulse-app
        } catch {
            # Container doesn't exist, continue
        }
        
        # Run container
        docker run -d -p 8501:8501 --name citypulse-app citypulse
        
        Write-Host "✅ Docker container running at http://localhost:8501" -ForegroundColor Green
    }
    
    default {
        Write-Host "❌ Unknown platform: $Platform" -ForegroundColor Red
        Write-Host "Available platforms: streamlit, heroku, railway, docker"
        exit 1
    }
}

Write-Host "🎉 Deployment complete!" -ForegroundColor Green
