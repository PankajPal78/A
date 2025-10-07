# Postman Collection for RAG Document Q&A System

This directory contains Postman collections and environments for testing the RAG Document Q&A System API.

## Files

- `RAG_Document_QA_System.postman_collection.json` - Main API collection with all endpoints
- `RAG_Environment.postman_environment.json` - Environment variables for the collection

## Setup Instructions

### 1. Import Collection and Environment

1. Open Postman
2. Click "Import" button
3. Select both JSON files from this directory
4. The collection and environment will be imported

### 2. Set Environment

1. In Postman, select the "RAG Document Q&A Environment" from the environment dropdown
2. Verify the `base_url` is set to your server URL (default: `http://localhost:5000/api`)

### 3. Start the Server

Make sure your RAG system is running:

```bash
# Using Docker
docker-compose up -d

# Or manually
python app.py
```

## Collection Structure

### Health Checks
- **Basic Health Check**: Test if the system is running
- **System Status**: Get detailed system status and component health

### Document Management
- **Upload Document**: Upload PDF, DOCX, or TXT files
- **List Documents**: Get paginated list of all documents
- **Get Document by ID**: Retrieve specific document details
- **Get Document Chunks**: View all chunks for a document
- **Delete Document**: Remove document and its chunks
- **Document Statistics**: Get collection statistics

### Query Processing
- **Process Query**: Send questions to the RAG pipeline
- **Process Query with Parameters**: Query with specific documents and settings
- **Search Documents**: Find relevant chunks without generating answers
- **Get Query History**: View recent queries and responses
- **Get Query Statistics**: Performance metrics and statistics

### Configuration
- **Get Pipeline Configuration**: View current RAG settings
- **Update Pipeline Configuration**: Modify retrieval parameters

## Usage Examples

### 1. Complete Workflow Test

1. **Check System Health**
   - Run "Basic Health Check"
   - Run "System Status" to verify all components

2. **Upload a Document**
   - Use "Upload Document" endpoint
   - Select a PDF, DOCX, or TXT file
   - Note the document ID from the response

3. **Verify Document Processing**
   - Use "List Documents" to see your uploaded document
   - Check that status is "processed"
   - Use "Get Document Chunks" to view the text chunks

4. **Query the System**
   - Use "Process Query" with a question about your document
   - Review the response with answer and sources

5. **View Analytics**
   - Use "Get Query History" to see your queries
   - Use "Get Query Statistics" for performance metrics

### 2. Testing Different Query Parameters

Use "Process Query with Parameters" to test:
- `document_ids`: Query specific documents only
- `top_k`: Number of chunks to retrieve (1-20)
- `similarity_threshold`: Minimum similarity score (0.0-1.0)

Example request body:
```json
{
  "query": "What is machine learning?",
  "document_ids": [1, 2],
  "top_k": 3,
  "similarity_threshold": 0.8
}
```

### 3. Configuration Testing

1. **Get Current Config**
   - Run "Get Pipeline Configuration"
   - Note current `top_k` and `similarity_threshold`

2. **Update Configuration**
   - Use "Update Pipeline Configuration"
   - Try different values and test query performance

## Environment Variables

The environment includes these variables that you can modify:

- `base_url`: API base URL (default: http://localhost:5000/api)
- `document_id`: Document ID for testing (default: 1)
- `query_text`: Sample query text

## Automated Tests

The collection includes basic automated tests:
- Response time validation (< 5 seconds)
- Status code verification
- JSON response format validation

## Error Testing

Test error scenarios:
- Upload invalid file types
- Query non-existent documents
- Send malformed JSON requests
- Test with missing API keys

## Tips

1. **File Upload**: When testing document upload, use small files first (< 1MB)
2. **API Keys**: Ensure your `.env` file has valid API keys for LLM providers
3. **Timeouts**: Some operations (document processing, first queries) may take longer
4. **Pagination**: Use page and per_page parameters for large document collections
5. **Error Handling**: Check error responses for debugging information

## Troubleshooting

### Common Issues

1. **Connection Refused**
   - Verify the server is running
   - Check the base_url in environment

2. **500 Internal Server Error**
   - Check server logs
   - Verify API keys are configured
   - Ensure required directories exist

3. **Document Upload Fails**
   - Check file size (max 100MB)
   - Verify file type (PDF, DOCX, TXT only)
   - Check available disk space

4. **Query Fails**
   - Ensure documents are processed (status: "processed")
   - Check if vector database is initialized
   - Verify LLM API keys are valid

### Debug Steps

1. Start with health check endpoints
2. Check system status for component issues
3. Test with small documents first
4. Use search endpoint before full queries
5. Review query history for patterns

## Support

For issues with the Postman collection:
1. Check the main project README
2. Verify your environment setup
3. Test endpoints individually
4. Check server logs for detailed errors