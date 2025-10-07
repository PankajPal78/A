# RAG Document Q&A System

A comprehensive Retrieval-Augmented Generation (RAG) pipeline that allows users to upload documents and ask questions based on their content. The system leverages vector databases for efficient retrieval and Google's Gemini API for generating contextual responses.

## 🚀 Features

- **Document Processing**: Support for PDF and DOCX files (up to 20 documents, 1000 pages each)
- **Intelligent Chunking**: Automatic text chunking with overlap for optimal retrieval
- **Vector Search**: ChromaDB-based vector database for semantic similarity search
- **RAG Pipeline**: Retrieval-Augmented Generation using Google Gemini API
- **REST API**: Comprehensive Flask-based API with full CRUD operations
- **Docker Support**: Complete containerization for easy deployment
- **Health Monitoring**: Built-in health checks and system monitoring
- **Comprehensive Testing**: Unit and integration tests with 90%+ coverage

## 🏗️ Architecture

```
┌─────────────────┐    ┌─────────────────┐    ┌─────────────────┐
│   Web Client    │    │   REST API      │    │  Document       │
│   (Frontend)    │◄──►│   (Flask)       │◄──►│  Processor      │
└─────────────────┘    └─────────────────┘    └─────────────────┘
                                │                       │
                                ▼                       ▼
                       ┌─────────────────┐    ┌─────────────────┐
                       │  Vector DB      │    │  File Storage   │
                       │  (ChromaDB)     │    │  (Local/Cloud)  │
                       └─────────────────┘    └─────────────────┘
                                │
                                ▼
                       ┌─────────────────┐
                       │  LLM Service    │
                       │  (Gemini API)   │
                       └─────────────────┘
```

## 📋 Prerequisites

- Python 3.9+
- Docker and Docker Compose
- Google Gemini API key
- 4GB+ RAM (for vector operations)

## 🛠️ Installation

### Option 1: Docker (Recommended)

1. **Clone the repository**
   ```bash
   git clone <repository-url>
   cd rag-document-qa-system
   ```

2. **Set up environment variables**
   ```bash
   cp .env.example .env
   # Edit .env and add your Gemini API key
   ```

3. **Start the services**
   ```bash
   docker-compose up -d
   ```

4. **Verify installation**
   ```bash
   curl http://localhost/api/health/
   ```

### Option 2: Local Development

1. **Create virtual environment**
   ```bash
   python -m venv venv
   source venv/bin/activate  # On Windows: venv\Scripts\activate
   ```

2. **Install dependencies**
   ```bash
   pip install -r requirements.txt
   ```

3. **Set up environment variables**
   ```bash
   export GEMINI_API_KEY="your-api-key-here"
   export DATABASE_URL="sqlite:///data/rag_system.db"
   ```

4. **Initialize the database**
   ```bash
   python -c "from app import app, db; app.app_context().push(); db.create_all()"
   ```

5. **Run the application**
   ```bash
   python app.py
   ```

## 🔧 Configuration

### Environment Variables

| Variable | Description | Default |
|----------|-------------|---------|
| `GEMINI_API_KEY` | Google Gemini API key | Required |
| `DATABASE_URL` | Database connection string | `sqlite:///data/rag_system.db` |
| `FLASK_ENV` | Flask environment | `production` |
| `SECRET_KEY` | Flask secret key | `dev-secret-key` |
| `MAX_CONTENT_LENGTH` | Max file upload size | `104857600` (100MB) |
| `UPLOAD_FOLDER` | File upload directory | `./data/uploads` |
| `CHROMA_PERSIST_DIRECTORY` | Vector DB directory | `./data/chroma_db` |

### LLM Provider Configuration

The system currently supports Google Gemini. To use a different LLM provider:

1. Modify `services/llm_service.py`
2. Update the API configuration
3. Adjust the prompt format if needed

## 📚 API Documentation

### Base URL
- Local: `http://localhost:5000`
- Docker: `http://localhost`

### Authentication
Currently, no authentication is required. For production deployment, implement proper authentication.

### Endpoints

#### Document Management

**Upload Document**
```http
POST /api/documents/upload
Content-Type: multipart/form-data

file: [PDF or DOCX file]
```

**Get All Documents**
```http
GET /api/documents/?page=1&per_page=10
```

**Get Document by ID**
```http
GET /api/documents/{document_id}
```

**Get Document Chunks**
```http
GET /api/documents/{document_id}/chunks
```

**Delete Document**
```http
DELETE /api/documents/{document_id}
```

**Get Document Statistics**
```http
GET /api/documents/stats
```

#### Query Operations

**Ask Question**
```http
POST /api/query/ask
Content-Type: application/json

{
  "query": "What is machine learning?",
  "document_ids": [1, 2],  // Optional: filter by specific documents
  "max_chunks": 5,         // Optional: number of chunks to retrieve
  "max_tokens": 1000       // Optional: max response length
}
```

