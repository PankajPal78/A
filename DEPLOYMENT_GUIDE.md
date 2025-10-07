# Deployment Guide

This guide provides detailed instructions for deploying the RAG Document Q&A system in various environments.

## Table of Contents

1. [Local Development](#local-development)
2. [Docker Deployment](#docker-deployment)
3. [AWS Deployment](#aws-deployment)
4. [Google Cloud Platform](#google-cloud-platform)
5. [Azure Deployment](#azure-deployment)
6. [Kubernetes Deployment](#kubernetes-deployment)
7. [Production Best Practices](#production-best-practices)

## Local Development

### Prerequisites
- Python 3.9+
- pip
- Virtual environment

### Setup Steps

```bash
# Clone repository
git clone <repository-url>
cd rag-document-qa

# Create virtual environment
python -m venv venv
source venv/bin/activate  # Windows: venv\Scripts\activate

# Install dependencies
pip install -r requirements.txt

# Configure environment
cp .env.example .env
# Edit .env with your API keys

# Run application
python run.py
```

### Development Mode

```bash
# With auto-reload
export FLASK_ENV=development
export FLASK_DEBUG=True
python run.py
```

## Docker Deployment

### Single Container

```bash
# Build image
docker build -t rag-api:latest .

# Run container
docker run -d \
  --name rag-api \
  -p 5000:5000 \
  -e GEMINI_API_KEY=your_key \
  -e LLM_PROVIDER=gemini \
  -v $(pwd)/data:/app/data \
  rag-api:latest
```

### Docker Compose (Recommended)

```bash
# Start all services
docker-compose up -d

# View logs
docker-compose logs -f rag-api

# Stop services
docker-compose down

# Rebuild after changes
docker-compose up -d --build
```

### Docker Compose with Ollama

```yaml
# Uncomment ollama service in docker-compose.yml
docker-compose up -d

# Pull Ollama model
docker-compose exec ollama ollama pull llama2

# Set environment
LLM_PROVIDER=ollama
OLLAMA_BASE_URL=http://ollama:11434
```

## AWS Deployment

### Option 1: EC2 with Docker

#### Step 1: Launch EC2 Instance

```bash
# Launch instance (Amazon Linux 2)
aws ec2 run-instances \
  --image-id ami-0c55b159cbfafe1f0 \
  --instance-type t2.medium \
  --key-name your-key \
  --security-group-ids sg-xxxxx \
  --subnet-id subnet-xxxxx
```

#### Step 2: Install Docker

```bash
# SSH into instance
ssh -i your-key.pem ec2-user@<instance-ip>

# Install Docker
sudo yum update -y
sudo yum install docker -y
sudo service docker start
sudo usermod -a -G docker ec2-user

# Install Docker Compose
sudo curl -L "https://github.com/docker/compose/releases/latest/download/docker-compose-$(uname -s)-$(uname -m)" -o /usr/local/bin/docker-compose
sudo chmod +x /usr/local/bin/docker-compose

# Logout and login for group changes
exit
ssh -i your-key.pem ec2-user@<instance-ip>
```

#### Step 3: Deploy Application

```bash
# Clone repository
git clone <repository-url>
cd rag-document-qa

# Configure environment
cp .env.example .env
nano .env  # Edit with your keys

# Start application
docker-compose up -d

# Check status
docker-compose ps
docker-compose logs -f
```

#### Step 4: Configure Security Group

Allow inbound traffic:
- Port 5000 (API)
- Port 22 (SSH)
- Port 443 (HTTPS, with reverse proxy)

### Option 2: ECS (Fargate)

#### Step 1: Create ECR Repository

```bash
# Create repository
aws ecr create-repository --repository-name rag-api

# Login to ECR
aws ecr get-login-password --region us-east-1 | \
  docker login --username AWS --password-stdin \
  <account-id>.dkr.ecr.us-east-1.amazonaws.com
```

#### Step 2: Build and Push Image

```bash
# Build image
docker build -t rag-api .

# Tag image
docker tag rag-api:latest \
  <account-id>.dkr.ecr.us-east-1.amazonaws.com/rag-api:latest

# Push image
docker push <account-id>.dkr.ecr.us-east-1.amazonaws.com/rag-api:latest
```

#### Step 3: Create ECS Resources

Create `task-definition.json`:

```json
{
  "family": "rag-api",
  "networkMode": "awsvpc",
  "requiresCompatibilities": ["FARGATE"],
  "cpu": "1024",
  "memory": "2048",
  "containerDefinitions": [{
    "name": "rag-api",
    "image": "<account-id>.dkr.ecr.us-east-1.amazonaws.com/rag-api:latest",
    "portMappings": [{
      "containerPort": 5000,
      "protocol": "tcp"
    }],
    "environment": [
      {"name": "LLM_PROVIDER", "value": "gemini"},
      {"name": "FLASK_ENV", "value": "production"}
    ],
    "secrets": [
      {
        "name": "GEMINI_API_KEY",
        "valueFrom": "arn:aws:secretsmanager:us-east-1:account-id:secret:gemini-key"
      }
    ],
    "logConfiguration": {
      "logDriver": "awslogs",
      "options": {
        "awslogs-group": "/ecs/rag-api",
        "awslogs-region": "us-east-1",
        "awslogs-stream-prefix": "ecs"
      }
    }
  }]
}
```

Register task:
```bash
aws ecs register-task-definition --cli-input-json file://task-definition.json
```

#### Step 4: Create ECS Service

```bash
aws ecs create-service \
  --cluster rag-cluster \
  --service-name rag-api-service \
  --task-definition rag-api \
  --desired-count 2 \
  --launch-type FARGATE \
  --network-configuration "awsvpcConfiguration={subnets=[subnet-xxx],securityGroups=[sg-xxx],assignPublicIp=ENABLED}" \
  --load-balancers "targetGroupArn=arn:aws:elasticloadbalancing:us-east-1:account-id:targetgroup/rag-api/xxx,containerName=rag-api,containerPort=5000"
```

### Option 3: Elastic Beanstalk

```bash
# Install EB CLI
pip install awsebcli

# Initialize EB application
eb init -p docker rag-api

# Create environment
eb create rag-api-env

# Deploy
eb deploy

# Open application
eb open
```

## Google Cloud Platform

### Option 1: Cloud Run

#### Step 1: Build Container

```bash
# Set project
gcloud config set project <project-id>

# Build image
gcloud builds submit --tag gcr.io/<project-id>/rag-api
```

#### Step 2: Deploy to Cloud Run

```bash
gcloud run deploy rag-api \
  --image gcr.io/<project-id>/rag-api \
  --platform managed \
  --region us-central1 \
  --allow-unauthenticated \
  --memory 2Gi \
  --cpu 2 \
  --max-instances 10 \
  --set-env-vars "LLM_PROVIDER=gemini" \
  --set-secrets "GEMINI_API_KEY=gemini-key:latest"
```

#### Step 3: Configure Domain (Optional)

```bash
gcloud run services update rag-api \
  --region us-central1 \
  --domain api.yourdomain.com
```

### Option 2: GKE (Google Kubernetes Engine)

See [Kubernetes Deployment](#kubernetes-deployment) section.

## Azure Deployment

### Option 1: Container Instances

```bash
# Create resource group
az group create --name rag-rg --location eastus

# Create container
az container create \
  --resource-group rag-rg \
  --name rag-api \
  --image <your-registry>/rag-api:latest \
  --dns-name-label rag-api-unique \
  --ports 5000 \
  --cpu 2 \
  --memory 4 \
  --environment-variables \
    LLM_PROVIDER=gemini \
  --secure-environment-variables \
    GEMINI_API_KEY=<your-key>

# Get URL
az container show \
  --resource-group rag-rg \
  --name rag-api \
  --query ipAddress.fqdn
```

### Option 2: App Service

```bash
# Create App Service plan
az appservice plan create \
  --name rag-plan \
  --resource-group rag-rg \
  --is-linux \
  --sku B1

# Create Web App
az webapp create \
  --resource-group rag-rg \
  --plan rag-plan \
  --name rag-api-webapp \
  --deployment-container-image-name <your-registry>/rag-api:latest

# Configure environment
az webapp config appsettings set \
  --resource-group rag-rg \
  --name rag-api-webapp \
  --settings \
    LLM_PROVIDER=gemini \
    GEMINI_API_KEY=<your-key>
```

## Kubernetes Deployment

### Prerequisites

- Kubernetes cluster (GKE, EKS, AKS, or local)
- kubectl configured
- Docker registry access

### Deployment Files

Create `k8s/deployment.yaml`:

```yaml
apiVersion: apps/v1
kind: Deployment
metadata:
  name: rag-api
spec:
  replicas: 3
  selector:
    matchLabels:
      app: rag-api
  template:
    metadata:
      labels:
        app: rag-api
    spec:
      containers:
      - name: rag-api
        image: gcr.io/<project-id>/rag-api:latest
        ports:
        - containerPort: 5000
        env:
        - name: LLM_PROVIDER
          value: "gemini"
        - name: GEMINI_API_KEY
          valueFrom:
            secretKeyRef:
              name: rag-secrets
              key: gemini-api-key
        resources:
          requests:
            memory: "1Gi"
            cpu: "500m"
          limits:
            memory: "2Gi"
            cpu: "1000m"
        livenessProbe:
          httpGet:
            path: /api/health
            port: 5000
          initialDelaySeconds: 30
          periodSeconds: 10
        readinessProbe:
          httpGet:
            path: /api/health
            port: 5000
          initialDelaySeconds: 5
          periodSeconds: 5
```

Create `k8s/service.yaml`:

```yaml
apiVersion: v1
kind: Service
metadata:
  name: rag-api-service
spec:
  type: LoadBalancer
  selector:
    app: rag-api
  ports:
  - protocol: TCP
    port: 80
    targetPort: 5000
```

Create `k8s/secrets.yaml`:

```yaml
apiVersion: v1
kind: Secret
metadata:
  name: rag-secrets
type: Opaque
stringData:
  gemini-api-key: your_key_here
```

### Deploy to Kubernetes

```bash
# Create namespace
kubectl create namespace rag-system

# Create secrets
kubectl apply -f k8s/secrets.yaml -n rag-system

# Deploy application
kubectl apply -f k8s/deployment.yaml -n rag-system
kubectl apply -f k8s/service.yaml -n rag-system

# Check status
kubectl get pods -n rag-system
kubectl get svc -n rag-system

# View logs
kubectl logs -f deployment/rag-api -n rag-system
```

## Production Best Practices

### 1. Environment Configuration

```bash
# Use production settings
FLASK_ENV=production
FLASK_DEBUG=False

# Use stronger secret key
SECRET_KEY=$(openssl rand -hex 32)

# Use production database
DATABASE_URL=postgresql://user:pass@host:5432/dbname
```

### 2. Reverse Proxy (Nginx)

```nginx
server {
    listen 80;
    server_name api.yourdomain.com;

    location / {
        proxy_pass http://localhost:5000;
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
        proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
        proxy_set_header X-Forwarded-Proto $scheme;
    }
}
```

### 3. SSL/TLS (Let's Encrypt)

```bash
# Install certbot
sudo apt-get install certbot python3-certbot-nginx

# Get certificate
sudo certbot --nginx -d api.yourdomain.com

# Auto-renewal
sudo certbot renew --dry-run
```

### 4. Monitoring

Use Prometheus + Grafana:

```yaml
# Add to docker-compose.yml
  prometheus:
    image: prom/prometheus
    ports:
      - "9090:9090"
    volumes:
      - ./prometheus.yml:/etc/prometheus/prometheus.yml
  
  grafana:
    image: grafana/grafana
    ports:
      - "3000:3000"
    environment:
      - GF_SECURITY_ADMIN_PASSWORD=admin
```

### 5. Logging

Configure structured logging:

```python
import logging
from pythonjsonlogger import jsonlogger

logHandler = logging.StreamHandler()
formatter = jsonlogger.JsonFormatter()
logHandler.setFormatter(formatter)
logger = logging.getLogger()
logger.addHandler(logHandler)
logger.setLevel(logging.INFO)
```

### 6. Backup Strategy

```bash
# Database backup
pg_dump $DATABASE_URL > backup_$(date +%Y%m%d).sql

# Vector DB backup
tar -czf vectordb_$(date +%Y%m%d).tar.gz data/vectordb/

# Automated daily backups
0 2 * * * /path/to/backup.sh
```

### 7. Health Checks

Implement comprehensive health checks:

```python
@app.route('/api/health')
def health():
    checks = {
        'database': check_database(),
        'vector_store': check_vector_store(),
        'llm_provider': check_llm()
    }
    status = 'healthy' if all(checks.values()) else 'unhealthy'
    return jsonify({'status': status, 'checks': checks})
```

### 8. Rate Limiting

```python
from flask_limiter import Limiter

limiter = Limiter(
    app,
    key_func=lambda: request.remote_addr,
    default_limits=["100 per hour"]
)

@app.route('/api/query')
@limiter.limit("10 per minute")
def query():
    pass
```

## Troubleshooting

### Container won't start
```bash
docker logs rag-api
docker-compose logs rag-api
```

### Out of memory
```bash
# Increase Docker memory
docker-compose down
# Edit docker-compose.yml, add:
deploy:
  resources:
    limits:
      memory: 4G
docker-compose up -d
```

### Database connection issues
```bash
# Check connection string
echo $DATABASE_URL

# Test connection
docker-compose exec rag-api python -c "from app.models import engine; print(engine.connect())"
```