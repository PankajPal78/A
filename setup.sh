#!/bin/bash
# Setup script for RAG Document Q&A System

echo "🚀 Setting up RAG Document Q&A System..."

# Check Python version
python_version=$(python3 --version 2>&1 | awk '{print $2}')
echo "✓ Python version: $python_version"

# Create virtual environment
echo "📦 Creating virtual environment..."
python3 -m venv venv
source venv/bin/activate

# Install dependencies
echo "📥 Installing dependencies..."
pip install --upgrade pip
pip install -r requirements.txt

# Create .env file if not exists
if [ ! -f .env ]; then
    echo "📝 Creating .env file from template..."
    cp .env.example .env
    echo "⚠️  Please edit .env file with your API keys!"
else
    echo "✓ .env file already exists"
fi

# Create necessary directories
echo "📁 Creating data directories..."
mkdir -p data/uploads data/vectordb

# Run tests
echo "🧪 Running tests..."
pytest tests/ -v

echo ""
echo "✅ Setup complete!"
echo ""
echo "Next steps:"
echo "1. Edit .env file with your LLM API keys"
echo "2. Run: source venv/bin/activate"
echo "3. Run: python run.py"
echo "4. Access API at http://localhost:5000"
echo ""