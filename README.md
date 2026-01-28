# CAE Digital Twin Platform

## Quick Start

### 1. Access the System

**Dashboard (Main Interface)**
- URL: http://localhost:8501
- All services are running and accessible

**Flower (Task Monitoring)**
- URL: http://localhost:5555
- Monitor Celery tasks and workers

### 2. System Status

All containers are currently running:
```
✓ cae_dashboard      - http://localhost:8501
✓ cae_flower         - http://localhost:5555
✓ cae_celery_worker  - Background tasks
✓ cae_gmsh           - Mesh generation
✓ cae_calculix       - FEM simulation
✓ cae_postgres       - Database:5432
✓ cae_redis          - Queue:6379
```

### 3. Quick Test

Verify system functionality:
```bash
cd E:\DeepSeek_Work
python quick_test.py
```

### 4. Common Commands

**View all containers:**
```bash
docker ps --filter "name=cae_"
```

**View service logs:**
```bash
docker logs cae_dashboard --tail 50 -f
docker logs cae_celery_worker --tail 50 -f
```

**Restart services:**
```bash
cd docker
docker-compose restart
```

**Stop all services:**
```bash
cd docker
docker-compose down
```

**Start all services:**
```bash
cd docker
docker-compose up -d
```

### 5. What Can You Do?

#### Via Dashboard (http://localhost:8501)
1. **Real-time Monitoring** - View simulation statistics
2. **Data Analysis** - Analyze results and trends
3. **Model Management** - Train and test ML models
4. **Visualization** - Generate 3D visualizations
5. **Task Management** - Submit and monitor tasks

#### Via Direct Commands
```bash
# Generate mesh with Gmsh
docker exec -it cae_gmsh bash
gmsh /app/input/model.step -2 -o /app/meshes/model.msh

# Run simulation with CalculiX
docker exec -it cae_calculix bash
ccx -i /app/analyses/model

# Check database
docker exec -it cae_postgres psql -U cae_user -d cae_platform

# Check Redis
docker exec -it cae_redis redis-cli
```

### 6. File Locations

**Input Files:** `E:\DeepSeek_Work\test\input\`
**Mesh Files:** `E:\DeepSeek_Work\test\meshes\`
**Analysis Files:** `E:\DeepSeek_Work\test\analyses\`
**Result Files:** `E:\DeepSeek_Work\test\results\`
**Visualizations:** `E:\DeepSeek_Work\test\visualizations\`

### 7. Documentation

- **Detailed User Guide:** `USER_GUIDE.md`
- **Test Script:** `quick_test.py`
- **Deployment Config:** `docker/docker-compose.yml`

### 8. Troubleshooting

**Dashboard not loading?**
```bash
docker logs cae_dashboard --tail 50
docker restart cae_dashboard
```

**Tasks not running?**
```bash
docker logs cae_celery_worker --tail 50
docker restart cae_celery_worker
```

**Check all service health:**
```bash
docker ps --filter "name=cae_"
docker stats --filter "name=cae_"
```

### 9. Next Steps

1. Open http://localhost:8501 in your browser
2. Explore the dashboard interface
3. Upload or create geometry files in `test/input/`
4. Run mesh generation and simulations
5. View results and visualizations

---

**System Version:** 1.0.0
**Deployment:** Docker Compose
**Status:** Running ✓

For detailed information, see `USER_GUIDE.md`
