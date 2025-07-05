# 🚀 WattWise AI Deployment Guide

This guide covers production deployment strategies for WattWise AI across different environments and platforms.

## 🎯 Deployment Options

1. **Cloud Platforms** (AWS, GCP, Azure)
2. **Kubernetes Clusters** (EKS, GKE, AKS)
3. **Container Platforms** (Docker Swarm, Nomad)
4. **Traditional Servers** (VMs, Bare Metal)

## ☁️ Cloud Platform Deployment

### AWS Deployment

#### Prerequisites
- AWS CLI configured
- EKS cluster or EC2 instances
- RDS PostgreSQL instance
- Application Load Balancer

#### EKS Deployment

```bash
# Create EKS cluster
eksctl create cluster --name wattwise-cluster --region us-west-2

# Configure kubectl
aws eks update-kubeconfig --region us-west-2 --name wattwise-cluster

# Deploy with Helm
helm install wattwise k8s/wattwise-helm/ \
  --namespace wattwise \
  --create-namespace \
  --set postgresql.enabled=false \
  --set externalDatabase.host=your-rds-endpoint.amazonaws.com \
  --set ingress.enabled=true \
  --set ingress.className=alb
```

#### EC2 Deployment

```bash
# Launch EC2 instances
aws ec2 run-instances \
  --image-id ami-0c02fb55956c7d316 \
  --instance-type t3.large \
  --key-name your-key-pair \
  --security-group-ids sg-xxxxxxxxx \
  --subnet-id subnet-xxxxxxxxx

# Deploy using SSH script
./deploy/deploy_ssh.sh production
```

### Google Cloud Platform

#### GKE Deployment

```bash
# Create GKE cluster
gcloud container clusters create wattwise-cluster \
  --zone us-central1-a \
  --num-nodes 3 \
  --machine-type n1-standard-4

# Get credentials
gcloud container clusters get-credentials wattwise-cluster --zone us-central1-a

# Deploy application
helm install wattwise k8s/wattwise-helm/ \
  --namespace wattwise \
  --create-namespace \
  --set postgresql.enabled=false \
  --set externalDatabase.host=your-cloud-sql-ip
```

### Azure Deployment

#### AKS Deployment

```bash
# Create resource group
az group create --name wattwise-rg --location eastus

# Create AKS cluster
az aks create \
  --resource-group wattwise-rg \
  --name wattwise-cluster \
  --node-count 3 \
  --node-vm-size Standard_D4s_v3 \
  --enable-addons monitoring

# Get credentials
az aks get-credentials --resource-group wattwise-rg --name wattwise-cluster

# Deploy application
helm install wattwise k8s/wattwise-helm/ \
  --namespace wattwise \
  --create-namespace
```

## ☸️ Kubernetes Production Deployment

### Production Values Configuration

Create `values-production.yaml`:

```yaml
# Production configuration
global:
  imageRegistry: "your-registry.com"
  imagePullSecrets:
    - name: registry-secret

backend:
  replicaCount: 3
  image:
    tag: "v1.0.0"
  resources:
    requests:
      cpu: 1000m
      memory: 2Gi
    limits:
      cpu: 2000m
      memory: 4Gi
  autoscaling:
    enabled: true
    minReplicas: 3
    maxReplicas: 10

frontend:
  replicaCount: 2
  image:
    tag: "v1.0.0"
  resources:
    requests:
      cpu: 500m
      memory: 1Gi
    limits:
      cpu: 1000m
      memory: 2Gi

postgresql:
  enabled: false

externalDatabase:
  host: "prod-postgres.example.com"
  username: "wattwise_prod"
  password: "secure-password"
  database: "wattwise_prod"

ingress:
  enabled: true
  className: "nginx"
  annotations:
    cert-manager.io/cluster-issuer: "letsencrypt-prod"
    nginx.ingress.kubernetes.io/ssl-redirect: "true"
  hosts:
    - host: wattwise.example.com
      paths:
        - path: /
          pathType: Prefix
          service: frontend
        - path: /api
          pathType: Prefix
          service: backend
  tls:
    - secretName: wattwise-tls
      hosts:
        - wattwise.example.com

prometheus:
  enabled: true
  server:
    persistentVolume:
      size: 50Gi

grafana:
  enabled: true
  adminPassword: "secure-admin-password"
  persistence:
    enabled: true
    size: 10Gi
```

### Deployment Commands

