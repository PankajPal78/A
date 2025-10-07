#!/bin/bash

# Setup script for RAG Document Q&A System
echo "🚀 Setting up RAG Document Q&A System..."

# Check if Docker is installed
if ! command -v docker &> /dev/null; then
    echo "❌ Docker is not installed. Please install Docker first."
    echo "Visit: https://docs.docker.com/get-docker/"
    exit 1
fi

# Check if Docker Compose is installed
if ! command -v docker-compose &> /dev/null; then
    echo "❌ Docker Compose is not installed. Please install Docker Compose first."
    echo "Visit: https://docs.docker.com/compose/install/"
    exit 1
fi

echo "✓ Docker and Docker Compose are installed"

# Create .env file if it doesn't exist
if [ ! -f .env ]; then
    echo "📝 Creating .env file from template..."
    cp .env.example .env
    echo "⚠️  Please edit .env and add your API keys before running the application"
    echo "   Required: GEMINI_API_KEY or OPENAI_API_KEY"
else
    echo "✓ .env file already exists"
fi

# Create data directories
echo "📁 Creating data directories..."
mkdir -p data/uploads data/vector_db data/metadata

# Create .gitkeep files
touch data/uploads/.gitkeep data/vector_db/.gitkeep data/metadata/.gitkeep

echo "✓ Data directories created"

# Check if API key is configured
if grep -q "your_gemini_api_key_here" .env || grep -q "your_openai_api_key_here" .env; then
    echo ""
    echo "⚠️  WARNING: API keys not configured!"
    echo "   Please edit .env file and add your LLM API key:"
    echo "   - For Gemini: GEMINI_API_KEY=your_actual_key"
    echo "   - For OpenAI: OPENAI_API_KEY=your_actual_key"
    echo ""
    echo "To get a Gemini API key: https://makersuite.google.com/app/apikey"
    echo "To get an OpenAI API key: https://platform.openai.com/api-keys"
    echo ""
    read -p "Do you want to enter your API key now? (y/n) " -n 1 -r
    echo
    if [[ $REPLY =~ ^[Yy]$ ]]; then
        read -p "Enter your Gemini API key: " api_key
        if [ -n "$api_key" ]; then
            sed -i.bak "s/GEMINI_API_KEY=.*/GEMINI_API_KEY=$api_key/" .env
            rm .env.bak 2>/dev/null
            echo "✓ API key saved"
        fi
    fi
fi

echo ""
echo "✅ Setup complete!"
echo ""
echo "Next steps:"
echo "1. Make sure your API key is configured in .env"
echo "2. Run: docker-compose up --build"
echo "3. Access the API at: http://localhost:5000"
echo ""
echo "For more information, see README.md"