# RAG (Retrieval-Augmented Generation) Document Q&A System

A comprehensive RAG pipeline that allows users to upload documents and ask questions based on their content. The system leverages vector databases for efficient retrieval and Gemini API for generating contextual responses.

## Features

- **Document Upload & Processing**: Support for PDF, DOCX, XLSX, and TXT files (up to 20 documents, 1000 pages each)
- **Intelligent Chunking**: Automatic text chunking with overlap for optimal retrieval
- **Vector Search**: ChromaDB integration for efficient similarity search
- **RAG Pipeline**: Integration with Gemini API for contextual response generation
- **REST API**: Flask-based API with comprehensive endpoints
- **Docker Support**: Complete containerization with Docker Compose
- **Scalable Architecture**: Designed for both local and cloud deployment

## Architecture

```
┌─────────────────┐    ┌──────────────────┐    ┌─────────────────┐
│   Document      │    │   Flask API      │    │   ChromaDB      │
│   Upload        │───▶│   (REST)         │───▶│   (Vector DB)   │
└─────────────────┘    └──────────────────┘    └─────────────────┘
                                │
                                ▼
                       ┌──────────────────┐    ┌─────────────────┐
                       │   Document       │    │   Gemini API    │
                       │   Processor      │───▶│   (LLM)         │
                       └──────────────────┘    └─────────────────┘
```

## Quick Start

### Prerequisites

- Docker and Docker Compose
- Python 3.9+ (for local development)
- Gemini API key

### 1. Clone and Setup

```bash
git clone <repository-url>
cd rag-document-qa-system
```

### 2. Environment Configuration

```bash
cp .env.example .env
```

Edit `.env` and add your Gemini API key:
```
GEMINI_API_KEY=your_gemini_api_key_here
```

### 3. Docker Deployment (Recommended)

```bash
# Build and start all services
docker-compose up --build

# Run in background
docker-compose up -d --build
```

The API will be available at `http://localhost:5000`

### 4. Local Development

```bash
# Install dependencies
pip install -r requirements.txt

# Set environment variables
export GEMINI_API_KEY=your_api_key_here

# Run the application
python app.py
```

## API Endpoints

### Document Management

#### Upload Document
```http
POST /api/documents/upload
Content-Type: multipart/form-data

file: [document file]
```

#### List Documents
```http
GET /api/documents/
Query Parameters:
- page: Page number (default: 1)
- per_page: Items per page (default: 10)
```

#### Get Document Details
```http
GET /api/documents/{document_id}
```

#### Delete Document
```http
DELETE /api/documents/{document_id}
```

#### Get Document Chunks
```http
GET /api/documents/{document_id}/chunks
Query Parameters:
- page: Page number (default: 1)
- per_page: Items per page (default: 20)
```

### Query & Search

#### Ask Question (RAG)
```http
POST /api/query/ask
Content-Type: application/json

{
  "question": "What is the main topic of the document?",
  "document_ids": [1, 2],  // Optional: filter by specific documents
  "max_results": 5,        // Optional: max chunks to retrieve
  "max_tokens": 1000       // Optional: max response length
}
```

#### Search Documents
```http
POST /api/query/search
Content-Type: application/json

{
  "query": "machine learning",
  "document_ids": [1, 2],  // Optional
  "max_results": 10        // Optional
}
```

#### Test LLM Connection
```http
GET /api/query/test-llm
```

### Health Check

```http
GET /
GET /api/health
```

## Usage Examples

### 1. Upload a Document

```bash
curl -X POST http://localhost:5000/api/documents/upload \
  -F "file=@sample_document.pdf"
```

### 2. Ask a Question

```bash
curl -X POST http://localhost:5000/api/query/ask \
  -H "Content-Type: application/json" \
  -d '{
    "question": "What are the key findings in this document?",
    "max_results": 5
  }'
```

### 3. Search for Information

