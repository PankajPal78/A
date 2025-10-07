#!/bin/bash

# RAG Document Q&A System Startup Script

echo "🚀 Starting RAG Document Q&A System..."

# Check if .env file exists
if [ ! -f .env ]; then
    echo "⚠️  .env file not found. Creating from template..."
    cp .env.example .env
    echo "📝 Please edit .env file and add your GEMINI_API_KEY"
    echo "   You can get an API key from: https://makersuite.google.com/app/apikey"
    exit 1
fi

# Create necessary directories
echo "📁 Creating necessary directories..."
mkdir -p data uploads logs

# Check if running in Docker
if [ -f /.dockerenv ]; then
    echo "🐳 Running in Docker container..."
    echo "Starting Flask application..."
    exec gunicorn --bind 0.0.0.0:5000 --workers 4 app:app
else
    echo "💻 Running locally..."
    
    # Check if virtual environment exists
    if [ ! -d "venv" ]; then
        echo "📦 Creating virtual environment..."
        python3 -m venv venv
    fi
    
    # Activate virtual environment
    echo "🔧 Activating virtual environment..."
    source venv/bin/activate
    
    # Install dependencies
    echo "📥 Installing dependencies..."
    pip install -r requirements.txt
    
    # Run the application
    echo "🚀 Starting Flask application..."
    python app.py
fi