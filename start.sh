#!/bin/bash

# RAG System Startup Script

echo "Starting RAG Document Q&A System..."
echo "=================================="

# Check if .env file exists
if [ ! -f .env ]; then
    echo "Creating .env file from template..."
    cp .env.example .env
    echo "Please edit .env file and add your Gemini API key"
    echo "Then run this script again"
    exit 1
fi

# Check if Docker is running
if ! docker info > /dev/null 2>&1; then
    echo "Docker is not running. Please start Docker and try again."
    exit 1
fi

# Check if docker-compose is available
if ! command -v docker-compose &> /dev/null; then
    echo "docker-compose is not installed. Please install it and try again."
    exit 1
fi

# Create necessary directories
echo "Creating necessary directories..."
mkdir -p data uploads

# Build and start services
echo "Building and starting services..."
docker-compose up --build -d

# Wait for services to be ready
echo "Waiting for services to start..."
sleep 10

# Check if services are running
if docker-compose ps | grep -q "Up"; then
    echo "✓ Services started successfully!"
    echo ""
    echo "API is available at: http://localhost:5000"
    echo "Health check: http://localhost:5000/"
    echo ""
    echo "To view logs: docker-compose logs -f"
    echo "To stop services: docker-compose down"
    echo ""
    echo "Upload a document and start asking questions!"
else
    echo "✗ Services failed to start. Check logs with: docker-compose logs"
    exit 1
fi