```bash
# Create namespace
kubectl create namespace wattwise

# Create secrets
kubectl create secret generic wattwise-secrets \
  --from-literal=OPENAI_API_KEY=your-api-key \
  --from-literal=DB_PASSWORD=secure-password \
  --namespace wattwise

# Deploy with production values
helm install wattwise k8s/wattwise-helm/ \
  --namespace wattwise \
  --values values-production.yaml

# Verify deployment
kubectl get pods -n wattwise
kubectl get services -n wattwise
kubectl get ingress -n wattwise
```

### SSL/TLS Configuration

#### Using cert-manager

```bash
# Install cert-manager
kubectl apply -f https://github.com/cert-manager/cert-manager/releases/download/v1.13.0/cert-manager.yaml

# Create ClusterIssuer
cat <<EOF | kubectl apply -f -
apiVersion: cert-manager.io/v1
kind: ClusterIssuer
metadata:
  name: letsencrypt-prod
spec:
  acme:
    server: https://acme-v02.api.letsencrypt.org/directory
    email: admin@example.com
    privateKeySecretRef:
      name: letsencrypt-prod
    solvers:
    - http01:
        ingress:
          class: nginx
EOF
```

## 🐳 Container Platform Deployment

### Docker Swarm

```bash
# Initialize swarm
docker swarm init

# Create overlay network
docker network create --driver overlay wattwise-network

# Deploy stack
docker stack deploy -c docker-compose.prod.yml wattwise

# Check services
docker service ls
```

### HashiCorp Nomad

Create `wattwise.nomad`:

```hcl
job "wattwise" {
  datacenters = ["dc1"]
  type = "service"

  group "backend" {
    count = 3

    task "backend" {
      driver = "docker"

      config {
        image = "wattwise/backend:v1.0.0"
        port_map {
          http = 8000
        }
      }

      resources {
        cpu    = 1000
        memory = 2048
        network {
          mbits = 10
          port "http" {}
        }
      }

      service {
        name = "wattwise-backend"
        port = "http"
        check {
          type     = "http"
          path     = "/health"
          interval = "10s"
          timeout  = "2s"
        }
      }
    }
  }

  group "frontend" {
    count = 2

    task "frontend" {
      driver = "docker"

      config {
        image = "wattwise/frontend:v1.0.0"
        port_map {
          http = 8501
        }
      }

      resources {
        cpu    = 500
        memory = 1024
        network {
          mbits = 10
          port "http" {}
        }
      }

      service {
        name = "wattwise-frontend"
        port = "http"
        check {
          type     = "http"
          path     = "/_stcore/health"
          interval = "10s"
          timeout  = "2s"
        }
      }
    }
  }
}
```

```bash
# Deploy to Nomad
nomad job run wattwise.nomad

# Check status
nomad job status wattwise
```

## 🖥️ Traditional Server Deployment

### Multi-Server Setup

#### Load Balancer Configuration (Nginx)

```nginx
upstream wattwise_backend {
    server 10.0.1.10:8000;
    server 10.0.1.11:8000;
    server 10.0.1.12:8000;
}

upstream wattwise_frontend {
    server 10.0.2.10:8501;
    server 10.0.2.11:8501;
}

server {
    listen 80;
    server_name wattwise.example.com;
    return 301 https://$server_name$request_uri;
}

server {
    listen 443 ssl http2;
    server_name wattwise.example.com;

    ssl_certificate /etc/ssl/certs/wattwise.crt;
    ssl_certificate_key /etc/ssl/private/wattwise.key;

    location / {
        proxy_pass http://wattwise_frontend;
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
        proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
        proxy_set_header X-Forwarded-Proto $scheme;
    }

    location /api/ {
        proxy_pass http://wattwise_backend/;
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
        proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
        proxy_set_header X-Forwarded-Proto $scheme;
    }
}
```

#### Database Cluster Setup

```bash
# Primary PostgreSQL server
# /etc/postgresql/15/main/postgresql.conf
listen_addresses = '*'
wal_level = replica
max_wal_senders = 3
wal_keep_size = 64

# /etc/postgresql/15/main/pg_hba.conf
host replication replicator 10.0.3.0/24 md5

# Create replication user
sudo -u postgres psql
CREATE USER replicator REPLICATION LOGIN ENCRYPTED PASSWORD 'repl_password';
```

### High Availability Setup

#### Database High Availability