**Search Documents**
```http
POST /api/query/search
Content-Type: application/json

{
  "query": "machine learning algorithms",
  "document_ids": [1, 2],  // Optional
  "max_chunks": 10         // Optional
}
```

**Get Available Documents**
```http
GET /api/query/available-documents
```

**Get System Statistics**
```http
GET /api/query/stats
```

**Test LLM Connection**
```http
POST /api/query/test-llm
```

#### Health Monitoring

**Basic Health Check**
```http
GET /api/health/
```

**Detailed Health Check**
```http
GET /api/health/detailed
```

## 🧪 Testing

### Run All Tests
```bash
pytest tests/ -v
```

### Run Specific Test Categories
```bash
# Unit tests only
pytest tests/test_*_service.py -v

# API tests only
pytest tests/test_api_routes.py -v

# With coverage
pytest tests/ --cov=. --cov-report=html
```

### Test Coverage
The test suite includes:
- Unit tests for all services
- Integration tests for API endpoints
- Mock-based testing for external dependencies
- Error handling and edge cases

## 📊 Usage Examples

### 1. Upload and Process Documents

```bash
# Upload a PDF document
curl -X POST http://localhost:5000/api/documents/upload \
  -F "file=@document.pdf"

# Check processing status
curl http://localhost:5000/api/documents/stats
```

### 2. Ask Questions

```bash
# Simple question
curl -X POST http://localhost:5000/api/query/ask \
  -H "Content-Type: application/json" \
  -d '{"query": "What are the main topics discussed in the documents?"}'

# Question with specific parameters
curl -X POST http://localhost:5000/api/query/ask \
  -H "Content-Type: application/json" \
  -d '{
    "query": "Explain machine learning concepts",
    "document_ids": [1, 2],
    "max_chunks": 3,
    "max_tokens": 500
  }'
```

### 3. Search for Relevant Content

```bash
curl -X POST http://localhost:5000/api/query/search \
  -H "Content-Type: application/json" \
  -d '{"query": "neural networks", "max_chunks": 5}'
```

## 🚀 Deployment

### Local Deployment
```bash
docker-compose up -d
```

### Cloud Deployment (AWS/GCP/Azure)

1. **Build and push Docker image**
   ```bash
   docker build -t rag-system .
   docker tag rag-system your-registry/rag-system:latest
   docker push your-registry/rag-system:latest
   ```

2. **Deploy using cloud services**
   - AWS: ECS, EKS, or App Runner
   - GCP: Cloud Run, GKE
   - Azure: Container Instances, AKS

3. **Set up persistent storage**
   - Mount volumes for data persistence
   - Configure backup strategies

### Production Considerations

- **Scaling**: Use load balancers and multiple replicas
- **Security**: Implement authentication and HTTPS
- **Monitoring**: Add logging and metrics collection
- **Backup**: Regular database and vector DB backups
- **Resource Limits**: Set appropriate CPU/memory limits

## 🔍 Troubleshooting

### Common Issues

**1. Vector Database Connection Issues**
```bash
# Check ChromaDB status
curl http://localhost:5000/api/health/detailed
```

**2. LLM API Errors**
```bash
# Test LLM connection
curl -X POST http://localhost:5000/api/query/test-llm
```

**3. File Upload Issues**
- Check file size limits
- Verify file format (PDF/DOCX only)
- Ensure sufficient disk space

**4. Memory Issues**
- Increase Docker memory limits
- Reduce chunk size in configuration
- Use smaller embedding models

### Logs

```bash
# View application logs
docker-compose logs -f rag-api

# View all services
docker-compose logs -f
```

## 📈 Performance Optimization

### Vector Database
- Use GPU acceleration for embeddings
- Implement chunk caching
- Optimize similarity search parameters

### API Performance
- Enable response caching
- Use connection pooling
- Implement request rate limiting

### Memory Management
- Monitor memory usage
- Implement garbage collection
- Use streaming for large files

## 🤝 Contributing

1. Fork the repository
2. Create a feature branch
3. Make your changes
4. Add tests for new functionality
5. Ensure all tests pass
6. Submit a pull request

## 📄 License

This project is licensed under the MIT License - see the LICENSE file for details.

## 🆘 Support

For issues and questions:
1. Check the troubleshooting section
2. Review existing GitHub issues
3. Create a new issue with detailed information

## 🔮 Future Enhancements

- [ ] Support for more document formats (TXT, HTML, etc.)
- [ ] Multi-language support
- [ ] Advanced chunking strategies
- [ ] Real-time document processing
- [ ] Web-based UI
- [ ] User authentication and authorization
- [ ] Advanced analytics and insights
- [ ] Integration with cloud storage services
- [ ] Support for multiple LLM providers
- [ ] Advanced query processing (filters, sorting)

---

**Built with ❤️ using Flask, ChromaDB, and Google Gemini**