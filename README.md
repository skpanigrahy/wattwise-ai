# ⚡ WattWise AI

> Run AI cheaper, greener, and smarter.

![Demo](docs/demo.gif)

![Python](https://img.shields.io/badge/Python-3.11-blue)
![FastAPI](https://img.shields.io/badge/FastAPI-Backend-green)
![Docker](https://img.shields.io/badge/Docker-Ready-blue)
![Status](https://img.shields.io/badge/Status-Active-orange)
![PostgreSQL](https://img.shields.io/badge/PostgreSQL-DB-blue)
![License](https://img.shields.io/badge/License-MIT-yellow)

# 🌱 WattWise AI

AI Efficiency Platform for Green Energy Optimization & Cost Intelligence

## 😓 The Problem

AI usage is growing rapidly, but:

- No visibility into cost
- Expensive models overused
- No optimization insights

👉 AI cost becomes the new cloud bill problem.

## 🚀 The Solution

**AI Efficiency Platform for Green Energy Optimization & Cost Intelligence**

WattWise AI is a platform that optimizes AI workloads across two critical dimensions:

- 🌱 **GreenOps**: Where AI workloads should run (energy, carbon, cost)
- 💰 **CostOps**: How efficiently AI is being used (tokens, models, prompts)
- 🧠 **Intelligence**: how to improve efficiency

It helps organizations minimize both **carbon footprint** and **AI usage cost**, while maintaining performance and scalability.

👉 One platform for complete AI efficiency.

## 🧠 Vision

To make AI workloads:

- 🌱 Sustainable (GreenOps)
- 💰 Cost-efficient (CostOps)
- 🧠 Intelligent (Optimization Engine)

WattWise AI aims to become the **“Datadog for AI efficiency”**.

## 🚀 Why WattWise AI?

Most platforms optimize either infrastructure OR AI usage.

WattWise AI uniquely optimizes BOTH:

| Dimension       | Capability                           |
| --------------- | ------------------------------------ |
| 🌱 GreenOps     | Reduce carbon & energy cost          |
| 💰 CostOps      | Reduce AI API cost                   |
| 🧠 Intelligence | Improve efficiency & decision making |

👉 This makes WattWise AI a **complete AI efficiency platform**.

## 🚀 Features

### Core Capabilities

- **Green Energy Optimization**: Schedules workloads based on renewable energy availability
- **Multi-Region Support**: Manages workloads across multiple cloud regions
- **Cost Optimization**: Balances green energy goals with cost efficiency
- **Carbon Tracking**: Monitors and reports carbon emissions for all workloads
- **AI Assistant**: LangChain-powered assistant for green computing recommendations

### Technical Features

- **FastAPI Backend**: High-performance REST API with automatic documentation
- **Streamlit Dashboard**: Interactive web interface for monitoring and management
- **PostgreSQL Database**: Robust data storage with SQLAlchemy ORM
- **Prometheus Monitoring**: Comprehensive metrics and observability
- **Kubernetes Ready**: Production-ready Helm charts for K8s deployment
- **CI/CD Pipeline**: Jenkins-based automated testing and deployment

### 💰 CostOps & AI Intelligence (NEW)

- **AI Usage Tracking**: Track token usage per user, model, and tool
- **Cost Analytics**: Real-time cost breakdown by model and user
- **Model Optimization**: Recommend cheaper models for same tasks
- **Prompt Optimization**: Reduce token usage via prompt rewriting
- **Multi-Model Benchmarking**: Compare cost vs quality across models
- **Quality Scoring**: Evaluate response efficiency
- **Cost Saving Insights**: Identify wasted spend and optimization opportunities

## 🏗️ Architecture

```
Frontend (Streamlit)
        │
        ▼
Backend (FastAPI)
   ├── GreenOps Engine (Scheduler)
   ├── CostOps Engine (NEW)
   ├── Optimization Engine (NEW)
        │
        ▼
Database (PostgreSQL)

```

🚀 Demo (Story)
📸 Screenshots
⚠️ Note: These are conceptual UI representations. Actual UI may vary.

WattWise AI Dashboard Overview

What This Shows
📊 AI cost tracking dashboard
🧠 Optimization recommendations
📈 Model cost breakdown
🔬 Benchmark comparison (cost vs quality)

These screenshots demonstrate the type of insights WattWise AI provides.

## 📋 Prerequisites

- **Docker & Docker Compose**: For containerized deployment
- **Python 3.11+**: For local development
- **PostgreSQL 15+**: Database (or use Docker)
- **Node.js 18+**: For any frontend tooling (optional)

## 🚀 Quick Start

### 1. Clone the Repository

```bash
git clone https://github.com/your-org/wattwise-ai.git
cd wattwise-ai
```

### 2. Environment Setup

```bash
# Copy environment files
cp backend/.env.example backend/.env
cp frontend/.env.example frontend/.env

# Edit configuration as needed
nano backend/.env
```

### 3. Start with Docker Compose

```bash
# Start all services
docker-compose up -d

# Check service status
docker-compose ps

# View logs
docker-compose logs -f
```

### 4. Access the Application

- **Frontend Dashboard**: http://localhost:8501
- **Backend API**: http://localhost:8000
- **API Documentation**: http://localhost:8000/docs
- **Prometheus**: http://localhost:9090
- **Grafana**: http://localhost:3000 (admin/admin123)

## 🛠️ Development Setup

### Backend Development

```bash
cd backend

# Create virtual environment
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate

# Install dependencies
pip install -r requirements.txt

# Initialize database
python manage_db.py init

# Start development server
python startup.py
```

### Frontend Development

```bash
cd frontend

# Install dependencies
pip install -r requirements.txt

# Start development server
python run.py
```

### Running Tests

```bash
cd tests

# Install test dependencies
pip install -r requirements.txt

# Run all tests
python run_tests.py

# Run specific test types
python run_tests.py --type api
python run_tests.py --type scheduler
```

## 📊 Usage Guide

### Scheduling a Workload

1. **Via Dashboard**: Navigate to "Schedule Workload" page
2. **Via API**: POST to `/jobs/schedule`

```python
import requests

workload = {
    "name": "LLM Training Job",
    "workload_type": "llm_training",
    "priority": "high",
    "estimated_duration_hours": 4.0,
    "gpu_requirements": {"A100": 2},
    "memory_gb": 64,
    "cpu_cores": 16,
    "max_cost_per_hour": 50.0,
    "max_carbon_emissions": 10.0
}

response = requests.post("http://localhost:8000/jobs/schedule", json=workload)
result = response.json()
print(f"Scheduled to region: {result['recommended_region']}")
```

### Querying the AI Assistant

```python
query = {
    "query": "Which region has the best green energy score right now?"
}

response = requests.post("http://localhost:8000/agent/query", json=query)
print(response.json()["response"])
```

## 🔧 Configuration

### Environment Variables

#### Backend (.env)

```bash
DATABASE_URL=postgresql://wattwise:wattwise123@localhost:5432/wattwise_db
OPENAI_API_KEY=your_openai_api_key_here  # Optional
PORT=8000
DEBUG=true
```

#### Frontend (.env)

```bash
BACKEND_URL=http://localhost:8000
```

### Database Configuration

```bash
# Check database connection
python backend/manage_db.py check

# Initialize with sample data
python backend/manage_db.py init

# Reset database (WARNING: Deletes all data)
python backend/manage_db.py reset
```

## 🚢 Production Deployment

### Docker Deployment

```bash
# Production docker-compose
docker-compose -f docker-compose.prod.yml up -d
```

### Kubernetes Deployment

```bash
# Add Helm repository dependencies
helm dependency update k8s/wattwise-helm/

# Install with Helm
helm install wattwise k8s/wattwise-helm/ \
  --namespace wattwise \
  --create-namespace \
  --values k8s/wattwise-helm/values-prod.yaml

# Check deployment
kubectl get pods -n wattwise
```

### SSH Deployment

```bash
# Deploy to staging
./deploy/deploy_ssh.sh staging

# Deploy to production
./deploy/deploy_ssh.sh production
```

## 📈 Monitoring & Observability

### Metrics Available

- **Request Metrics**: Rate, duration, status codes
- **Workload Metrics**: Scheduled jobs, duration, costs
- **Region Metrics**: Green energy scores, carbon intensity
- **System Metrics**: CPU, memory, disk usage

### Grafana Dashboards

1. **WattWise AI Overview**: Main application metrics
2. **Green Energy Tracking**: Regional energy data
3. **Cost Analysis**: Workload costs and optimization
4. **System Health**: Infrastructure monitoring

### Alerts (Prometheus)

- High error rates
- Long response times
- Low green energy scores
- High carbon emissions

## 🧪 Testing

### Test Structure

```
tests/
├── conftest.py          # Test configuration and fixtures
├── test_api.py          # API endpoint tests
├── test_scheduler.py    # Scheduling logic tests
├── test_assistant.py    # AI assistant tests
├── test_models.py       # Database model tests
└── run_tests.py         # Test runner script
```

### Running Tests

```bash
# All tests with coverage
python tests/run_tests.py

# Specific test categories
python tests/run_tests.py --type api
python tests/run_tests.py --type scheduler
python tests/run_tests.py --type models

# Without coverage
python tests/run_tests.py --no-coverage
```

## 🔒 Security

### Security Features

- **Non-root containers**: All Docker containers run as non-root users
- **Read-only filesystems**: Containers use read-only root filesystems
- **Secret management**: Sensitive data stored in Kubernetes secrets
- **Network policies**: Kubernetes network segmentation (optional)
- **HTTPS/TLS**: Production deployments use encrypted connections

### Security Checklist

- [ ] Change default passwords
- [ ] Configure TLS certificates
- [ ] Set up network policies
- [ ] Enable audit logging
- [ ] Regular security updates

## 🤝 Contributing

### Development Workflow

1. Fork the repository
2. Create a feature branch: `git checkout -b feature/amazing-feature`
3. Make your changes
4. Run tests: `python tests/run_tests.py`
5. Commit changes: `git commit -m 'Add amazing feature'`
6. Push to branch: `git push origin feature/amazing-feature`
7. Open a Pull Request

### Code Standards

- **Python**: Follow PEP 8, use type hints
- **Testing**: Maintain >90% test coverage
- **Documentation**: Update docs for new features
- **Commits**: Use conventional commit messages

## 📚 API Documentation

### Core Endpoints

| Endpoint                      | Method | Description              |
| ----------------------------- | ------ | ------------------------ |
| `/`                           | GET    | Health check and info    |
| `/jobs/schedule`              | POST   | Schedule a new workload  |
| `/regions/scores`             | GET    | Get green energy scores  |
| `/agent/query`                | POST   | Query AI assistant       |
| `/metrics`                    | GET    | Prometheus metrics       |
| `/costops/usage`              | POST   | Track AI usage           |
| `/costops/analytics/models`   | GET    | Cost by model            |
| `/costops/optimize/model`     | POST   | Model optimization       |
| `/costops/optimize/prompt`    | POST   | Prompt optimization      |
| `/costops/advanced/benchmark` | POST   | Multi-model benchmarking |

### Full API Documentation

Visit http://localhost:8000/docs for interactive API documentation.

## 🗂️ Project Structure

```
### 🔹 Backend Modules

- **GreenOps** → AI workload scheduling
- **CostOps** → AI usage & cost tracking
- **Optimization Engine** → Efficiency & intelligence layer

## 🗂️ Project Structure

```

wattwise-ai/
├── backend/ # FastAPI backend
│ ├── agent/ # LangChain AI assistant
│ ├── scheduler/ # GreenOps: workload scheduling logic
│ ├── api/ # API layer
│ │ ├── usage.py # CostOps: usage tracking
│ │ ├── analytics.py # Cost analytics
│ │ ├── optimization.py # Model & prompt optimization
│ │ ├── benchmark.py # Multi-model benchmarking
│ │ └── (existing APIs...)
│ │
│ ├── models/ # Database models
│ │ ├── usage_event.py # CostOps usage tracking model
│ │ └── (existing models...)
│ │
│ ├── service/ # Business logic layer (NEW)
│ │ ├── cost_calculator.py # Token → cost calculation
│ │ ├── pricing_registry.py # Model pricing config
│ │ ├── analytics_service.py # Cost aggregation logic
│ │ ├── optimization_service.py # Cost optimization engine
│ │ ├── model_recommender.py # Model recommendation logic
│ │ ├── prompt_optimizer.py # Rule-based prompt optimization
│ │ ├── benchmarking_service.py # Multi-model execution
│ │ ├── quality_scorer.py # Response quality scoring
│ │ ├── llm_client.py # LLM abstraction layer
│ │ └── prompt_rewriter.py # LLM-based prompt rewriting
│ │
│ ├── db/ # Database configuration
│ ├── alembic/ # Database migrations
│ └── main.py # FastAPI entry point
│
├── frontend/ # Streamlit dashboard
│ └── app.py # Main UI (CostOps + GreenOps)
│
├── tests/ # Test suite
│
├── monitoring/ # Prometheus & Grafana configs
├── k8s/ # Kubernetes Helm charts
├── deploy/ # Deployment scripts
│
├── docker-compose.yml # Local development setup
├── Jenkinsfile # CI/CD pipeline
├── README.md # Project documentation
└── sample_data/ # Demo datasets (CostOps)

````

## 🐛 Troubleshooting

### Common Issues

**Database Connection Failed**

```bash
# Check PostgreSQL status
docker-compose ps postgres

# Check logs
docker-compose logs postgres

# Reset database
python backend/manage_db.py reset
````

**Frontend Can't Connect to Backend**

```bash
# Check backend status
curl http://localhost:8000/health

# Check environment variables
cat frontend/.env
```

**High Memory Usage**

```bash
# Check container resources
docker stats

# Scale down replicas
docker-compose up -d --scale backend=1
```

## 🎬 Demo: From Cost Leak to Optimization

### 👨‍💻 Scenario

A developer uses expensive AI models like GPT-4 for most tasks without visibility into cost.

---

### 🟥 Before WattWise AI

- Monthly AI Spend: ₹48,000
- GPT-4 Usage: 80%
- No visibility into cost

---

### 🟩 After WattWise AI

- Monthly AI Spend: ₹14,000
- Savings: **70% reduction**
- Optimized model usage

---

### 🧠 Insight Generated

> “70% of queries can be handled by cheaper models with minimal quality loss”

---

### 📊 Key Features Demonstrated

- Cost tracking per user and model
- Model optimization recommendations
- Multi-model benchmarking
- Prompt efficiency improvements

---

👉 WattWise AI helps organizations run AI **cheaper, greener, and smarter** ⚡

## 📄 License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.

## 🙏 Acknowledgments

- **FastAPI**: High-performance web framework
- **Streamlit**: Rapid dashboard development
- **LangChain**: AI assistant capabilities
- **Prometheus**: Monitoring and alerting
- **PostgreSQL**: Reliable data storage

## 📞 Support

- **Documentation**: [Wiki](https://github.com/your-org/wattwise-ai/wiki)
- **Issues**: [GitHub Issues](https://github.com/your-org/wattwise-ai/issues)
- **Discussions**: [GitHub Discussions](https://github.com/your-org/wattwise-ai/discussions)
- **Email**: support@wattwise.ai

---

**Made with 💚 for a sustainable future**
