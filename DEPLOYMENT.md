# Deployment Guide

This guide provides detailed instructions for deploying the RAG Document Q&A System to various environments.

## Table of Contents
- [Local Development](#local-development)
- [Docker Deployment](#docker-deployment)
- [AWS Deployment](#aws-deployment)
- [Google Cloud Platform](#google-cloud-platform)
- [Azure Deployment](#azure-deployment)
- [Production Considerations](#production-considerations)

---

## Local Development

### Prerequisites
- Python 3.11+
- pip
- Virtual environment (recommended)

### Steps

1. **Clone repository**
```bash
git clone <repository-url>
cd rag-document-qa
```

2. **Create virtual environment**
```bash
python -m venv venv
source venv/bin/activate  # Windows: venv\Scripts\activate
```

3. **Install dependencies**
```bash
pip install -r requirements.txt
```

4. **Configure environment**
```bash
cp .env.example .env
# Edit .env with your settings
```

5. **Run application**
```bash
python app.py
```

---

## Docker Deployment

### Quick Start

```bash
# Run setup script
chmod +x setup.sh
./setup.sh

# Build and run
docker-compose up --build
```

### Manual Docker Setup

1. **Build image**
```bash
docker build -t rag-document-qa .
```

2. **Run container**
```bash
docker run -d \
  -p 5000:5000 \
  -e GEMINI_API_KEY=your_key \
  -v $(pwd)/data:/app/data \
  --name rag-api \
  rag-document-qa
```

### Docker Compose (Recommended)

```bash
# Start services
docker-compose up -d

# View logs
docker-compose logs -f

# Stop services
docker-compose down

# Rebuild after changes
docker-compose up --build
```

---

## AWS Deployment

### Option 1: EC2 Instance

#### 1. Launch EC2 Instance
```bash
# Instance type: t2.medium or larger
# OS: Ubuntu 22.04 LTS
# Storage: 20GB+ EBS volume
```

#### 2. Configure Security Group
```
Inbound Rules:
- Port 22 (SSH) - Your IP
- Port 5000 (HTTP) - 0.0.0.0/0 or specific IPs
```

#### 3. Connect and Setup
```bash
# Connect to instance
ssh -i your-key.pem ubuntu@your-instance-ip

# Update system
sudo apt update && sudo apt upgrade -y

# Install Docker
curl -fsSL https://get.docker.com -o get-docker.sh
sudo sh get-docker.sh
sudo usermod -aG docker ubuntu

# Install Docker Compose
sudo curl -L "https://github.com/docker/compose/releases/latest/download/docker-compose-$(uname -s)-$(uname -m)" -o /usr/local/bin/docker-compose
sudo chmod +x /usr/local/bin/docker-compose

# Clone repository
git clone <repository-url>
cd rag-document-qa

# Configure environment
cp .env.example .env
nano .env  # Add your API keys

# Deploy
docker-compose up -d
```

#### 4. Setup Nginx Reverse Proxy (Optional)
```bash
# Install Nginx
sudo apt install nginx -y

# Create Nginx config
sudo nano /etc/nginx/sites-available/rag-api
```

```nginx
server {
    listen 80;
    server_name your-domain.com;

    location / {
        proxy_pass http://localhost:5000;
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
        proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
        proxy_set_header X-Forwarded-Proto $scheme;
    }
}
```

```bash
# Enable site
sudo ln -s /etc/nginx/sites-available/rag-api /etc/nginx/sites-enabled/
sudo nginx -t
sudo systemctl restart nginx
```

### Option 2: ECS (Elastic Container Service)

#### 1. Push to ECR
```bash
# Create ECR repository
aws ecr create-repository --repository-name rag-document-qa

# Login to ECR
aws ecr get-login-password --region us-east-1 | docker login --username AWS --password-stdin <account-id>.dkr.ecr.us-east-1.amazonaws.com

# Build and tag
docker build -t rag-document-qa .
docker tag rag-document-qa:latest <account-id>.dkr.ecr.us-east-1.amazonaws.com/rag-document-qa:latest

# Push to ECR
docker push <account-id>.dkr.ecr.us-east-1.amazonaws.com/rag-document-qa:latest
```

#### 2. Create ECS Task Definition
Create `task-definition.json`:
```json
{
  "family": "rag-document-qa",
  "containerDefinitions": [
    {
      "name": "rag-api",
      "image": "<account-id>.dkr.ecr.us-east-1.amazonaws.com/rag-document-qa:latest",
      "portMappings": [
        {
          "containerPort": 5000,
          "hostPort": 5000,
          "protocol": "tcp"
        }
      ],
      "environment": [
        {"name": "GEMINI_API_KEY", "value": "your-key"},
        {"name": "LLM_PROVIDER", "value": "gemini"}
      ],
      "memory": 2048,
      "cpu": 1024
    }
  ]
}
```

#### 3. Deploy to ECS
```bash
# Register task definition
aws ecs register-task-definition --cli-input-json file://task-definition.json

# Create service
aws ecs create-service \
  --cluster default \
  --service-name rag-api \
  --task-definition rag-document-qa \
  --desired-count 1 \
  --launch-type FARGATE \
  --network-configuration "awsvpcConfiguration={subnets=[subnet-xxx],securityGroups=[sg-xxx],assignPublicIp=ENABLED}"
```

---

## Google Cloud Platform

### Option 1: Compute Engine

```bash
# Create instance
gcloud compute instances create rag-api-instance \
  --zone=us-central1-a \
  --machine-type=e2-medium \
  --image-family=ubuntu-2204-lts \
  --image-project=ubuntu-os-cloud \
  --boot-disk-size=20GB

# SSH into instance
gcloud compute ssh rag-api-instance --zone=us-central1-a

# Follow Docker setup steps from AWS EC2 section
```

### Option 2: Cloud Run (Serverless)

```bash
# Build and push to Container Registry
gcloud builds submit --tag gcr.io/PROJECT_ID/rag-document-qa

# Deploy to Cloud Run
gcloud run deploy rag-api \
  --image gcr.io/PROJECT_ID/rag-document-qa \
  --platform managed \
  --region us-central1 \
  --allow-unauthenticated \
  --set-env-vars GEMINI_API_KEY=your-key,LLM_PROVIDER=gemini \
  --memory 2Gi \
  --timeout 300
```

---

## Azure Deployment

### Option 1: Azure Container Instances

```bash
# Login to Azure
az login

# Create resource group
az group create --name rag-rg --location eastus

# Create container registry
az acr create --resource-group rag-rg --name ragregistry --sku Basic

# Build and push image
az acr build --registry ragregistry --image rag-document-qa .

# Deploy container
az container create \
  --resource-group rag-rg \
  --name rag-api \
  --image ragregistry.azurecr.io/rag-document-qa:latest \
  --dns-name-label rag-api-unique \
  --ports 5000 \
  --environment-variables GEMINI_API_KEY=your-key LLM_PROVIDER=gemini \
  --cpu 2 \
  --memory 4
```

### Option 2: Azure App Service

```bash
# Create App Service plan
az appservice plan create \
  --name rag-plan \
  --resource-group rag-rg \
  --is-linux \
  --sku B1

# Create web app
az webapp create \
  --resource-group rag-rg \
  --plan rag-plan \
  --name rag-api-webapp \
  --deployment-container-image-name ragregistry.azurecr.io/rag-document-qa:latest

# Configure settings
az webapp config appsettings set \
  --resource-group rag-rg \
  --name rag-api-webapp \
  --settings GEMINI_API_KEY=your-key LLM_PROVIDER=gemini
```

---

## Production Considerations

### Security

1. **Environment Variables**
```bash
# Use secret management services
# AWS: Secrets Manager
# GCP: Secret Manager
# Azure: Key Vault
```

2. **HTTPS/SSL**
```bash
# Use Let's Encrypt with Certbot
sudo apt install certbot python3-certbot-nginx
sudo certbot --nginx -d your-domain.com
```

3. **Rate Limiting**
```python
# Add to requirements.txt
flask-limiter==3.5.0

# In app/__init__.py
from flask_limiter import Limiter
limiter = Limiter(app, key_func=lambda: request.remote_addr)
```

### Monitoring

1. **Application Logs**
```bash
# Centralized logging with CloudWatch/Stackdriver
# Add logging configuration
```

2. **Health Checks**
```bash
# Automated monitoring
# AWS: CloudWatch
# GCP: Cloud Monitoring
# Azure: Application Insights
```

### Scaling

1. **Horizontal Scaling**
```yaml
# docker-compose.yml
services:
  rag-api:
    deploy:
      replicas: 3
```

2. **Load Balancing**
```bash
# Use cloud provider load balancers
# AWS: Application Load Balancer
# GCP: Cloud Load Balancing
# Azure: Load Balancer
```

### Database

1. **Production Database**
```python
# Switch to PostgreSQL
DATABASE_URL=postgresql://user:password@host:5432/dbname
```

2. **Vector Store**
```python
# Consider managed services
# Pinecone: Fully managed
# Weaviate Cloud: Managed Weaviate
```

### Backup Strategy

```bash
# Regular backups of:
# 1. Vector database
# 2. SQL database
# 3. Uploaded documents

# Example backup script
#!/bin/bash
DATE=$(date +%Y%m%d_%H%M%S)
tar -czf backup_$DATE.tar.gz data/
aws s3 cp backup_$DATE.tar.gz s3://your-backup-bucket/
```

### Environment-Specific Configurations

#### Development
```env
DEBUG=True
LLM_TEMPERATURE=0.9
```

#### Staging
```env
DEBUG=False
LLM_TEMPERATURE=0.7
```

#### Production
```env
DEBUG=False
LLM_TEMPERATURE=0.5
WORKERS=4
```

---

## Troubleshooting

### Common Issues

1. **Port Already in Use**
```bash
# Find process using port 5000
lsof -i :5000
# Kill process
kill -9 <PID>
```

2. **Docker Disk Space**
```bash
# Clean up Docker
docker system prune -a
docker volume prune
```

3. **Memory Issues**
```bash
# Increase Docker memory in Docker Desktop
# Or use smaller embedding model
EMBEDDING_MODEL=sentence-transformers/all-MiniLM-L6-v2
```

---

## Support

For deployment issues:
1. Check application logs
2. Verify environment variables
3. Test API endpoints
4. Review security group/firewall rules
5. Check cloud provider documentation