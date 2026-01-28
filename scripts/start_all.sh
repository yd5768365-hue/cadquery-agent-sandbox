echo "🚀 启动 CAE 自动化平台..."

cd E:/DeepSeek_Work/docker

# 启动 Docker 服务
docker-compose up -d

echo "✓ Docker 服务已启动"

# 启动 MCP 服务器（后台）
cd E:/DeepSeek_Work
nohup python server/server.py > server.log 2>&1 &

echo "✓ MCP 服务器已启动"

echo ""
echo "所有服务已启动！"
echo "访问 http://localhost:8501 查看仪表盘"


