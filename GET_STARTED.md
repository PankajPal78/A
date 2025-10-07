# 🚀 Get Started - RAG Document Q&A System

## Welcome! 👋

You now have a complete, production-ready RAG (Retrieval-Augmented Generation) system for document question-answering!

---

## ⚡ Quick Start (5 Minutes)

### Step 1: Get an API Key

Get a free Google Gemini API key:
👉 https://makersuite.google.com/app/apikey

### Step 2: Configure

```bash
# Edit the .env file
nano .env

# Add your API key (replace the empty value):
GEMINI_API_KEY=your_actual_api_key_here
```

### Step 3: Run with Docker (Recommended)

```bash
# Start the application
docker-compose up --build

# Wait for: "Running on http://0.0.0.0:5000"
```

### Step 4: Test It!

Open a new terminal:

```bash
# Check if it's running
curl http://localhost:5000/api/health

# Upload a document
curl -X POST http://localhost:5000/api/documents \
  -F "file=@your_document.pdf"

# Ask a question
curl -X POST http://localhost:5000/api/query \
  -H "Content-Type: application/json" \
  -d '{"question": "What is this document about?"}'
```

**That's it! You're now running a RAG system! 🎉**

---

## 📚 What You Can Do

### 1. Upload Documents
- PDF files (up to 1000 pages)
- TXT files
- Up to 20 documents total

### 2. Ask Questions
- Questions about specific documents
- Questions across all documents
- Get AI-powered answers with sources

### 3. Manage Documents
- View all documents
- Check processing status
- Delete documents
- View system statistics

---

## 🎯 Example Usage

### Upload Multiple Documents

```bash
curl -X POST http://localhost:5000/api/documents -F "file=@research_paper.pdf"
curl -X POST http://localhost:5000/api/documents -F "file=@thesis.pdf"
curl -X POST http://localhost:5000/api/documents -F "file=@notes.txt"
```

### Ask Questions

```bash
# General question
curl -X POST http://localhost:5000/api/query \
  -H "Content-Type: application/json" \
  -d '{"question": "What are the main findings?"}'

# Query specific document (ID: 1)
curl -X POST http://localhost:5000/api/query \
  -H "Content-Type: application/json" \
  -d '{"question": "Summarize this document", "document_id": 1}'
```

### View Documents

```bash
# List all documents
curl http://localhost:5000/api/documents

# View specific document
curl http://localhost:5000/api/documents/1

# Get statistics
curl http://localhost:5000/api/stats
```

---

## 🛠️ Alternative: Run Without Docker

If you prefer to run without Docker:

```bash
# 1. Create virtual environment
python -m venv venv
source venv/bin/activate  # Windows: venv\Scripts\activate

# 2. Install dependencies
pip install -r requirements.txt

# 3. Run the app
python app.py
```

---

## 📖 Documentation

Choose your path:

### For Quick Testing
👉 Use the **Postman Collection**: `postman_collection.json`
- Import into Postman
- Set base_url to `http://localhost:5000`
- Try all endpoints with one click

### For Code Examples
👉 Run the **Example Script**: `python example_usage.py`
- Interactive demonstration
- Shows all API features
- Copy-paste ready code

### For Full Documentation
👉 Read **README.md**
- Complete API reference
- Configuration options
- Troubleshooting guide
- Architecture details

### For Deployment
👉 Read **DEPLOYMENT.md**
- AWS deployment
- Google Cloud deployment
- Azure deployment
- Production tips

---

## 🧪 Running Tests

```bash
# Run all tests
./run_tests.sh

# Or with Docker
docker-compose exec rag-api pytest app/tests/ -v
```

---

## 🔧 Configuration Options

Edit `.env` to customize:

```env
# LLM Settings
LLM_PROVIDER=gemini          # or 'openai'
GEMINI_API_KEY=your_key
LLM_TEMPERATURE=0.7          # 0.0-1.0 (higher = more creative)
LLM_MAX_TOKENS=1000          # Max response length

# Document Settings
MAX_DOCUMENTS=20             # Maximum documents
MAX_PAGES_PER_DOCUMENT=1000  # Max pages per doc
CHUNK_SIZE=1000              # Text chunk size
CHUNK_OVERLAP=200            # Chunk overlap

# Retrieval Settings
TOP_K_RESULTS=5              # Number of chunks to retrieve
```

---

## 📊 Project Structure

```
rag-document-qa/
├── app/                     # Application code
│   ├── api/                # API endpoints
│   ├── services/           # Business logic
│   ├── models/             # Database models
│   ├── utils/              # Utilities
│   └── tests/              # Test suite
├── config/                  # Configuration
├── data/                    # Data storage
├── Dockerfile              # Container definition
├── docker-compose.yml      # Service orchestration
├── requirements.txt        # Dependencies
├── README.md               # Full documentation
├── QUICKSTART.md          # Quick start guide
├── DEPLOYMENT.md          # Deployment guide
└── postman_collection.json # API tests
```

---

## ❓ Common Questions

### Q: How do I stop the application?
```bash
docker-compose down
```

### Q: How do I view logs?
```bash
docker-compose logs -f
```

### Q: How do I reset everything?
```bash
docker-compose down -v
rm -rf data/uploads/* data/vector_db/* data/metadata/*
```

### Q: Can I use OpenAI instead of Gemini?
Yes! Just set in `.env`:
```env
LLM_PROVIDER=openai
OPENAI_API_KEY=your_openai_key
```

### Q: How do I deploy to production?
See `DEPLOYMENT.md` for detailed guides for AWS, GCP, and Azure.

---

## 🎓 Learn More

| Topic | File | Description |
|-------|------|-------------|
| Getting Started | `QUICKSTART.md` | 5-minute setup guide |
| Full Documentation | `README.md` | Complete reference |
| Deployment | `DEPLOYMENT.md` | Cloud deployment |
| API Testing | `postman_collection.json` | Postman collection |
| Code Examples | `example_usage.py` | Usage examples |
| Contributing | `CONTRIBUTING.md` | Development guide |
| Project Overview | `PROJECT_SUMMARY.md` | Architecture & design |

---

## 🆘 Need Help?

1. **Check the logs**: `docker-compose logs -f`
2. **Verify setup**: `./verify_setup.sh`
3. **Read troubleshooting**: See README.md → Troubleshooting
4. **Check configuration**: Make sure API key is set in `.env`

---

## 🎉 What's Included

✅ **Complete RAG Pipeline**
- Document upload & processing
- Vector-based search
- AI-powered Q&A
- Source attribution

✅ **Production Ready**
- Docker containerization
- Cloud deployment guides
- Health monitoring
- Error handling

✅ **Developer Friendly**
- Comprehensive tests
- API documentation
- Code examples
- Postman collection

✅ **Well Documented**
- 6 documentation files
- Setup scripts
- Usage examples
- Troubleshooting guides

---

## 🚀 Next Steps

1. ✅ Start the application
2. ✅ Upload your first document
3. ✅ Ask a question
4. ✅ Explore the API
5. ✅ Read the documentation
6. ✅ Deploy to production

---

## 📞 Resources

- **API Endpoint**: http://localhost:5000
- **Health Check**: http://localhost:5000/api/health
- **Documentation**: README.md
- **Examples**: example_usage.py
- **Tests**: run_tests.sh

---

**Ready to build amazing document Q&A applications! 🎊**

For detailed information, see `README.md`