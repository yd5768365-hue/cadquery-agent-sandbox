# GitHub 上传指南

## 步骤 1: 在 GitHub 上创建仓库

1. 访问 https://github.com/new
2. 仓库名称输入：`cae-digital-twin`
3. 设置仓库为 **Public** 或 **Private**
4. **不要** 勾选 "Initialize this repository with a README"
5. **不要** 勾选 "Add .gitignore"
6. **不要** 勾选 "Choose a license"
7. 点击 **Create repository**

## 步骤 2: 推送代码到 GitHub

执行以下命令（替换 `YOUR_USERNAME` 为你的 GitHub 用户名）：

```bash
cd E:\DeepSeek_Work
git remote add origin https://github.com/YOUR_USERNAME/cae-digital-twin.git
git push -u origin main
```

或者，如果你使用 SSH：

```bash
cd E:\DeepSeek_Work
git remote add origin git@github.com:YOUR_USERNAME/cae-digital-twin.git
git push -u origin main
```

## 步骤 3: 验证

推送成功后，访问你的仓库：
https://github.com/YOUR_USERNAME/cae-digital-twin

## 项目结构

```
cae-digital-twin/
├── docker/              # Docker Compose 配置
├── dashboard/           # Streamlit 仪表盘
├── server/             # 后端服务器
├── ml/                 # 机器学习模型
├── services/           # 外部服务集成
├── test/               # 测试文件和数据
├── config/             # 配置文件
├── scripts/            # 脚本工具
└── README.md           # 项目文档
```

## 快速开始

克隆仓库后：

```bash
cd docker
docker-compose up -d
```

访问 http://localhost:8501 查看仪表盘。

## 注意事项

- 项目已包含 `.gitignore` 文件
- 已初始化 Git 仓库并创建了初始提交
- 主分支已重命名为 `main`
- 包含完整的 Docker Compose 配置
