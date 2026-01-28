echo "🔄 更新系统..."

cd E:/DeepSeek_Work

# 拉取最新代码（如果使用 Git）
# git pull

# 重建镜像
echo "重建 Docker 镜像..."
cd docker
docker-compose build --no-cache

# 重启服务
echo "重启服务..."
docker-compose down
docker-compose up -d

# 更新 Python 依赖
echo "更新 Python 依赖..."
pip install --upgrade -r requirements.txt

echo "✓ 更新完成"
