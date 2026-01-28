echo "================================"
echo "CAE 自动化平台 - 一键部署"
echo "================================"

# 检查 Docker
if ! command -v docker &> /dev/null; then
    echo "❌ Docker 未安装，请先安装 Docker Desktop"
    exit 1
fi

echo "✓ Docker 已安装"

# 检查 Docker Compose
if ! command -v docker-compose &> /dev/null; then
    echo "❌ Docker Compose 未安装"
    exit 1
fi

echo "✓ Docker Compose 已安装"

# 创建目录结构
echo ""
echo "📁 创建目录结构..."

BASE_DIR="E:/DeepSeek_Work"

mkdir -p "$BASE_DIR/docker"
mkdir -p "$BASE_DIR/server"
mkdir -p "$BASE_DIR/ml/models"
mkdir -p "$BASE_DIR/ml/trainers"
mkdir -p "$BASE_DIR/ml/data"
mkdir -p "$BASE_DIR/dashboard/pages"
mkdir -p "$BASE_DIR/dashboard/components"
mkdir -p "$BASE_DIR/services"
mkdir -p "$BASE_DIR/config"
mkdir -p "$BASE_DIR/scripts"
mkdir -p "$BASE_DIR/test/input"
mkdir -p "$BASE_DIR/test/parts"
mkdir -p "$BASE_DIR/test/meshes"
mkdir -p "$BASE_DIR/test/analyses"
mkdir -p "$BASE_DIR/test/results"
mkdir -p "$BASE_DIR/test/visualizations"

echo "✓ 目录结构创建完成"

# 构建镜像
echo ""
echo "🐳 构建 Docker 镜像..."

cd "$BASE_DIR/docker"

# 构建各个服务
docker-compose build

if [ $? -ne 0 ]; then
    echo "❌ 镜像构建失败"
    exit 1
fi

echo "✓ 镜像构建完成"

# 启动服务
echo ""
echo "🚀 启动服务..."

docker-compose up -d

if [ $? -ne 0 ]; then
    echo "❌ 服务启动失败"
    exit 1
fi

echo "✓ 服务启动成功"

# 等待服务就绪
echo ""
echo "⏳ 等待服务就绪..."
sleep 10

# 检查服务状态
echo ""
echo "🔍 检查服务状态..."

docker-compose ps

# 初始化数据库
echo ""
echo "💾 初始化数据库..."

python3 << EOF
import sys
sys.path.append('$BASE_DIR')
from server.data_collector import SimulationDataCollector

collector = SimulationDataCollector()
print("✓ 数据库初始化完成")
EOF

# 显示访问信息
echo ""
echo "================================"
echo "✅ 部署完成！"
echo "================================"
echo ""
echo "服务访问地址："
echo "  - 数字孪生仪表盘: http://localhost:8501"
echo "  - Celery 监控 (Flower): http://localhost:5555"
echo "  - Redis: localhost:6379"
echo "  - PostgreSQL: localhost:5432"
echo ""
echo "后续步骤："
echo "  1. 启动 MCP 服务器: python server/server.py"
echo "  2. 配置 Cherry Studio 连接到 MCP"
echo "  3. 访问仪表盘查看系统状态"
echo ""
echo "管理命令："
echo "  - 查看日志: docker-compose logs -f [服务名]"
echo "  - 停止服务: docker-compose down"
echo "  - 重启服务: docker-compose restart"
echo ""