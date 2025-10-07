# Quick Start Guide

Get the RAG Document Q&A System up and running in 5 minutes!

## Prerequisites

- Docker & Docker Compose installed
- Google Gemini API key (get one [here](https://makersuite.google.com/app/apikey))

## Setup Steps

### 1. Clone & Setup

```bash
# Clone the repository
git clone <repository-url>
cd rag-document-qa

# Run setup script
chmod +x setup.sh
./setup.sh
```

### 2. Configure API Key

Edit the `.env` file and add your Gemini API key:

```bash
nano .env
```

Change this line:
```env
GEMINI_API_KEY=your_gemini_api_key_here
```

To:
```env
GEMINI_API_KEY=your_actual_api_key
```

Save and exit (Ctrl+X, then Y, then Enter)

### 3. Start the Application

```bash
docker-compose up --build
```

Wait for the message: `Running on http://0.0.0.0:5000`

### 4. Test the API

Open a new terminal and try these commands:

#### Check Health
```bash
curl http://localhost:5000/api/health
```

#### Upload a Document
```bash
curl -X POST http://localhost:5000/api/documents \
  -F "file=@/path/to/your/document.pdf"
```

#### Ask a Question
```bash
curl -X POST http://localhost:5000/api/query \
  -H "Content-Type: application/json" \
  -d '{"question": "What is this document about?"}'
```

## Usage Examples

### Example 1: Upload and Query a Research Paper

```bash
# 1. Upload the paper
curl -X POST http://localhost:5000/api/documents \
  -F "file=@research_paper.pdf"

# Response will include document ID, e.g., "id": 1

# 2. Ask questions about it
curl -X POST http://localhost:5000/api/query \
  -H "Content-Type: application/json" \
  -d '{
    "question": "What are the main findings?",
    "document_id": 1
  }'
```

### Example 2: Multiple Documents

```bash
# Upload multiple documents
curl -X POST http://localhost:5000/api/documents -F "file=@doc1.pdf"
curl -X POST http://localhost:5000/api/documents -F "file=@doc2.pdf"
curl -X POST http://localhost:5000/api/documents -F "file=@doc3.pdf"

# Query across all documents
curl -X POST http://localhost:5000/api/query \
  -H "Content-Type: application/json" \
  -d '{"question": "What are common themes across all documents?"}'
```

### Example 3: View System Stats

```bash
curl http://localhost:5000/api/stats
```

## Using Postman

1. Import the Postman collection:
   - Open Postman
   - Click Import
   - Select `postman_collection.json`

2. Set the base URL:
   - Go to Variables tab
   - Set `base_url` to `http://localhost:5000`

3. Try the requests in this order:
   - Health Check
   - Upload Document
   - Query Documents
   - Get Statistics

## Web Browser Testing

You can also test in your browser:

1. **Health Check**
   - Open: http://localhost:5000/api/health

2. **API Info**
   - Open: http://localhost:5000/

3. **View Documents**
   - Open: http://localhost:5000/api/documents

4. **View Stats**
   - Open: http://localhost:5000/api/stats

## Next Steps

- Read the full [README.md](README.md) for detailed documentation
- Check [DEPLOYMENT.md](DEPLOYMENT.md) for cloud deployment
- Review the API endpoints in detail
- Customize settings in `.env`

## Common Issues

### Issue: "Connection refused"
**Solution:** Make sure Docker is running and the container is started
```bash
docker-compose up
```

### Issue: "API key not configured"
**Solution:** Check your `.env` file has the correct API key
```bash
cat .env | grep GEMINI_API_KEY
```

### Issue: "Out of memory"
**Solution:** Increase Docker memory in Docker Desktop settings (minimum 4GB recommended)

### Issue: "Document processing failed"
**Solution:** Check if the document is a valid PDF or TXT file under 100MB

## Stopping the Application

```bash
# Stop the containers
docker-compose down

# Stop and remove all data
docker-compose down -v
```

## Need Help?

- Check the logs: `docker-compose logs -f`
- Read the [README.md](README.md)
- Review [DEPLOYMENT.md](DEPLOYMENT.md)
- Open an issue on GitHub

---

**You're all set! Start uploading documents and asking questions! 🚀**