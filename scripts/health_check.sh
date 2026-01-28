echo "🏥 系统健康检查..."

# 检查 Docker 服务
echo ""
echo "检查 Docker 服务:"
docker ps --format "table {{.Names}}\t{{.Status}}\t{{.Ports}}"

# 检查 Redis
echo ""
echo "检查 Redis:"
docker exec cae_redis redis-cli ping

# 检查 PostgreSQL
echo ""
echo "检查 PostgreSQL:"
docker exec cae_postgres pg_isready -U cae_user

# 检查 Celery Worker
echo ""
echo "检查 Celery Worker:"
docker exec cae_celery_worker celery -A tasks inspect active

# 检查磁盘空间
echo ""
echo "检查磁盘空间:"
df -h E:/DeepSeek_Work

echo ""
echo "✓ 健康检查完成"
