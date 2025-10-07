# Document Q&A RAG System

> **🚀 New here? Start with [GETTING_STARTED.md](GETTING_STARTED.md) for a quick path to success!**

A production-ready Retrieval-Augmented Generation (RAG) pipeline that allows users to upload documents and ask questions based on their content. The system leverages vector databases for efficient retrieval and LLM APIs for generating accurate, contextual responses.

## 🚀 Features

- **Document Ingestion**: Support for PDF and TXT files (up to 20 documents, 1000 pages each)
- **Smart Chunking**: Intelligent text segmentation for optimal retrieval
- **Vector Search**: ChromaDB-powered semantic search with embeddings
- **Multiple LLM Providers**: Support for Google Gemini, OpenAI, and Ollama
- **REST API**: Clean Flask-based API with comprehensive endpoints
- **Metadata Storage**: SQLAlchemy-based document metadata management
- **Docker Support**: Complete containerization for easy deployment
- **Production Ready**: Includes tests, logging, and health checks

## 📋 Table of Contents

- [Architecture](#architecture)
- [Prerequisites](#prerequisites)
- [Installation](#installation)
- [Configuration](#configuration)
- [Usage](#usage)
- [API Endpoints](#api-endpoints)
- [Testing](#testing)
- [Deployment](#deployment)
- [Cloud Deployment](#cloud-deployment)
- [Troubleshooting](#troubleshooting)

## 🏗️ Architecture

```
┌─────────────┐      ┌──────────────┐      ┌─────────────┐
│   Client    │─────▶│  Flask API   │─────▶│  Document   │
│             │      │              │      │  Processor  │
└─────────────┘      └──────────────┘      └─────────────┘
                            │                      │
                            ▼                      ▼
                     ┌──────────────┐      ┌─────────────┐
                     │  RAG Pipeline│◀─────│  Vector DB  │
                     │              │      │  (ChromaDB) │
                     └──────────────┘      └─────────────┘
                            │
                            ▼
                     ┌──────────────┐
                     │  LLM Provider│
                     │ (Gemini/GPT) │
                     └──────────────┘
```

### Components

1. **Document Processor**: Handles PDF/TXT parsing and text chunking
2. **Vector Store**: ChromaDB for semantic search with sentence transformers
3. **RAG Pipeline**: Orchestrates retrieval and generation
4. **LLM Provider**: Pluggable interface for different LLM APIs
5. **API Layer**: Flask REST API with comprehensive endpoints
6. **Metadata DB**: SQLAlchemy for document metadata

## 📦 Prerequisites

### Local Development
- Python 3.9+
- pip package manager
- Virtual environment (recommended)

### Docker Deployment
- Docker 20.10+
- Docker Compose 2.0+

### LLM API Keys
At least one of:
- Google Gemini API key ([Get one here](https://makersuite.google.com/app/apikey))
- OpenAI API key ([Get one here](https://platform.openai.com/api-keys))
- Local Ollama installation ([Install here](https://ollama.ai))

## 🔧 Installation

### Option 1: Local Installation

1. **Clone the repository**
```bash
git clone <repository-url>
cd rag-document-qa
```

2. **Create virtual environment**
```bash
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate
```

3. **Install dependencies**
```bash
pip install -r requirements.txt
```

4. **Set up environment variables**
```bash
cp .env.example .env
# Edit .env with your configuration
```

5. **Run the application**
```bash
python run.py
```

The API will be available at `http://localhost:5000`

### Option 2: Docker Installation

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

3. **Build and run with Docker Compose**
```bash
docker-compose up -d
```

The API will be available at `http://localhost:5000`

## ⚙️ Configuration

### Environment Variables

Edit `.env` file with your configuration:

```bash
# LLM Provider (choose: gemini, openai, or ollama)
LLM_PROVIDER=gemini

# API Keys
GEMINI_API_KEY=your_gemini_api_key_here
OPENAI_API_KEY=your_openai_api_key_here

# Application Settings
FLASK_ENV=development
UPLOAD_FOLDER=./data/uploads
VECTOR_DB_PATH=./data/vectordb
DATABASE_URL=sqlite:///./data/documents.db

# Chunking Settings
CHUNK_SIZE=1000
CHUNK_OVERLAP=200

# Retrieval Settings
TOP_K_RESULTS=5
```

### Using Different LLM Providers

#### Google Gemini (Recommended for free tier)
```bash
LLM_PROVIDER=gemini
GEMINI_API_KEY=your_key_here
```

#### OpenAI
```bash
LLM_PROVIDER=openai
OPENAI_API_KEY=your_key_here
```

#### Ollama (Local, no API key needed)
```bash
LLM_PROVIDER=ollama
OLLAMA_BASE_URL=http://localhost:11434
OLLAMA_MODEL=llama2
```

For Ollama, uncomment the ollama service in `docker-compose.yml`

## 🎯 Usage

### Quick Start

1. **Start the server**
```bash
# Local
python run.py

# Docker
docker-compose up -d
```

2. **Upload a document**
```bash
curl -X POST http://localhost:5000/api/upload \
  -F "file=@/path/to/document.pdf"
```

3. **Ask a question**
```bash
curl -X POST http://localhost:5000/api/query \
  -H "Content-Type: application/json" \
  -d '{"question": "What is the main topic?"}'
```

### Using Postman

Import the `postman_collection.json` file into Postman for a complete set of API requests.

## 🔌 API Endpoints

### Health Check
```http
GET /api/health
```
Check if the API is running.

### Upload Document
```http
POST /api/upload
Content-Type: multipart/form-data

file: <document.pdf>
```
Upload a document for processing. Supports PDF and TXT files.

**Response:**
```json
{
  "message": "Document uploaded and processed successfully",
  "document": {
    "id": 1,
    "filename": "document.pdf",
    "page_count": 10,
    "chunk_count": 25,
    "status": "completed"
  }
}
```

### Query Documents
```http
POST /api/query
Content-Type: application/json

{
  "question": "What is RAG?",
  "top_k": 5
}
```
Ask a question based on uploaded documents.

**Response:**
```json
{
  "answer": "RAG stands for Retrieval-Augmented Generation...",
  "sources": [
    {
      "document_id": "1",
      "chunk_index": 3,
      "text_preview": "...",
      "relevance_score": 0.95
    }
  ],
  "retrieved_chunks": 5
}
```

### List Documents
```http
GET /api/documents
```
Get all uploaded documents with metadata.

### Get Document
```http
GET /api/documents/{id}
```
Get specific document metadata.

### Delete Document
```http
DELETE /api/documents/{id}
```
Delete a document and its associated data.

### System Statistics
```http
GET /api/stats
```
Get system statistics.

**Response:**
```json
{
  "documents": {
    "total": 5,
    "completed": 4,
    "processing": 1,
    "failed": 0
  },
  "vector_store": {
    "total_chunks": 120
  },
  "limits": {
    "max_documents": 20,
    "max_pages_per_document": 1000
  }
}
```

## 🧪 Testing

### Run All Tests
```bash
# Local
pytest

# With coverage
pytest --cov=app --cov-report=html

# Docker
docker-compose exec rag-api pytest
```

### Run Specific Tests
```bash
# API tests only
pytest tests/test_api.py

# Document processor tests
pytest tests/test_document_processor.py

# Vector store tests
pytest tests/test_vector_store.py
```

### Test Coverage
```bash
pytest --cov=app --cov-report=term-missing
```

## 🚢 Deployment

### Local Deployment

1. Set `FLASK_ENV=production` in `.env`
2. Use gunicorn for production:
```bash
gunicorn --bind 0.0.0.0:5000 --workers 4 run:app
```

### Docker Deployment

```bash
# Build
docker-compose build

# Run in detached mode
docker-compose up -d

# View logs
docker-compose logs -f

# Stop
docker-compose down
```

### Docker with Custom Configuration

```bash
# Use custom .env file
docker-compose --env-file .env.production up -d

# Scale workers
docker-compose up -d --scale rag-api=3
```

## ☁️ Cloud Deployment

### AWS Deployment

#### Option 1: EC2 with Docker

1. **Launch EC2 instance** (t2.medium or larger recommended)

2. **Install Docker**
```bash
sudo yum update -y
sudo yum install docker -y
sudo service docker start
sudo usermod -a -G docker ec2-user
```

3. **Install Docker Compose**
```bash
sudo curl -L "https://github.com/docker/compose/releases/latest/download/docker-compose-$(uname -s)-$(uname -m)" -o /usr/local/bin/docker-compose
sudo chmod +x /usr/local/bin/docker-compose
```

4. **Deploy application**
```bash
git clone <your-repo>
cd rag-document-qa
cp .env.example .env
# Edit .env with your API keys
docker-compose up -d
```

5. **Configure security group** to allow inbound traffic on port 5000

#### Option 2: AWS ECS (Fargate)

1. **Build and push Docker image**
```bash
aws ecr create-repository --repository-name rag-api
docker build -t rag-api .
docker tag rag-api:latest <account-id>.dkr.ecr.<region>.amazonaws.com/rag-api:latest
aws ecr get-login-password --region <region> | docker login --username AWS --password-stdin <account-id>.dkr.ecr.<region>.amazonaws.com
docker push <account-id>.dkr.ecr.<region>.amazonaws.com/rag-api:latest
```

2. **Create ECS task definition** with environment variables
3. **Create ECS service** with application load balancer
4. **Configure auto-scaling** based on CPU/memory

### GCP Deployment

#### Cloud Run

1. **Build and push to Container Registry**
```bash
gcloud builds submit --tag gcr.io/<project-id>/rag-api
```

2. **Deploy to Cloud Run**
```bash
gcloud run deploy rag-api \
  --image gcr.io/<project-id>/rag-api \
  --platform managed \
  --region us-central1 \
  --allow-unauthenticated \
  --set-env-vars "GEMINI_API_KEY=<your-key>,LLM_PROVIDER=gemini"
```

### Azure Deployment

#### Azure Container Instances

1. **Create resource group**
```bash
az group create --name rag-rg --location eastus
```

2. **Create container instance**
```bash
az container create \
  --resource-group rag-rg \
  --name rag-api \
  --image <your-dockerhub-username>/rag-api:latest \
  --dns-name-label rag-api-unique \
  --ports 5000 \
  --environment-variables \
    GEMINI_API_KEY=<your-key> \
    LLM_PROVIDER=gemini
```

## 🔍 Troubleshooting

### Common Issues

#### 1. Import Errors
```
Error: No module named 'app'
```
**Solution**: Ensure you're in the project root and virtual environment is activated.

#### 2. API Key Not Found
```
Error: GEMINI_API_KEY not configured
```
**Solution**: Check `.env` file exists and contains valid API key.

#### 3. ChromaDB Permission Error
```
Error: Permission denied: './data/vectordb'
```
**Solution**: 
```bash
mkdir -p data/vectordb data/uploads
chmod -R 755 data/
```

#### 4. Docker Container Won't Start
```bash
# Check logs
docker-compose logs rag-api

# Rebuild containers
docker-compose down
docker-compose build --no-cache
docker-compose up -d
```

#### 5. Out of Memory Error
**Solution**: Reduce `CHUNK_SIZE` in `.env` or increase Docker memory limit in Docker Desktop settings.

### Performance Optimization

1. **Increase workers** in production:
```bash
gunicorn --workers 8 --timeout 120 run:app
```

2. **Use faster embedding model** (trade-off with accuracy):
```python
# In app/vector_store.py
self.embedding_model = SentenceTransformer('all-MiniLM-L6-v2')  # Fast
# vs
self.embedding_model = SentenceTransformer('all-mpnet-base-v2')  # Accurate
```

3. **Adjust chunk size** based on your use case:
- Smaller chunks (500-800): Better for specific facts
- Larger chunks (1200-1500): Better for context

## 📚 Additional Resources

- [LangChain Documentation](https://python.langchain.com/)
- [ChromaDB Documentation](https://docs.trychroma.com/)
- [Sentence Transformers](https://www.sbert.net/)
- [Flask Documentation](https://flask.palletsprojects.com/)

## 📄 License

MIT License - feel free to use this project for learning or production.

## 🤝 Contributing

Contributions are welcome! Please feel free to submit a Pull Request.

## 📧 Support

For issues and questions, please open an issue in the GitHub repository.

---

**Built with ❤️ using Flask, LangChain, ChromaDB, and modern LLMs**