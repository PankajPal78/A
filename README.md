# RAG (Retrieval-Augmented Generation) Document Q&A System

A comprehensive document question-answering system that allows users to upload documents and ask questions based on their content. The system uses vector databases for efficient retrieval and LLM APIs for generating contextual responses.

## 🚀 Features

- **Document Upload**: Support for PDF, DOCX, and TXT files (up to 20 documents, max 1000 pages each)
- **Intelligent Chunking**: Automatic text chunking with configurable size and overlap
- **Vector Search**: ChromaDB-based vector database for efficient similarity search
- **LLM Integration**: Google Gemini Pro API for response generation
- **REST API**: Flask-based API with comprehensive endpoints
- **Docker Support**: Complete containerization with Docker Compose
- **Metadata Storage**: SQLite database for document and query metadata
- **Health Monitoring**: Built-in health checks and system statistics

## 📋 Requirements

- Python 3.9+
- Docker and Docker Compose
- Google Gemini API key
- 4GB+ RAM (for embedding model)
- 10GB+ disk space (for vector database)

## 🛠️ Installation

### Option 1: Docker (Recommended)

1. **Clone the repository:**
   ```bash
   git clone <repository-url>
   cd rag-document-qa
   ```

2. **Set up environment variables:**
   ```bash
   cp .env.example .env
   # Edit .env and add your Google API key
   ```

3. **Build and run with Docker Compose:**
   ```bash
   docker-compose up --build
   ```

### Option 2: Local Development

1. **Create virtual environment:**
   ```bash
   python -m venv venv
   source venv/bin/activate  # On Windows: venv\Scripts\activate
   ```

2. **Install dependencies:**
   ```bash
   pip install -r requirements.txt
   ```

3. **Set up environment variables:**
   ```bash
   cp .env.example .env
   # Edit .env and add your Google API key
   ```

4. **Initialize the database:**
   ```bash
   python -c "from app import create_app; from database import init_db; app = create_app(); init_db()"
   ```

5. **Run the application:**
   ```bash
   python app.py
   ```

## 🔧 Configuration

### Environment Variables

Create a `.env` file with the following variables:

```env
# Google Gemini API Key (Required)
GOOGLE_API_KEY=your_google_api_key_here

# Database Configuration
DATABASE_URL=sqlite:///data/rag_database.db

# Flask Configuration
FLASK_ENV=development
FLASK_DEBUG=True

# Vector Database Configuration
VECTOR_DB_PATH=./data/vector_db

# Document Storage
UPLOAD_FOLDER=./uploads
MAX_CONTENT_LENGTH=104857600  # 100MB

# Chunking Configuration
CHUNK_SIZE=1000
CHUNK_OVERLAP=200
```

### Getting a Google API Key

