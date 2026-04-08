# 📦 WattWise AI Installation Guide

This guide provides detailed instructions for installing and setting up WattWise AI in different environments.

## 🎯 Installation Options

1. **Docker Compose** (Recommended for development)
2. **Local Development** (For contributors)
3. **Kubernetes** (Production deployment)
4. **Manual Installation** (Custom setups)

## 🐳 Docker Compose Installation

### Prerequisites

- Docker 20.10+
- Docker Compose 2.0+
- 4GB+ RAM
- 10GB+ disk space

### Quick Installation

```bash
# Clone repository
git clone https://github.com/your-org/wattwise-ai.git
cd wattwise-ai

# Copy environment files
cp backend/.env.example backend/.env
cp frontend/.env.example frontend/.env

# Start all services
docker-compose up -d

# Verify installation
docker-compose ps
```

### Configuration

Edit the environment files as needed:

**backend/.env**
```bash
DATABASE_URL=postgresql://wattwise:wattwise123@postgres:5432/wattwise_db
OPENAI_API_KEY=your_openai_api_key_here  # Optional
PORT=8000
DEBUG=false
```

**frontend/.env**
```bash
BACKEND_URL=http://backend:8000
```

### Verification

```bash
# Check all services are running
docker-compose ps

# Test backend API
curl http://localhost:8000/health

# Test frontend
curl http://localhost:8501/_stcore/health

# View logs
docker-compose logs -f
```

## 💻 Local Development Installation

### Prerequisites

- Python 3.11+
- PostgreSQL 15+
- Git
- 8GB+ RAM (recommended)

### Backend Setup

```bash
# Clone repository
git clone https://github.com/your-org/wattwise-ai.git
cd wattwise-ai/backend

# Create virtual environment
python -m venv venv
source venv/bin/activate  # Windows: venv\Scripts\activate

# Install dependencies
pip install -r requirements.txt

# Set up environment
cp .env.example .env
# Edit .env with your database credentials

# Initialize database
python manage_db.py init

# Start backend
python startup.py
```

### Frontend Setup

```bash
# In a new terminal
cd wattwise-ai/frontend

# Create virtual environment
python -m venv venv
source venv/bin/activate  # Windows: venv\Scripts\activate

# Install dependencies
pip install -r requirements.txt

# Set up environment
cp .env.example .env
# Edit .env with backend URL

# Start frontend
python run.py
```

### Database Setup

#### Option 1: Local PostgreSQL

```bash
# Install PostgreSQL (Ubuntu/Debian)
sudo apt update
sudo apt install postgresql postgresql-contrib

# Create database and user
sudo -u postgres psql
CREATE DATABASE wattwise_db;
CREATE USER wattwise WITH PASSWORD 'wattwise123';
GRANT ALL PRIVILEGES ON DATABASE wattwise_db TO wattwise;
\q

# Update backend/.env
DATABASE_URL=postgresql://wattwise:wattwise123@localhost:5432/wattwise_db
```

#### Option 2: Docker PostgreSQL

```bash
# Start PostgreSQL container
docker run -d \
  --name wattwise-postgres \
  -e POSTGRES_DB=wattwise_db \
  -e POSTGRES_USER=wattwise \
  -e POSTGRES_PASSWORD=wattwise123 \
  -p 5432:5432 \
  postgres:15-alpine

# Update backend/.env
DATABASE_URL=postgresql://wattwise:wattwise123@localhost:5432/wattwise_db
```

## ☸️ Kubernetes Installation

### Prerequisites

- Kubernetes cluster 1.24+
- Helm 3.8+
- kubectl configured
- 16GB+ RAM across nodes
- 50GB+ storage

### Installation Steps

```bash
# Clone repository
git clone https://github.com/your-org/wattwise-ai.git
cd wattwise-ai

# Add Helm dependencies
helm dependency update k8s/wattwise-helm/

# Create namespace
kubectl create namespace wattwise

# Install with Helm
helm install wattwise k8s/wattwise-helm/ \
  --namespace wattwise \
  --values k8s/wattwise-helm/values.yaml

# Check deployment
kubectl get pods -n wattwise
```

### Custom Configuration

