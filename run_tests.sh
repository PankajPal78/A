#!/bin/bash

# Run tests script
echo "Running RAG System Tests..."

# Activate virtual environment if it exists
if [ -d "venv" ]; then
    source venv/bin/activate
fi

# Run pytest with coverage
pytest app/tests/ -v --cov=app --cov-report=html --cov-report=term-missing

# Check exit code
if [ $? -eq 0 ]; then
    echo "✓ All tests passed!"
    echo "Coverage report generated in htmlcov/index.html"
else
    echo "✗ Some tests failed"
    exit 1
fi