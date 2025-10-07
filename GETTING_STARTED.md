# 🚀 Getting Started - Choose Your Path

Welcome to the RAG Document Q&A System! Choose your path based on your goal:

## 🎯 I Want to Try It NOW (5 minutes)

**Best for**: Quick demo, first-time users

```bash
# 1. Start with Docker
docker-compose up -d

# 2. Create test document
cat > test.txt << 'TXT'
Artificial Intelligence is the simulation of human intelligence by machines.
Machine Learning is a subset of AI that learns from data.
RAG combines retrieval with generation for better answers.
TXT

# 3. Upload it
curl -X POST http://localhost:5000/api/upload -F "file=@test.txt"

# 4. Ask a question
curl -X POST http://localhost:5000/api/query \
  -H "Content-Type: application/json" \
  -d '{"question": "What is RAG?"}'
```

**Note**: You'll need to add your API key to `.env` first!

📖 **Next**: Read [QUICKSTART.md](QUICKSTART.md)

---

## 👨‍💻 I Want to Develop/Customize (1 hour)

**Best for**: Developers who want to understand and modify the code

```bash
# 1. Setup environment
./setup.sh
source venv/bin/activate

# 2. Configure
cp .env.example .env
# Edit .env with your API keys

# 3. Run tests
pytest -v

# 4. Start development server
python run.py

# 5. Explore the code
ls app/  # See all modules
```

📖 **Next**: Read [README.md](README.md) and [ARCHITECTURE.md](ARCHITECTURE.md)

---

## 🚢 I Want to Deploy to Production (2-4 hours)

**Best for**: DevOps engineers deploying to cloud

### AWS
```bash
# See DEPLOYMENT_GUIDE.md for complete steps
# Quick: EC2 with Docker
ssh ec2-user@your-instance
git clone <repo>
docker-compose up -d
```

### Google Cloud
```bash
gcloud builds submit --tag gcr.io/PROJECT/rag-api
gcloud run deploy rag-api --image gcr.io/PROJECT/rag-api
```

### Azure
```bash
az container create --resource-group rag-rg --name rag-api \
  --image your-registry/rag-api:latest
```

📖 **Next**: Read [DEPLOYMENT_GUIDE.md](DEPLOYMENT_GUIDE.md)

---

## 📚 I Want to Understand How It Works (1-2 hours)

**Best for**: Learning RAG systems, architects

**Reading order**:
1. [SUMMARY.md](SUMMARY.md) - High-level overview
2. [ARCHITECTURE.md](ARCHITECTURE.md) - System design
3. [PROJECT_STRUCTURE.md](PROJECT_STRUCTURE.md) - Code organization
4. Explore `app/rag_pipeline.py` - Core RAG logic

📖 **Start with**: [ARCHITECTURE.md](ARCHITECTURE.md)

---

## 🧪 I Want to Test the API (30 minutes)

**Best for**: API integration, testing endpoints

### With cURL
```bash
# Health check
curl http://localhost:5000/api/health

# Upload
curl -X POST http://localhost:5000/api/upload -F "file=@doc.pdf"

# Query
curl -X POST http://localhost:5000/api/query \
  -H "Content-Type: application/json" \
  -d '{"question": "Summary?"}'
```

### With Postman
1. Import `postman_collection.json`
2. Set `base_url` to `http://localhost:5000`
3. Try all endpoints

📖 **Next**: Read [API_TESTING_GUIDE.md](API_TESTING_GUIDE.md)

---

## 🎓 I Want to Learn RAG Concepts (Educational)

**Best for**: Students, researchers

**Hands-on learning path**:

1. **Understand the basics**
   - Read: What is RAG? (in README.md)
   - Read: Architecture overview (ARCHITECTURE.md)

2. **See it in action**
   - Start the system
   - Upload a document
   - Ask questions
   - Check sources in response

3. **Explore the code**
   - `app/document_processor.py` - See chunking
   - `app/vector_store.py` - See embeddings
   - `app/rag_pipeline.py` - See RAG logic
   - `app/llm_provider.py` - See LLM integration

