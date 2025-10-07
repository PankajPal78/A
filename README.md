# RAG Document Q&A System

A comprehensive Retrieval-Augmented Generation (RAG) pipeline that allows users to upload documents and ask questions based on their content. The system leverages vector databases for efficient retrieval and LLM APIs (Gemini, OpenAI) for generating accurate responses.

## 🚀 Features

- **Document Processing**: Support for PDF, DOCX, and TXT files (up to 20 documents, 1000 pages each)
- **Smart Chunking**: Intelligent text splitting with configurable chunk size and overlap
- **Vector Storage**: ChromaDB integration for efficient similarity search
- **Multiple LLM Support**: Compatible with Google Gemini and OpenAI APIs
- **REST API**: Complete Flask-based API with comprehensive endpoints
- **Docker Ready**: Full containerization with Docker Compose
- **Comprehensive Testing**: Unit and integration tests with pytest
- **Production Ready**: Gunicorn WSGI server, health checks, and monitoring

## 📋 Table of Contents

- [Quick Start](#quick-start)
- [Installation](#installation)
- [Configuration](#configuration)
- [API Documentation](#api-documentation)
- [Docker Deployment](#docker-deployment)
- [Development](#development)
- [Testing](#testing)
- [Architecture](#architecture)
- [Contributing](#contributing)

## 🚀 Quick Start

### Using Docker (Recommended)

1. **Clone the repository**
   ```bash
   git clone <repository-url>
   cd rag-document-qa
   ```

2. **Set up environment variables**
   ```bash
   cp .env.example .env
   # Edit .env with your API keys
   ```

3. **Run with Docker Compose**
   ```bash
   docker-compose up -d
   ```

4. **Access the API**
   - Health check: http://localhost:5000/api/health/
   - API documentation: See [API Documentation](#api-documentation)

### Manual Installation

1. **Prerequisites**
   - Python 3.11+
   - pip

2. **Install dependencies**
   ```bash
   pip install -r requirements.txt
   ```

3. **Set up environment**
   ```bash
   cp .env.example .env
   # Configure your API keys and settings
   ```

4. **Run the application**
   ```bash
   python app.py
   ```

## ⚙️ Installation

### System Requirements

- **Python**: 3.11 or higher
- **Memory**: Minimum 4GB RAM (8GB recommended)
- **Storage**: 10GB free space for documents and vector database
- **Network**: Internet access for LLM API calls

### Dependencies

The system uses the following key dependencies:

- **Flask**: Web framework and API server
- **ChromaDB**: Vector database for embeddings
- **Sentence Transformers**: Text embedding generation
- **LangChain**: Text processing and chunking
- **PyPDF2**: PDF text extraction
- **python-docx**: DOCX file processing
- **Google Generative AI**: Gemini API integration
- **OpenAI**: GPT API integration

### Installation Steps

1. **Create virtual environment**
   ```bash
   python -m venv venv
   source venv/bin/activate  # On Windows: venv\Scripts\activate
   ```

2. **Install dependencies**
   ```bash
   pip install -r requirements.txt
   ```

3. **Create required directories**
   ```bash
   mkdir -p uploads chroma_db logs
   ```

4. **Set up environment variables**
   ```bash
   cp .env.example .env
   ```

## 🔧 Configuration

### Environment Variables

Create a `.env` file based on `.env.example`:

```bash
# Flask Configuration
FLASK_ENV=development
SECRET_KEY=your-secret-key-here
PORT=5000

# Database Configuration
DATABASE_URL=sqlite:///rag_system.db

# File Upload Configuration
UPLOAD_FOLDER=uploads
MAX_DOCUMENTS=20
MAX_PAGES_PER_DOCUMENT=1000

# Vector Database Configuration
CHROMA_PERSIST_DIRECTORY=./chroma_db
COLLECTION_NAME=documents

# Text Processing Configuration
CHUNK_SIZE=1000
CHUNK_OVERLAP=200

# Embedding Configuration
EMBEDDING_MODEL=all-MiniLM-L6-v2

# LLM Configuration
LLM_PROVIDER=gemini  # gemini or openai
GEMINI_API_KEY=your_gemini_api_key_here
OPENAI_API_KEY=your_openai_api_key_here

# RAG Configuration
TOP_K_RETRIEVAL=5
SIMILARITY_THRESHOLD=0.7
```

### LLM Provider Setup

#### Google Gemini
1. Visit [Google AI Studio](https://makersuite.google.com/app/apikey)
2. Create an API key
3. Set `GEMINI_API_KEY` in your `.env` file

#### OpenAI
1. Visit [OpenAI API Keys](https://platform.openai.com/api-keys)
2. Create an API key
3. Set `OPENAI_API_KEY` in your `.env` file

## 📚 API Documentation

### Base URL
```
http://localhost:5000/api
```

### Health Endpoints

#### GET /health/
Basic health check
```bash
curl http://localhost:5000/api/health/
```

#### GET /health/status
Detailed system status
```bash
curl http://localhost:5000/api/health/status
```

### Document Endpoints

#### POST /documents/upload
Upload a document for processing
```bash
curl -X POST \
  -F "file=@document.pdf" \
  http://localhost:5000/api/documents/upload
```

#### GET /documents/
List all documents with pagination
```bash
curl "http://localhost:5000/api/documents/?page=1&per_page=10"
```

#### GET /documents/{id}
Get document details by ID
```bash
curl http://localhost:5000/api/documents/1
```

#### DELETE /documents/{id}
Delete a document and its chunks
```bash
curl -X DELETE http://localhost:5000/api/documents/1
```

#### GET /documents/{id}/chunks
Get all chunks for a document
```bash
curl http://localhost:5000/api/documents/1/chunks
```

#### GET /documents/stats
Get document collection statistics
```bash
curl http://localhost:5000/api/documents/stats
```

### Query Endpoints

#### POST /query/
Process a query through the RAG pipeline
```bash
curl -X POST \
  -H "Content-Type: application/json" \
  -d '{"query": "What is machine learning?"}' \
  http://localhost:5000/api/query/
```

Optional parameters:
```bash
curl -X POST \
  -H "Content-Type: application/json" \
  -d '{
    "query": "What is machine learning?",
    "document_ids": [1, 2],
    "top_k": 3,
    "similarity_threshold": 0.8
  }' \
  http://localhost:5000/api/query/
```

#### GET /query/history
Get query history
```bash
curl "http://localhost:5000/api/query/history?limit=50"
```

#### GET /query/stats
Get query and pipeline statistics
```bash
curl http://localhost:5000/api/query/stats
```

#### GET /query/config
Get current pipeline configuration
```bash
curl http://localhost:5000/api/query/config
```

#### PUT /query/config
Update pipeline configuration
```bash
curl -X PUT \
  -H "Content-Type: application/json" \
  -d '{"top_k": 3, "similarity_threshold": 0.8}' \
  http://localhost:5000/api/query/config
```

#### POST /query/search
Search documents without generating answers
```bash
curl -X POST \
  -H "Content-Type: application/json" \
  -d '{"query": "machine learning", "top_k": 5}' \
  http://localhost:5000/api/query/search
```

## 🐳 Docker Deployment

### Development Environment

```bash
# Build and run development environment
docker-compose -f docker-compose.dev.yml up --build

# Run in background
docker-compose -f docker-compose.dev.yml up -d
```

### Production Environment

```bash
# Build and run production environment
docker-compose up --build -d

# View logs
docker-compose logs -f

# Stop services
docker-compose down
```

### Environment Variables for Docker

Create a `.env` file for Docker deployment:

```bash
# Required API Keys
GEMINI_API_KEY=your_gemini_api_key
OPENAI_API_KEY=your_openai_api_key

# Optional Configuration
FLASK_ENV=production
LLM_PROVIDER=gemini
CHUNK_SIZE=1000
TOP_K_RETRIEVAL=5
```

### Docker Commands

```bash
# Build image
docker build -t rag-system .

# Run container
docker run -d \
  -p 5000:5000 \
  -e GEMINI_API_KEY=your_key \
  -v $(pwd)/uploads:/app/uploads \
  -v $(pwd)/chroma_db:/app/chroma_db \
  rag-system

# View logs
docker logs <container_id>

# Execute commands in container
docker exec -it <container_id> bash
```

## 💻 Development

### Project Structure

```
rag-document-qa/
├── app.py                 # Main Flask application
├── requirements.txt       # Python dependencies
├── Dockerfile            # Production Docker image
├── docker-compose.yml    # Production Docker Compose
├── config/
│   └── settings.py       # Configuration management
├── models/
│   └── document.py       # Database models
├── services/
│   ├── document_processor.py  # Document processing
│   ├── vector_store.py        # ChromaDB integration
│   ├── llm_service.py         # LLM provider management
│   └── rag_pipeline.py        # Main RAG pipeline
├── routes/
│   ├── document_routes.py     # Document API endpoints
│   ├── query_routes.py        # Query API endpoints
│   └── health_routes.py       # Health check endpoints
├── utils/
│   └── helpers.py        # Utility functions
└── tests/
    ├── test_*.py         # Test files
    └── conftest.py       # Test configuration
```

### Development Setup

1. **Install development dependencies**
   ```bash
   pip install -r requirements.txt
   pip install pytest pytest-flask pytest-cov black flake8
   ```

2. **Set up pre-commit hooks**
   ```bash
   pip install pre-commit
   pre-commit install
   ```

3. **Run in development mode**
   ```bash
   export FLASK_ENV=development
   export FLASK_DEBUG=1
   python app.py
   ```

### Code Style

The project uses:
- **Black** for code formatting
- **Flake8** for linting
- **Type hints** for better code documentation

```bash
# Format code
black .

# Lint code
flake8 .

# Type checking (optional)
mypy .
```

## 🧪 Testing

### Running Tests

```bash
# Run all tests
pytest

# Run with coverage
pytest --cov=. --cov-report=html

# Run specific test categories
pytest -m unit          # Unit tests only
pytest -m integration   # Integration tests only

# Run specific test file
pytest tests/test_document_processor.py

# Run with verbose output
pytest -v
```

### Test Categories

- **Unit Tests**: Test individual components in isolation
- **Integration Tests**: Test complete workflows
- **API Tests**: Test REST API endpoints

### Test Configuration

Tests use:
- **pytest** as the test runner
- **Mock/patch** for isolating components
- **Temporary directories** for file operations
- **In-memory SQLite** for database tests

### Writing Tests

Example test structure:
```python
def test_document_upload(client):
    """Test document upload functionality"""
    response = client.post('/api/documents/upload', data={
        'file': (BytesIO(b'test content'), 'test.txt')
    })
    assert response.status_code == 201
```

## 🏗️ Architecture

### System Architecture

```
┌─────────────────┐    ┌─────────────────┐    ┌─────────────────┐
│   Client App    │    │   REST API      │    │   Document      │
│                 │────│   (Flask)       │────│   Processor     │
└─────────────────┘    └─────────────────┘    └─────────────────┘
                                │                        │
                                │                        ▼
┌─────────────────┐    ┌─────────────────┐    ┌─────────────────┐
│   Vector DB     │    │   RAG Pipeline  │    │   Text Chunks   │
│   (ChromaDB)    │────│                 │────│                 │
└─────────────────┘    └─────────────────┘    └─────────────────┘
                                │
                                ▼
                       ┌─────────────────┐
                       │   LLM Service   │
                       │ (Gemini/OpenAI) │
                       └─────────────────┘
```

### Component Overview

1. **Document Processor**: Extracts text from various file formats and chunks it
2. **Vector Store**: Manages embeddings and similarity search using ChromaDB
3. **LLM Service**: Handles multiple LLM providers with fallback support
4. **RAG Pipeline**: Orchestrates retrieval and generation processes
5. **REST API**: Provides HTTP endpoints for all functionality

### Data Flow

1. **Document Upload**: File → Text Extraction → Chunking → Embedding → Vector Storage
2. **Query Processing**: Query → Embedding → Similarity Search → Context Retrieval → LLM Generation → Response

### Scalability Considerations

- **Horizontal Scaling**: Multiple Flask instances behind a load balancer
- **Database**: Can be switched to PostgreSQL for production
- **Caching**: Redis integration for query caching
- **Storage**: S3 or similar for document storage
- **Vector Database**: Can be scaled with distributed ChromaDB or Pinecone

## 🤝 Contributing

### Development Workflow

1. **Fork the repository**
2. **Create a feature branch**
   ```bash
   git checkout -b feature/your-feature-name
   ```
3. **Make changes and add tests**
4. **Run tests and linting**
   ```bash
   pytest
   black .
   flake8 .
   ```
5. **Commit changes**
   ```bash
   git commit -m "Add your feature description"
   ```
6. **Push and create pull request**

### Code Guidelines

- Follow PEP 8 style guidelines
- Add type hints to functions
- Write comprehensive tests
- Update documentation for new features
- Use meaningful commit messages

### Issue Reporting

When reporting issues, please include:
- Python version
- Operating system
- Error messages and stack traces
- Steps to reproduce
- Expected vs actual behavior

## 📄 License

This project is licensed under the MIT License - see the LICENSE file for details.

## 🙏 Acknowledgments

- **ChromaDB** for vector database functionality
- **LangChain** for text processing utilities
- **Sentence Transformers** for embedding generation
- **Flask** for the web framework
- **Google** and **OpenAI** for LLM APIs

## 📞 Support

For support and questions:
- Create an issue in the repository
- Check the documentation
- Review existing issues and discussions

---

**Built with ❤️ for the AI community**