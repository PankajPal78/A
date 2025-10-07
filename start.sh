#!/bin/bash

# RAG Document Q&A System Startup Script

echo "🚀 Starting RAG Document Q&A System"
echo "=================================="

# Check if .env file exists
if [ ! -f .env ]; then
    echo "⚠️  .env file not found. Creating from template..."
    cp .env.example .env
    echo "📝 Please edit .env file and add your GEMINI_API_KEY"
    echo "   Then run this script again."
    exit 1
fi

# Load environment variables
source .env

# Check if GEMINI_API_KEY is set
if [ -z "$GEMINI_API_KEY" ] || [ "$GEMINI_API_KEY" = "your_gemini_api_key_here" ]; then
    echo "❌ GEMINI_API_KEY not set in .env file"
    echo "   Please edit .env file and add your actual Gemini API key"
    exit 1
fi

# Create necessary directories
echo "📁 Creating necessary directories..."
mkdir -p data/uploads
mkdir -p data/chroma_db
mkdir -p logs

# Check if running in Docker
if [ -f /.dockerenv ]; then
    echo "🐳 Running in Docker container"
    echo "🔧 Starting Flask application..."
    python app.py
else
    echo "💻 Running locally"
    
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
    
    # Create sample PDF if it doesn't exist
    if [ ! -f "sample_document.pdf" ]; then
        echo "📄 Creating sample PDF for testing..."
        python create_sample_pdf.py
    fi
    
    # Start the application
    echo "🚀 Starting Flask application..."
    python app.py
fi