```bash
# Install and configure Patroni
pip install patroni[etcd]

# Patroni configuration
cat > /etc/patroni.yml << EOF
scope: wattwise-cluster
namespace: /db/
name: node1

restapi:
  listen: 0.0.0.0:8008
  connect_address: 10.0.3.10:8008

etcd:
  hosts: 10.0.4.10:2379,10.0.4.11:2379,10.0.4.12:2379

bootstrap:
  dcs:
    ttl: 30
    loop_wait: 10
    retry_timeout: 30
    maximum_lag_on_failover: 1048576
    postgresql:
      use_pg_rewind: true
      use_slots: true
      parameters:
        wal_level: replica
        hot_standby: "on"
        wal_keep_segments: 8
        max_wal_senders: 10
        max_replication_slots: 10
        wal_log_hints: "on"

  initdb:
  - encoding: UTF8
  - data-checksums

  pg_hba:
  - host replication replicator 127.0.0.1/32 md5
  - host replication replicator 10.0.3.0/24 md5
  - host all all 0.0.0.0/0 md5

postgresql:
  listen: 0.0.0.0:5432
  connect_address: 10.0.3.10:5432
  data_dir: /var/lib/postgresql/15/main
  bin_dir: /usr/lib/postgresql/15/bin
  pgpass: /tmp/pgpass
  authentication:
    replication:
      username: replicator
      password: repl_password
    superuser:
      username: postgres
      password: postgres_password
EOF

# Start Patroni
systemctl enable patroni
systemctl start patroni
```

## 🔄 CI/CD Pipeline Setup

### Jenkins Pipeline

```groovy
pipeline {
    agent any
    
    environment {
        DOCKER_REGISTRY = 'your-registry.com'
        KUBECONFIG = credentials('kubeconfig')
    }
    
    stages {
        stage('Build') {
            parallel {
                stage('Backend') {
                    steps {
                        script {
                            def image = docker.build("${DOCKER_REGISTRY}/wattwise-backend:${BUILD_NUMBER}", "./backend")
                            docker.withRegistry("https://${DOCKER_REGISTRY}", 'docker-registry-creds') {
                                image.push()
                                image.push("latest")
                            }
                        }
                    }
                }
                stage('Frontend') {
                    steps {
                        script {
                            def image = docker.build("${DOCKER_REGISTRY}/wattwise-frontend:${BUILD_NUMBER}", "./frontend")
                            docker.withRegistry("https://${DOCKER_REGISTRY}", 'docker-registry-creds') {
                                image.push()
                                image.push("latest")
                            }
                        }
                    }
                }
            }
        }
        
        stage('Deploy to Staging') {
            steps {
                sh '''
                    helm upgrade --install wattwise-staging k8s/wattwise-helm/ \
                        --namespace wattwise-staging \
                        --create-namespace \
                        --set backend.image.tag=${BUILD_NUMBER} \
                        --set frontend.image.tag=${BUILD_NUMBER} \
                        --values values-staging.yaml
                '''
            }
        }
        
        stage('Integration Tests') {
            steps {
                sh '''
                    # Wait for deployment
                    kubectl rollout status deployment/wattwise-staging-backend -n wattwise-staging
                    kubectl rollout status deployment/wattwise-staging-frontend -n wattwise-staging
                    
                    # Run integration tests
                    python tests/integration_tests.py --env staging
                '''
            }
        }
        
        stage('Deploy to Production') {
            when {
                branch 'main'
            }
            steps {
                input message: 'Deploy to production?', ok: 'Deploy'
                sh '''
                    helm upgrade --install wattwise k8s/wattwise-helm/ \
                        --namespace wattwise \
                        --set backend.image.tag=${BUILD_NUMBER} \
                        --set frontend.image.tag=${BUILD_NUMBER} \
                        --values values-production.yaml
                '''
            }
        }
    }
    
    post {
        always {
            sh 'docker system prune -f'
        }
    }
}
```

### GitHub Actions