Create a custom values file:

```yaml
# values-custom.yaml
backend:
  replicaCount: 3
  resources:
    requests:
      cpu: 1000m
      memory: 2Gi

postgresql:
  auth:
    postgresPassword: "your-secure-password"
    password: "your-secure-password"

ingress:
  enabled: true
  hosts:
    - host: wattwise.yourdomain.com
      paths:
        - path: /
          pathType: Prefix
          service: frontend
        - path: /api
          pathType: Prefix
          service: backend
```

```bash
# Install with custom values
helm install wattwise k8s/wattwise-helm/ \
  --namespace wattwise \
  --values values-custom.yaml
```

### Monitoring Setup

```bash
# Enable monitoring components
helm upgrade wattwise k8s/wattwise-helm/ \
  --namespace wattwise \
  --set prometheus.enabled=true \
  --set grafana.enabled=true
```

## 🔧 Manual Installation

### System Requirements

- Ubuntu 20.04+ / CentOS 8+ / RHEL 8+
- Python 3.11+
- PostgreSQL 15+
- Nginx (optional, for reverse proxy)

### Step-by-Step Installation

#### 1. System Preparation

```bash
# Update system
sudo apt update && sudo apt upgrade -y

# Install dependencies
sudo apt install -y python3.11 python3.11-venv python3-pip \
  postgresql postgresql-contrib nginx git curl

# Install Docker (optional)
curl -fsSL https://get.docker.com -o get-docker.sh
sudo sh get-docker.sh
sudo usermod -aG docker $USER
```

#### 2. Database Setup

```bash
# Configure PostgreSQL
sudo -u postgres psql
CREATE DATABASE wattwise_db;
CREATE USER wattwise WITH PASSWORD 'secure_password_here';
GRANT ALL PRIVILEGES ON DATABASE wattwise_db TO wattwise;
ALTER USER wattwise CREATEDB;
\q

# Configure PostgreSQL for connections
sudo nano /etc/postgresql/15/main/postgresql.conf
# Uncomment and set: listen_addresses = 'localhost'

sudo nano /etc/postgresql/15/main/pg_hba.conf
# Add: local   wattwise_db   wattwise   md5

sudo systemctl restart postgresql
```

#### 3. Application Setup

```bash
# Create application user
sudo useradd -m -s /bin/bash wattwise
sudo su - wattwise

# Clone and setup application
git clone https://github.com/your-org/wattwise-ai.git
cd wattwise-ai

# Backend setup
cd backend
python3.11 -m venv venv
source venv/bin/activate
pip install -r requirements.txt

# Configure environment
cp .env.example .env
nano .env  # Edit database credentials

# Initialize database
python manage_db.py init

# Frontend setup (new terminal)
cd ../frontend
python3.11 -m venv venv
source venv/bin/activate
pip install -r requirements.txt
cp .env.example .env
```

#### 4. Service Configuration

Create systemd services:

**Backend Service** (`/etc/systemd/system/wattwise-backend.service`):
```ini
[Unit]
Description=WattWise AI Backend
After=network.target postgresql.service

[Service]
Type=simple
User=wattwise
WorkingDirectory=/home/wattwise/wattwise-ai/backend
Environment=PATH=/home/wattwise/wattwise-ai/backend/venv/bin
ExecStart=/home/wattwise/wattwise-ai/backend/venv/bin/python startup.py
Restart=always
RestartSec=10

[Install]
WantedBy=multi-user.target
```

**Frontend Service** (`/etc/systemd/system/wattwise-frontend.service`):
```ini
[Unit]
Description=WattWise AI Frontend
After=network.target wattwise-backend.service

[Service]
Type=simple
User=wattwise
WorkingDirectory=/home/wattwise/wattwise-ai/frontend
Environment=PATH=/home/wattwise/wattwise-ai/frontend/venv/bin
ExecStart=/home/wattwise/wattwise-ai/frontend/venv/bin/python run.py
Restart=always
RestartSec=10

[Install]
WantedBy=multi-user.target
```

```bash
# Enable and start services
sudo systemctl daemon-reload
sudo systemctl enable wattwise-backend wattwise-frontend
sudo systemctl start wattwise-backend wattwise-frontend

# Check status
sudo systemctl status wattwise-backend wattwise-frontend
```

