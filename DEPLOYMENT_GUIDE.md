# CAE 数字孪生平台部署指南

## 🚀 快速部署

### 系统要求

- **操作系统**: Linux/macOS/Windows (推荐 Linux 或 macOS)
- **Docker**: 20.10 或更高版本
- **Docker Compose**: 2.0 或更高版本
- **内存**: 至少 8GB RAM (推荐 16GB)
- **CPU**: 至少 4 核心 (推荐 8 核心)
- **存储**: 至少 50GB 可用空间

### 1. 克隆项目

```bash
git clone https://github.com/yd5768365-hue/cadquery-agent-sandbox.git
cd cadquery-agent-sandbox
```

### 2. 配置环境变量

```bash
# 复制并编辑环境变量文件
cd docker
cp .env.example .env

# 编辑 .env 文件，设置密码和配置
vim .env
```

```env
# .env 文件内容
POSTGRES_PASSWORD=your_secure_password
POSTGRES_USER=cae_user
POSTGRES_DB=cae_platform
DATABASE_URL=postgresql://cae_user:your_secure_password@postgres:5432/cae_platform
REDIS_URL=redis://redis:6379/0
CELERY_BROKER_URL=redis://redis:6379/0
CELERY_RESULT_BACKEND=redis://redis:6379/0
```

### 3. 启动服务

```bash
# 启动所有服务
cd docker
docker-compose up -d

# 检查服务状态
docker-compose ps

# 查看服务日志
docker-compose logs -f
```

### 4. 访问平台

服务启动后，可以通过以下地址访问：

- **Dashboard**: http://localhost:8501 (Streamlit 可视化界面)
- **Flower**: http://localhost:5555 (Celery 监控界面，用户: admin, 密码: secure_password)
- **API Server**: http://localhost:8000 (FastAPI 接口)

### 5. 验证部署

```bash
# 运行快速测试
cd ..
python quick_test.py
```

## 📦 项目架构

```
CAE Digital Twin Platform
├── 前端界面: Streamlit 仪表盘 (dashboard/)
├── 后端服务: FastAPI + Celery 异步任务队列 (server/)
├── 核心服务:
│   ├── 网格生成服务 (services/mesh_service.py)
│   ├── 仿真求解服务 (services/solve_service.py)
│   └── 可视化服务 (services/viz_service.py)
├── 机器学习: 代理模型、几何编码器 (ml/)
├── 智能体系统: 记忆管理与对话系统 (memory_skill/)
├── 部署配置: Docker + Kubernetes (docker/, k8s/)
└── 测试与文档: 完整的测试用例和文档
```

## 🔧 服务说明

### 1. 核心服务

| 服务名 | 端口 | 描述 |
|--------|------|------|
| **dashboard** | 8501 | Streamlit 可视化界面 |
| **flower** | 5555 | Celery 任务监控界面 |
| **postgres** | 5432 | PostgreSQL 数据库 |
| **redis** | 6379 | Redis 缓存和消息队列 |
| **gmsh-service** | - | Gmsh 网格生成服务 |
| **calculix-service** | - | CalculiX 仿真求解服务 |
| **ml-service** | - | 机器学习服务 |
| **visualize-service** | - | 可视化服务 |
| **celery-worker** | - | Celery 任务 worker |
| **celery-beat** | - | Celery 定时任务调度器 |

### 2. 数据存储

- **PostgreSQL**: 存储仿真参数、结果、用户信息等
- **Redis**: 缓存、消息队列
- **文件系统**: 存储 STEP 文件、网格文件、结果文件等

## 🚀 进阶部署

### 1. 生产环境部署

#### 1.1 Kubernetes 部署

```bash
cd k8s

# 1. 创建命名空间
kubectl create namespace cae-platform

# 2. 配置密码和证书
kubectl apply -f secrets.yaml
kubectl apply -f configmap.yaml

# 3. 部署服务
kubectl apply -f deployment.yml

# 4. 检查部署状态
kubectl get pods -n cae-platform
kubectl get services -n cae-platform
```