```yaml
name: Deploy WattWise AI

on:
  push:
    branches: [main]
  pull_request:
    branches: [main]

jobs:
  test:
    runs-on: ubuntu-latest
    steps:
    - uses: actions/checkout@v3
    - name: Set up Python
      uses: actions/setup-python@v4
      with:
        python-version: '3.11'
    - name: Run tests
      run: |
        cd tests
        pip install -r requirements.txt
        python run_tests.py

  build:
    needs: test
    runs-on: ubuntu-latest
    if: github.ref == 'refs/heads/main'
    steps:
    - uses: actions/checkout@v3
    - name: Build and push Docker images
      env:
        DOCKER_REGISTRY: ${{ secrets.DOCKER_REGISTRY }}
        DOCKER_USERNAME: ${{ secrets.DOCKER_USERNAME }}
        DOCKER_PASSWORD: ${{ secrets.DOCKER_PASSWORD }}
      run: |
        echo $DOCKER_PASSWORD | docker login $DOCKER_REGISTRY -u $DOCKER_USERNAME --password-stdin
        
        # Build and push backend
        docker build -t $DOCKER_REGISTRY/wattwise-backend:$GITHUB_SHA ./backend
        docker push $DOCKER_REGISTRY/wattwise-backend:$GITHUB_SHA
        
        # Build and push frontend
        docker build -t $DOCKER_REGISTRY/wattwise-frontend:$GITHUB_SHA ./frontend
        docker push $DOCKER_REGISTRY/wattwise-frontend:$GITHUB_SHA

  deploy:
    needs: build
    runs-on: ubuntu-latest
    if: github.ref == 'refs/heads/main'
    steps:
    - uses: actions/checkout@v3
    - name: Deploy to Kubernetes
      env:
        KUBE_CONFIG: ${{ secrets.KUBE_CONFIG }}
      run: |
        echo "$KUBE_CONFIG" | base64 -d > kubeconfig
        export KUBECONFIG=kubeconfig
        
        helm upgrade --install wattwise k8s/wattwise-helm/ \
          --namespace wattwise \
          --set backend.image.tag=$GITHUB_SHA \
          --set frontend.image.tag=$GITHUB_SHA \
          --values values-production.yaml
```

## 📊 Monitoring & Observability

### Production Monitoring Stack

```yaml
# monitoring-stack.yaml
apiVersion: v1
kind: Namespace
metadata:
  name: monitoring
---
# Prometheus Operator
apiVersion: argoproj.io/v1alpha1
kind: Application
metadata:
  name: prometheus-operator
  namespace: argocd
spec:
  project: default
  source:
    repoURL: https://prometheus-community.github.io/helm-charts
    chart: kube-prometheus-stack
    targetRevision: 45.7.1
    helm:
      values: |
        prometheus:
          prometheusSpec:
            retention: 30d
            storageSpec:
              volumeClaimTemplate:
                spec:
                  storageClassName: fast-ssd
                  accessModes: ["ReadWriteOnce"]
                  resources:
                    requests:
                      storage: 100Gi
        grafana:
          adminPassword: secure-password
          persistence:
            enabled: true
            size: 10Gi
  destination:
    server: https://kubernetes.default.svc
    namespace: monitoring
```

### Alerting Rules

```yaml
# alerts.yaml
groups:
- name: wattwise.rules
  rules:
  - alert: WattWiseBackendDown
    expr: up{job="wattwise-backend"} == 0
    for: 1m
    labels:
      severity: critical
    annotations:
      summary: "WattWise backend is down"
      description: "WattWise backend has been down for more than 1 minute"

  - alert: HighResponseTime
    expr: histogram_quantile(0.95, rate(wattwise_request_duration_seconds_bucket[5m])) > 2
    for: 5m
    labels:
      severity: warning
    annotations:
      summary: "High response time detected"
      description: "95th percentile response time is {{ $value }}s"

  - alert: HighErrorRate
    expr: rate(wattwise_requests_total{status=~"5.."}[5m]) / rate(wattwise_requests_total[5m]) > 0.1
    for: 5m
    labels:
      severity: critical
    annotations:
      summary: "High error rate detected"
      description: "Error rate is {{ $value | humanizePercentage }}"
```

## 🔒 Security Hardening

### Container Security

```dockerfile
# Secure Dockerfile example
FROM python:3.11-slim

# Create non-root user
RUN groupadd -r wattwise && useradd -r -g wattwise wattwise

# Install security updates
RUN apt-get update && apt-get upgrade -y && \
    apt-get clean && rm -rf /var/lib/apt/lists/*

# Set working directory
WORKDIR /app

# Copy and install dependencies
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Copy application code
COPY . .
RUN chown -R wattwise:wattwise /app

# Switch to non-root user
USER wattwise

# Use read-only filesystem
VOLUME ["/tmp"]

# Health check
HEALTHCHECK --interval=30s --timeout=3s --start-period=5s --retries=3 \
  CMD curl -f http://localhost:8000/health || exit 1

EXPOSE 8000
CMD ["python", "startup.py"]
```

### Kubernetes Security

