# RAG Document Q&A System

A comprehensive Retrieval-Augmented Generation (RAG) pipeline that allows users to upload documents and ask questions based on their content. The system leverages vector databases for efficient retrieval and Google Gemini for generating responses.

## 🚀 Features

- **Document Processing**: Support for PDF, DOCX, TXT, and XLSX files (up to 20 documents, 1000 pages each)
- **Intelligent Chunking**: Automatic text chunking with overlap for optimal retrieval
- **Vector Search**: ChromaDB-based vector storage for efficient similarity search
- **LLM Integration**: Google Gemini API for contextual response generation
- **REST API**: Complete Flask-based API with all necessary endpoints
- **Docker Support**: Full containerization for easy deployment
- **Comprehensive Testing**: Unit and integration tests included

## 📋 Requirements

- Python 3.11+
- Docker & Docker Compose
- Google Gemini API Key

## 🛠️ Installation & Setup

### 1. Clone the Repository

```bash
git clone <repository-url>
cd rag-document-qa-system
```

### 2. Environment Configuration

Copy the example environment file and configure your settings:

```bash
cp .env.example .env
```

Edit `.env` and add your Google Gemini API key:

```env
GEMINI_API_KEY=your_gemini_api_key_here
```

### 3. Docker Deployment (Recommended)

```bash
# Build and start the application
docker-compose up --build

# Run in background
docker-compose up -d --build
```

The application will be available at `http://localhost:5000`

### 4. Local Development Setup

```bash
# Create virtual environment
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate

# Install dependencies
pip install -r requirements.txt

# Create necessary directories
mkdir -p data uploads

# Run the application
python app.py
```

## 📚 API Documentation

### Base URL
```
http://localhost:5000
```

### Endpoints

#### Health Check
```http
GET /health
```
Returns system health status.

#### Upload Document
```http
POST /api/documents
Content-Type: multipart/form-data

file: [document file]
```

**Supported file types**: PDF, DOCX, TXT, XLSX

**Response**:
```json
{
  "message": "Document uploaded successfully",
  "document_id": "uuid",
  "status": "processing"
}
```

#### List Documents
```http
GET /api/documents
```

**Response**:
```json
[
  {
    "id": "uuid",
    "filename": "document.pdf",
    "original_filename": "document.pdf",
    "file_type": ".pdf",
    "file_size": 1024000,
    "upload_date": "2024-01-01T00:00:00",
    "status": "completed",
    "chunk_count": 15,
    "error_message": null
  }
]
```

#### Get Document Details
```http
GET /api/documents/{document_id}
```

#### Delete Document
```http
DELETE /api/documents/{document_id}
```

#### Query Documents
```http
POST /api/query
Content-Type: application/json

{
  "query": "What is machine learning?",
  "top_k": 5
}
```

**Response**:
```json
{
  "query": "What is machine learning?",
  "response": "Machine learning is a subset of artificial intelligence...",
  "sources": [
    {
      "document_id": "uuid",
      "chunk_id": "chunk_1",
      "chunk_index": 0,
      "similarity_score": 0.95
    }
  ],
  "metadata": {
    "model": "gemini-pro",
    "context_chunks_used": 3,
    "retrieved_chunks": 3
  }
}
```

#### System Statistics
```http
GET /api/stats
```

**Response**:
```json
{
  "total_documents": 5,
  "completed_documents": 4,
  "failed_documents": 1,
  "total_chunks": 150
}
```

## 🧪 Testing

Run the test suite:

```bash
# Run all tests
pytest

# Run with coverage
pytest --cov=services --cov=app

# Run specific test file
pytest tests/test_document_processor.py

# Run with verbose output
pytest -v
```

## 🐳 Docker Configuration

### Docker Compose Services

- **rag-app**: Main Flask application
- **postgres** (optional): PostgreSQL database for production

### Environment Variables

| Variable | Description | Default |
|----------|-------------|---------|
| `GEMINI_API_KEY` | Google Gemini API key | Required |
| `DATABASE_URL` | Database connection string | `sqlite:///data/rag_system.db` |
| `CHROMA_PERSIST_DIRECTORY` | ChromaDB storage path | `data/chroma_db` |
| `FLASK_ENV` | Flask environment | `production` |

## 🏗️ Architecture

### Components

1. **Document Processor**: Handles file upload, text extraction, and chunking
2. **Vector Store**: Manages embeddings storage and similarity search using ChromaDB
3. **LLM Service**: Interfaces with Google Gemini for response generation
4. **RAG Pipeline**: Orchestrates retrieval and generation process
5. **Flask API**: RESTful API for client interactions
6. **Database**: SQLite/PostgreSQL for document metadata

### Data Flow

```
Document Upload → Text Extraction → Chunking → Embedding → Vector Storage
                                                                    ↓
User Query → Vector Search → Context Retrieval → LLM Generation → Response
```

## 🔧 Configuration

### Document Processing
- **Chunk Size**: 1000 characters (configurable)
- **Chunk Overlap**: 200 characters (configurable)
- **Max File Size**: 100MB
- **Max Documents**: 20

### Vector Search
- **Embedding Model**: `all-MiniLM-L6-v2`
- **Similarity Metric**: Cosine similarity
- **Default Top-K**: 5 chunks

### LLM Settings
- **Model**: Google Gemini Pro
- **Temperature**: Default (configurable)
- **Max Tokens**: Model default

## 🚀 Deployment

### Local Deployment
```bash
docker-compose up -d
```

### Cloud Deployment

#### AWS
1. Create EC2 instance
2. Install Docker and Docker Compose
3. Clone repository and configure environment
4. Run `docker-compose up -d`

#### Google Cloud Platform
1. Create Compute Engine instance
2. Install Docker and Docker Compose
3. Configure firewall rules for port 5000
4. Deploy using Docker Compose

#### Azure
1. Create Azure Container Instance
2. Configure environment variables
3. Deploy using Azure CLI or portal

## 📊 Monitoring

### Health Check
```bash
curl http://localhost:5000/health
```

### Logs
```bash
# Docker logs
docker-compose logs -f rag-app

# Application logs
tail -f logs/app.log
```

## 🔒 Security Considerations

- API key management through environment variables
- File upload validation and sanitization
- Input validation for all endpoints
- Rate limiting (recommended for production)
- HTTPS enforcement (recommended for production)

## 🤝 Contributing

1. Fork the repository
2. Create a feature branch
3. Make your changes
4. Add tests for new functionality
5. Run the test suite
6. Submit a pull request

## 📄 License

This project is licensed under the MIT License - see the LICENSE file for details.

## 🆘 Troubleshooting

### Common Issues

1. **ChromaDB initialization error**
   - Ensure `data/chroma_db` directory exists and is writable

2. **Gemini API errors**
   - Verify API key is correct and has sufficient quota
   - Check internet connectivity

3. **File upload failures**
   - Verify file size is under 100MB
   - Check file format is supported

4. **Memory issues**
   - Reduce chunk size in DocumentProcessor
   - Limit number of concurrent uploads

### Support

For issues and questions:
- Check the logs for error messages
- Verify environment configuration
- Run the test suite to identify problems

## 📈 Performance Optimization

- Use PostgreSQL for production instead of SQLite
- Implement Redis for caching
- Add load balancing for multiple instances
- Optimize chunk size based on your documents
- Use GPU acceleration for embeddings (if available)