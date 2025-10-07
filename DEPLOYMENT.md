# Deployment Guide

This guide covers different deployment options for the RAG Document Q&A System.

## 🐳 Docker Deployment (Recommended)

### Prerequisites
- Docker and Docker Compose installed
- Google Gemini API key

### Steps

1. **Clone and configure**:
   ```bash
   git clone <repository-url>
   cd rag-document-qa-system
   cp .env.example .env
   # Edit .env and add your GEMINI_API_KEY
   ```

2. **Deploy with Docker Compose**:
   ```bash
   # Build and start services
   docker-compose up --build -d
   
   # Check logs
   docker-compose logs -f rag-app
   
   # Stop services
   docker-compose down
   ```

3. **Access the application**:
   - Web Interface: http://localhost:5000
   - API: http://localhost:5000/api/

## ☁️ Cloud Deployment

### AWS EC2

1. **Launch EC2 instance**:
   - Instance type: t3.medium or larger
   - OS: Ubuntu 20.04 LTS
   - Security group: Allow HTTP (80), HTTPS (443), and custom port 5000

2. **Install Docker**:
   ```bash
   sudo apt update
   sudo apt install docker.io docker-compose
   sudo usermod -aG docker ubuntu
   ```

3. **Deploy application**:
   ```bash
   git clone <repository-url>
   cd rag-document-qa-system
   cp .env.example .env
   # Edit .env with your API key
   docker-compose up -d --build
   ```

4. **Set up reverse proxy (optional)**:
   ```bash
   sudo apt install nginx
   # Configure nginx to proxy to localhost:5000
   ```

### Google Cloud Platform

1. **Create Compute Engine instance**:
   - Machine type: e2-medium or larger
   - OS: Ubuntu 20.04 LTS
   - Firewall: Allow HTTP traffic

2. **Deploy using Cloud Shell**:
   ```bash
   # Clone repository
   git clone <repository-url>
   cd rag-document-qa-system
   
   # Set up environment
   cp .env.example .env
   # Edit .env with your API key
   
   # Deploy
   docker-compose up -d --build
   ```

3. **Access via external IP**:
   - Find external IP in GCP console
   - Access: http://EXTERNAL_IP:5000

### Azure Container Instances

1. **Create resource group**:
   ```bash
   az group create --name rag-system --location eastus
   ```

2. **Deploy container**:
   ```bash
   az container create \
     --resource-group rag-system \
     --name rag-app \
     --image your-registry/rag-system:latest \
     --ports 5000 \
     --environment-variables GEMINI_API_KEY=your_key
   ```

## 🔧 Production Configuration

### Environment Variables

```env
# Production settings
FLASK_ENV=production
SECRET_KEY=your-secret-key-here
DATABASE_URL=postgresql://user:password@localhost/rag_system

# LLM Configuration
GEMINI_API_KEY=your-gemini-api-key

# ChromaDB Configuration
CHROMA_PERSIST_DIRECTORY=/app/data/chroma_db

# Security
MAX_CONTENT_LENGTH=104857600  # 100MB
```

### Database Configuration

For production, use PostgreSQL instead of SQLite:

1. **Update docker-compose.yml**:
   ```yaml
   services:
     postgres:
       image: postgres:15
       environment:
         POSTGRES_DB: rag_system
         POSTGRES_USER: rag_user
         POSTGRES_PASSWORD: rag_password
       volumes:
         - postgres_data:/var/lib/postgresql/data
   
   volumes:
     postgres_data:
   ```

2. **Update DATABASE_URL**:
   ```env
   DATABASE_URL=postgresql://rag_user:rag_password@postgres:5432/rag_system
   ```

### Security Considerations

1. **HTTPS Setup**:
   - Use Let's Encrypt for SSL certificates
   - Configure reverse proxy (nginx/Apache)
   - Redirect HTTP to HTTPS

2. **API Security**:
   - Implement API key authentication
   - Add rate limiting
   - Validate file uploads

3. **Data Security**:
   - Encrypt sensitive data
   - Regular backups
   - Access logging

## 📊 Monitoring and Logging

### Application Logs

```bash
# Docker logs
docker-compose logs -f rag-app

# Application logs
tail -f logs/app.log
```

### Health Monitoring

```bash
# Health check
curl http://localhost:5000/health

# System stats
curl http://localhost:5000/api/stats
```

### Performance Monitoring

- Monitor CPU and memory usage
- Track API response times
- Monitor vector database performance
- Set up alerts for failures

## 🔄 Backup and Recovery

### Data Backup

```bash
# Backup ChromaDB
tar -czf chroma_backup.tar.gz data/chroma_db/

# Backup database
pg_dump rag_system > rag_system_backup.sql

# Backup uploaded files
tar -czf uploads_backup.tar.gz uploads/
```

### Recovery

```bash
# Restore ChromaDB
tar -xzf chroma_backup.tar.gz

# Restore database
psql rag_system < rag_system_backup.sql

# Restore uploads
tar -xzf uploads_backup.tar.gz
```

## 🚀 Scaling

### Horizontal Scaling

1. **Load Balancer**: Use nginx or AWS ALB
2. **Multiple Instances**: Deploy multiple app containers
3. **Shared Storage**: Use shared volume for ChromaDB
4. **Database**: Use managed PostgreSQL service

### Vertical Scaling

1. **Increase Resources**: More CPU/RAM for containers
2. **Optimize Chunking**: Adjust chunk size based on performance
3. **Caching**: Implement Redis for frequently accessed data

## 🛠️ Troubleshooting

### Common Issues

1. **ChromaDB Initialization Error**:
   ```bash
   # Check directory permissions
   ls -la data/chroma_db/
   # Fix permissions
   chmod 755 data/chroma_db/
   ```

2. **Memory Issues**:
   ```bash
   # Monitor memory usage
   docker stats
   # Increase container memory limits
   ```

3. **API Key Issues**:
   ```bash
   # Test API key
   curl -H "Authorization: Bearer $GEMINI_API_KEY" \
        https://generativelanguage.googleapis.com/v1beta/models
   ```

4. **File Upload Issues**:
   ```bash
   # Check file permissions
   ls -la uploads/
   # Check disk space
   df -h
   ```

### Performance Optimization

1. **Chunk Size Tuning**:
   - Smaller chunks: Better precision, more chunks
   - Larger chunks: Better context, fewer chunks

2. **Vector Search Optimization**:
   - Adjust top_k parameter
   - Use document filtering
   - Implement result caching

3. **LLM Optimization**:
   - Optimize prompts
   - Use streaming responses
   - Implement response caching

## 📈 Maintenance

### Regular Tasks

1. **Daily**:
   - Check application health
   - Monitor error logs
   - Verify backups

2. **Weekly**:
   - Update dependencies
   - Clean up old files
   - Review performance metrics

3. **Monthly**:
   - Security updates
   - Database optimization
   - Capacity planning

### Updates

```bash
# Update application
git pull origin main
docker-compose down
docker-compose up --build -d

# Update dependencies
pip install -r requirements.txt --upgrade
```

This deployment guide should help you successfully deploy the RAG Document Q&A System in various environments.