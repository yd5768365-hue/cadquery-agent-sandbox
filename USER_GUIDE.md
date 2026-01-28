# CAE Digital Twin Platform - User Guide

## Quick Start

### 1. System Overview

The CAE (Computer-Aided Engineering) Digital Twin Platform is a comprehensive simulation and analysis system that includes:

- **Dashboard** (Streamlit): Web-based interface for monitoring and analysis
- **Task Queue** (Celery + Redis): Asynchronous task processing
- **Database** (PostgreSQL): Metadata and result storage
- **Mesh Generation** (Gmsh): Finite element mesh generation
- **Simulation** (CalculiX): Finite element analysis solver
- **Visualization** (PyVista): 3D result visualization

### 2. Access the System

#### Main Dashboard
- URL: **http://localhost:8501**
- Features:
  - Real-time monitoring
  - Data analysis
  - Model management
  - 3D visualization
  - Task management

#### Flower Monitoring (Celery)
- URL: **http://localhost:5555**
- Features:
  - Task queue monitoring
  - Worker status
  - Task history
  - Performance metrics

### 3. System Commands

#### Start All Services
```bash
cd E:\DeepSeek_Work\docker
docker-compose up -d
```

#### Stop All Services
```bash
cd E:\DeepSeek_Work\docker
docker-compose down
```

#### Check Service Status
```bash
docker ps --filter "name=cae_"
```

#### View Service Logs
```bash
# Dashboard
docker logs cae_dashboard --tail 50 -f

# Celery Worker
docker logs cae_celery_worker --tail 50 -f

# Gmsh Service
docker logs cae_gmsh --tail 50

# CalculiX Service
docker logs cae_calculix --tail 50
```

#### Restart a Specific Service
```bash
docker restart cae_dashboard
docker restart cae_celery_worker
```

### 4. Quick Test

Run the quick test script to verify system functionality:

```bash
cd E:\DeepSeek_Work
python quick_test.py
```

### 5. Using the Dashboard

#### Page 1: Real-time Monitoring
- View simulation statistics
- Monitor success rates
- Track average computation time
- View recent simulation records

#### Page 2: Data Analysis
- Analyze simulation data by type
- View stress distributions
- Examine parameter correlations
- Generate statistical reports

#### Page 3: Model Management
- Train surrogate models
- Make quick predictions
- Evaluate model performance
- Export trained models

#### Page 4: Visualization
- Generate stress contour plots
- Create displacement visualizations
- Produce animation sequences
- View historical visualizations

#### Page 5: Task Management
- Monitor running tasks
- View task history
- Submit batch jobs
- Cancel active tasks

### 6. Workflow Example

#### Step 1: Prepare Geometry
Place your STEP files in:
```
E:\DeepSeek_Work\test\input\
```

#### Step 2: Generate Mesh
```bash
# In Gmsh container
docker exec -it cae_gmsh bash

# Generate mesh
gmsh /app/input/your_part.step -2 -o /app/meshes/your_part.msh
```

#### Step 3: Run Simulation
```bash
# In CalculiX container
docker exec -it cae_calculix bash

# Run analysis
ccx -i /app/analyses/your_model
```

#### Step 4: Visualize Results
- Access Dashboard at http://localhost:8501
- Navigate to "Visualization" page
- Enter result file path
- Select visualization type
- Click "Generate Visualization"

### 7. File Structure

```
E:\DeepSeek_Work\
├── docker/                  # Docker deployment files
│   ├── docker-compose.yml   # Service orchestration
│   └── *.Dockerfile         # Individual service containers
├── server/                  # Backend services
│   ├── server.py           # MCP server
│   ├── tasks.py            # Celery tasks
│   └── data_collector.py   # Data collection
├── dashboard/              # Frontend interface
│   └── app.py             # Streamlit application
├── ml/                     # Machine learning
│   ├── models/            # Model definitions
│   └── trainers/          # Training scripts
├── services/               # Additional services
│   └── viz_service.py     # Visualization service
└── test/                   # Working directory
    ├── input/             # Input files (STEP, etc.)
    ├── parts/             # Split assembly parts
    ├── meshes/            # Generated meshes
    ├── analyses/          # Simulation inputs
    ├── results/           # Calculation results
    └── visualizations/    # Generated images
```

### 8. Database Access

#### PostgreSQL
- Host: localhost
- Port: 5432
- Database: cae_platform
- User: cae_user
- Password: cae_pass_2024

Connect with:
```bash
docker exec -it cae_postgres psql -U cae_user -d cae_platform
```

#### Redis
- Host: localhost
- Port: 6379

Connect with:
```bash
docker exec -it cae_redis redis-cli
```

### 9. Troubleshooting

#### Dashboard not accessible
```bash
# Check container status
docker ps --filter name=cae_dashboard

# View logs
docker logs cae_dashboard --tail 100

# Restart service
docker restart cae_dashboard
```

#### Tasks not executing
```bash
# Check Celery worker
docker logs cae_celery_worker --tail 50

# Check Redis
docker logs cae_redis --tail 50

# Restart worker
docker restart cae_celery_worker
```

#### Container failed to start
```bash
# View container logs
docker logs <container_name>

# Check Docker disk space
docker system df

# Clean up unused resources
docker system prune -a
```

#### Port conflicts
If ports 8501 or 5555 are already in use, modify docker-compose.yml:
```yaml
dashboard:
  ports:
    - "8502:8501"  # Change external port

flower:
  ports:
    - "5556:5555"  # Change external port
```

### 10. Performance Tips

1. **Increase worker concurrency**: Modify `docker-compose.yml` for Celery worker:
   ```yaml
   celery-worker:
     command: sh -c "python -m celery -A tasks worker --loglevel=info --concurrency=8"
   ```

2. **Optimize mesh parameters**: Adjust Gmsh parameters in your workflow:
   ```
   -clmax 5.0    # Maximum element size
   -clmin 0.5    # Minimum element size
   -optimize     # Mesh optimization
   ```

3. **Monitor resource usage**:
   ```bash
   docker stats --filter "name=cae_"
   ```

### 11. Advanced Usage

#### Submit Celery Task via Python
```python
from celery import Celery

# Connect to Celery
celery_app = Celery('tasks', broker='redis://localhost:6379/0')

# Submit task
from server.tasks import run_gmsh_meshing
result = run_gmsh_meshing.delay('path/to/geometry.step', {'clmax': 5.0})

# Check status
print(f"Task ID: {result.id}")
print(f"Status: {result.status}")
print(f"Result: {result.get(timeout=300)}")
```

#### Access MCP Server
The MCP server (`server/server.py`) provides tools for:
- File operations
- STEP file analysis
- Assembly splitting
- Mesh generation
- CalculiX simulation
- Batch processing

### 12. Security Notes

- Default passwords are for development only
- Change database credentials before production use
- Limit external access to ports 8501, 5555, 5432, 6379
- Use Docker networks for inter-container communication
- Regularly update container images

### 13. Backup and Restore

#### Backup Database
```bash
docker exec cae_postgres pg_dump -U cae_user cae_platform > backup.sql
```

#### Restore Database
```bash
docker exec -i cae_postgres psql -U cae_user cae_platform < backup.sql
```

#### Backup Data Files
```bash
# Archive test directory
tar -czf cae_data_backup.tar.gz E:\DeepSeek_Work\test
```

### 14. Contact & Support

For issues or questions:
- Check container logs first
- Review the Quick Test output
- Consult the troubleshooting section
- Check Flower monitoring at http://localhost:5555

---

**Version:** 1.0.0
**Last Updated:** 2024-01-28
