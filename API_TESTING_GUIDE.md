# API Testing Guide

This guide provides comprehensive examples for testing the RAG Document Q&A API endpoints.

## Table of Contents

1. [Setup](#setup)
2. [Health Check](#health-check)
3. [Upload Documents](#upload-documents)
4. [Query System](#query-system)
5. [Document Management](#document-management)
6. [System Statistics](#system-statistics)
7. [Testing Scenarios](#testing-scenarios)
8. [Using Postman](#using-postman)

## Setup

### Start the Server

```bash
# Local development
python run.py

# Docker
docker-compose up -d
```

The API will be available at: `http://localhost:5000`

### Set Environment Variables (for examples)

```bash
export API_BASE_URL="http://localhost:5000"
```

## Health Check

### Check if API is Running

```bash
curl -X GET $API_BASE_URL/api/health
```

**Expected Response:**
```json
{
  "status": "healthy",
  "message": "RAG API is running"
}
```

## Upload Documents

### Upload a PDF Document

```bash
curl -X POST $API_BASE_URL/api/upload \
  -F "file=@/path/to/document.pdf"
```

**Expected Response:**
```json
{
  "message": "Document uploaded and processed successfully",
  "document": {
    "id": 1,
    "filename": "1234567890_document.pdf",
    "original_filename": "document.pdf",
    "file_size": 1024000,
    "page_count": 25,
    "chunk_count": 50,
    "upload_date": "2024-01-15T10:30:00",
    "status": "completed",
    "error_message": null
  }
}
```

### Upload a Text File

```bash
curl -X POST $API_BASE_URL/api/upload \
  -F "file=@/path/to/document.txt"
```

### Create Test Document

```bash
# Create a sample text file
cat > sample.txt << EOF
This is a sample document about artificial intelligence.

Artificial Intelligence (AI) is the simulation of human intelligence by machines.
Machine learning is a subset of AI that enables systems to learn from data.

Natural Language Processing (NLP) is a field of AI focused on language understanding.
Retrieval-Augmented Generation (RAG) combines information retrieval with text generation.

RAG systems retrieve relevant documents and use them as context for generating responses.
This approach improves accuracy and reduces hallucinations in language models.
EOF

# Upload it
curl -X POST $API_BASE_URL/api/upload \
  -F "file=@sample.txt"
```

### Error Cases

#### File Too Large
```bash
# Upload will fail if file exceeds 100MB
curl -X POST $API_BASE_URL/api/upload \
  -F "file=@large_file.pdf"
```

**Expected Error:**
```json
{
  "error": "File too large. Maximum size is 100MB"
}
```

#### Invalid File Type
```bash
curl -X POST $API_BASE_URL/api/upload \
  -F "file=@image.jpg"
```

**Expected Error:**
```json
{
  "error": "File type not allowed. Supported types: {'pdf', 'txt', 'docx', 'doc'}"
}
```

#### Document Limit Reached
```bash
# After uploading 20 documents
curl -X POST $API_BASE_URL/api/upload \
  -F "file=@document21.pdf"
```

**Expected Error:**
```json
{
  "error": "Maximum document limit (20) reached"
}
```

## Query System

### Basic Query

```bash
curl -X POST $API_BASE_URL/api/query \
  -H "Content-Type: application/json" \
  -d '{
    "question": "What is artificial intelligence?"
  }'
```

**Expected Response:**
```json
{
  "answer": "Artificial Intelligence (AI) is the simulation of human intelligence by machines, as described in the uploaded documents. It encompasses various technologies including machine learning and natural language processing.",
  "sources": [
    {
      "document_id": "1",
      "chunk_index": 0,
      "text_preview": "This is a sample document about artificial intelligence. Artificial Intelligence (AI) is the simulation of human intelligence by machines...",
      "relevance_score": 0.95
    }
  ],
  "retrieved_chunks": 5
}
```

### Query with Custom Top-K

```bash
curl -X POST $API_BASE_URL/api/query \
  -H "Content-Type: application/json" \
  -d '{
    "question": "What is RAG?",
    "top_k": 3
  }'
```

**Expected Response:**
```json
{
  "answer": "RAG stands for Retrieval-Augmented Generation. It is a system that combines information retrieval with text generation. RAG systems retrieve relevant documents and use them as context for generating responses, which improves accuracy and reduces hallucinations in language models.",
  "sources": [
    {
      "document_id": "1",
      "chunk_index": 2,
      "text_preview": "Retrieval-Augmented Generation (RAG) combines information retrieval...",
      "relevance_score": 0.98
    },
    {
      "document_id": "1",
      "chunk_index": 3,
      "text_preview": "RAG systems retrieve relevant documents and use them as context...",
      "relevance_score": 0.92
    }
  ],
  "retrieved_chunks": 3
}
```

### Query Before Uploading Documents

```bash
curl -X POST $API_BASE_URL/api/query \
  -H "Content-Type: application/json" \
  -d '{
    "question": "Test question"
  }'
```

**Expected Response:**
```json
{
  "answer": "No relevant documents found. Please upload documents first.",
  "sources": [],
  "retrieved_chunks": 0
}
```

## Document Management

### List All Documents

```bash
curl -X GET $API_BASE_URL/api/documents
```

**Expected Response:**
```json
{
  "documents": [
    {
      "id": 1,
      "filename": "1234567890_sample.txt",
      "original_filename": "sample.txt",
      "file_size": 512,
      "page_count": 1,
      "chunk_count": 3,
      "upload_date": "2024-01-15T10:30:00",
      "status": "completed",
      "error_message": null
    },
    {
      "id": 2,
      "filename": "1234567891_document.pdf",
      "original_filename": "document.pdf",
      "file_size": 2048000,
      "page_count": 50,
      "chunk_count": 125,
      "upload_date": "2024-01-15T11:00:00",
      "status": "completed",
      "error_message": null
    }
  ],
  "total": 2
}
```

### Get Specific Document

```bash
curl -X GET $API_BASE_URL/api/documents/1
```

**Expected Response:**
```json
{
  "id": 1,
  "filename": "1234567890_sample.txt",
  "original_filename": "sample.txt",
  "file_size": 512,
  "page_count": 1,
  "chunk_count": 3,
  "upload_date": "2024-01-15T10:30:00",
  "status": "completed",
  "error_message": null
}
```

### Delete Document

```bash
curl -X DELETE $API_BASE_URL/api/documents/1
```

**Expected Response:**
```json
{
  "message": "Document deleted successfully"
}
```

### Error: Document Not Found

```bash
curl -X GET $API_BASE_URL/api/documents/999
```

**Expected Response:**
```json
{
  "error": "Document not found"
}
```

## System Statistics

### Get System Stats

```bash
curl -X GET $API_BASE_URL/api/stats
```

**Expected Response:**
```json
{
  "documents": {
    "total": 5,
    "completed": 4,
    "processing": 1,
    "failed": 0
  },
  "vector_store": {
    "total_chunks": 250,
    "collection_name": "documents"
  },
  "limits": {
    "max_documents": 20,
    "max_pages_per_document": 1000
  }
}
```

## Testing Scenarios

### Scenario 1: Complete Workflow

```bash
# 1. Check health
curl -X GET $API_BASE_URL/api/health

# 2. Upload document
curl -X POST $API_BASE_URL/api/upload \
  -F "file=@sample.txt"

# 3. List documents
curl -X GET $API_BASE_URL/api/documents

# 4. Query the system
curl -X POST $API_BASE_URL/api/query \
  -H "Content-Type: application/json" \
  -d '{"question": "What is AI?"}'

# 5. Get stats
curl -X GET $API_BASE_URL/api/stats

# 6. Delete document
curl -X DELETE $API_BASE_URL/api/documents/1
```

### Scenario 2: Multiple Documents

```bash
# Upload multiple documents
for i in {1..5}; do
  echo "Document $i content about topic $i" > doc$i.txt
  curl -X POST $API_BASE_URL/api/upload -F "file=@doc$i.txt"
  sleep 1
done

# Query across all documents
curl -X POST $API_BASE_URL/api/query \
  -H "Content-Type: application/json" \
  -d '{"question": "What topics are covered?"}'
```

### Scenario 3: Error Handling

```bash
# Test invalid request
curl -X POST $API_BASE_URL/api/query \
  -H "Content-Type: application/json" \
  -d '{}'

# Test missing file
curl -X POST $API_BASE_URL/api/upload

# Test non-existent document
curl -X GET $API_BASE_URL/api/documents/9999
```

### Scenario 4: Performance Testing

```bash
# Upload large document
curl -X POST $API_BASE_URL/api/upload \
  -F "file=@large_document.pdf"

# Query with different top_k values
for k in 3 5 10 20; do
  echo "Testing with top_k=$k"
  time curl -X POST $API_BASE_URL/api/query \
    -H "Content-Type: application/json" \
    -d "{\"question\": \"What is the summary?\", \"top_k\": $k}"
done
```

## Using Postman

### Import Collection

1. Open Postman
2. Click **Import**
3. Select `postman_collection.json`
4. Collection will appear in the sidebar

### Set Environment Variables

1. Click **Environments** (gear icon)
2. Create new environment "RAG API Local"
3. Add variable:
   - Key: `base_url`
   - Value: `http://localhost:5000`
4. Save and select environment

### Run Tests

1. Select a request from the collection
2. Click **Send**
3. View response in the lower panel

### Create Test Scripts

Add to request **Tests** tab:

```javascript
// Test: Health Check
pm.test("Status is healthy", function () {
    var jsonData = pm.response.json();
    pm.expect(jsonData.status).to.eql("healthy");
});

// Test: Upload Document
pm.test("Document uploaded successfully", function () {
    var jsonData = pm.response.json();
    pm.expect(jsonData.message).to.include("successfully");
    pm.environment.set("document_id", jsonData.document.id);
});

// Test: Query Response
pm.test("Answer is provided", function () {
    var jsonData = pm.response.json();
    pm.expect(jsonData.answer).to.exist;
    pm.expect(jsonData.answer.length).to.be.above(0);
});
```

### Collection Runner

1. Click **Runner** button
2. Select "RAG API" collection
3. Select environment
4. Click **Run RAG API**
5. View results

## Advanced Testing

### Using Python Requests

```python
import requests

BASE_URL = "http://localhost:5000/api"

# Upload document
with open('sample.txt', 'rb') as f:
    response = requests.post(
        f"{BASE_URL}/upload",
        files={'file': f}
    )
    print(response.json())

# Query
response = requests.post(
    f"{BASE_URL}/query",
    json={'question': 'What is AI?', 'top_k': 5}
)
print(response.json())

# List documents
response = requests.get(f"{BASE_URL}/documents")
print(response.json())
```

### Using JavaScript/Node.js

```javascript
const axios = require('axios');
const FormData = require('form-data');
const fs = require('fs');

const BASE_URL = 'http://localhost:5000/api';

// Upload document
async function uploadDocument() {
  const form = new FormData();
  form.append('file', fs.createReadStream('sample.txt'));
  
  const response = await axios.post(`${BASE_URL}/upload`, form, {
    headers: form.getHeaders()
  });
  
  console.log(response.data);
}

// Query
async function query() {
  const response = await axios.post(`${BASE_URL}/query`, {
    question: 'What is AI?',
    top_k: 5
  });
  
  console.log(response.data);
}

// Run
uploadDocument().then(query);
```

### Load Testing with Apache Bench

```bash
# Test query endpoint
ab -n 100 -c 10 \
  -p query.json \
  -T "application/json" \
  http://localhost:5000/api/query

# query.json content:
# {"question": "What is AI?"}
```

### Integration Testing Script

```bash
#!/bin/bash
# test_api.sh

API_BASE="http://localhost:5000/api"

echo "Testing RAG API..."

# Health check
echo "1. Health check..."
curl -s $API_BASE/health | jq .

# Upload
echo "2. Uploading document..."
UPLOAD_RESPONSE=$(curl -s -X POST $API_BASE/upload -F "file=@sample.txt")
echo $UPLOAD_RESPONSE | jq .
DOC_ID=$(echo $UPLOAD_RESPONSE | jq -r '.document.id')

# Query
echo "3. Querying..."
curl -s -X POST $API_BASE/query \
  -H "Content-Type: application/json" \
  -d '{"question": "What is AI?"}' | jq .

# Stats
echo "4. Getting stats..."
curl -s $API_BASE/stats | jq .

# Delete
echo "5. Deleting document..."
curl -s -X DELETE $API_BASE/documents/$DOC_ID | jq .

echo "Testing complete!"
```

## Troubleshooting

### API Not Responding

```bash
# Check if server is running
curl -I http://localhost:5000/api/health

# Check logs
docker-compose logs rag-api

# Check port
lsof -i :5000
```

### Upload Failing

```bash
# Verify file exists
ls -lh /path/to/file

# Check file type
file /path/to/file.pdf

# Test with small file first
echo "test" > test.txt
curl -X POST $API_BASE_URL/api/upload -F "file=@test.txt"
```

### Query Returning No Results

```bash
# Verify documents are uploaded
curl $API_BASE_URL/api/documents

# Check stats
curl $API_BASE_URL/api/stats

# Try simpler query
curl -X POST $API_BASE_URL/api/query \
  -H "Content-Type: application/json" \
  -d '{"question": "test"}'
```