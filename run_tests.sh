#!/bin/bash

# RAG Document Q&A System - Test Runner Script

set -e

echo "🧪 Running RAG Document Q&A System Tests"
echo "========================================"

# Check if virtual environment exists
if [ ! -d "venv" ]; then
    echo "📦 Creating virtual environment..."
    python -m venv venv
fi

# Activate virtual environment
echo "🔧 Activating virtual environment..."
source venv/bin/activate

# Install dependencies
echo "📥 Installing dependencies..."
pip install -r requirements.txt
pip install pytest pytest-flask pytest-cov black flake8

# Create necessary directories
echo "📁 Creating test directories..."
mkdir -p uploads chroma_db logs test_chroma_db

# Run code formatting
echo "🎨 Formatting code with Black..."
black . --check || (echo "❌ Code formatting issues found. Run 'black .' to fix." && exit 1)

# Run linting
echo "🔍 Running flake8 linting..."
flake8 . --max-line-length=100 --ignore=E203,W503 || (echo "❌ Linting issues found." && exit 1)

# Run tests with coverage
echo "🧪 Running tests with coverage..."
pytest --cov=. --cov-report=html --cov-report=term-missing -v

# Check test results
if [ $? -eq 0 ]; then
    echo "✅ All tests passed!"
    echo "📊 Coverage report generated in htmlcov/index.html"
else
    echo "❌ Some tests failed!"
    exit 1
fi

# Run specific test categories
echo "🔬 Running unit tests..."
pytest -m unit -v

echo "🔗 Running integration tests..."
pytest -m integration -v

echo "🎉 Test run completed successfully!"
echo "📋 Summary:"
echo "   - Code formatting: ✅"
echo "   - Linting: ✅"
echo "   - Unit tests: ✅"
echo "   - Integration tests: ✅"
echo "   - Coverage report: htmlcov/index.html"