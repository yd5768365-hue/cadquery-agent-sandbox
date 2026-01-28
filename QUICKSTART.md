# 快速开始指南

## 1. 确认服务状态

所有服务正在运行：

```bash
docker ps --filter "name=cae_"
```

访问：
- Dashboard: http://localhost:8501
- Flower: http://localhost:5555

## 2. 准备第一个任务

### 方案 A：使用 Dashboard（推荐）

1. **打开 Dashboard**
   - 访问：http://localhost:8501
   - 选择：实时监控 页面
   - 查看系统状态

2. **提交网格任务**
   - 点击：任务管理
   - 任务类型：网格生成
   - 几何文件：输入或选择
   - 参数：
     - 最大网格尺寸：5.0
     - 最小网格尺寸：0.5
     - 单元类型：tetra
   - 点击：提交任务

3. **提交仿真任务**
   - 任务类型：应力分析
   - 输入文件：/app/test/analyses/test_cube.inp
   - 材料参数：
     - 弹性模量：210000 MPa
     - 泊松比：0.3
   - 提交任务

4. **查看结果**
   - 点击：可视化
   - 结果文件：/app/test/results/test_cube.frd
   - 可视化类型：应力云图
   - 生成可视化

### 方案 B：使用命令行（快速测试）

```bash
# 1. 进入 CalculiX 容器
docker exec -it cae_calculix bash

# 2. 运行仿真
cd /app/test/analyses
ccx -i test_cube

# 3. 查看结果
ls -la /app/test/results/
cat test_cube.out
```

## 3. 监控任务

### 使用 Flower
访问：http://localhost:5555

查看：
- Worker 状态
- 任务队列
- 任务执行历史
- 成功/失败统计

### 使用 Dashboard
- 实时监控页面：查看系统指标
- 任务管理页面：查看任务进度
- 数据分析页面：分析结果数据

## 4. 查看结果

结果文件位置：
```
E:\DeepSeek_Work\test\results\
```

文件类型：
- .frd - CalculiX 结果文件
- .dat - 数值结果
- .out - 仿真日志
- .sta - 状态文件

## 5. 常用命令

```bash
# 查看日志
docker logs cae_dashboard -f
docker logs cae_celery_worker -f
docker logs cae_calculix -f

# 重启服务
docker restart cae_dashboard
docker restart cae_celery_worker

# 进入容器
docker exec -it cae_gmsh bash
docker exec -it cae_calculix bash
docker exec -it cae_dashboard bash

# 查看文件
docker exec -it cae_dashboard ls -la /app/test/
```

## 6. 文件路径映射

容器内路径 -> Windows 路径：
```
/app/test/            -> E:\DeepSeek_Work\test\
/app/test/input/     -> E:\DeepSeek_Work\test\input\
/app/test/meshes/    -> E:\DeepSeek_Work\test\meshes\
/app/test/analyses/ -> E:\DeepSeek_Work\test\analyses\
/app/test/results/    -> E:\DeepSeek_Work\test\results\
```

## 7. 测试文件说明

已创建的测试文件：
- test_cube.inp - 简单立方体 CalculiX 输入
  - 8 个节点
  - 1 个单元
  - 底部固定
  - 顶部加载

## 8. 下一步

1. 熟悉界面
2. 运行第一个测试任务
3. 查看结果
4. 尝试不同的参数
5. 上传自己的几何文件

## 9. 故障排除

### 问题：任务不执行

```bash
# 检查 Celery worker
docker logs cae_celery_worker

# 检查 Redis
docker logs cae_redis

# 重启 worker
docker restart cae_celery_worker
```

### 问题：数据库错误

```bash
# 创建数据目录
docker exec -it cae_dashboard mkdir -p /data

# 重启 dashboard
docker restart cae_dashboard
```

### 问题：容器无法访问

```bash
# 检查容器状态
docker ps

# 查看端口
docker ps --filter "name=cae_" --format "{{.Names}}: {{.Ports}}"
```

## 10. 完整流程示例

```bash
# 1. 准备输入文件（已完成）
ls E:/DeepSeek_Work/test/analyses/test_cube.inp

# 2. 运行仿真
docker exec -it cae_calculix bash -c "cd /app/test/analyses && ccx -i test_cube"

# 3. 等待完成（约 1-2 秒）

# 4. 查看结果
docker exec -it cae_calculix bash -c "cat /app/test/analyses/test_cube.out"

# 5. 访问 Dashboard
# 打开浏览器访问 http://localhost:8501

# 6. 可视化结果
# 在"可视化"页面中输入结果文件路径
# 生成应力云图
```

---

需要更多信息？
查看：OPERATION_GUIDE.md
