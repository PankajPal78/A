# Quick Start Guide

Get the RAG Document Q&A system running in minutes!

## 🚀 Fastest Way to Start (Docker)

### Prerequisites
- Docker and Docker Compose installed
- A Gemini API key ([Get free key](https://makersuite.google.com/app/apikey))

### Steps

```bash
# 1. Clone the repository
git clone <repository-url>
cd rag-document-qa

# 2. Set up environment
cp .env.example .env
echo "GEMINI_API_KEY=your_actual_api_key_here" >> .env

# 3. Start the system
docker-compose up -d

# 4. Wait for startup (30 seconds)
sleep 30

# 5. Test the API
curl http://localhost:5000/api/health
```

**Expected output:**
```json
{"status": "healthy", "message": "RAG API is running"}
```

## 📝 Try Your First Query

### 1. Create a test document

```bash
cat > sample.txt << 'EOF'
Artificial Intelligence Overview

Artificial Intelligence (AI) is the simulation of human intelligence 
processes by machines, especially computer systems. These processes 
include learning, reasoning, and self-correction.

Machine Learning is a subset of AI that provides systems the ability 
to automatically learn and improve from experience without being 
explicitly programmed.

Natural Language Processing (NLP) is a branch of AI that helps 
computers understand, interpret and manipulate human language.

Retrieval-Augmented Generation (RAG) is a technique that enhances 
language models by retrieving relevant information from a knowledge 
base before generating responses.
EOF
```

### 2. Upload the document

```bash
curl -X POST http://localhost:5000/api/upload \
  -F "file=@sample.txt"
```

**Expected output:**
```json
{
  "message": "Document uploaded and processed successfully",
  "document": {
    "id": 1,
    "filename": "sample.txt",
    "page_count": 1,
    "chunk_count": 2,
    "status": "completed"
  }
}
```

### 3. Ask a question

```bash
curl -X POST http://localhost:5000/api/query \
  -H "Content-Type: application/json" \
  -d '{"question": "What is RAG?"}'
```

**Expected output:**
```json
{
  "answer": "Retrieval-Augmented Generation (RAG) is a technique that enhances language models by retrieving relevant information from a knowledge base before generating responses.",
  "sources": [...],
  "retrieved_chunks": 5
}
```

### 4. View all documents

```bash
curl http://localhost:5000/api/documents
```

## 🐍 Local Python Setup (Alternative)

### Prerequisites
- Python 3.9 or higher
- pip
- A Gemini API key

### Steps

```bash
# 1. Clone and navigate
git clone <repository-url>
cd rag-document-qa

# 2. Run setup script
chmod +x setup.sh
./setup.sh

# 3. Configure API key
echo "GEMINI_API_KEY=your_actual_api_key_here" >> .env

# 4. Activate virtual environment
source venv/bin/activate  # On Windows: venv\Scripts\activate

# 5. Start the server
python run.py
```

The server will start at `http://localhost:5000`

## 🎯 Common Tasks

### Upload a PDF

```bash
curl -X POST http://localhost:5000/api/upload \
  -F "file=@/path/to/your/document.pdf"
```

### Ask Multiple Questions

```bash
# Question 1
curl -X POST http://localhost:5000/api/query \
  -H "Content-Type: application/json" \
  -d '{"question": "What is machine learning?"}'

# Question 2
curl -X POST http://localhost:5000/api/query \
  -H "Content-Type: application/json" \
  -d '{"question": "How does NLP work?"}'
```

### Delete a Document

```bash
# Get document ID first
curl http://localhost:5000/api/documents

# Delete by ID
curl -X DELETE http://localhost:5000/api/documents/1
```

### Check System Statistics

```bash
curl http://localhost:5000/api/stats
```

## 🔧 Using Different LLM Providers

### Switch to OpenAI

```bash
# Edit .env file
LLM_PROVIDER=openai
OPENAI_API_KEY=sk-your-openai-key

# Restart
docker-compose restart
```

### Use Local Ollama

```bash
# 1. Uncomment ollama service in docker-compose.yml

# 2. Edit .env
LLM_PROVIDER=ollama
OLLAMA_BASE_URL=http://ollama:11434
OLLAMA_MODEL=llama2

# 3. Start services
docker-compose up -d

# 4. Pull model (first time only)
docker-compose exec ollama ollama pull llama2
```

## 🧪 Run Tests

### Using Docker

```bash
docker-compose exec rag-api pytest -v
```

### Using Local Python

```bash
source venv/bin/activate
pytest -v
```

## 📱 Use Postman

1. Import `postman_collection.json` into Postman
2. Set base_url variable to `http://localhost:5000`
3. Run the "Health Check" request
4. Try other requests in the collection

## 🌐 Access from Browser

### Health Check
Open in browser: http://localhost:5000/api/health

### API Documentation
See `API_TESTING_GUIDE.md` for complete endpoint documentation

## 🛠️ Troubleshooting

### Problem: Container won't start

```bash
# Check logs
docker-compose logs rag-api

# Common fix: Rebuild
docker-compose down
docker-compose up -d --build
```

### Problem: "GEMINI_API_KEY not configured"

```bash
# Verify .env file exists
cat .env | grep GEMINI_API_KEY

# Should show your key (not empty)
# If empty, add it:
echo "GEMINI_API_KEY=your_key_here" >> .env

# Restart
docker-compose restart
```

### Problem: Upload fails

```bash
# Check file size (max 100MB)
ls -lh your-file.pdf

# Check file type (must be PDF or TXT)
file your-file.pdf

# Try with a small test file first
echo "test content" > test.txt
curl -X POST http://localhost:5000/api/upload -F "file=@test.txt"
```

### Problem: Port 5000 already in use

```bash
# Option 1: Stop other service using port 5000
lsof -ti:5000 | xargs kill -9

# Option 2: Use different port
# Edit docker-compose.yml, change ports:
# - "5001:5000"
```

## 📚 Next Steps

1. **Read Full Documentation**: Check `README.md` for detailed information
2. **API Testing**: See `API_TESTING_GUIDE.md` for all endpoints
3. **Architecture**: Read `ARCHITECTURE.md` to understand the system
4. **Deployment**: Check `DEPLOYMENT_GUIDE.md` for cloud deployment

## 🎓 Example Use Cases

### Academic Research
```bash
# Upload research papers
curl -X POST http://localhost:5000/api/upload -F "file=@paper1.pdf"
curl -X POST http://localhost:5000/api/upload -F "file=@paper2.pdf"

# Ask research questions
curl -X POST http://localhost:5000/api/query \
  -H "Content-Type: application/json" \
  -d '{"question": "What are the key findings about neural networks?"}'
```

### Legal Documents
```bash
# Upload contracts
curl -X POST http://localhost:5000/api/upload -F "file=@contract.pdf"

# Query clauses
curl -X POST http://localhost:5000/api/query \
  -H "Content-Type: application/json" \
  -d '{"question": "What are the payment terms?"}'
```

### Technical Documentation
```bash
# Upload API docs
curl -X POST http://localhost:5000/api/upload -F "file=@api-guide.pdf"

# Ask how-to questions
curl -X POST http://localhost:5000/api/query \
  -H "Content-Type: application/json" \
  -d '{"question": "How do I authenticate with the API?"}'
```

## 💡 Pro Tips

1. **Chunk Size**: Adjust `CHUNK_SIZE` in `.env` for better results
   - Smaller (500-800): Better for specific facts
   - Larger (1200-1500): Better for context

2. **Retrieval Count**: Use `top_k` parameter in queries
   ```bash
   curl -X POST http://localhost:5000/api/query \
     -H "Content-Type: application/json" \
     -d '{"question": "...", "top_k": 10}'
   ```

3. **Multiple Documents**: Upload related documents together for better cross-referencing

4. **Descriptive Questions**: More specific questions get better answers
   - ❌ "Tell me about this"
   - ✅ "What are the security features described in the document?"

## 🚀 Ready for Production?

See `DEPLOYMENT_GUIDE.md` for:
- AWS deployment
- Google Cloud deployment
- Azure deployment
- Kubernetes setup
- Monitoring and logging

## 🤝 Need Help?

- **Issues**: Open an issue on GitHub
- **Documentation**: Check the `/docs` folder
- **Examples**: See `API_TESTING_GUIDE.md`

---

**Happy querying! 🎉**