```yaml
# security-policies.yaml
apiVersion: policy/v1beta1
kind: PodSecurityPolicy
metadata:
  name: wattwise-psp
spec:
  privileged: false
  allowPrivilegeEscalation: false
  requiredDropCapabilities:
    - ALL
  volumes:
    - 'configMap'
    - 'emptyDir'
    - 'projected'
    - 'secret'
    - 'downwardAPI'
    - 'persistentVolumeClaim'
  runAsUser:
    rule: 'MustRunAsNonRoot'
  seLinux:
    rule: 'RunAsAny'
  fsGroup:
    rule: 'RunAsAny'
---
apiVersion: networking.k8s.io/v1
kind: NetworkPolicy
metadata:
  name: wattwise-netpol
  namespace: wattwise
spec:
  podSelector:
    matchLabels:
      app.kubernetes.io/name: wattwise-ai
  policyTypes:
  - Ingress
  - Egress
  ingress:
  - from:
    - namespaceSelector:
        matchLabels:
          name: ingress-nginx
    ports:
    - protocol: TCP
      port: 8000
    - protocol: TCP
      port: 8501
  egress:
  - to:
    - namespaceSelector:
        matchLabels:
          name: kube-system
    ports:
    - protocol: TCP
      port: 53
    - protocol: UDP
      port: 53
```

## 🔄 Backup & Disaster Recovery

### Database Backup

```bash
#!/bin/bash
# backup-database.sh

BACKUP_DIR="/backups/wattwise"
DATE=$(date +%Y%m%d_%H%M%S)
BACKUP_FILE="wattwise_backup_${DATE}.sql"

# Create backup directory
mkdir -p $BACKUP_DIR

# Perform backup
pg_dump -h $DB_HOST -U $DB_USER -d $DB_NAME > $BACKUP_DIR/$BACKUP_FILE

# Compress backup
gzip $BACKUP_DIR/$BACKUP_FILE

# Upload to S3 (optional)
aws s3 cp $BACKUP_DIR/${BACKUP_FILE}.gz s3://your-backup-bucket/database/

# Clean old backups (keep last 30 days)
find $BACKUP_DIR -name "*.gz" -mtime +30 -delete

echo "Backup completed: ${BACKUP_FILE}.gz"
```

### Application State Backup

```bash
#!/bin/bash
# backup-application.sh

BACKUP_DIR="/backups/wattwise"
DATE=$(date +%Y%m%d_%H%M%S)

# Backup Kubernetes resources
kubectl get all,configmaps,secrets,pvc -n wattwise -o yaml > $BACKUP_DIR/k8s_resources_${DATE}.yaml

# Backup Helm values
helm get values wattwise -n wattwise > $BACKUP_DIR/helm_values_${DATE}.yaml

# Backup persistent volumes
kubectl get pv -o yaml > $BACKUP_DIR/persistent_volumes_${DATE}.yaml

echo "Application state backup completed"
```

## 📈 Scaling Strategies

### Horizontal Scaling

```yaml
# HPA configuration
apiVersion: autoscaling/v2
kind: HorizontalPodAutoscaler
metadata:
  name: wattwise-backend-hpa
spec:
  scaleTargetRef:
    apiVersion: apps/v1
    kind: Deployment
    name: wattwise-backend
  minReplicas: 3
  maxReplicas: 20
  metrics:
  - type: Resource
    resource:
      name: cpu
      target:
        type: Utilization
        averageUtilization: 70
  - type: Resource
    resource:
      name: memory
      target:
        type: Utilization
        averageUtilization: 80
  behavior:
    scaleUp:
      stabilizationWindowSeconds: 60
      policies:
      - type: Percent
        value: 100
        periodSeconds: 15
    scaleDown:
      stabilizationWindowSeconds: 300
      policies:
      - type: Percent
        value: 10
        periodSeconds: 60
```

### Vertical Scaling

```yaml
# VPA configuration
apiVersion: autoscaling.k8s.io/v1
kind: VerticalPodAutoscaler
metadata:
  name: wattwise-backend-vpa
spec:
  targetRef:
    apiVersion: apps/v1
    kind: Deployment
    name: wattwise-backend
  updatePolicy:
    updateMode: "Auto"
  resourcePolicy:
    containerPolicies:
    - containerName: backend
      maxAllowed:
        cpu: 4
        memory: 8Gi
      minAllowed:
        cpu: 100m
        memory: 128Mi
```

---

**Ready for production?** Follow this guide step by step and your WattWise AI deployment will be robust, scalable, and secure! 🚀

