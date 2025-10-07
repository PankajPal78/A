# RAG Document Q&A System

A production-ready Retrieval-Augmented Generation (RAG) system that enables users to upload documents and ask questions based on their content. Built with Flask, ChromaDB, and Google Gemini API, fully containerized with Docker.

## 🚀 Features

- **Document Processing**: Upload and process up to 20 documents (PDF, TXT) with max 1000 pages each
- **Intelligent Chunking**: Automatic document chunking with configurable size and overlap
- **Vector Search**: Efficient similarity search using ChromaDB and sentence transformers
- **RAG Pipeline**: Context-aware responses using Google Gemini API
- **REST API**: Comprehensive API with endpoints for document management and queries
- **Metadata Storage**: SQLite database for tracking document metadata
- **Docker Support**: Full containerization for easy deployment
- **Testing**: Unit and integration tests with pytest
- **Cloud Ready**: Deployable on AWS, GCP, Azure, or local environments

## 📋 Requirements

- Docker & Docker Compose (recommended)
- OR Python 3.11+ with pip
- Google Gemini API key (or OpenAI API key)

## 🛠️ Installation & Setup

### Option 1: Docker Deployment (Recommended)

1. **Clone the repository**
```bash
git clone <repository-url>
cd rag-document-qa
```

2. **Configure environment variables**
```bash
cp .env.example .env
# Edit .env and add your API keys
nano .env  # or use your preferred editor
```

Required environment variables:
```env
GEMINI_API_KEY=your_gemini_api_key_here
LLM_PROVIDER=gemini
```

3. **Build and run with Docker Compose**
```bash
docker-compose up --build
```

The API will be available at `http://localhost:5000`

### Option 2: Local Development Setup

1. **Create virtual environment**
```bash
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate
```

2. **Install dependencies**
```bash
pip install -r requirements.txt
```

3. **Configure environment**
```bash
cp .env.example .env
# Edit .env with your settings
```

4. **Run the application**
```bash
python app.py
```

## 🔑 API Key Setup