```bash
curl -X POST http://localhost:5000/api/query/search \
  -H "Content-Type: application/json" \
  -d '{
    "query": "financial analysis",
    "max_results": 10
  }'
```

## Configuration

### Environment Variables

| Variable | Description | Default |
|----------|-------------|---------|
| `GEMINI_API_KEY` | Gemini API key (required) | - |
| `DATABASE_URL` | Database connection string | `sqlite:///data/rag_database.db` |
| `CHROMA_DB_PATH` | ChromaDB storage path | `./data/chroma_db` |
| `UPLOAD_FOLDER` | File upload directory | `./uploads` |
| `MAX_CONTENT_LENGTH` | Max file size in bytes | `104857600` (100MB) |
| `SECRET_KEY` | Flask secret key | `dev-secret-key` |

### LLM Configuration

The system supports different LLM providers. Currently configured for Gemini:

```python
# In llm_service.py
self.model = genai.GenerativeModel('gemini-pro')
```

To use a different model, modify the `LLMService` class.

## Testing

### Run Tests

```bash
# Install test dependencies
pip install pytest pytest-flask

# Run all tests
pytest

# Run with coverage
pytest --cov=.

# Run specific test file
pytest tests/test_app.py
```

### Test Coverage

The test suite includes:
- Unit tests for document processing
- Integration tests for API endpoints
- Vector search functionality tests
- LLM service tests

## Deployment

### Cloud Deployment

#### AWS ECS/Fargate

1. Build and push Docker image to ECR
2. Create ECS task definition
3. Configure load balancer
4. Set environment variables

#### Google Cloud Run

```bash
# Build and push to GCR
gcloud builds submit --tag gcr.io/PROJECT_ID/rag-system

# Deploy to Cloud Run
gcloud run deploy rag-system --image gcr.io/PROJECT_ID/rag-system
```

#### Azure Container Instances

```bash
# Build and push to ACR
az acr build --registry myregistry --image rag-system .

# Deploy to Container Instances
az container create --resource-group myRG --name rag-system --image myregistry.azurecr.io/rag-system
```

### Production Considerations

1. **Database**: Use PostgreSQL or MySQL for production
2. **Vector DB**: Consider managed ChromaDB or Pinecone
3. **Caching**: Implement Redis for response caching
4. **Monitoring**: Add logging and metrics collection
5. **Security**: Implement authentication and rate limiting
6. **Scaling**: Use horizontal pod autoscaling

## Performance Optimization

### Document Processing
- Implement async processing with Celery
- Use GPU acceleration for embeddings
- Optimize chunking strategy based on content type

### Vector Search
- Tune similarity thresholds
- Implement query caching
- Use approximate nearest neighbor search

### API Performance
- Implement response caching
- Use connection pooling
- Add request rate limiting

## Troubleshooting

### Common Issues

1. **ChromaDB Connection Error**
   - Ensure data directory is writable
   - Check disk space availability

2. **Gemini API Error**
   - Verify API key is correct
   - Check API quota and limits

3. **File Upload Issues**
   - Verify file size limits
   - Check supported file formats

4. **Memory Issues**
   - Reduce chunk size
   - Process documents in batches

### Logs

```bash
# View application logs
docker-compose logs rag-app

# View all logs
docker-compose logs

# Follow logs
docker-compose logs -f rag-app
```

## Contributing

1. Fork the repository
2. Create a feature branch
3. Make your changes
4. Add tests
5. Submit a pull request

## License

This project is licensed under the MIT License - see the LICENSE file for details.

## Support

For issues and questions:
- Create an issue in the repository
- Check the troubleshooting section
- Review the API documentation

## Roadmap

- [ ] Support for more document formats (PPTX, HTML, etc.)
- [ ] Multi-language support
- [ ] Advanced chunking strategies
- [ ] Query expansion and refinement
- [ ] User authentication and authorization
- [ ] Advanced analytics and insights
- [ ] Web UI for document management
- [ ] Batch processing capabilities