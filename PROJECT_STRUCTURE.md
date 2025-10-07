# Project Structure

Complete file and folder organization of the RAG Document Q&A system.

## Directory Tree

```
rag-document-qa/
│
├── app/                          # Main application package
│   ├── __init__.py              # Flask app factory
│   ├── config.py                # Configuration management
│   ├── models.py                # Database models (SQLAlchemy)
│   ├── routes.py                # API endpoints
│   ├── document_processor.py   # Document ingestion & chunking
│   ├── vector_store.py          # Vector database operations (ChromaDB)
│   ├── llm_provider.py          # LLM provider abstraction
│   └── rag_pipeline.py          # RAG orchestration
│
├── tests/                        # Test suite
│   ├── __init__.py
│   ├── conftest.py              # Pytest configuration & fixtures
│   ├── test_api.py              # API endpoint tests
│   ├── test_document_processor.py
│   └── test_vector_store.py
│
├── data/                         # Data directory (created at runtime)
│   ├── uploads/                 # Uploaded documents
│   ├── vectordb/                # ChromaDB persistent storage
│   └── documents.db             # SQLite database
│
├── docs/                         # Documentation (optional)
│
├── .env                          # Environment variables (not in git)
├── .env.example                 # Environment template
├── .gitignore                   # Git ignore rules
├── .dockerignore                # Docker ignore rules
│
├── requirements.txt             # Python dependencies
├── pytest.ini                   # Pytest configuration
│
├── run.py                        # Application entry point
├── setup.sh                      # Setup script for local development
│
├── Dockerfile                    # Docker image definition
├── docker-compose.yml           # Docker Compose configuration
│
├── README.md                     # Main documentation
├── QUICKSTART.md                # Quick start guide
├── API_TESTING_GUIDE.md         # API testing examples
├── ARCHITECTURE.md              # System architecture
├── DEPLOYMENT_GUIDE.md          # Deployment instructions
├── PROJECT_STRUCTURE.md         # This file
│
└── postman_collection.json      # Postman API collection
```

## File Descriptions

### Core Application Files

#### `app/__init__.py`
- Flask application factory
- CORS configuration
- Blueprint registration
- Directory initialization

#### `app/config.py`
- Environment variable management
- Configuration classes
- Default values
- LLM provider settings

#### `app/models.py`
- SQLAlchemy ORM models
- Database initialization
- Document metadata schema
- Session management

#### `app/routes.py`
- REST API endpoints
- Request validation
- Response formatting
- Error handling

#### `app/document_processor.py`
- PDF text extraction (PyPDF2)
- TXT file processing
- Text chunking (LangChain)
- Page limit enforcement

#### `app/vector_store.py`
- ChromaDB client management
- Embedding generation (sentence-transformers)
- Vector similarity search
- Document CRUD operations

#### `app/llm_provider.py`
- LLM provider abstraction
- Gemini integration
- OpenAI integration
- Ollama integration
- Provider factory pattern

#### `app/rag_pipeline.py`
- RAG workflow orchestration
- Query processing
- Context assembly
- Response generation

### Test Files

#### `tests/conftest.py`
- Pytest fixtures
- Test app configuration
- Mock data setup

#### `tests/test_api.py`
- API endpoint tests
- Request/response validation
- Error case testing

#### `tests/test_document_processor.py`
- Document processing tests
- Chunking logic tests

#### `tests/test_vector_store.py`
- Vector operations tests
- Search functionality tests

### Configuration Files

#### `.env.example`
Template for environment variables:
- LLM provider selection
- API keys
- Application settings
- Chunking configuration

#### `requirements.txt`
Python dependencies:
- Flask (web framework)
- LangChain (document processing)
- ChromaDB (vector database)
- Sentence Transformers (embeddings)
- PyPDF2 (PDF parsing)
- SQLAlchemy (ORM)
- Google Generative AI (Gemini)
- OpenAI (GPT integration)
- Pytest (testing)

#### `pytest.ini`
- Test discovery patterns
- Test execution options
- Test markers

### Docker Files

#### `Dockerfile`
Multi-stage Docker build:
1. Base Python image
2. System dependencies
3. Python dependencies
4. Application code
5. Runtime configuration

#### `docker-compose.yml`
Service definitions:
- `rag-api`: Main application
- `ollama`: Optional local LLM (commented)
- Volume mounts
- Environment variables
- Health checks

#### `.dockerignore`
Excludes from Docker build:
- Python cache files
- Virtual environments
- Test files
- Documentation
- Data directories

