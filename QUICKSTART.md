# Quick Start Guide

## 🚀 Get Started in 5 Minutes

### 1. Prerequisites
- Docker and Docker Compose installed
- Google Gemini API key

### 2. Setup
```bash
# Clone and navigate to the project
git clone <repository-url>
cd rag-document-qa

# Set up environment
cp .env.example .env
# Edit .env and add your Google API key

# Start the system
docker-compose up --build
```

### 3. Test the System
```bash
# Check if API is running
curl http://localhost:5000/health

# Upload a document
curl -X POST -F "file=@your_document.pdf" http://localhost:5000/api/documents/upload

# Query the documents
curl -X POST -H "Content-Type: application/json" \
  -d '{"question": "What is the main topic?"}' \
  http://localhost:5000/api/query
```

### 4. Use the Example Script
```bash
# Run the example usage script
python example_usage.py
```

### 5. Test with Postman
Import `RAG_API.postman_collection.json` into Postman and test all endpoints.

## 🔧 Configuration

### Required Environment Variables
```env
GOOGLE_API_KEY=your_google_api_key_here
```

### Optional Configuration
```env
CHUNK_SIZE=1000          # Text chunk size
CHUNK_OVERLAP=200        # Overlap between chunks
MAX_CONTENT_LENGTH=104857600  # Max file size (100MB)
```

## 📊 Monitoring

- **Health Check**: `GET /health`
- **System Stats**: `GET /api/stats`
- **Document List**: `GET /api/documents`

## 🧪 Testing

```bash
# Run all tests
./run_tests.sh

# Or run specific tests
pytest test_app.py -v
pytest test_integration.py -v
```

## 🆘 Troubleshooting

### Common Issues

1. **API Key Error**
   - Ensure `GOOGLE_API_KEY` is set in `.env`
   - Verify the API key is valid

2. **Memory Issues**
   - Increase Docker memory limit to 4GB+
   - Check system resources

3. **File Upload Fails**
   - Check file size (max 100MB)
   - Verify file format (PDF, DOCX, TXT)

4. **Slow Responses**
   - Check network connection
   - Verify API key limits

### Logs
```bash
# View logs
docker-compose logs -f rag-app

# Check specific service
docker-compose logs rag-app
```

## 📚 Next Steps

1. **Upload Documents**: Use the API to upload your documents
2. **Query System**: Ask questions about your documents
3. **Monitor Performance**: Check system stats and logs
4. **Scale Up**: Deploy to cloud for production use

## 🔗 Useful Links

- [Full Documentation](README.md)
- [API Reference](README.md#api-usage)
- [Postman Collection](RAG_API.postman_collection.json)
- [Example Usage](example_usage.py)