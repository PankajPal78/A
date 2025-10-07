#!/bin/bash

# RAG System Test Runner
# This script runs all tests and provides a summary

echo "RAG System Test Runner"
echo "======================"

# Check if virtual environment exists
if [ ! -d "venv" ]; then
    echo "Creating virtual environment..."
    python3 -m venv venv
fi

# Activate virtual environment
echo "Activating virtual environment..."
source venv/bin/activate

# Install dependencies
echo "Installing dependencies..."
pip install -r requirements.txt

# Run setup test
echo "Running setup test..."
python test_setup.py

# Run unit tests
echo "Running unit tests..."
pytest test_app.py -v

# Run integration tests
echo "Running integration tests..."
pytest test_integration.py -v

# Run all tests with coverage
echo "Running tests with coverage..."
pytest --cov=. --cov-report=html --cov-report=term-missing

echo "Test run completed!"
echo "Coverage report available in htmlcov/index.html"