### Entry Points

#### `run.py`
- Flask app initialization
- Development server startup
- Production server config (gunicorn)

#### `setup.sh`
Automated setup script:
1. Python version check
2. Virtual environment creation
3. Dependency installation
4. Environment file setup
5. Directory creation
6. Test execution

### Documentation

#### `README.md`
- Project overview
- Feature list
- Installation instructions
- API documentation
- Configuration guide
- Deployment overview

#### `QUICKSTART.md`
- Fast setup (Docker)
- First query tutorial
- Common tasks
- Troubleshooting

#### `API_TESTING_GUIDE.md`
- Endpoint documentation
- cURL examples
- Postman usage
- Testing scenarios
- Error cases

#### `ARCHITECTURE.md`
- System design
- Component interaction
- Data flow
- Scalability considerations
- Security notes

#### `DEPLOYMENT_GUIDE.md`
- Local deployment
- Docker deployment
- AWS deployment (EC2, ECS, EB)
- GCP deployment (Cloud Run, GKE)
- Azure deployment (ACI, App Service)
- Kubernetes setup
- Production best practices

#### `PROJECT_STRUCTURE.md`
- File organization (this file)
- Directory purposes
- File descriptions

### API Testing

#### `postman_collection.json`
Postman collection with:
- All API endpoints
- Example requests
- Environment variables
- Test scripts

## Data Flow Through Files

### Document Upload Flow

```
Client Request
    ↓
routes.py (/api/upload)
    ↓
document_processor.py (extract & chunk)
    ↓
vector_store.py (generate embeddings & store)
    ↓
models.py (save metadata)
    ↓
routes.py (return response)
```

### Query Flow

```
Client Request
    ↓
routes.py (/api/query)
    ↓
rag_pipeline.py (orchestrate)
    ↓
vector_store.py (retrieve chunks)
    ↓
llm_provider.py (generate answer)
    ↓
routes.py (format & return)
```

## Configuration Hierarchy

```
Environment Variables (.env)
    ↓
config.py (Config class)
    ↓
app/__init__.py (app creation)
    ↓
Individual modules (import Config)
```

## Dependency Graph

```
run.py
    └── app/__init__.py
        ├── app/config.py
        ├── app/models.py
        └── app/routes.py
            ├── app/document_processor.py
            ├── app/vector_store.py
            └── app/rag_pipeline.py
                ├── app/vector_store.py
                └── app/llm_provider.py
```

## File Sizes (Approximate)

```
app/__init__.py           ~1 KB
app/config.py            ~2 KB
app/models.py            ~3 KB
app/routes.py            ~8 KB
app/document_processor.py ~4 KB
app/vector_store.py      ~5 KB
app/llm_provider.py      ~5 KB
app/rag_pipeline.py      ~3 KB

tests/                   ~8 KB total
requirements.txt         ~0.5 KB
Dockerfile              ~1 KB
docker-compose.yml      ~2 KB

README.md               ~20 KB
QUICKSTART.md           ~10 KB
API_TESTING_GUIDE.md    ~15 KB
ARCHITECTURE.md         ~15 KB
DEPLOYMENT_GUIDE.md     ~20 KB
```

## Adding New Features

### To add a new API endpoint:
1. Add route in `app/routes.py`
2. Add business logic in relevant module
3. Add tests in `tests/test_api.py`
4. Update `postman_collection.json`
5. Document in `API_TESTING_GUIDE.md`

### To add a new LLM provider:
1. Add provider class in `app/llm_provider.py`
2. Update `get_llm_provider()` factory
3. Add config in `app/config.py`
4. Update `.env.example`
5. Document in `README.md`

### To add a new document format:
1. Add parser in `app/document_processor.py`
2. Update `ALLOWED_EXTENSIONS` in `app/config.py`
3. Add tests in `tests/test_document_processor.py`
4. Update documentation

## Best Practices

### File Organization
- Keep files focused and single-purpose
- Group related functionality in modules
- Maintain clear separation of concerns
- Use meaningful file names

### Code Structure
- Follow PEP 8 style guide
- Add docstrings to functions/classes
- Keep functions small and focused
- Use type hints where helpful

### Documentation
- Update README when adding features
- Add examples for new endpoints
- Document configuration options
- Keep architecture docs current

### Testing
- Write tests for new features
- Maintain test coverage
- Use fixtures for common setup
- Test edge cases and errors