### Google Gemini API
1. Visit [Google AI Studio](https://makersuite.google.com/app/apikey)
2. Create a new API key
3. Add to `.env` file: `GEMINI_API_KEY=your_key_here`

### OpenAI API (Alternative)
1. Visit [OpenAI Platform](https://platform.openai.com/api-keys)
2. Create a new API key
3. Add to `.env` file: `OPENAI_API_KEY=your_key_here` and set `LLM_PROVIDER=openai`

## 📚 API Documentation

### Base URL
```
http://localhost:5000
```

### Endpoints

#### 1. Health Check
```http
GET /api/health
```

**Response:**
```json
{
  "status": "healthy",
  "timestamp": "2024-01-01T12:00:00",
  "service": "RAG Document Q&A System"
}
```

#### 2. Upload Document
```http
POST /api/documents
Content-Type: multipart/form-data
```

**Parameters:**
- `file`: Document file (PDF or TXT)

**Response:**
```json
{
  "id": 1,
  "filename": "20240101_120000_document.pdf",
  "original_filename": "document.pdf",
  "file_size": 1024000,
  "file_type": "pdf",
  "page_count": 10,
  "chunk_count": 25,
  "upload_date": "2024-01-01T12:00:00",
  "status": "indexed"
}
```

**Example with curl:**
```bash
curl -X POST http://localhost:5000/api/documents \
  -F "file=@/path/to/document.pdf"
```

#### 3. List Documents
```http
GET /api/documents?status=indexed&limit=10
```

**Query Parameters:**
- `status` (optional): Filter by status (uploaded, processing, indexed, failed)
- `limit` (optional): Limit number of results

**Response:**
```json
{
  "documents": [
    {
      "id": 1,
      "filename": "document.pdf",
      "status": "indexed",
      "page_count": 10,
      "chunk_count": 25,
      "upload_date": "2024-01-01T12:00:00"
    }
  ],
  "count": 1
}
```

#### 4. Get Document Details
```http
GET /api/documents/{id}
```

**Response:**
```json
{
  "id": 1,
  "filename": "document.pdf",
  "original_filename": "document.pdf",
  "file_size": 1024000,
  "file_type": "pdf",
  "page_count": 10,
  "chunk_count": 25,
  "upload_date": "2024-01-01T12:00:00",
  "status": "indexed"
}
```

#### 5. Delete Document
```http
DELETE /api/documents/{id}
```

**Response:**
```json
{
  "message": "Document deleted successfully",
  "id": 1
}
```

#### 6. Query Documents
```http
POST /api/query
Content-Type: application/json
```

**Request Body:**
```json
{
  "question": "What is the main topic of the document?",
  "document_id": 1,  // optional - query specific document
  "top_k": 5  // optional - number of chunks to retrieve
}
```

**Response:**
```json
{
  "answer": "The main topic is...",
  "sources": [
    {
      "document_id": "1",
      "filename": "document.pdf",
      "page_count": 10
    }
  ],
  "chunks_retrieved": 5,
  "context_chunks": [
    {
      "text": "Relevant text chunk...",
      "metadata": {
        "document_id": "1",
        "chunk_index": "0",
        "filename": "document.pdf"
      }
    }
  ],
  "success": true
}
```

**Example with curl:**
```bash
curl -X POST http://localhost:5000/api/query \
  -H "Content-Type: application/json" \
  -d '{"question": "What is the main topic?"}'
```

#### 7. Get Statistics
```http
GET /api/stats
```

**Response:**
```json
{
  "documents": {
    "total": 5,
    "indexed": 4,
    "failed": 1,
    "processing": 0
  },
  "pages": 100,
  "chunks": 250,
  "vector_store": {
    "total_chunks": 250,
    "collection_name": "documents"
  },
  "limits": {
    "max_documents": 20,
    "max_file_size_mb": 100
  }
}
```

## 🧪 Testing

### Run Tests with Docker
```bash
docker-compose exec rag-api pytest app/tests/ -v
```

### Run Tests Locally
```bash
# Using the test script
./run_tests.sh

# Or directly with pytest
pytest app/tests/ -v --cov=app --cov-report=html
```

### Test Coverage
After running tests, view the coverage report:
```bash
open htmlcov/index.html  # On macOS
# or
xdg-open htmlcov/index.html  # On Linux
```

## 🏗️ Architecture

```
┌─────────────┐
│   Client    │
└──────┬──────┘
       │
       v
┌─────────────────────────────────────┐
│         Flask REST API              │
│  ┌───────────────────────────────┐  │
│  │  Document Upload Endpoint     │  │
│  │  Query Endpoint               │  │
│  │  Management Endpoints         │  │
│  └───────────────────────────────┘  │
└──────┬──────────────────────┬───────┘
       │                      │
       v                      v
┌─────────────────┐    ┌──────────────┐
│  Document       │    │   Vector     │
│  Processor      │───>│   Store      │
│  - PDF Parser   │    │  (ChromaDB)  │
│  - Chunker      │    └──────┬───────┘
└─────────────────┘           │
                              │
                              v
                       ┌──────────────┐
                       │     RAG      │
                       │   Pipeline   │
                       └──────┬───────┘
                              │
                              v
                       ┌──────────────┐
                       │  LLM Service │
                       │   (Gemini)   │
                       └──────────────┘
```

### Components

1. **Flask API**: RESTful API endpoints
2. **Document Processor**: PDF/TXT parsing and text chunking
3. **Vector Store**: ChromaDB for semantic search
4. **RAG Service**: Orchestrates retrieval and generation
5. **LLM Service**: Integrates with Gemini/OpenAI APIs
6. **Database**: SQLite for document metadata

## ⚙️ Configuration

### Environment Variables

| Variable | Description | Default |
|----------|-------------|---------|
| `LLM_PROVIDER` | LLM provider (gemini/openai) | `gemini` |
| `GEMINI_API_KEY` | Google Gemini API key | - |
| `OPENAI_API_KEY` | OpenAI API key | - |
| `MAX_DOCUMENTS` | Maximum number of documents | `20` |
| `MAX_PAGES_PER_DOCUMENT` | Maximum pages per document | `1000` |
| `CHUNK_SIZE` | Text chunk size in characters | `1000` |
| `CHUNK_OVERLAP` | Overlap between chunks | `200` |
| `TOP_K_RESULTS` | Number of chunks to retrieve | `5` |
| `EMBEDDING_MODEL` | Sentence transformer model | `all-MiniLM-L6-v2` |
| `LLM_TEMPERATURE` | LLM temperature (0-1) | `0.7` |
| `LLM_MAX_TOKENS` | Maximum tokens in response | `1000` |

### Customizing LLM Providers

#### Using Gemini (Default)
```env
LLM_PROVIDER=gemini
GEMINI_API_KEY=your_key_here
```

#### Using OpenAI
```env
LLM_PROVIDER=openai
OPENAI_API_KEY=your_key_here
```

## 🌐 Cloud Deployment

### AWS EC2

1. **Launch EC2 instance** (Ubuntu 22.04)
```bash
# Connect to instance
ssh -i your-key.pem ubuntu@your-instance-ip
```

2. **Install Docker**
```bash
curl -fsSL https://get.docker.com -o get-docker.sh
sudo sh get-docker.sh
sudo usermod -aG docker ubuntu
```

3. **Clone and deploy**
```bash
git clone <repository-url>
cd rag-document-qa
cp .env.example .env
# Edit .env with your API keys
docker-compose up -d
```

4. **Configure security group** to allow port 5000

### Google Cloud Platform (GCP)

1. **Create Compute Engine instance**
2. **Follow similar steps as AWS**
3. **Or use Cloud Run** for serverless deployment

### Azure

1. **Create Virtual Machine**
2. **Install Docker**
3. **Deploy with Docker Compose**

### Heroku

```bash
heroku container:login
heroku create your-app-name
heroku config:set GEMINI_API_KEY=your_key
heroku container:push web
heroku container:release web
```

## 📊 Performance Optimization

### Recommended Settings for Production

```env
# Use multiple workers
GUNICORN_WORKERS=4

# Optimize chunk settings
CHUNK_SIZE=800
CHUNK_OVERLAP=150

# Tune retrieval
TOP_K_RESULTS=3
```

### Scaling Considerations

- **Vertical Scaling**: Increase RAM for larger embedding models
- **Horizontal Scaling**: Use load balancer with multiple instances
- **Database**: Switch to PostgreSQL for better concurrency
- **Vector Store**: Consider Pinecone or Weaviate for production scale

## 🔒 Security Best Practices

1. **API Keys**: Never commit `.env` file to version control
2. **File Uploads**: Implement virus scanning for production
3. **Rate Limiting**: Add rate limiting to prevent abuse
4. **Authentication**: Implement JWT or OAuth for production
5. **HTTPS**: Use SSL/TLS in production environments

## 🐛 Troubleshooting

### Common Issues

#### Docker build fails
```bash
# Clear Docker cache
docker-compose down
docker system prune -a
docker-compose up --build
```

#### ChromaDB errors
```bash
# Remove vector database and restart
rm -rf data/vector_db/*
docker-compose restart
```

#### Out of memory
```bash
# Increase Docker memory limit in Docker Desktop settings
# Or reduce CHUNK_SIZE and MAX_DOCUMENTS
```

#### API key errors
```bash
# Verify API key is set correctly
docker-compose exec rag-api env | grep API_KEY
```

## 📈 Monitoring

### Logs
```bash
# View application logs
docker-compose logs -f rag-api

# View specific lines
docker-compose logs --tail=100 rag-api
```

### Health Check
```bash
curl http://localhost:5000/api/health
```

## 🤝 Contributing

1. Fork the repository
2. Create feature branch (`git checkout -b feature/AmazingFeature`)
3. Commit changes (`git commit -m 'Add AmazingFeature'`)
4. Push to branch (`git push origin feature/AmazingFeature`)
5. Open Pull Request

## 📄 License

This project is licensed under the MIT License.

## 👥 Support

For issues and questions:
- Open an issue on GitHub
- Check existing documentation
- Review troubleshooting section

## 🗺️ Roadmap

- [ ] Support for DOCX files
- [ ] Multi-language support
- [ ] Advanced authentication
- [ ] Web UI frontend
- [ ] Batch document upload
- [ ] Export conversation history
- [ ] Advanced analytics dashboard
- [ ] Support for additional LLM providers

## 📚 Additional Resources

- [LangChain Documentation](https://python.langchain.com/)
- [ChromaDB Documentation](https://docs.trychroma.com/)
- [Google Gemini API](https://ai.google.dev/)
- [Flask Documentation](https://flask.palletsprojects.com/)

---

**Built with ❤️ for efficient document question-answering**