#### 5. Nginx Configuration (Optional)

```nginx
# /etc/nginx/sites-available/wattwise
server {
    listen 80;
    server_name your-domain.com;

    # Frontend
    location / {
        proxy_pass http://localhost:8501;
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
        proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
        proxy_set_header X-Forwarded-Proto $scheme;
    }

    # Backend API
    location /api/ {
        proxy_pass http://localhost:8000/;
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
        proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
        proxy_set_header X-Forwarded-Proto $scheme;
    }
}
```

```bash
# Enable site
sudo ln -s /etc/nginx/sites-available/wattwise /etc/nginx/sites-enabled/
sudo nginx -t
sudo systemctl restart nginx
```

## 🔍 Verification & Testing

### Health Checks

```bash
# Backend health
curl http://localhost:8000/health

# Frontend health
curl http://localhost:8501/_stcore/health

# Database connection
python backend/manage_db.py check
```

### Functional Testing

```bash
# Run test suite
cd tests
pip install -r requirements.txt
python run_tests.py

# Test API endpoints
curl -X POST http://localhost:8000/jobs/schedule \
  -H "Content-Type: application/json" \
  -d '{
    "name": "Test Job",
    "workload_type": "llm_inference",
    "estimated_duration_hours": 1.0,
    "gpu_requirements": {"T4": 1}
  }'
```

### Performance Testing

```bash
# Install testing tools
pip install locust

# Run load test
locust -f tests/load_test.py --host=http://localhost:8000
```

## 🚨 Troubleshooting

### Common Issues

#### Database Connection Issues

```bash
# Check PostgreSQL status
sudo systemctl status postgresql

# Check database connectivity
psql -h localhost -U wattwise -d wattwise_db

# Reset database
python backend/manage_db.py reset
```

#### Permission Issues

```bash
# Fix file permissions
sudo chown -R wattwise:wattwise /home/wattwise/wattwise-ai
chmod +x deploy/deploy_ssh.sh
```

#### Port Conflicts

```bash
# Check port usage
sudo netstat -tlnp | grep :8000
sudo netstat -tlnp | grep :8501

# Kill conflicting processes
sudo kill -9 <PID>
```

#### Memory Issues

```bash
# Check memory usage
free -h
docker stats

# Reduce resource usage
# Edit docker-compose.yml or values.yaml
```

### Log Analysis

```bash
# Application logs
tail -f /var/log/wattwise/backend.log
tail -f /var/log/wattwise/frontend.log

# System logs
sudo journalctl -u wattwise-backend -f
sudo journalctl -u wattwise-frontend -f

# Docker logs
docker-compose logs -f backend
docker-compose logs -f frontend
```

## 🔄 Updates & Maintenance

### Updating the Application

```bash
# Docker Compose
git pull origin main
docker-compose pull
docker-compose up -d

# Kubernetes
helm upgrade wattwise k8s/wattwise-helm/

# Manual installation
sudo systemctl stop wattwise-backend wattwise-frontend
git pull origin main
# Reinstall dependencies if needed
sudo systemctl start wattwise-backend wattwise-frontend
```

### Database Migrations

```bash
# Check current database version
python backend/manage_db.py stats

# Run migrations (if using Alembic)
cd backend
alembic upgrade head
```

### Backup & Restore

```bash
# Database backup
pg_dump -h localhost -U wattwise wattwise_db > backup.sql

# Database restore
psql -h localhost -U wattwise wattwise_db < backup.sql

# Application backup
tar -czf wattwise-backup-$(date +%Y%m%d).tar.gz wattwise-ai/
```

## 📞 Support

If you encounter issues during installation:

1. Check the [Troubleshooting](#-troubleshooting) section
2. Review logs for error messages
3. Search [GitHub Issues](https://github.com/your-org/wattwise-ai/issues)
4. Create a new issue with:
   - Installation method used
   - Operating system and version
   - Error messages and logs
   - Steps to reproduce

---

**Need help?** Join our [Discord community](https://discord.gg/wattwise) or email support@wattwise.ai

