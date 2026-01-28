echo "💾 开始备份..."

BACKUP_DIR="E:/DeepSeek_Work/backups/$(date +%Y%m%d_%H%M%S)"
mkdir -p "$BACKUP_DIR"

# 备份数据库
echo "备份数据库..."
docker exec cae_postgres pg_dump -U cae_user cae_platform > "$BACKUP_DIR/database.sql"

# 备份仿真历史
echo "备份仿真历史..."
cp E:/DeepSeek_Work/ml/data/simulation_history.db "$BACKUP_DIR/"

# 备份模型
echo "备份模型..."
cp -r E:/DeepSeek_Work/ml/models/*.pkl "$BACKUP_DIR/" 2>/dev/null

# 备份配置
echo "备份配置..."
cp -r E:/DeepSeek_Work/config "$BACKUP_DIR/"

echo "✓ 备份完成: $BACKUP_DIR"