4. **Experiment**
   - Change chunk size
   - Try different LLM providers
   - Test with different documents

📖 **Resources**: All `.md` files in this repo

---

## 🔧 Common First Tasks

### Configure LLM Provider

**Gemini (Free, Recommended)**:
```bash
echo "LLM_PROVIDER=gemini" >> .env
echo "GEMINI_API_KEY=your_key" >> .env
```
Get key: https://makersuite.google.com/app/apikey

**OpenAI**:
```bash
echo "LLM_PROVIDER=openai" >> .env
echo "OPENAI_API_KEY=sk-..." >> .env
```

**Ollama (Local)**:
```bash
echo "LLM_PROVIDER=ollama" >> .env
# Uncomment ollama service in docker-compose.yml
docker-compose up -d
docker-compose exec ollama ollama pull llama2
```

### Run Your First Query

```bash
# 1. Check it's running
curl http://localhost:5000/api/health

# 2. Upload a document
curl -X POST http://localhost:5000/api/upload \
  -F "file=@your-document.pdf"

# 3. Ask a question
curl -X POST http://localhost:5000/api/query \
  -H "Content-Type: application/json" \
  -d '{
    "question": "What are the main points?",
    "top_k": 5
  }'
```

### View All Documents

```bash
curl http://localhost:5000/api/documents | jq
```

### Check System Stats

```bash
curl http://localhost:5000/api/stats | jq
```

---

## 📖 Documentation Guide

**Too many docs? Start here based on your role:**

### For Developers
1. **README.md** - Complete overview
2. **PROJECT_STRUCTURE.md** - Navigate the code
3. **ARCHITECTURE.md** - Understand design

### For DevOps
1. **QUICKSTART.md** - Fast setup
2. **DEPLOYMENT_GUIDE.md** - Production deployment
3. **docker-compose.yml** - Service config

### For API Users
1. **QUICKSTART.md** - Get started
2. **API_TESTING_GUIDE.md** - All endpoints
3. **postman_collection.json** - Import & test

### For Managers/PMs
1. **SUMMARY.md** - Project overview
2. **PROJECT_COMPLETION_REPORT.md** - Status & metrics
3. **ARCHITECTURE.md** - Scalability section

---

## 🆘 Quick Troubleshooting

### "Connection refused"
```bash
# Check if running
docker-compose ps
# Start if needed
docker-compose up -d
```

### "GEMINI_API_KEY not configured"
```bash
# Add to .env
echo "GEMINI_API_KEY=your_key_here" >> .env
docker-compose restart
```

### "File upload fails"
```bash
# Check file size (max 100MB)
ls -lh your-file.pdf
# Check file type (must be PDF or TXT)
file your-file.pdf
```

### "Port 5000 in use"
```bash
# Option 1: Stop other service
lsof -ti:5000 | xargs kill -9
# Option 2: Change port in docker-compose.yml
```

---

## 🎯 Success Indicators

You'll know it's working when:

✅ Health check returns `{"status": "healthy"}`
✅ Document upload returns success with chunk count
✅ Query returns an answer with sources
✅ Stats show your uploaded documents

---

## 📞 Need Help?

1. **Check documentation**: [INDEX.md](INDEX.md) - Navigate all docs
2. **Common issues**: Each guide has troubleshooting
3. **Examples**: [API_TESTING_GUIDE.md](API_TESTING_GUIDE.md)

---

## 🎉 Ready? Pick Your Path Above!

**Most Popular Starting Points**:
- 🚀 Quick Demo → Docker + QUICKSTART.md
- 👨‍💻 Development → setup.sh + README.md  
- 🚢 Production → DEPLOYMENT_GUIDE.md
- 📚 Learning → ARCHITECTURE.md

**Not sure?** Start with [QUICKSTART.md](QUICKSTART.md) - it's designed for everyone!

---

*Built with ❤️ - Ready for development, testing, and production use*
