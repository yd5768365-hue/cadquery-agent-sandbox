# CAE Digital Twin Platform

A comprehensive Computer-Aided Engineering (CAE) Digital Twin platform built with Docker, Celery, and Streamlit for real-time simulation, mesh generation, and data visualization.

## 🚀 Features

- **Real-time Simulation** - FEM analysis using CalculiX
- **Mesh Generation** - High-quality mesh generation with Gmsh
- **Dashboard** - Interactive web interface built with Streamlit
- **Task Queue** - Asynchronous task processing with Celery
- **ML Integration** - Machine learning models for optimization
- **Data Visualization** - 3D visualization with PyVista
- **Monitoring** - Real-time task monitoring with Flower

## 📋 Table of Contents

- [Prerequisites](#prerequisites)
- [Quick Start](#quick-start)
- [Development](#development)
- [Production Deployment](#production-deployment)
- [CI/CD Pipeline](#cicd-pipeline)
- [Configuration](#configuration)
- [Testing](#testing)
- [Troubleshooting](#troubleshooting)
- [Contributing](#contributing)

## 🛠️ Prerequisites

- Docker Desktop (or Docker Engine)
- Docker Compose
- Python 3.10+
- Git

## 🚀 Quick Start

### 1. Clone the Repository

```bash
git clone https://github.com/yd5768365-hue/cadquery-agent-sandbox.git
cd cadquery-agent-sandbox
```

### 2. Start Services

```bash
cd docker
docker-compose up -d
```

### 3. Access the Dashboard

Open your browser and navigate to:
- **Dashboard**: http://localhost:8501
- **Flower Monitoring**: http://localhost:5555
- **API Health**: http://localhost/health

### 4. Run Quick Tests

```bash
cd ..
python quick_test.py
```

## 💻 Development

### Local Development Setup

#### Option 1: Using Docker (Recommended)

```bash
# Start all services
cd docker
docker-compose up -d

# View logs
docker-compose logs -f

# Stop services
docker-compose down
```

#### Option 2: Local Python Environment

```bash
# Install dependencies
pip install -r requirements.txt

# Start Dashboard
cd dashboard
streamlit run app.py --server.port=8501

# Start Celery Worker (new terminal)
cd server
celery -A tasks worker --loglevel=info

# Start Flower (new terminal)
celery -A tasks flower --port=5555
```

### Running Tests

```bash
# Run all tests
pytest

# Run with coverage
pytest --cov=. --cov-report=html

# Run specific test
pytest tests/test_dashboard.py
```

### Code Quality Checks

```bash
# Format code
black .
isort .

# Lint code
flake8 .
mypy server/

# Run security scan
trivy fs .
```

## 🌐 Production Deployment

### Docker Compose Production

#### 1. Setup Secrets

```bash
cd docker-production

# Generate secure passwords
openssl rand -base64 32 > ../secrets/postgres_password.txt
openssl rand -base64 16 > ../secrets/flower_password.txt

# Generate htpasswd for Nginx
htpasswd -bnC admin YOUR_PASSWORD > ../nginx/.htpasswd
```

#### 2. Configure Environment

Edit `docker-compose.yml` and update:
- Database credentials
- Redis configuration
- API keys and secrets

#### 3. Deploy

```bash
# Build and start services
docker-compose -f docker-production/docker-compose.yml up -d --build

# Check service health
docker-compose -f docker-production/docker-compose.yml ps
docker-compose -f docker-production/docker-compose.yml logs
```

#### 4. Access Services

- **Application**: http://your-server-ip
- **Flower**: http://your-server-ip/flower/
- **Health Check**: http://your-server-ip/health

### Kubernetes Deployment

#### 1. Install kubectl and Configure Cluster

```bash
# Install kubectl (if not installed)
curl -LO "https://dl.k8s.io/release/$(curl -L -s https://dl.k8s.io/release/stable.txt)/bin/linux/amd64/kubectl"
sudo install -o root -g root -m 0755 kubectl /usr/local/bin/kubectl

# Configure cluster context
kubectl config use-context your-cluster-name
```

#### 2. Deploy to Kubernetes

```bash
# Create namespace
kubectl create namespace cae-platform

# Deploy all resources
kubectl apply -f k8s/

# Check deployment status
kubectl get pods -n cae-platform
kubectl get services -n cae-platform

# View logs
kubectl logs -n cae-platform -l app=cae-dashboard -f
```

#### 3. Configure Ingress (Optional)

```yaml
apiVersion: networking.k8s.io/v1
kind: Ingress
metadata:
  name: cae-ingress
  namespace: cae-platform
  annotations:
    kubernetes.io/ingress.class: nginx
    cert-manager.io/cluster-issuer: letsencrypt-prod
spec:
  tls:
  - hosts:
    - cae.yourdomain.com
    secretName: cae-tls
  rules:
  - host: cae.yourdomain.com
    http:
      paths:
      - path: /
        pathType: Prefix
        backend:
          service:
            name: cae-dashboard
            port:
              number: 80
```

## 🔄 CI/CD Pipeline

The project uses GitHub Actions for continuous integration and deployment.

### Workflow Triggers

- Push to `main` or `develop` branches
- Pull requests to `main` or `develop` branches

### Pipeline Stages

1. **Lint** - Code quality checks (Black, isort, flake8, mypy)
2. **Security** - Vulnerability scanning with Trivy
3. **Test** - Unit tests with coverage reporting
4. **Build** - Docker image build and push to registry
5. **Deploy** - Automatic deployment to production (main branch only)

### Manual Deployment

```bash
# Build and push images manually
docker build -f docker/dashboard.Dockerfile -t ghcr.io/yd5768365-hue/cadquery-agent-sandbox-dashboard:latest .
docker push ghcr.io/yd5768365-hue/cadquery-agent-sandbox-dashboard:latest
```

## ⚙️ Configuration

### Environment Variables

| Variable | Description | Default |
|----------|-------------|---------|
| `DATABASE_URL` | PostgreSQL connection string | `postgresql://cae_user:cae_pass_2024@postgres:5432/cae_platform` |
| `REDIS_URL` | Redis connection string | `redis://redis:6379/0` |
| `CELERY_BROKER_URL` | Celery broker URL | `redis://redis:6379/0` |
| `CELERY_RESULT_BACKEND` | Celery result backend | `redis://redis:6379/0` |
| `PYTHONPATH` | Python module path | `/app:/server:/ml:/services` |

### File Structure

```
cae-digital-twin/
├── docker/                    # Development Docker Compose
├── docker-production/         # Production Docker Compose
├── k8s/                       # Kubernetes manifests
├── dashboard/                 # Streamlit dashboard
│   ├── app.py                # Main application
│   └── pages/                # Additional pages
├── server/                   # Backend services
│   ├── server.py             # FastAPI server
│   ├── tasks.py              # Celery tasks
│   └── data_collector.py     # Data collection
├── ml/                       # Machine learning models
├── services/                 # External service integrations
├── scripts/                  # Utility scripts
├── test/                     # Test files and data
├── config/                   # Configuration files
├── nginx/                    # Nginx configuration
├── secrets/                  # Sensitive data (not committed)
└── requirements.txt          # Python dependencies
```

## 🧪 Testing

### Unit Tests

```bash
# Run all tests
pytest

# Run with coverage
pytest --cov=. --cov-report=html

# Run specific test file
pytest tests/test_tasks.py
```

### Integration Tests

```bash
# Run integration tests
pytest tests/integration/

# Test API endpoints
pytest tests/integration/test_api.py
```

### E2E Tests

```bash
# Run end-to-end tests
python test_system.py
```

## 🔧 Troubleshooting

### Docker Issues

**Containers won't start**
```bash
# Check Docker is running
docker ps

# View container logs
docker logs cae_dashboard

# Restart containers
docker-compose restart
```

**Out of memory**
```bash
# Reduce memory limits in docker-compose.yml
# Or increase Docker Desktop memory allocation
```

### Database Issues

**Connection refused**
```bash
# Check PostgreSQL is running
docker ps | grep postgres

# View PostgreSQL logs
docker logs cae_postgres

# Connect to database
docker exec -it cae_postgres psql -U cae_user -d cae_platform
```

### Celery Issues

**Tasks not executing**
```bash
# Check Celery worker is running
docker logs cae_celery_worker

# Check Redis is running
docker logs cae_redis

# Connect to Redis
docker exec -it cae_redis redis-cli
> PING
```

### Dashboard Issues

**Streamlit not loading**
```bash
# Check dashboard logs
docker logs cae_dashboard

# Restart dashboard
docker restart cae_dashboard

# Verify Streamlit configuration
cat dashboard/.streamlit/config.toml
```

## 📊 Monitoring

### Flower Monitoring

Access Flower at http://localhost:5555 to monitor:
- Active Celery tasks
- Worker status
- Task history
- Performance metrics

### Logs

```bash
# View all logs
docker-compose logs

# View specific service logs
docker logs cae_dashboard -f
docker logs cae_celery_worker -f

# View logs from Kubernetes
kubectl logs -n cae-platform -l app=cae-dashboard -f
```

### Metrics

The platform integrates with Prometheus for metrics collection:
- Request latency
- Task execution time
- Error rates
- Resource utilization

## 🤝 Contributing

We welcome contributions! Please follow these steps:

1. Fork the repository
2. Create a feature branch (`git checkout -b feature/amazing-feature`)
3. Commit your changes (`git commit -m 'Add amazing feature'`)
4. Push to the branch (`git push origin feature/amazing-feature`)
5. Open a Pull Request

### Code Style

- Follow PEP 8 for Python code
- Use Black for code formatting
- Write unit tests for new features
- Update documentation as needed

## 📄 License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.

## 🙏 Acknowledgments

- CalculiX for FEM simulation
- Gmsh for mesh generation
- Streamlit for the web interface
- Celery for task queue management
- PyVista for 3D visualization

## 📞 Support

For support, please:
- Open an issue on GitHub
- Email: support@example.com
- Documentation: [USER_GUIDE.md](USER_GUIDE.md)

## 🔗 Links

- [GitHub Repository](https://github.com/yd5768365-hue/cadquery-agent-sandbox)
- [Docker Hub](https://hub.docker.com/r/yd5768365-hue/cae-digital-twin)
- [Documentation](https://cae-digital-twin.readthedocs.io)

---

**System Version**: 1.0.0
**Last Updated**: 2026-01-28