1. Go to [Google AI Studio](https://makersuite.google.com/app/apikey)
2. Create a new API key
3. Add it to your `.env` file

## 📚 API Usage

### Base URL
- Local: `http://localhost:5000`
- Docker: `http://localhost:5000`

### Endpoints

#### 1. Health Check
```http
GET /health
```

#### 2. Upload Document
```http
POST /api/documents/upload
Content-Type: multipart/form-data

file: [document file]
metadata: {"title": "Document Title"} (optional)
```

**Response:**
```json
{
  "message": "Document uploaded successfully",
  "document": {
    "id": 1,
    "filename": "20231201_120000_document.pdf",
    "original_filename": "document.pdf",
    "file_size": 1024000,
    "file_type": "pdf",
    "upload_date": "2023-12-01T12:00:00",
    "processing_status": "processed",
    "chunk_count": 15
  }
}
```

#### 3. Get All Documents
```http
GET /api/documents
```

#### 4. Get Specific Document
```http
GET /api/documents/{document_id}
```

#### 5. Delete Document
```http
DELETE /api/documents/{document_id}
```

#### 6. Query Documents
```http
POST /api/query
Content-Type: application/json

{
  "question": "What is the main topic of the document?",
  "document_ids": [1, 2],  // optional: filter by specific documents
  "max_chunks": 5,         // optional: max chunks to retrieve
  "max_tokens": 1000       // optional: max response length
}
```

**Response:**
```json
{
  "answer": "The main topic is artificial intelligence and machine learning...",
  "sources": [
    {
      "document_id": 1,
      "filename": "ai_document.pdf",
      "file_type": "pdf",
      "relevance_score": 0.95
    }
  ],
  "metadata": {
    "chunks_retrieved": 3,
    "response_time": 1.2,
    "llm_metadata": {
      "model": "gemini-pro",
      "context_chunks_used": 3
    }
  },
  "success": true
}
```

#### 7. Get Document Summary
```http
GET /api/documents/{document_id}/summary
```

#### 8. Get System Statistics
```http
GET /api/stats
```

## 🧪 Testing

### Run Unit Tests
```bash
pytest test_app.py -v
```

### Run Integration Tests
```bash
pytest test_integration.py -v
```

### Run All Tests
```bash
pytest -v
```

## 📁 Project Structure

```
rag-document-qa/
├── app.py                 # Main Flask application
├── database.py            # Database models and operations
├── document_processor.py  # Document processing and chunking
├── vector_store.py        # ChromaDB vector database operations
├── llm_client.py         # Google Gemini API client
├── rag_pipeline.py       # Complete RAG pipeline
├── api_routes.py         # Flask API routes
├── test_app.py           # Unit tests
├── test_integration.py   # Integration tests
├── requirements.txt      # Python dependencies
├── Dockerfile           # Docker configuration
├── docker-compose.yml   # Docker Compose setup
├── .env.example         # Environment variables template
├── README.md            # This file
├── data/                # Data directory (created automatically)
│   ├── vector_db/       # ChromaDB storage
│   └── rag_database.db  # SQLite database
└── uploads/             # Uploaded documents (created automatically)
```

## 🔍 How It Works

1. **Document Upload**: Users upload documents via the REST API
2. **Text Extraction**: Documents are processed to extract text content
3. **Chunking**: Text is split into manageable chunks with overlap
4. **Embedding**: Chunks are converted to vector embeddings using sentence-transformers
5. **Storage**: Embeddings are stored in ChromaDB vector database
6. **Query Processing**: User queries are converted to embeddings
7. **Retrieval**: Similar chunks are retrieved from the vector database
8. **Generation**: Retrieved chunks are passed to Gemini for response generation
9. **Response**: Contextual answers are returned with source information

## 🚀 Deployment

### Local Deployment
```bash
docker-compose up -d
```

### Cloud Deployment (AWS/GCP/Azure)

1. **Set up environment variables** in your cloud platform
2. **Configure persistent storage** for the `data` directory
3. **Deploy using Docker Compose** or container orchestration
4. **Set up load balancing** if needed for high availability

### Environment Variables for Production
```env
FLASK_ENV=production
FLASK_DEBUG=False
GOOGLE_API_KEY=your_production_api_key
DATABASE_URL=postgresql://user:pass@host:port/dbname  # For production DB
```

## 📊 Performance Considerations

- **Memory Usage**: ~2GB for embedding model + vector database
- **Storage**: ~100MB per 1000 pages of documents
- **Response Time**: 1-3 seconds per query (depending on document size)
- **Concurrent Users**: Supports 10-50 concurrent users (depending on hardware)

## 🔧 Troubleshooting

### Common Issues

1. **API Key Error**: Ensure `GOOGLE_API_KEY` is set correctly
2. **Memory Issues**: Increase Docker memory limit to 4GB+
3. **File Upload Fails**: Check file size limits and supported formats
4. **Slow Responses**: Consider using a more powerful embedding model

### Logs
```bash
# View application logs
docker-compose logs -f rag-app

# View specific service logs
docker-compose logs rag-app
```

## 🤝 Contributing

1. Fork the repository
2. Create a feature branch
3. Make your changes
4. Add tests for new functionality
5. Submit a pull request

## 📄 License

This project is licensed under the MIT License - see the LICENSE file for details.

## 🆘 Support

For issues and questions:
1. Check the troubleshooting section
2. Review the API documentation
3. Open an issue on GitHub
4. Check the logs for error details

## 🔮 Future Enhancements

- [ ] Support for more document formats (PPTX, XLSX, etc.)
- [ ] Multi-language support
- [ ] Advanced chunking strategies
- [ ] Caching for improved performance
- [ ] User authentication and authorization
- [ ] Web UI for document management
- [ ] Batch document processing
- [ ] Advanced analytics and insights