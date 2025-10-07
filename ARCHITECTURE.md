# System Architecture

## Overview

This document describes the architecture of the Document Q&A RAG (Retrieval-Augmented Generation) system.

## Architecture Diagram

```
┌──────────────────────────────────────────────────────────────┐
│                        Client Layer                           │
│  (Web Browser, Postman, cURL, Custom Applications)           │
└──────────────────────┬───────────────────────────────────────┘
                       │ HTTP/REST
┌──────────────────────▼───────────────────────────────────────┐
│                     API Layer (Flask)                         │
│  ┌────────────┬──────────────┬─────────────┬──────────────┐  │
│  │  Upload    │    Query     │  Documents  │    Stats     │  │
│  │  Endpoint  │   Endpoint   │  Endpoint   │   Endpoint   │  │
│  └────────────┴──────────────┴─────────────┴──────────────┘  │
└──────────┬────────────────────────────────────┬──────────────┘
           │                                    │
┌──────────▼──────────┐              ┌─────────▼────────────┐
│  Document Processor │              │  Metadata Database   │
│  ┌───────────────┐  │              │   (SQLAlchemy)       │
│  │ PDF Parser    │  │              │  ┌────────────────┐  │
│  ├───────────────┤  │              │  │  Document      │  │
│  │ Text Chunker  │  │              │  │  Metadata      │  │
│  └───────────────┘  │              │  └────────────────┘  │
└──────────┬──────────┘              └──────────────────────┘
           │
┌──────────▼───────────────────────────────────────┐
│            Vector Store (ChromaDB)                │
│  ┌──────────────┐        ┌──────────────────┐    │
│  │  Embedding   │        │  Vector Index    │    │
│  │  Generator   │───────▶│  (HNSW)          │    │
│  │ (Sentence-   │        │                  │    │
│  │ Transformers)│        │  Cosine          │    │
│  └──────────────┘        │  Similarity      │    │
│                          └──────────────────┘    │
└──────────┬───────────────────────────────────────┘
           │
┌──────────▼──────────┐
│   RAG Pipeline      │
│  ┌───────────────┐  │
│  │  Retriever    │  │
│  ├───────────────┤  │
│  │  Context      │  │
│  │  Builder      │  │
│  └───────────────┘  │
└──────────┬──────────┘
           │
┌──────────▼──────────────────────────┐
│       LLM Provider Layer            │
│  ┌──────────┬──────────┬─────────┐  │
│  │  Gemini  │  OpenAI  │ Ollama  │  │
│  │  API     │  API     │  Local  │  │
│  └──────────┴──────────┴─────────┘  │
└─────────────────────────────────────┘
```

## Components

### 1. API Layer (Flask)

**Responsibilities:**
- Handle HTTP requests and responses
- Route requests to appropriate services
- Validate input data
- Error handling and logging

**Endpoints:**
- `POST /api/upload` - Document upload
- `POST /api/query` - Question answering
- `GET /api/documents` - List documents
- `GET /api/documents/{id}` - Get document details
- `DELETE /api/documents/{id}` - Delete document
- `GET /api/stats` - System statistics
- `GET /api/health` - Health check

### 2. Document Processor

**Responsibilities:**
- Extract text from documents (PDF, TXT)
- Validate document constraints (page limits)
- Chunk text into manageable pieces
- Handle various file formats

**Key Classes:**
- `DocumentProcessor`: Main processing logic
- Uses `PyPDF2` for PDF extraction
- Uses `RecursiveCharacterTextSplitter` from LangChain

**Chunking Strategy:**
- Default chunk size: 1000 characters
- Overlap: 200 characters
- Separators: `["\n\n", "\n", " ", ""]`

### 3. Vector Store (ChromaDB)

**Responsibilities:**
- Generate embeddings for text chunks
- Store and index vectors
- Perform similarity search
- Manage document lifecycle

**Key Classes:**
- `VectorStore`: Wrapper around ChromaDB
- Uses `sentence-transformers/all-MiniLM-L6-v2` for embeddings

**Features:**
- Persistent storage on disk
- Cosine similarity for search
- HNSW index for fast retrieval
- Metadata filtering

### 4. RAG Pipeline

**Responsibilities:**
- Orchestrate retrieval and generation
- Retrieve relevant chunks based on query
- Format context for LLM
- Generate final answer

