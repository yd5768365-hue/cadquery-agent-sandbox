# 停止所有服务

echo "🛑 停止 CAE 自动化平台..."

# 停止 MCP 服务器
pkill -f "python server/server.py"

echo "✓ MCP 服务器已停止"

# 停止 Docker 服务
cd E:/DeepSeek_Work/docker
docker-compose down

echo "✓ Docker 服务已停止"

echo ""
echo "所有服务已停止"