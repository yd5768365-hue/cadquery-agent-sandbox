FROM python:3.10-slim

# 配置阿里云镜像
RUN echo "deb http://mirrors.aliyun.com/debian/ bookworm main contrib non-free" > /etc/apt/sources.list

# 安装 Gmsh
RUN apt-get update && apt-get install -y \
    gmsh \
    libgl1-mesa-glx \
    libglu1-mesa \
    && rm -rf /var/lib/apt/lists/*

# 安装 Python 包
RUN pip install --no-cache-dir -i https://pypi.tuna.tsinghua.edu.cn/simple \
    numpy \
    gmsh

WORKDIR /app

ENV OMP_NUM_THREADS=4

CMD ["tail", "-f", "/dev/null"]