**Flow:**
1. Accept user query
2. Generate query embedding
3. Retrieve top-k similar chunks
4. Format chunks as context
5. Send to LLM with prompt
6. Return answer with sources

### 5. LLM Provider Layer

**Responsibilities:**
- Abstract different LLM APIs
- Format prompts consistently
- Handle API-specific errors
- Manage rate limits and retries

**Supported Providers:**

1. **Google Gemini**
   - Model: gemini-pro
   - Best for: Free tier usage
   - Configuration: `GEMINI_API_KEY`

2. **OpenAI**
   - Model: gpt-3.5-turbo
   - Best for: Production quality
   - Configuration: `OPENAI_API_KEY`

3. **Ollama**
   - Model: Configurable (llama2, mistral, etc.)
   - Best for: Privacy, local deployment
   - Configuration: `OLLAMA_BASE_URL`, `OLLAMA_MODEL`

### 6. Metadata Database

**Responsibilities:**
- Store document metadata
- Track processing status
- Provide query interface

**Schema:**
```sql
CREATE TABLE documents (
    id INTEGER PRIMARY KEY,
    filename VARCHAR(255),
    original_filename VARCHAR(255),
    file_path VARCHAR(512),
    file_size INTEGER,
    page_count INTEGER,
    chunk_count INTEGER,
    upload_date DATETIME,
    status VARCHAR(50),
    error_message TEXT
);
```

## Data Flow

### Upload Flow

```
1. Client uploads file
   ↓
2. API validates file (size, type, limits)
   ↓
3. File saved to disk
   ↓
4. Document record created (status: processing)
   ↓
5. DocumentProcessor extracts text
   ↓
6. Text chunked into pieces
   ↓
7. Embeddings generated for chunks
   ↓
8. Chunks stored in VectorStore
   ↓
9. Document status updated (completed/failed)
   ↓
10. Response returned to client
```

### Query Flow

```
1. Client sends question
   ↓
2. API validates input
   ↓
3. RAG Pipeline processes query
   ↓
4. Query embedding generated
   ↓
5. VectorStore retrieves top-k chunks
   ↓
6. Chunks formatted as context
   ↓
7. LLM generates answer
   ↓
8. Answer + sources returned
```

## Scalability Considerations

### Current Limitations
- Single server deployment
- In-memory processing
- Local file storage
- SQLite database

### Scaling Strategies

**Horizontal Scaling:**
- Use load balancer (nginx, HAProxy)
- Multiple API instances
- Shared file storage (NFS, S3)
- Distributed database (PostgreSQL, MySQL)

**Vertical Scaling:**
- Increase server resources
- Use faster embedding models
- Optimize chunk size
- Cache frequent queries

**Database Scaling:**
- Replace SQLite with PostgreSQL
- Add read replicas
- Implement connection pooling
- Use database indexing

**Storage Scaling:**
- Move to S3/GCS/Azure Blob
- Implement CDN for documents
- Use object storage for vectors
- Implement file cleanup policies

**Vector Store Scaling:**
- Use managed vector DB (Pinecone, Weaviate)
- Implement sharding
- Add caching layer
- Optimize embedding model

## Security Considerations

1. **Input Validation**
   - File type checking
   - Size limits
   - Content scanning

2. **API Security**
   - Rate limiting
   - Authentication (to be added)
   - CORS configuration
   - Input sanitization

3. **Data Privacy**
   - Encrypted storage (to be added)
   - Secure API keys
   - Access control
   - Audit logging

4. **Production Hardening**
   - HTTPS only
   - Security headers
   - Error message sanitization
   - Dependency scanning

## Performance Metrics

**Target Performance:**
- Upload: < 5s for 100-page PDF
- Query: < 2s for answer generation
- Retrieval: < 500ms for top-5 chunks
- Throughput: 100 concurrent users

**Monitoring:**
- Request latency
- Error rates
- Document count
- Storage usage
- API quota usage

## Future Enhancements

1. **Features**
   - Multi-modal support (images, tables)
   - Conversation history
   - Document comparison
   - Batch processing

2. **Infrastructure**
   - Kubernetes deployment
   - Auto-scaling
   - Multi-region support
   - Disaster recovery

3. **Intelligence**
   - Fine-tuned embeddings
   - Custom LLM models
   - Advanced chunking strategies
   - Query understanding

4. **User Experience**
   - Web UI
   - Real-time updates
   - Document preview
   - Export capabilities