#### 1.2 使用 Helm 部署

```bash
cd helm-chart

# 查看默认配置
cat values.yaml

# 部署到 Kubernetes
helm install cae-platform . -n cae-platform --create-namespace
```

### 2. 自定义配置

#### 2.1 调整资源限制

编辑 `docker-compose.yml` 或 `k8s/deployment.yml` 中的 `resources` 部分：

```yaml
resources:
  requests:
    memory: "1Gi"
    cpu: "500m"
  limits:
    memory: "2Gi"
    cpu: "1000m"
```

#### 2.2 配置域名和 SSL

创建 `nginx/nginx.conf` 文件，配置域名和 SSL：

```nginx
server {
    listen 80;
    server_name your-domain.com;

    location / {
        proxy_pass http://localhost:8501;
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
        proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
        proxy_set_header X-Forwarded-Proto $scheme;
    }
}
```

## 🔍 故障排除

### 1. 常见问题

#### 1.1 端口冲突

```bash
# 检查端口占用
netstat -tuln | grep 8501
netstat -tuln | grep 5432
netstat -tuln | grep 6379

# 修改配置文件中的端口
# docker/.env 文件
# docker-compose.yml 文件
```

#### 1.2 服务启动失败

```bash
# 查看服务日志
docker-compose logs -f [service-name]

# 检查容器状态
docker-compose ps

# 重新启动服务
docker-compose restart [service-name]
```

#### 1.3 数据库连接失败

```bash
# 检查 PostgreSQL 服务是否正常
docker-compose logs -f postgres

# 连接到 PostgreSQL 容器
docker exec -it cae_postgres psql -U cae_user -d cae_platform

# 检查数据库连接字符串
# docker/.env 文件
# server/database.py 文件
```

### 2. 日志分析

```bash
# 查看所有服务日志
docker-compose logs -f

# 查看特定服务日志
docker-compose logs -f dashboard
docker-compose logs -f flower
docker-compose logs -f postgres
docker-compose logs -f redis
```

## 📈 监控与维护

### 1. 性能监控

#### 1.1 使用 Flower 监控 Celery

```
访问地址: http://localhost:5555
用户: admin
密码: secure_password
```

#### 1.2 使用 Prometheus + Grafana 监控

```bash
cd monitoring

# 启动 Prometheus 和 Grafana
docker-compose up -d

# 访问 Grafana
# 地址: http://localhost:3000
# 用户: admin
# 密码: admin123
```

### 2. 数据备份

```bash
# 备份 PostgreSQL 数据
docker exec -it cae_postgres pg_dump -U cae_user -d cae_platform > backup_$(date +%Y%m%d).sql

# 恢复 PostgreSQL 数据
cat backup_20240120.sql | docker exec -i cae_postgres psql -U cae_user -d cae_platform

# 备份 Redis 数据
docker exec -it cae_redis redis-cli bgsave
docker cp cae_redis:/data/dump.rdb backup_$(date +%Y%m%d).rdb

# 备份文件系统
tar -czf backup_$(date +%Y%m%d).tar.gz test/
```

## 📞 技术支持

### 1. 联系信息

- **GitHub Issues**: https://github.com/yd5768365-hue/cadquery-agent-sandbox/issues
- **Email**: [待补充]
- **B 站**: [待开通]

### 2. 社区支持

如果您在使用过程中遇到问题，可以：

1. 查看项目的 `README.md` 文件
2. 检查项目的 `docs/` 目录
3. 在 GitHub Issues 中搜索类似问题
4. 提交新的 Issue
5. 加入项目的 Discord 或 Slack 社区（待开通）

## 📄 许可证

本项目采用 MIT 许可证，详细信息请查看 `LICENSE` 文件。

## 🤝 贡献指南

如果您想为项目做出贡献，请查看 `CONTRIBUTING.md` 文件，了解如何提交 Pull Request 和报告问题。

---

**最后更新**: 2024-01-28
**版本**: v1.0.0
**作者**: 一位热爱 CAE 的大一学生
